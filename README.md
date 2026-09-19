# Avins

An advanced, proactive AI desktop assistant equipped with terminal and GUI automation capabilities.

## Features
- **Cross-Platform**: Supports Windows, macOS, and Linux (including Wayland and X11).
- **GUI Automation**: Abstracted GUI controls for typing, clicking, scrolling, and hotkeys.
- **Terminal Execution**: Safely execute shell commands directly on your system (with user confirmation).
- **Dynamic Tool Creation**: The agent can write its own Python tools and add them dynamically.

## Installation

```bash
pip install avins
```

## Usage

Run the assistant via the command line:

```bash
avins
```

This will start an interactive ReAct (Reason + Act) loop where you can instruct the assistant to perform various operations on your desktop.
