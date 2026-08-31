"""
Deep Agents Research Agent with Langfuse Tracing
================================================
Instruments the Deep Agent research quickstart with Langfuse tracing and
observability best practices.

Reference: https://langfuse.com/integrations/frameworks/langgraph
"""

from os import name

import os
import sys
from dotenv import load_dotenv
from typing import Literal
from tavily import TavilyClient

# 1. Load environment variables before initializing Langfuse/LLM clients
load_dotenv()

from deepagents import create_deep_agent
from langfuse import get_client, propagate_attributes
from langfuse.langchain import CallbackHandler

# 2. Initialize Langfuse CallbackHandler for LangChain / LangGraph tracing
langfuse_handler = CallbackHandler()
langfuse = get_client()


tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


# internet_search = {"google_search": {}}
# System prompt to steer the agent to be an expert researcher
research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

You have access to an internet search tool as your primary means of gathering information.

## `internet_search`

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""

# 3. Create the deep agent
agent = create_deep_agent(
    # model="openrouter:google/gemma-4-31b-it",
    model="google_genai:gemini-1.5-flash",
    tools=[internet_search],
    system_prompt="""You are an orchestrator demo agent. Your job is to showcase parallel subagents: spin up a small set of specialists at once, let each do a short piece of work, then synthesize and finish.

        For every user request:
        1. Write one short sentence explaining which specialists you will run in parallel.
        2. In the very next tool-calling turn, spawn exactly 2–3 subagents using multiple task() calls in that single turn. Each task must be independent so they can run in parallel.
        3. Give each subagent one narrow assignment — cover a single topic, option, or angle only.
        4. Never ask the user questions. Never spawn more than 3 subagents for one request. Do not delegate in multiple rounds unless a subagent failed.
        5. After all subagents return, write one concise synthesis and stop. No follow-up questions.

        Do not do the specialist work yourself. Delegate all research and analysis via task(), then synthesize the results.""",
    subagents=[
        {
            "name": "researcher",
            "description": "Delegate one focused research task: gather key facts on a single topic. Use for parallel coverage of distinct subjects.",
            "system_prompt": "You are a research specialist. Complete your assigned topic only. Return 3–5 bullet points with the most important facts. No preamble, no follow-up questions, and do not delegate further work.",
        },
        {
            "name": "analyzer",
            "description": "Delegate one focused analysis task: pros, cons, and trade-offs for a single option or approach. Use when comparing alternatives in parallel.",
            "system_prompt": "You are an analysis specialist. Complete your assigned option or angle only. Return 3–5 bullet points covering strengths, weaknesses, and key trade-offs. No preamble, no follow-up questions, and do not delegate further work.",
        },
        {
            "name": "writer",
            "description": "Delegate one focused summary task: turn findings on a single subtopic into clear prose. Use when each parallel subagent should produce readable copy.",
            "system_prompt": "You are a writing specialist. Complete your assigned subtopic only. Return a short paragraph or 3–5 bullets with the key takeaways. No preamble, no follow-up questions, and do not delegate further work.",
        },
    ],
)


def run_agent_with_tracing(
    query: str = "What is LangGraph?",
    user_id: str = "user-123",
    session_id: str = "session-quickstart",
):
    """
    Runs the deep agent with propagated trace metadata, tags, and Langfuse callback.
    """
    print(f"🚀 Running Deep Agent with query: {query}")

    with propagate_attributes(
        trace_name="Deep Agents Research",
        user_id=user_id,
        session_id=session_id,
        tags=["deepagents", "langgraph", "research-quickstart"],
        metadata={"framework": "langgraph", "agent": "deepagents-quickstart"},
    ):
        result = agent.invoke(
            {"messages": [{"role": "user", "content": query}]},
            config={
                "callbacks": [langfuse_handler],
                "run_name": "execute-research-task",
            },
        )

    # 4. Flush events to Langfuse before script exit in short-lived executions
    langfuse.flush()
    return result


def run_agent(
    query: str = "What is LangGraph?",
):
    """
    Runs the deep agent with propagated trace metadata, tags, and Langfuse callback.
    """
    print(f"🚀 Running Deep Agent with query: {query}")

    return agent.invoke(
        {"messages": [{"role": "user", "content": query}]},
    )


if __name__ == "__main__":
    user_query = sys.argv[1] if len(sys.argv) > 1 else "What is LangGraph?"
    stream = agent.stream_events(
        {
            "messages": [{"role": "user", "content": user_query}],
        },
        version="v3",
    )

    for message in stream.messages:
        for delta in message.text:
            print(delta, end="", flush=True)

    for message in stream:
        print(message)
