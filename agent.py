"""SiteHeat agent loop: Bedrock Converse API with tool use."""
import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import boto3
from tools import TOOL_FUNCTIONS, TOOL_SPECS

MODEL_ID = os.environ["SITEHEAT_MODEL_ID"]  # inference profile ID
MAX_TURNS = 8                                # stops runaway tool loops

client = boto3.client("bedrock-runtime", region_name="ap-southeast-2")

SYSTEM_PROMPT = """You are SiteHeat, a heat-risk information assistant for outdoor work crews in Victoria, Australia.
Today's date in Melbourne is {today}.

Rules:
- Every coordinate, temperature and heat-stress number you state must come from a tool result. Never estimate or adjust numbers yourself.
- The forecast is a gridded regional forecast with no site-level correction. Do not claim it is specific to the site.
- You are not yet connected to safety guidance. Do not state work/rest ratios, legal duties or specific controls. Say that guidance is not connected yet.
- You provide information, not instructions. Decisions about work on site rest with the site supervisor and the business responsible for the site.
- If a question is not about heat or weather at a work site in Victoria, say it is out of scope."""


def run_tool(tool_use: dict) -> dict:
    name, args = tool_use["name"], tool_use["input"]
    print(f"  -> {name}({json.dumps(args)})")  # trace for debugging and demos
    try:
        out = TOOL_FUNCTIONS[name](**args)
        content = [{"json": out}]
    except Exception as exc:
        content = [{"text": f"Tool error: {exc}"}]  # let the model explain the failure
    print(f"  <- {content[0]}")
    return {"toolResult": {"toolUseId": tool_use["toolUseId"], "content": content}}


def ask(question: str) -> str:
    today = datetime.now(ZoneInfo("Australia/Melbourne")).date().isoformat()
    messages = [{"role": "user", "content": [{"text": question}]}]
    tokens = 0

    for _ in range(MAX_TURNS):
        resp = client.converse(
            modelId=MODEL_ID,
            system=[{"text": SYSTEM_PROMPT.format(today=today)}],
            messages=messages,
            toolConfig={"tools": TOOL_SPECS},
            inferenceConfig={"temperature": 0},
        )
        tokens += resp["usage"]["totalTokens"]
        msg = resp["output"]["message"]
        messages.append(msg)  # model's turn goes into history

        if resp["stopReason"] != "tool_use":  # final answer, no more tools
            print(f"  [total tokens: {tokens}]")
            return "".join(b.get("text", "") for b in msg["content"])

        results = [run_tool(b["toolUse"]) for b in msg["content"] if "toolUse" in b]
        messages.append({"role": "user", "content": results})  # tool results go back as a user turn

    return "Stopped: too many tool calls without a final answer."


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "How hot will it get at a Docklands site tomorrow for heavy manual work?"
    print(ask(q))
