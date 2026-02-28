#Pretty logging utilities for agent formatting
import json
from enum import Enum
from typing import Any


class Colors:
    RESET   = '\033[0m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    RED     = '\033[31m'
    GREEN   = '\033[32m'
    YELLOW  = '\033[33m'
    BLUE    = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN    = '\033[36m'
    WHITE   = '\033[37m'


class LogType(Enum):
    TOOL_CALL        = "▶ TOOL CALL"
    HUMAN_IN_LOOP    = "▶ HUMAN IN LOOP"
    TOOL_RESPONSE    = "▶ TOOL RESPONSE"
    TOOL_ERROR       = "▶ TOOL ERROR"
    LLM_RESPONSE     = "▶ LLM RESPONSE"
    LLM_ERROR        = "▶ LLM ERROR"
    MEMORY_SAVE      = "▶ MEMORY SAVED"
    MEMORY_RETRIEVE  = "▶ MEMORY RETRIEVED"
    PARSING_ERROR    = "▶ PARSING ERROR"
    AGENT_INFO       = "▶ AGENT INFO"


_COLOR_MAP = {
    LogType.TOOL_CALL:       Colors.BLUE,
    LogType.TOOL_RESPONSE:   Colors.GREEN,
    LogType.TOOL_ERROR:      Colors.RED,
    LogType.LLM_RESPONSE:    Colors.CYAN,
    LogType.LLM_ERROR:       Colors.RED,
    LogType.MEMORY_SAVE:     Colors.MAGENTA,
    LogType.MEMORY_RETRIEVE: Colors.MAGENTA,
    LogType.PARSING_ERROR:   Colors.RED,
    LogType.AGENT_INFO:      Colors.BLUE,
    LogType.HUMAN_IN_LOOP:   Colors.YELLOW,
}


def pretty_print(log_type: LogType, title: str = "", content: Any = None, is_error: bool = False):
    color = _COLOR_MAP.get(log_type, Colors.YELLOW)

    heading = f"{color}{Colors.BOLD}{log_type.value}"
    if title:
        heading += f" - {title}"
    heading += Colors.RESET

    print(heading)

    if content is not None:
        if isinstance(content, dict):
            try:
                formatted = json.dumps(content, indent=2)
            except Exception:
                formatted = str(content)
        else:
            formatted = str(content)
        print(f"{Colors.DIM}{formatted}{Colors.RESET}")


def pretty_error(title: str, error_msg: str, context: Any = None):
    print(f"{Colors.RED}{Colors.BOLD} ERROR - {title}{Colors.RESET}")

    if error_msg:
        print(f"{Colors.RED}{error_msg}{Colors.RESET}")

    if context:
        if isinstance(context, dict):
            try:
                formatted = json.dumps(context, indent=2)
            except Exception:
                formatted = str(context)
        else:
            formatted = str(context)
        print(f"{Colors.DIM}{formatted}{Colors.RESET}")


def section_header(title: str, emoji: str = "━"):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{emoji * 40}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{emoji * 40}{Colors.RESET}\n")


def inline_highlight(text: str, key: str, color: str = Colors.YELLOW) -> str:
    return text.replace(key, f"{Colors.BOLD}{color}{key}{Colors.RESET}")