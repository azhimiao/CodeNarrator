"""Install or explicitly update the skill, retaining a ZIP backup on upgrade."""
import argparse
from contextlib import contextmanager
import os
from pathlib import Path
import shutil
import sys
import tempfile
import uuid
import zipfile


@contextmanager
def installation_stage(parent):
    # Windows tempfile directories have a private ACL. Publishing their children
    # by rename would keep that ACL and make the skill unreadable to the agent.
    # Ordinary sibling directories inherit the chosen skills parent's access.
    path = parent / (".code-narrator-stage-" + uuid.uuid4().hex)
    path.mkdir()
    try:
        yield path
    finally:
        if path.exists():
            if path.resolve().parent != parent:
                raise ValueError("临时安装路径越界")
            shutil.rmtree(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path)
    parser.add_argument("--update", action="store_true", help="更新已有 CodeNarrator，保留旧版 ZIP 备份")
    args = parser.parse_args()
    codex_base = Path(os.environ["CODEX_HOME"]) if os.environ.get("CODEX_HOME") else Path.home() / ".codex"
    parent = (args.skills_dir or codex_base / "skills").resolve()
    destination = parent / "code-narrator"
    source = Path(__file__).resolve().parents[1] / "code-narrator"
    if destination.exists() and not args.update:
        print(f"已有安装，未覆盖：{destination}", file=sys.stderr)
        return 1
    if destination.exists():
        if destination.is_symlink() or (hasattr(destination, "is_junction") and destination.is_junction()):
            raise ValueError("不更新链接目录")
        marker = destination / "SKILL.md"
        if not marker.is_file() or "name: code-narrator" not in marker.read_text(encoding="utf-8-sig"):
            raise ValueError("已有目录无法确认为 CodeNarrator，未修改")
    parent.mkdir(parents=True, exist_ok=True)
    with installation_stage(parent) as staged, tempfile.TemporaryDirectory(dir=parent, prefix=".code-narrator-install-") as temp:
        shutil.copytree(source, staged, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        backup = Path(temp) / "previous"
        archive_path = parent / ("code-narrator.backup-" + uuid.uuid4().hex[:12] + ".zip")
        # All directory moves stay inside the explicitly resolved skills parent.
        if (destination.resolve().parent != parent or backup.resolve().parent != Path(temp).resolve()
                or archive_path.resolve().parent != parent):
            raise ValueError("安装路径越界")
        had_previous = destination.exists()
        if had_previous:
            # Publish the recoverable archive before touching the installation.
            # A zip cannot be discovered as another active skill.
            with zipfile.ZipFile(Path(temp) / "previous.zip", "w", zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(destination.rglob("*")):
                    if path.is_file():
                        archive.write(path, path.relative_to(destination))
            (Path(temp) / "previous.zip").rename(archive_path)
            destination.rename(backup)
        try:
            staged.rename(destination)
        except BaseException:
            if had_previous:
                if destination.exists():
                    destination.rename(Path(temp) / "failed-install")
                backup.rename(destination)
            raise
        if had_previous:
            print(f"旧版备份：{archive_path}")
    print(f"已安装：{destination}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
