"""Selection keeps references to the original records."""


def select_records(records, minimum, limit):
    selected = []
    for record in records:
        score = record.get("score")
        if score is None:
            continue
        if score >= minimum:
            selected.append(record)
            if len(selected) >= limit:
                break
    return selected
