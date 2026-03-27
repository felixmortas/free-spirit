from typing import Annotated

from langchain.messages import ToolMessage
from langgraph.types import Command
from langchain.tools import InjectedToolCallId, tool, ToolRuntime

@tool
async def check_website() -> str:
    """
    Check information on the hostel from the website
    """
    return ""


def get_tools() -> list:
    base_tools = [
        check_website,
    ]
        
    return base_tools