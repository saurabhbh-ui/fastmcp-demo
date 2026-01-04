from fastmcp import FastMCP
import os
import sqlite3
from datetime import datetime
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "expenses.db")

mcp = FastMCP("ExpenseTracker")

def init_db():
    """Initialize the expenses database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
            )
        """)
        conn.commit()
    finally:
        conn.close()

init_db()

@mcp.tool()
def add_expense(
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = ""
) -> dict:
    """
    Add a new expense entry to the database.
    
    Args:
        date: Date in YYYY-MM-DD format
        amount: Expense amount (positive number)
        category: Main expense category (e.g., 'Food', 'Transport')
        subcategory: Optional subcategory
        note: Optional note or description
    
    Returns:
        Dictionary with status and inserted expense ID
    """
    # Validate date format
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return {"status": "error", "message": "Date must be in YYYY-MM-DD format"}
    
    # Validate amount
    if amount <= 0:
        return {"status": "error", "message": "Amount must be positive"}
    
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )
        conn.commit()
        return {"status": "ok", "id": cur.lastrowid}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

@mcp.tool()
def get_expenses(
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 50
) -> dict:
    """
    Retrieve expenses with optional filtering.
    
    Args:
        category: Filter by category (optional)
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
        limit: Maximum number of results (default 50)
    
    Returns:
        Dictionary with status and list of expenses
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        query = "SELECT * FROM expenses WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date DESC LIMIT ?"
        params.append(limit)
        
        cur = conn.cursor()
        cur.execute(query, params)
        rows = cur.fetchall()
        
        expenses = [dict(row) for row in rows]
        return {"status": "ok", "expenses": expenses, "count": len(expenses)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

@mcp.tool()
def get_expense_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """
    Get summary statistics for expenses.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (optional)
        end_date: End date in YYYY-MM-DD format (optional)
    
    Returns:
        Dictionary with total, count, and breakdown by category
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        query = "SELECT category, SUM(amount) as total, COUNT(*) as count FROM expenses WHERE 1=1"
        params = []
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " GROUP BY category ORDER BY total DESC"
        
        cur = conn.cursor()
        cur.execute(query, params)
        categories = [dict(row) for row in cur.fetchall()]
        
        # Get overall total
        total_query = "SELECT SUM(amount) as total, COUNT(*) as count FROM expenses WHERE 1=1"
        if start_date:
            total_query += " AND date >= ?"
        if end_date:
            total_query += " AND date <= ?"
        
        cur.execute(total_query, params[:len([p for p in [start_date, end_date] if p])])
        overall = dict(cur.fetchone())
        
        return {
            "status": "ok",
            "total": overall['total'] or 0,
            "count": overall['count'] or 0,
            "by_category": categories
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

@mcp.tool()
def delete_expense(expense_id: int) -> dict:
    """
    Delete an expense by ID.
    
    Args:
        expense_id: The ID of the expense to delete
    
    Returns:
        Dictionary with status message
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        
        if cur.rowcount == 0:
            return {"status": "error", "message": f"No expense found with ID {expense_id}"}
        
        return {"status": "ok", "message": f"Deleted expense {expense_id}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        conn.close()

# Run the server
if __name__ == "__main__":
    mcp.run()