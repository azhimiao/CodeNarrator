"""Offline contracts of the pinned real project, without importing its ML stack.

Compile only the selected upstream definitions. No weights, network, environment
variables, filesystem operations or original top-level imports are executed.
"""
import ast
import contextlib
import io
import math
from pathlib import Path
from types import SimpleNamespace
import tokenize
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "research/visprog"


def definitions(path, names, namespace):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    selected = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names]
    if {node.name for node in selected} != set(names):
        raise AssertionError("Pinned contract definitions changed")
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)


@unittest.skipUnless((SOURCE / "engine/utils.py").exists(), "固定 VisProg 输入未准备；见 examples/VISPROG.md")
class VisProgContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        namespace = {"io": io, "tokenize": tokenize, "torch": SimpleNamespace(no_grad=contextlib.nullcontext),
                     "np": SimpleNamespace(mean=lambda xs: sum(xs)/len(xs), sum=sum, exp=math.exp)}
        definitions(SOURCE / "engine/step_interpreters.py", ["parse_step", "EvalInterpreter", "ResultInterpreter", "CountInterpreter",
                    "CropInterpreter", "CropAboveInterpreter", "CropBelowInterpreter", "ClassifyInterpreter"], namespace)
        definitions(SOURCE / "engine/utils.py", ["Program", "ProgramInterpreter", "ProgramGenerator"], namespace)
        cls.ns = namespace

    def blank(self, name):
        cls = self.ns[name]
        return cls.__new__(cls)

    def interpreter(self):
        obj = self.blank("ProgramInterpreter")
        obj.step_interpreters = {"EVAL": self.blank("EvalInterpreter"), "RESULT": self.blank("ResultInterpreter"), "COUNT": self.blank("CountInterpreter")}
        return obj

    def test_existing_program_state_result_does_not_stop_or_assign(self):
        initial, ignored = {"BOX": [1,2]}, {"BOX": []}
        program = self.ns["Program"]("N=COUNT(box=BOX)\nR=RESULT(var=N)\nK=EVAL(expr='{N} + 1')", initial)
        with contextlib.redirect_stdout(io.StringIO()):
            result, final = self.interpreter().execute(program, ignored)
        self.assertEqual(result, 3)
        self.assertIs(final, initial)
        self.assertNotIn("R", initial)
        self.assertNotIn("N", ignored)

    def test_failure_keeps_prior_mutation(self):
        initial = {"BOX": [1,2]}
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(KeyError):
            self.interpreter().execute("N=COUNT(box=BOX)\nR=RESULT(var=MISSING)", initial)
        self.assertEqual(initial["N"], 2)

    def test_count_inspection_failure_happens_after_count_is_written(self):
        initial = {"BOX": []}
        program = self.ns["Program"]("N=COUNT(box=BOX)", initial)
        counter = self.blank("CountInterpreter")
        self.assertEqual(counter.execute(program, False), 0)
        with self.assertRaises(KeyError):
            counter.execute(program, True)
        self.assertEqual(initial["N"], 0)

    def test_empty_relative_crops_and_base_aliasing(self):
        class Image:
            size = (100,80)
            def crop(self, box):
                return tuple(box)
        image = Image()
        for kind in ("CropAboveInterpreter", "CropBelowInterpreter"):
            obj = self.blank(kind)
            state = {"IMAGE": image, "BOX": []}
            text = "OUT=" + obj.step_name + "(image=IMAGE,box=BOX)"
            result = obj.execute(self.ns["Program"](text, state))
            self.assertEqual(result, (0,0,50,79))
        base = self.blank("CropInterpreter")
        self.assertIs(base.execute(self.ns["Program"]("OUT=CROP(image=IMAGE,box=BOX)", {"IMAGE":image,"BOX":[]})), image)

    def test_single_class_adds_other_and_nonpositive_class_has_empty_winner(self):
        seen = []
        class Scores:
            def cpu(self): return self
            def numpy(self): return self
            def argmax(self, axis): return [0]
            def __getitem__(self, key): return -0.2
        obj = self.blank("ClassifyInterpreter")
        obj.device = "cpu"
        def process(**kwargs):
            seen.extend(kwargs["text"])
            return {}
        obj.processor = process
        obj.calculate_sim = lambda inputs: Scores()
        candidate = {"box": [0,0,2,2]}
        image = SimpleNamespace(crop=lambda box: image)
        query = ["actor"]
        result = obj.query_obj(query, [candidate], image)
        self.assertEqual(result, [None])
        self.assertEqual(query, ["actor"])
        self.assertEqual(len(seen), 2)
        self.assertEqual(candidate["class"], "actor")
        self.assertEqual(candidate["class_score"], -20.0)

    def test_probability_omits_final_token_when_eos_absent(self):
        obj = self.blank("ProgramGenerator")
        obj.prob_agg = "mean"
        response = SimpleNamespace(choices=[{"logprobs":{"tokens":["a","b","c"], "token_logprobs":[-0.1,-0.2,-9.0]}}])
        self.assertAlmostEqual(obj.compute_prob(response), math.exp(-0.15))
        response.choices[0]["logprobs"]["tokens"] = []
        with self.assertRaises(UnboundLocalError):
            obj.compute_prob(response)

    def test_empty_classification_writes_empty_list_without_inference(self):
        obj = self.blank("ClassifyInterpreter")
        image = SimpleNamespace(crop=lambda box: None)
        state = {"IMAGE":image,"OBJECTS":[],"CATEGORIES":["actor"]}
        step = self.ns["Program"]("OUT=CLASSIFY(image=IMAGE,object=OBJECTS,categories=CATEGORIES)", state)
        self.assertEqual(obj.execute(step), [])
        self.assertEqual(state["OUT"], [])

    def test_duplicate_step_parameters_overwrite(self):
        result = self.ns["parse_step"]("X=EVAL(expr='1',expr='2')")
        self.assertEqual(result["args"], {"expr": "'2'"})

    def test_prompt_fragments_include_unexecutable_examples(self):
        tree = ast.parse((SOURCE / "prompts/gqa.py").read_text(encoding="utf-8"))
        examples = ast.literal_eval(next(node.value for node in tree.body if isinstance(node, ast.Assign)))
        self.assertEqual(len(examples), 19)
        self.assertEqual(sum(text.count("Program:") for text in examples), 20)
        malformed = [line for text in examples for line in text.splitlines() if "and else" in line]
        self.assertEqual(len(malformed), 2)
        for line in malformed:
            step = self.ns["Program"](line, {"ANSWER0": 1})
            with self.assertRaises(SyntaxError):
                self.blank("EvalInterpreter").execute(step)


if __name__ == "__main__":
    unittest.main()
