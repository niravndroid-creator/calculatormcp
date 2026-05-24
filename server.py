import json
from pathlib import Path
import sys
from typing import Union
from mcp.server.fastmcp import FastMCP

arguments = sys.argv[1:]

CONFIG_PATH = Path(__file__).parent / "config.json"
VALID_DATA_TYPES = {"integer", "float", "both"}
VALID_TRANSPORTS = {"stdio", "http", "sse"}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    data_type = config.get("data_type", "both")
    if data_type not in VALID_DATA_TYPES:
        raise ValueError(
            f"Invalid data_type '{data_type}'. Must be one of: {', '.join(VALID_DATA_TYPES)}"
        )
    transport = config.get("transport", "stdio")
    if transport not in VALID_TRANSPORTS:
        raise ValueError(
            f"Invalid transport '{transport}'. Must be one of: {', '.join(VALID_TRANSPORTS)}"
        )
    return config


def parse_number(value: Union[int, float], param_name: str, data_type: str) -> Union[int, float]:
    """Validate and coerce a number based on the configured data_type."""
    if data_type == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError(f"Parameter '{param_name}' must be an integer (data_type=integer).")
        return int(value)
    elif data_type == "float":
        if isinstance(value, bool):
            raise ValueError(f"Parameter '{param_name}' must be a float (data_type=float).")
        if not isinstance(value, (int, float)):
            raise ValueError(f"Parameter '{param_name}' must be a float (data_type=float).")
        return float(value)
    else:  # "both"
        if isinstance(value, bool):
            raise ValueError(f"Parameter '{param_name}' must be a number.")
        if not isinstance(value, (int, float)):
            raise ValueError(f"Parameter '{param_name}' must be an integer or float.")
        return value


config = load_config()
DATA_TYPE: str = config["data_type"]
TRANSPORT: str = config["transport"]

mcp = FastMCP(
    name="calculator",
    instructions=(
        f"A calculator MCP server supporting addition and multiplication. "
        f"Configured data_type: '{DATA_TYPE}'. "
        f"Accepted input types: "
        + ("integers only." if DATA_TYPE == "integer" else
           "floats only." if DATA_TYPE == "float" else
           "integers and floats.")
    ),
)


@mcp.tool(
    name="add",
    description=(
        "Add two numbers together. "
        f"Accepted data_type: '{DATA_TYPE}'. "
        "Provide 'a' and 'b' as the two operands."
    ),
)
def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Add two numbers (a + b)."""
    a = parse_number(a, "a", DATA_TYPE)
    b = parse_number(b, "b", DATA_TYPE)
    result = a + b
    return result


@mcp.tool(
    name="multiply",
    description=(
        "Multiply two numbers together. "
        f"Accepted data_type: '{DATA_TYPE}'. "
        "Provide 'a' and 'b' as the two operands."
    ),
)
def multiply(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    """Multiply two numbers (a * b)."""
    a = parse_number(a, "a", DATA_TYPE)
    b = parse_number(b, "b", DATA_TYPE)
    result = a * b
    return result


if __name__ == "__main__":
    if "stdio" in arguments:
        mcp.run()
    else:
        mcp.run(TRANSPORT, host="0.0.0.0", port=8000)
