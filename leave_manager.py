from mcp.server.fastmcp import FastMCP
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LeaveType(str, Enum):
    CASUAL = "casual"
    SICK = "sick"
    EARNED = "earned"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    UNPAID = "unpaid"

# Embedded employee data
EMPLOYEE_DATA = {
    "E001": {
        "name": "John Smith",
        "department": "Engineering",
        "balance": {
            "casual": 12,
            "sick": 10,
            "earned": 15,
            "maternity": 0,
            "paternity": 5
        },
        "history": [
            {"date": "2024-12-25", "type": "casual", "status": "approved", "days": 1, "reason": "Christmas"},
            {"date": "2025-01-01", "type": "casual", "status": "approved", "days": 1, "reason": "New Year"}
        ]
    },
    "E002": {
        "name": "Emily Johnson",
        "department": "Marketing",
        "balance": {
            "casual": 15,
            "sick": 8,
            "earned": 20,
            "maternity": 12,
            "paternity": 0
        },
        "history": [
            {"date": "2025-02-14", "type": "casual", "status": "approved", "days": 1, "reason": "Valentine's Day"}
        ]
    },
    "E003": {
        "name": "Michael Brown",
        "department": "Sales",
        "balance": {
            "casual": 10,
            "sick": 12,
            "earned": 18,
            "maternity": 0,
            "paternity": 5
        },
        "history": [
            {"date": "2025-01-15", "type": "sick", "status": "approved", "days": 2, "reason": "Flu"},
            {"date": "2025-03-01", "type": "earned", "status": "approved", "days": 5, "reason": "Vacation"}
        ]
    },
    "E004": {
        "name": "Sarah Davis",
        "department": "HR",
        "balance": {
            "casual": 18,
            "sick": 15,
            "earned": 22,
            "maternity": 0,
            "paternity": 0
        },
        "history": []
    },
    "E005": {
        "name": "Robert Wilson",
        "department": "Engineering",
        "balance": {
            "casual": 8,
            "sick": 10,
            "earned": 12,
            "maternity": 0,
            "paternity": 0
        },
        "history": [
            {"date": "2024-12-24", "type": "casual", "status": "approved", "days": 1, "reason": "Christmas Eve"},
            {"date": "2025-01-02", "type": "casual", "status": "approved", "days": 1, "reason": "Holiday"},
            {"date": "2025-03-15", "type": "sick", "status": "approved", "days": 3, "reason": "Medical procedure"}
        ]
    },
    "E006": {
        "name": "Jennifer Miller",
        "department": "Finance",
        "balance": {
            "casual": 20,
            "sick": 12,
            "earned": 25,
            "maternity": 0,
            "paternity": 0
        },
        "history": [
            {"date": "2025-01-26", "type": "casual", "status": "pending", "days": 2, "reason": "Family event"}
        ]
    },
    "E007": {
        "name": "David Taylor",
        "department": "Operations",
        "balance": {
            "casual": 14,
            "sick": 10,
            "earned": 15,
            "maternity": 0,
            "paternity": 0
        },
        "history": [
            {"date": "2025-02-28", "type": "casual", "status": "approved", "days": 1, "reason": "Weekend getaway"},
            {"date": "2025-03-01", "type": "casual", "status": "approved", "days": 1, "reason": "Weekend getaway"},
            {"date": "2025-04-18", "type": "sick", "status": "approved", "days": 1, "reason": "Doctor appointment"}
        ]
    },
    "E008": {
        "name": "Jessica Anderson",
        "department": "Engineering",
        "balance": {
            "casual": 16,
            "sick": 12,
            "earned": 18,
            "maternity": 0,
            "paternity": 0
        },
        "history": [
            {"date": "2025-03-08", "type": "casual", "status": "approved", "days": 1, "reason": "Women's Day"}
        ]
    },
    "E009": {
        "name": "Thomas Martinez",
        "department": "Sales",
        "balance": {
            "casual": 10,
            "sick": 8,
            "earned": 12,
            "maternity": 0,
            "paternity": 0
        },
        "history": [
            {"date": "2025-01-10", "type": "sick", "status": "approved", "days": 1, "reason": "Cold"},
            {"date": "2025-02-15", "type": "casual", "status": "approved", "days": 1, "reason": "Personal"},
            {"date": "2025-04-05", "type": "sick", "status": "approved", "days": 2, "reason": "Fever"}
        ]
    },
    "E010": {
        "name": "Lisa Robinson",
        "department": "Marketing",
        "balance": {
            "casual": 18,
            "sick": 15,
            "earned": 20,
            "maternity": 0,
            "paternity": 0
        },
        "history": [
            {"date": "2025-05-15", "type": "casual", "status": "pending", "days": 3, "reason": "Summer vacation"}
        ]
    }
}

