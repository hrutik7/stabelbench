"""Usage:
    python run.py                  # run all baselines and print a table
    python run.py --agent llm      # run your LLM agent (after you implement it)
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent / "src"))
from agents import AGENTS, agent_view  # noqa: E402
from grade import grade_task, summarize  # noqa: E402

DATA = pathlib.Path(__file__).parent / "data" / "tasks.jsonl"


def load_tasks():
    return [json.loads(line) for line in DATA.read_text().splitlines() if line.strip()]


def fmt(m):
    if m is None:
        return "   -   "
    lo, hi = m["ci"]
    return f"{m['rate']:.0%} [{lo:.0%}-{hi:.0%}] n={m['n']}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--agent", default=None, choices=list(AGENTS))
    args = p.parse_args()

    tasks = load_tasks()
    names = [args.agent] if args.agent else ["always_db", "always_page", "newest_wins"]

    print(f"{'agent':<13}{'accuracy':<26}{'stale-trust':<26}{'false-override':<26}")
    for name in names:
        agent = AGENTS[name]
        results = []
        for t in tasks:
            # Baselines peek at the full task; real agents only get agent_view().
            ans = agent(t) if name != "llm" else agent(agent_view(t))
            results.append(grade_task(t, ans))
        s = summarize(results)
        print(f"{name:<13}{fmt(s['accuracy']):<26}{fmt(s['stale_trust']):<26}{fmt(s['false_override']):<26}")


if __name__ == "__main__":
    main()
