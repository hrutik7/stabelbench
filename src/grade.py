"""Graders: pure code, no LLM judge needed (that's why this eval is cheap to trust)."""
import random


def norm(s: str) -> str:
    return " ".join(str(s).lower().split())


def grade_task(task: dict, answer: dict) -> dict:
    ans = norm(answer["value"])
    gold = norm(task["gold"])
    out = {"id": task["id"], "type": task["type"], "correct": ans == gold,
           "stale_trust": None, "false_override": None}

    if task["type"] == "conflict":
        # The database is WRONG here. Did the agent still use it?
        # Like 'false positive': trusting something it should have rejected.
        out["stale_trust"] = ans == norm(task["db"]["value"])
    elif task["type"] == "db_right":
        # The page is old/misleading here. Did the agent follow it anyway?
        # Without this metric, 'always trust the page' would look perfect.
        out["false_override"] = ans == norm(task["page"]["claim"])
    return out


def bootstrap_ci(flags, n_boot=10000, seed=0):
    """95% interval for a rate, by resampling the per-task 0/1 outcomes (Lesson 2)."""
    if not flags:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    k = len(flags)
    rates = sorted(sum(rng.choices(flags, k=k)) / k for _ in range(n_boot))
    return rates[int(0.025 * n_boot)], rates[int(0.975 * n_boot) - 1]


def summarize(results: list[dict]) -> dict:
    def rate(key, only=None):
        flags = [int(r[key]) for r in results
                 if r[key] is not None and (only is None or r["type"] == only)]
        if not flags:
            return None
        return {"rate": sum(flags) / len(flags), "n": len(flags),
                "ci": bootstrap_ci(flags)}

    return {
        "accuracy": rate("correct"),
        "stale_trust": rate("stale_trust"),
        "false_override": rate("false_override"),
    }