# Initialize with embedded data
employee_leaves = {k: v.copy() for k, v in EMPLOYEE_DATA.items()}

mcp = FastMCP("LeaveManager")

def extract_field(data: Dict, field_name: str, default=None) -> Any:
    """Extract field from either direct or nested data structure"""
    try:
        # Try direct access first
        if field_name in data:
            return data[field_name]
        # Try nested in 'data' object
        if 'data' in data and isinstance(data['data'], dict):
            return data['data'].get(field_name, default)
        return default
    except Exception as e:
        logger.error(f"Error extracting {field_name}: {str(e)}")
        return default

def validate_date(date_str: str) -> Optional[datetime]:
    """Validate date format (YYYY-MM-DD)"""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None

@mcp.tool()
def get_leave_balance(data: Dict) -> str:
    """Get remaining leave balance for an employee by leave type"""
    try:
        emp_id = extract_field(data, 'employee_id')
        if not emp_id:
            return "Error: employee_id field is required"
        
        if emp_id not in employee_leaves:
            return f"Error: Employee {emp_id} not found. Available: {', '.join(employee_leaves.keys())}"
        
        leave_type = extract_field(data, 'leave_type')
        employee = employee_leaves[emp_id]
        
        if leave_type:
            if leave_type not in employee["balance"]:
                return f"Error: Invalid leave type. Valid types: {', '.join(employee['balance'].keys())}"
            return f"{emp_id} ({employee['name']}) has {employee['balance'][leave_type]} {leave_type} leave days remaining"
        
        # Return all balances if no specific type requested
        balances = [f"{k}: {v}" for k, v in employee["balance"].items()]
        return f"{emp_id} ({employee['name']}) leave balances:\n" + "\n".join(balances)
    except Exception as e:
        logger.error(f"Error in get_leave_balance: {str(e)}")
        return "Error processing request"

@mcp.tool()
def apply_leave(data: Dict) -> str:
    """Apply for leave on specific dates"""
    try:
        emp_id = extract_field(data, 'employee_id')
        start_date = extract_field(data, 'start_date')
        end_date = extract_field(data, 'end_date', start_date)
        leave_type = extract_field(data, 'leave_type', LeaveType.CASUAL)
        reason = extract_field(data, 'reason', "")
        
        if not emp_id:
            return "Error: employee_id field is required"
        if not start_date:
            return "Error: start_date field is required"
        if emp_id not in employee_leaves:
            return f"Error: Employee {emp_id} not found"
        
        # Validate dates
        start = validate_date(start_date)
        end = validate_date(end_date) if end_date else start
        if not start or not end:
            return "Error: Invalid date format (use YYYY-MM-DD)"
        if start > end:
            return "Error: start_date cannot be after end_date"
        
        # Calculate business days (excluding weekends)
        delta = end - start
        leave_days = 0
        current = start
        while current <= end:
            if current.weekday() < 5:  # Monday to Friday
                leave_days += 1
            current += timedelta(days=1)
        
        employee = employee_leaves[emp_id]
        
        # Check leave balance
        if leave_type not in employee["balance"]:
            return f"Error: Invalid leave type. Valid types: {', '.join(employee['balance'].keys())}"
        
        if employee["balance"][leave_type] < leave_days:
            return (
                f"Error: Insufficient {leave_type} leave balance. "
                f"Requested {leave_days}, available {employee['balance'][leave_type]}"
            )
        
        # Apply leave
        leave_entry = {
            "date": start_date,
            "end_date": end_date if end_date != start_date else None,
            "type": leave_type,
            "status": "pending",
            "reason": reason,
            "days": leave_days,
            "applied_on": datetime.now().strftime("%Y-%m-%d")
        }
        
        employee["history"].append(leave_entry)
        employee["balance"][leave_type] -= leave_days
        
        return (
            f"Leave application submitted for {emp_id} ({employee['name']}):\n"
            f"Type: {leave_type}\n"
            f"Dates: {start_date} to {end_date}\n"
            f"Days: {leave_days}\n"
            f"New balance: {employee['balance'][leave_type]}"
        )
    except Exception as e:
        logger.error(f"Error in apply_leave: {str(e)}")
        return "Error processing leave request"

