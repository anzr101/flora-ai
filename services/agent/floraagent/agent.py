"""The botanical agent: a tool-using, RAG-grounded reasoning loop over Claude.

Flow per turn:
  1. Send the conversation + tool schemas to Claude.
  2. If Claude requests tools, execute them (knowledge search / ML prediction)
     and feed the results back — repeat up to `max_tool_iterations`.
  3. Return the final grounded answer with citations and the tools it used.

If no ANTHROPIC_API_KEY is configured, the agent degrades to a retrieval-only
answer so the service still demonstrates RAG without an LLM bill.
"""

from __future__ import annotations

from flora_common import get_logger
from flora_common.schemas import AgentRequest, AgentResponse, Citation

from floraagent import tools as tools_mod
from floraagent.config import settings
from floraagent.retriever import retrieve_with_citations

log = get_logger("floraagent.agent")

SYSTEM_PROMPT = """You are FloraAI, an expert botanical assistant.

Rules:
- For any factual horticultural question, FIRST call `search_botanical_knowledge`
  and ground your answer in what it returns. Do not invent care facts.
- If the user gives sensor/care numbers, call `predict_plant_health` and explain
  the prediction and its top drivers in plain language.
- Be concise, practical, and specific. Prefer actionable steps.
- If the knowledge base does not cover something, say so briefly rather than
  guessing. Never claim a plant is safe for pets unless the knowledge supports it.
"""


def _offline_answer(message: str) -> AgentResponse:
    """Retrieval-only fallback when no LLM key is set."""
    context, citations = retrieve_with_citations(message)
    answer = (
        "LLM generation is disabled (no ANTHROPIC_API_KEY set), so here is the "
        "most relevant knowledge retrieved for your question:\n\n" + context
    )
    return AgentResponse(answer=answer, citations=citations, tools_used=["search_botanical_knowledge"])


def run_agent(req: AgentRequest) -> AgentResponse:
    if not settings.anthropic_api_key:
        log.warning("No ANTHROPIC_API_KEY; using retrieval-only fallback.")
        return _offline_answer(req.message)

    import anthropic

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    tools_mod.LAST_CITATIONS.clear()
    tools_used: list[str] = []

    messages = [{"role": m.role, "content": m.content} for m in req.history]
    messages.append({"role": "user", "content": req.message})

    final_text = ""
    for _ in range(settings.max_tool_iterations):
        resp = client.messages.create(
            model=settings.flora_agent_model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=tools_mod.TOOL_SCHEMAS,
            messages=messages,
        )

        if resp.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": resp.content})
            tool_results = []
            for block in resp.content:
                if block.type == "tool_use":
                    tools_used.append(block.name)
                    result = tools_mod.execute_tool(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )
            messages.append({"role": "user", "content": tool_results})
            continue

        # Normal completion — gather text blocks and stop.
        final_text = "".join(b.text for b in resp.content if b.type == "text")
        break
    else:
        final_text = final_text or "I wasn't able to complete the reasoning in time."

    citations = [Citation(**c) for c in _dedupe(tools_mod.LAST_CITATIONS)]
    return AgentResponse(
        answer=final_text.strip(),
        citations=citations,
        tools_used=sorted(set(tools_used)),
    )


def _dedupe(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for it in items:
        key = (it["source"], it["snippet"][:60])
        if key not in seen:
            seen.add(key)
            out.append(it)
    return out
