import asyncio
import json
import platform
from typing import Any, Dict, List, Optional

from config.asyncModel import async_client
from model.tool import Tool
from model.user import User
from tools.tools_defination import tool as tools_definition
from tools.tools import use_terminal, gui_control

user = User()
tool_log_history: dict[str, list[str]] = {}

_PLATFORM = platform.system()   

_OS_GUIDELINES: dict[str, str] = {
    "Windows": """\
### WINDOWS DESKTOP AUTOMATION GUIDELINES:
- Use PowerShell or cmd.exe commands for terminal actions.
  e.g., `Start-Process chrome "https://www.google.com/search?q=<query>"`
       or `start chrome "https://..."` (cmd style)
- For file paths always use Windows-style separators: C:\\Users\\...
- To get screen dimensions: `powershell "[System.Windows.Forms.Screen]::PrimaryScreen.Bounds"`
  or simply call gui_control with action='move' to a known position.
- For GUI control: pyautogui is used automatically — no extra tools needed.
""",
    "Darwin": """\
### macOS DESKTOP AUTOMATION GUIDELINES:
- Use bash/zsh commands for terminal actions.
  e.g., `open -a "Google Chrome" "https://www.google.com/search?q=<query>"`
- To get screen dimensions: `system_profiler SPDisplaysDataType | grep Resolution`
- For GUI control: pyautogui is used automatically.
""",
    "Linux": """\
### LINUX DESKTOP AUTOMATION GUIDELINES:
- Use bash commands for terminal actions.
  e.g., `google-chrome "https://www.google.com/search?q=<query>"`
  or `firefox "https://..."`
- To get screen geometry: `xdpyinfo | grep dimensions` or `xdotool getdisplaygeometry`
  Once you have dimensions (e.g. 1920x1080), compute center (960, 540) and
  call `gui_control(action='move', x=960, y=540)` immediately.
- On Wayland: ydotool is used automatically; on X11 pyautogui is used.
""",
}

_OS_SECTION = _OS_GUIDELINES.get(_PLATFORM, _OS_GUIDELINES["Linux"])

SYSTEM_PROMPT = f"""\
You are an advanced, proactive AI desktop assistant equipped with terminal and GUI automation capabilities.
You are running on: {_PLATFORM}

### OPERATIONAL FRAMEWORK: CHAIN OF THOUGHT & REACT
For every user instruction, you MUST reason step-by-step before acting:
1. **THINK (Reasoning & Plan)**: Analyze the user's intent. Break down the task into concrete, atomic steps.
2. **ACT (Tool Execution)**: Call the appropriate tool(s) for the next immediate step.
3. **OBSERVE & REFLECT**: Review the tool execution output. Did the step succeed? What information was obtained?
4. **REPEAT or FINISH**: Continue executing the remaining steps until the user's request is 100% fulfilled. Only provide your final message once all actions are physically completed.

{_OS_SECTION}
### GENERAL GUIDELINES:
- **Mouse & Screen Interaction**:
  - Once screen dimensions are obtained, immediately compute center coordinates and move there.
- **Do NOT hallucinate completion**:
  - Never state an action has been completed unless the corresponding tool call has been executed and confirmed.
- **Output Format**:
  - Keep final responses direct, concise, and informative in plain text (no unnecessary markdown).
"""


def execute_tool(name: str, arguments: str) -> str:
    """Safely executes a tool by name with JSON arguments and returns string result."""
    try:
        args: Dict[str, Any] = json.loads(arguments) if arguments else {}
    except json.JSONDecodeError as e:
        return f"Error: Failed to parse tool arguments for '{name}': {e}"

    if name == "use_terminal":
        command = args.get("text", "")
        if not command:
            return "Error: No command provided to use_terminal."

        res = use_terminal(command)
        terminal_tool = Tool(name="use_terminal")

        if res.returncode == 0:
            output = res.stdout.strip() if res.stdout else "(Command completed with no stdout output)"
            terminal_tool.message.append(f"Command '{command}' succeeded: {output}")
            result_str = f"Stdout:\n{output}"
        else:
            err = (res.stderr or res.stdout or "Command failed with non-zero exit code").strip()
            terminal_tool.message.append(f"Command '{command}' failed: {err} (Exit code {res.returncode})")
            result_str = f"Exit Code {res.returncode}\nStderr/Output:\n{err}"

        tool_log_history.setdefault(name, []).extend(terminal_tool.message)
        return result_str

    if name == "gui_control":
        gui_tool = Tool(name="gui_control")
        try:
            result_str = gui_control(
                action=args.get("action"),
                x=args.get("x"),
                y=args.get("y"),
                duration=args.get("duration", 0.0),
                clicks=args.get("clicks", 1),
                interval=args.get("interval", 0.0),
                button=args.get("button", "left"),
                text=args.get("text"),
                keys=args.get("keys"),
                scroll=args.get("scroll"),
            )
        except Exception as e:
            result_str = f"Error executing gui_control: {e}"

        gui_tool.message.append(f"gui_control({args}) -> {result_str}")
        tool_log_history.setdefault(name, []).extend(gui_tool.message)
        return result_str

    return f"Error: Tool '{name}' is not supported."


async def loop(message: str, max_iterations: int = 10):
    """Executes the agentic Chain-of-Thought loop with persistent multi-turn memory."""
    # Build context: system prompt + past conversation turns + current user message
    messages: List[Dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(user.last_messages)
    messages.append({"role": "user", "content": message})

    for iteration in range(1, max_iterations + 1):
        try:
            chat_completion = await async_client.chat.completions.create(
                messages=messages,
                tools=tools_definition,
                model="openai/gpt-oss-120b",
            )
        except Exception as e:
            print(f"\n[Model Error]: {e}")
            break

        msg = chat_completion.choices[0].message
        content = msg.content or ""

        if content.strip():
            print(f"\n[Thought / Plan]:\n{content.strip()}\n")

        # Handle tool execution
        if msg.tool_calls:
            assistant_msg: Dict[str, Any] = {
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": t.id,
                        "type": "function",
                        "function": {"name": t.function.name, "arguments": t.function.arguments},
                    }
                    for t in msg.tool_calls
                ],
            }
            messages.append(assistant_msg)

            for t in msg.tool_calls:
                function_name = t.function.name
                args_str = t.function.arguments
                print(f"[Action]: Calling tool '{function_name}' with args: {args_str}")

                tool_output = execute_tool(function_name, args_str)
                print(f"[Observation]:\n{tool_output}\n")

                messages.append({
                    "role": "tool",
                    "tool_call_id": t.id,
                    "name": function_name,
                    "content": tool_output,
                })
        else:
            # final completion reached without further tool calls
            print(f"[Assistant]:\n{content.strip()}\n")
            
            user.last_messages = messages[1:]
            user.last_messages.append({"role": "assistant", "content": content})
            return

    # if max iterations reached, persist current state
    user.last_messages = messages[1:]
    print("\n[Notice]: Maximum task iterations reached.")


async def main():
    print("=" * 60)
    print(f" Desktop Agent initialized  [{_PLATFORM}]")
    print("  Chain-of-Thought + ReAct loop enabled")
    print("  Type 'exit' or 'quit' to close.")
    print("=" * 60 + "\n")

    while True:
        try:
            msg = input("Enter Your Message: ").strip()
            if not msg:
                continue
            if msg.lower() in ("exit", "quit"):
                print("Goodbye!")
                break
            user.message = msg
            await loop(user.message)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break


def cli():
    asyncio.run(main())


if __name__ == "__main__":
    cli()