@mcp.tool()
def get_leave_history(data: Dict) -> str:
    """Get leave history for an employee with filtering options"""
    try:
        emp_id = extract_field(data, 'employee_id')
        leave_type = extract_field(data, 'leave_type')
        status = extract_field(data, 'status')
        year = extract_field(data, 'year')
        
        if not emp_id:
            return "Error: employee_id field is required"
        if emp_id not in employee_leaves:
            return f"Error: Employee {emp_id} not found"
        
        history = employee_leaves[emp_id]["history"]
        if not history:
            return f"No leave history found for {emp_id}"
        
        # Apply filters
        filtered = []
        for entry in history:
            if leave_type and entry["type"] != leave_type:
                continue
            if status and entry["status"] != status:
                continue
            if year and not entry["date"].startswith(year):
                continue
            filtered.append(entry)
        
        if not filtered:
            return "No matching leave records found"
        
        result = []
        for entry in filtered:
            date_range = f"{entry['date']} to {entry['end_date']}" if entry.get('end_date') else entry['date']
            line = (
                f"{date_range}: {entry['type']} leave ({entry['status']}), "
                f"{entry['days']} day(s), Reason: {entry.get('reason', 'none')}"
            )
            result.append(line)
        
        return f"Leave history for {emp_id}:\n" + "\n".join(result)
    except Exception as e:
        logger.error(f"Error in get_leave_history: {str(e)}")
        return "Error fetching leave history"

@mcp.tool()
def approve_leave(data: Dict) -> str:
    """Approve a pending leave request"""
    try:
        emp_id = extract_field(data, 'employee_id')
        leave_date = extract_field(data, 'leave_date')
        
        if not emp_id:
            return "Error: employee_id field is required"
        if not leave_date:
            return "Error: leave_date field is required"
        if emp_id not in employee_leaves:
            return f"Error: Employee {emp_id} not found"
        
        employee = employee_leaves[emp_id]
        for entry in employee["history"]:
            if entry["date"] == leave_date and entry["status"] == "pending":
                entry["status"] = "approved"
                return f"Leave on {leave_date} for {emp_id} has been approved"
        
        return f"No pending leave found on {leave_date} for {emp_id}"
    except Exception as e:
        logger.error(f"Error in approve_leave: {str(e)}")
        return "Error approving leave"

@mcp.tool()
def reject_leave(data: Dict) -> str:
    """Reject a pending leave request and restore balance"""
    try:
        emp_id = extract_field(data, 'employee_id')
        leave_date = extract_field(data, 'leave_date')
        reason = extract_field(data, 'reason', "Not specified")
        
        if not emp_id:
            return "Error: employee_id field is required"
        if not leave_date:
            return "Error: leave_date field is required"
        if emp_id not in employee_leaves:
            return f"Error: Employee {emp_id} not found"
        
        employee = employee_leaves[emp_id]
        for entry in employee["history"]:
            if entry["date"] == leave_date and entry["status"] == "pending":
                leave_type = entry["type"]
                days = entry["days"]
                employee["balance"][leave_type] += days
                entry["status"] = "rejected"
                entry["reject_reason"] = reason
                return (
                    f"Leave on {leave_date} for {emp_id} has been rejected.\n"
                    f"Reason: {reason}\n"
                    f"Restored {days} {leave_type} leave days"
                )
        
        return f"No pending leave found on {leave_date} for {emp_id}"
    except Exception as e:
        logger.error(f"Error in reject_leave: {str(e)}")
        return "Error rejecting leave"

