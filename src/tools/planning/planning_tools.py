from langchain.tools import tool
from tools.planning.planning_runner import run_planning_pipeline


@tool
def run_planning_tool():
    """
    Runs full supply chain planning:
    forecast → optimization → dispatch → reporting → Excel output
    Use this when user asks to run planning.
    """

    result = run_planning_pipeline()

    return result