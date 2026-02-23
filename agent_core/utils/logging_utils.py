"""Pretty logging utilities for agent formatting"""
import json
from enum import Enum
from typing import Any

class Colors:
    """ANSI color codes"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Background colors (optional)
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'

class LogType(Enum):
    """Log type categories"""
    TOOL_CALL = "▶ TOOL CALL"
    HUMAN_IN_LOOP = "▶ HUMAN IN LOOP"
    TOOL_RESPONSE = "▶ TOOL RESPONSE"
    TOOL_ERROR = "▶ TOOL ERROR"
    LLM_RESPONSE = "▶ LLM RESPONSE"
    LLM_ERROR = "▶ LLM ERROR"
    MEMORY_SAVE = "▶ MEMORY SAVED"
    MEMORY_RETRIEVE = "▶ MEMORY RETRIEVED "
    PARSING_ERROR = "▶ PARSING ERROR"
    AGENT_INFO = "▶  AGENT INFO"

def _get_color_for_type(log_type: LogType) -> str:
    """Get appropriate color for log type"""
    color_map = {
        LogType.TOOL_CALL: Colors.BLUE,
        LogType.TOOL_RESPONSE: Colors.GREEN,
        LogType.TOOL_ERROR: Colors.RED,
        LogType.LLM_RESPONSE: Colors.CYAN,
        LogType.LLM_ERROR: Colors.RED,
        LogType.MEMORY_SAVE: Colors.MAGENTA,
        LogType.MEMORY_RETRIEVE: Colors.MAGENTA,
        LogType.PARSING_ERROR: Colors.RED,
        LogType.AGENT_INFO: Colors.BLUE,
        LogType.HUMAN_IN_LOOP: Colors.YELLOW,
    }
    return color_map.get(log_type, Colors.YELLOW)

def pretty_print(log_type: LogType, title: str = "", content: Any = None, is_error: bool = False):
    """Print formatted log message"""
    color = _get_color_for_type(log_type)
    reset = Colors.RESET
    bold = Colors.BOLD
    dim = Colors.DIM
    
    # Header
    header = f"{color}{bold}{log_type.value}"
    if title:
        header += f" - {title}"
    header += reset
    
    print(f"\n{header}")
    print(f"{color}{'─' * 80}{reset}")
    
    # Content
    if content is not None:
        if isinstance(content, dict):
            try:
                formatted = json.dumps(content, indent=2)
            except:
                formatted = str(content)
        elif isinstance(content, str):
            formatted = content
        else:
            formatted = str(content)
        
        print(f"{dim}{formatted}{reset}")
    
    print(f"{color}{'─' * 80}{reset}\n")

def pretty_error(title: str, error_msg: str, context: Any = None):
    """Print formatted error message"""
    print(f"\n{Colors.RED}{Colors.BOLD} ERROR - {title}{Colors.RESET}")
    print(f"{Colors.RED}{'─' * 80}{Colors.RESET}")
    
    if error_msg:
        print(f"{Colors.RED}{error_msg}{Colors.RESET}")
    
    if context:
        print(f"\n{Colors.DIM}Context:{Colors.RESET}")
        if isinstance(context, dict):
            try:
                formatted = json.dumps(context, indent=2)
            except:
                formatted = str(context)
        else:
            formatted = str(context)
        print(f"{Colors.DIM}{formatted}{Colors.RESET}")
    
    print(f"{Colors.RED}{'─' * 80}{Colors.RESET}\n")

def section_header(title: str, emoji: str = "━"):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{emoji * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{emoji * 80}{Colors.RESET}\n")

def inline_highlight(text: str, key: str, color: str = Colors.YELLOW) -> str:
    """Highlight a key in text inline"""
    return text.replace(key, f"{Colors.BOLD}{color}{key}{Colors.RESET}")