@mcp.tool()
def cancel_leave(data: Dict) -> str:
    """Cancel an approved leave and restore balance"""
    try:
        emp_id = extract_field(data, 'employee_id')
        leave_date = extract_field(data, 'leave_date')
        
        if not emp_id:
            return "Error: employee_id field is required"
        if not leave_date:
            return "Error: leave_date field is required"
        if emp_id not in employee_leaves:
            return f"Error: Employee {emp_id} not found"
        
        employee = employee_leaves[emp_id]
        for entry in employee["history"]:
            if entry["date"] == leave_date and entry["status"] == "approved":
                leave_type = entry["type"]
                days = entry["days"]
                employee["balance"][leave_type] += days
                entry["status"] = "cancelled"
                return (
                    f"Leave on {leave_date} for {emp_id} has been cancelled.\n"
                    f"Restored {days} {leave_type} leave days"
                )
        
        return f"No approved leave found on {leave_date} for {emp_id}"
    except Exception as e:
        logger.error(f"Error in cancel_leave: {str(e)}")
        return "Error cancelling leave"

@mcp.tool()
def get_upcoming_leaves(data: Dict) -> str:
    """Get upcoming approved leaves with filtering options"""
    try:
        department = extract_field(data, 'department')
        leave_type = extract_field(data, 'leave_type')
        days_ahead = int(extract_field(data, 'days_ahead', 30))
        
        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)
        upcoming = []
        
        for emp_id, employee in employee_leaves.items():
            if department and employee["department"] != department:
                continue
                
            for entry in employee["history"]:
                if entry["status"] != "approved":
                    continue
                
                entry_date = validate_date(entry["date"])
                if not entry_date:
                    continue
                    
                if leave_type and entry["type"] != leave_type:
                    continue
                
                if today <= entry_date <= end_date:
                    date_str = f"{entry['date']} to {entry['end_date']}" if entry.get('end_date') else entry['date']
                    upcoming.append(
                        f"{emp_id} ({employee['name']}): {date_str}, "
                        f"{entry['type']} leave, {entry['days']} day(s)"
                    )
        
        if not upcoming:
            return "No upcoming leaves found"
        
        return f"Upcoming leaves (next {days_ahead} days):\n" + "\n".join(upcoming)
    except Exception as e:
        logger.error(f"Error in get_upcoming_leaves: {str(e)}")
        return "Error fetching upcoming leaves"

@mcp.tool()
def add_employee(data: Dict) -> str:
    """Add a new employee to the system"""
    try:
        emp_id = extract_field(data, 'employee_id')
        name = extract_field(data, 'name')
        department = extract_field(data, 'department')
        
        if not emp_id:
            return "Error: employee_id field is required"
        if not name:
            return "Error: name field is required"
        if not department:
            return "Error: department field is required"
        if emp_id in employee_leaves:
            return f"Error: Employee {emp_id} already exists"
        
        # Default leave balances
        employee_leaves[emp_id] = {
            "name": name,
            "department": department,
            "balance": {
                "casual": 12,
                "sick": 10,
                "earned": 15,
                "maternity": 0,
                "paternity": 0
            },
            "history": []
        }
        
        return f"Employee {emp_id} ({name}) added to {department} department"
    except Exception as e:
        logger.error(f"Error in add_employee: {str(e)}")
        return "Error adding employee"

@mcp.tool()
def update_leave_balance(data: Dict) -> str:
    """Update an employee's leave balance (admin only)"""
    try:
        emp_id = extract_field(data, 'employee_id')
        leave_type = extract_field(data, 'leave_type')
        days = int(extract_field(data, 'days'))
        
        if not emp_id:
            return "Error: employee_id field is required"
        if not leave_type:
            return "Error: leave_type field is required"
        if emp_id not in employee_leaves:
            return f"Error: Employee {emp_id} not found"
        
        employee = employee_leaves[emp_id]
        if leave_type not in employee["balance"]:
            return f"Error: Invalid leave type. Valid types: {', '.join(employee['balance'].keys())}"
        
        employee["balance"][leave_type] += days
        return (
            f"Updated {emp_id}'s {leave_type} leave balance by {days} days.\n"
            f"New balance: {employee['balance'][leave_type]}"
        )
    except Exception as e:
        logger.error(f"Error in update_leave_balance: {str(e)}")
        return "Error updating leave balance"

if __name__ == "__main__":
    logger.info("Starting LeaveManager MCP server...")
    logger.info(f"Available employees: {list(employee_leaves.keys())}")
    mcp.run()