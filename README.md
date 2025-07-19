# 🏖️ Leave Management MCP Server

This project implements a **Leave Management System** using the [**Model Context Protocol (MCP)**](https://modelcontextprotocol.io/introduction), enabling secure interaction between Claude (an LLM) and your backend tools like `get_leave_balance`, `apply_leave`, and `get_leave_history`. The system communicates via STDIO and is fully integrated with Claude for Desktop.

---

## 📌 Features

* ✅ Check leave balances
* 📝 Apply for leave
* 📚 View leave history
* 🔒 Secure, structured communication using MCP
* 🤖 Works seamlessly with Claude via natural language

---

## 🧰 Tools Implemented

| Tool Name           | Description                             |
| ------------------- | --------------------------------------- |
| `get_leave_balance` | Returns remaining leave for an employee |
| `apply_leave`       | Submits a leave application             |
| `get_leave_history` | Shows the past leave records            |

All tools follow the structure:

```python
@mcp.tool()
def tool_name(data: Dict) -> str:
    ...
```

---

## ⚙️ Setup Instructions

### 1. Install Requirements

```bash
pip install uv
uv init leave_manager
pip install mcp
```

> Requires Python **3.10+** and `mcp[cli] >= 1.2.0`
[quick mcp guide](https://pypi.org/project/mcp/)
---

### 2. Project Structure

```
leave_manager/
├── leave_manager.py             # Your main MCP server script
└── claude_desktop_config.json  # Claude Desktop integration config (optional)
```

---

### 3. Write Your Server

Sample starter code:

```python
from typing import Dict
import logging
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("LeaveManager")
employee_leaves = {"E001": 18, "E002": 12}

@mcp.tool()
def get_leave_balance(data: Dict) -> str:
    emp_id = data.get("employee_id", "")
    if emp_id not in employee_leaves:
        return f"Error: Employee {emp_id} not found"
    return f"Employee {emp_id} has {employee_leaves[emp_id]} leave days remaining"

if __name__ == "__main__":
    mcp.run()
```

> ✅ **Use `logging.info()` instead of `print()` to avoid breaking STDIO**.

---

### 4. Run the Server

```bash
uv run leave_manager.py
```

---

## 🖥️ Claude Desktop Integration

Create or edit the following file:

```
%AppData%\Claude\claude_desktop_config.json
```

Add your server configuration:

```json
{
  "mcpServers": {
    "LeaveManager": {
      "command": "uv",
      "args": [
        "--directory",
        "C:\\ABSOLUTE\\PATH\\TO\\leave_manager",
        "run",
        "leave_manager.py"
      ]
    }
  }
}
```

> Use absolute paths and restart Claude Desktop after editing.

---

## 🔍 Testing Without Claude

You can directly call your tools in Python:

```python
print(get_leave_balance({"employee_id": "E001"}))
```

---

## 📡 MCP Request/Response Format

### 📤 Request (from Claude)

```json
{
  "method": "get_leave_balance",
  "params": {
    "data": {
      "employee_id": "E001"
    }
  },
  "id": 1
}
```

### 📥 Response (from your server)

```json
{
  "result": "Employee E001 has 18 leave days remaining",
  "id": 1
}
```

---

## 🧐 Understanding MCP

MCP enables three main components:

| Component    | Description                                |
| ------------ | ------------------------------------------ |
| 🛠️ Tools    | Callable functions for Claude interaction  |
| 📁 Resources | File-like data (e.g., logs, API responses) |
| 💬 Prompts   | Predefined templates for user guidance     |

---

## ⚠️ Debugging Tips

| Issue                      | Solution                                       |
| -------------------------- | ---------------------------------------------- |
| `print()` causes errors    | ❌ Never use `print()` in STDIO MCP servers     |
| Claude doesn't detect tool | ✅ Use absolute paths in config and restart app |
| Missing logs               | ✅ Use `logging.info()` or `logging.error()`    |

---

## 🧰 Internal Flow

```text
Claude → MCP JSON-RPC request → Server handles it → Returns result → Claude responds
```

---

## 📘 Example Tool Implementations

```python
@mcp.tool()
def apply_leave(data: Dict) -> str:
    emp_id = data.get("employee_id")
    days = data.get("days")
    if emp_id not in employee_leaves:
        return f"Error: Employee {emp_id} not found"
    if employee_leaves[emp_id] < days:
        return f"Error: Not enough leave balance"
    employee_leaves[emp_id] -= days
    return f"Leave applied for {days} days. Remaining: {employee_leaves[emp_id]}"

@mcp.tool()
def get_leave_history(data: Dict) -> str:
    # Replace this with actual history data
    return f"Leave history for {data.get('employee_id', 'unknown')}: 3 leaves taken in 2024."
```

---

## 🙌 Credits

* Based on [Anthropic's MCP SDK](https://docs.anthropic.com/claude/docs/mcp-overview)
* Uses `FastMCP` for rapid server setup
* Integrated with Claude for Desktop via STDIO transport

---

## ✅ Final Checklist

* [x] Tools implemented with `@mcp.tool()`
* [x] Uses `uv` as the package manager
* [x] STDIO-only server (no `print()` used)
* [x] Claude integration configured properly
* [x] Tested locally via direct Python calls

---

Reference Documentations:

[For Server Developers](https://modelcontextprotocol.io/quickstart/server#windows)

[Building MCP with LLMs](https://modelcontextprotocol.io/tutorials/building-mcp-with-llms)

[Debugging MCP](https://modelcontextprotocol.io/docs/tools/debugging)

Happy Coding! 💼🧠🌤️
