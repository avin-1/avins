"""
Tool-creation agent.

Given a task, asks an LLM whether a new tool is needed. If so, it
creates the tool (installing dependencies via use_terminal first),
persists it into tools.py / tools_defination.py, and makes it callable
immediately. If not, it just returns the model's answer.
"""

import asyncio
import importlib
import json
from pathlib import Path
from pprint import pformat
import multiprocessing
from config.asyncModel import async_client
from tools.tools_defination import tool
from tools.tools import use_terminal
import tools.tools as tools_module
from logger.logs import logging
import threading

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_FILE = PROJECT_ROOT / "tools" / "tools.py"
TOOLS_DEFINITION_FILE = PROJECT_ROOT / "tools" / "tools_defination.py"

MAX_TURNS = 6  

SYSTEM_PROMPT = """Your job is to make a tool for a master agent.

The tool is a Python function, if needed, that uses lightweight and
safe libraries. Any library you use must first be installed with the
use_terminal tool, and the code you return must contain the imports
for those libraries.

No mistakes. This is a high stake task.

Always respond with ONLY a JSON object, nothing else (no prose, no
Markdown fences), in exactly this shape:

{
    "tool": null,
    "defination": null,
    "result": null
}

- If the task requires a NEW tool: set "tool" to the full Python
  source of the function, and "defination" to its OpenAI-style tool
  definition (with "type", "function.name", "function.description",
  "function.parameters"). Leave "result" null.
- If the task does NOT require a new tool: leave "tool" and
  "defination" null, and put your final answer in "result".

You may also make a tool call yourself (e.g. use_terminal to install
a dependency) instead of returning JSON, when you need to act before
you can answer.
"""

tool_call_history = []


def build_history_note() -> str:
    if not tool_call_history:
        return "No tools have been called yet."
    return (
        "Here is the tool call history so far:\n"
        f"{tool_call_history}\n\n"
        "If the requested operation has already been executed "
        "successfully, do not run it again."
    )


async def chat_completion(msg: str):
    return await async_client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": msg},
            {"role": "system", "content": build_history_note()},
        ],
        tools=tool,
        model="openai/gpt-oss-120b",
    )


def save_tool_definition(tool_list):
    """Persist tool definitions into tools_defination.py."""
    content = f"tool = {pformat(tool_list, indent=4)}\n\n__all__ = [\"tool\"]\n"
    TOOLS_DEFINITION_FILE.write_text(content)


def execute_tool(name: str, arguments: str) -> str:
    """Execute a tool by name with JSON arguments."""
    try:
        args = json.loads(arguments) if arguments else {}
    except json.JSONDecodeError as e:
        return f"Error: could not parse arguments for '{name}': {e}"

    if name == "use_terminal":
        command = args.get("text", "")
        res = use_terminal(command)
        if res.returncode == 0:
            output = res.stdout or "(Command executed successfully with no output)"
            return f"Stdout:\n{output}"
        return f"Stderr:\n{res.stderr}"

    importlib.reload(tools_module)
    func = getattr(tools_module, name, None)
    if func is None:
        return f"Error: Tool '{name}' is not supported."

    try:
        return str(func(**args))
    except Exception as e:
        return f"Error while executing '{name}': {e}"


def create_tool(task: str) -> str:
    """
    One turn with the model. Returns "Tool Called", "Success", or "Error".
    """
    try:
        chat = asyncio.run(chat_completion(task))
    except Exception as e:
        print("API call failed:", e)
        return "Error"

    message = chat.choices[0].message
    content = message.content

    if message.tool_calls:
        for call in message.tool_calls:
            output = execute_tool(call.function.name, call.function.arguments)
            tool_call_history.append({call.function.name: output})
        return "Tool Called"

    if content is None:
        print("No response received from model.")
        return "Error"

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        print("Result:", content)
        return "Success"

    tool_code = parsed.get("tool")
    definition = parsed.get("defination")
    result_text = parsed.get("result")

    if tool_code and definition:
        with open(TOOLS_FILE, "a") as f:
            f.write("\n\n")
            f.write(tool_code)

        tool.append(definition)
        save_tool_definition(tool)

        print("Tool created successfully!")
        return "Success"

    if result_text:
        print("Result:", result_text)
        return "Success"

    print("Model returned neither a tool nor a result.")
    return "Error"


def wrapper(task: str) -> None:
    res = None
    for _ in range(MAX_TURNS):
        res = create_tool(task)
        if res != "Tool Called":
            print("Success")
            break
    else:
        print(f"Stopped after {MAX_TURNS} turns without a final answer.")
        return

    if res == "Success":
        print("Task completed successfully.")
    else:
        print("Task execution failed.")


def create(user_task: str):
    p = threading.Thread(target=wrapper, args=(user_task,))
    p.start()
    p.join(timeout=120) 
    if p.is_alive():
        p.terminate()

if __name__ == "__main__":
    user_task = input("Enter a task: ")
    create(user_task)