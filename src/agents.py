"""Agents under test.

Contract (the thing that makes a benchmark pluggable):
    agent(view) -> {"value": str, "source": "db" | "page"}

`view` is what the agent is ALLOWED to see. It never includes the gold
answer or the structured `claim` field (that would be leaking the key).
"""


def agent_view(task: dict) -> dict:
    return {
        "question": task["question"],
        "db": task["db"],                                   # value + as_of date
        "page": {"text": task["page"]["text"], "as_of": task["page"]["as_of"]},
    }


# --- Dumb baselines -----------------------------------------------------
# These need the full task (they peek at `claim`). They exist ONLY to give
# the scores context. If a dumb rule scores 100%, the task is too easy.

def always_db(task: dict) -> dict:
    """Trust the database every time (the failure mode in the PipelineBench post)."""
    return {"value": task["db"]["value"], "source": "db"}


def always_page(task: dict) -> dict:
    """Trust the page every time. Looks great on conflicts, fails when the page is old."""
    return {"value": task["page"]["claim"], "source": "page"}


def newest_wins(task: dict) -> dict:
    """Trust whichever source has the later as_of date. A rule-based 'ceiling'.

    In this v0 every task states its dates, so this scores 100%. That tells you
    the question is really 'can the model reason about dates?'. A harder v1 would
    hide or blur the dates.
    """
    if task["page"]["as_of"] >= task["db"]["as_of"]:
        return {"value": task["page"]["claim"], "source": "page"}
    return {"value": task["db"]["value"], "source": "db"}


# --- Your LLM agent (you fill this in) ----------------------------------

def llm_agent(view: dict) -> dict:
    """Wire up your model provider here.

    `view` is already filtered by agent_view() (no gold, no structured claim).
    Build a prompt from it, ask for JSON {"value", "source"}, parse it, and
    return it. Pin the model name and temperature in the README.
    """
    raise NotImplementedError("Implement call to your LLM provider in llm_agent()")


AGENTS = {
    "always_db": always_db,
    "always_page": always_page,
    "newest_wins": newest_wins,
    "llm": llm_agent,
}
