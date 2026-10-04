"""SQLite persistence and validated CRUD operations for Personal Finance Dashboard."""

from __future__ import annotations

import sqlite3
import math
from datetime import date, datetime
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).with_name("finance.db")


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS income (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                source TEXT NOT NULL CHECK(length(trim(source)) > 0),
                category TEXT NOT NULL CHECK(length(trim(category)) > 0),
                amount REAL NOT NULL CHECK(amount > 0),
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL CHECK(length(trim(category)) > 0),
                amount REAL NOT NULL CHECK(amount > 0),
                payment_method TEXT NOT NULL CHECK(length(trim(payment_method)) > 0),
                description TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS budget (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month TEXT NOT NULL,
                category TEXT NOT NULL CHECK(length(trim(category)) > 0),
                budget_amount REAL NOT NULL CHECK(budget_amount > 0),
                UNIQUE(month, category)
            );
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK(length(trim(name)) > 0),
                target_amount REAL NOT NULL CHECK(target_amount > 0),
                current_saved REAL NOT NULL DEFAULT 0 CHECK(current_saved >= 0),
                target_date TEXT NOT NULL
            );
            """
        )


def _text(value: Any, field: str) -> str:
    result = str(value).strip() if value is not None else ""
    if not result:
        raise ValueError(f"{field} cannot be empty.")
    return result


def _date(value: Any, field: str = "Date") -> str:
    result = value.isoformat() if isinstance(value, date) else str(value).strip()
    try:
        return date.fromisoformat(result).isoformat()
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be a valid date.") from None


def _month(value: str) -> str:
    try:
        parsed = datetime.strptime(str(value).strip(), "%Y-%m")
        return parsed.strftime("%Y-%m")
    except (TypeError, ValueError):
        raise ValueError("Month must use the YYYY-MM format.") from None


def _positive_amount(value: Any, field: str = "Amount") -> float:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be a valid number.") from None
    if not math.isfinite(amount):
        raise ValueError(f"{field} must be a finite number.")
    if amount <= 0:
        raise ValueError(f"{field} must be greater than zero.")
    return amount


def _nonnegative_amount(value: Any, field: str) -> float:
    try:
        amount = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} must be a valid number.") from None
    if not math.isfinite(amount):
        raise ValueError(f"{field} must be a finite number.")
    if amount < 0:
        raise ValueError(f"{field} cannot be negative.")
    return amount


def add_income(transaction_date: Any, source: str, category: str, amount: Any, description: str = "") -> int:
    values = (_date(transaction_date), _text(source, "Source"), _text(category, "Category"),
              _positive_amount(amount), str(description or "").strip())
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO income (date, source, category, amount, description) VALUES (?, ?, ?, ?, ?)", values
        )
        return int(cursor.lastrowid)


def add_expense(transaction_date: Any, category: str, amount: Any, payment_method: str,
                description: str = "") -> int:
    values = (_date(transaction_date), _text(category, "Category"), _positive_amount(amount),
              _text(payment_method, "Payment method"), str(description or "").strip())
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO expenses (date, category, amount, payment_method, description) VALUES (?, ?, ?, ?, ?)", values
        )
        return int(cursor.lastrowid)


def get_income() -> list[dict[str, Any]]:
    with get_connection() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM income ORDER BY date DESC, id DESC")]


def get_expenses() -> list[dict[str, Any]]:
    with get_connection() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM expenses ORDER BY date DESC, id DESC")]


def get_all_transactions() -> list[dict[str, Any]]:
    query = """
        SELECT id, date, 'Income' AS type, category, source AS source_or_method,
               amount, description FROM income
        UNION ALL
        SELECT id, date, 'Expense' AS type, category, payment_method AS source_or_method,
               amount, description FROM expenses
        ORDER BY date DESC, type, id DESC
    """
    with get_connection() as connection:
        return [dict(row) for row in connection.execute(query)]


def get_transaction(transaction_type: str, transaction_id: int) -> dict[str, Any] | None:
    table = {"Income": "income", "Expense": "expenses"}.get(transaction_type)
    if table is None:
        raise ValueError("Unknown transaction type.")
    with get_connection() as connection:
        row = connection.execute(f"SELECT * FROM {table} WHERE id = ?", (int(transaction_id),)).fetchone()
        return dict(row) if row else None


def update_income(transaction_id: int, transaction_date: Any, source: str, category: str,
                  amount: Any, description: str = "") -> None:
    values = (_date(transaction_date), _text(source, "Source"), _text(category, "Category"),
              _positive_amount(amount), str(description or "").strip(), int(transaction_id))
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE income SET date=?, source=?, category=?, amount=?, description=? WHERE id=?", values
        )
        if cursor.rowcount == 0:
            raise ValueError("Income transaction was not found.")


def update_expense(transaction_id: int, transaction_date: Any, category: str, amount: Any,
                   payment_method: str, description: str = "") -> None:
    values = (_date(transaction_date), _text(category, "Category"), _positive_amount(amount),
              _text(payment_method, "Payment method"), str(description or "").strip(), int(transaction_id))
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE expenses SET date=?, category=?, amount=?, payment_method=?, description=? WHERE id=?", values
        )
        if cursor.rowcount == 0:
            raise ValueError("Expense transaction was not found.")


def delete_transaction(transaction_type: str, transaction_id: int) -> None:
    table = {"Income": "income", "Expense": "expenses"}.get(transaction_type)
    if table is None:
        raise ValueError("Unknown transaction type.")
    with get_connection() as connection:
        cursor = connection.execute(f"DELETE FROM {table} WHERE id = ?", (int(transaction_id),))
        if cursor.rowcount == 0:
            raise ValueError("Transaction was not found.")


def upsert_budget(month: str, category: str, budget_amount: Any) -> None:
    values = (_month(month), _text(category, "Category"), _positive_amount(budget_amount, "Budget"))
    with get_connection() as connection:
        connection.execute(
            "INSERT INTO budget (month, category, budget_amount) VALUES (?, ?, ?) "
            "ON CONFLICT(month, category) DO UPDATE SET budget_amount=excluded.budget_amount", values
        )


def get_budgets(month: str | None = None) -> list[dict[str, Any]]:
    with get_connection() as connection:
        if month:
            rows = connection.execute("SELECT * FROM budget WHERE month=? ORDER BY category", (_month(month),))
        else:
            rows = connection.execute("SELECT * FROM budget ORDER BY month DESC, category")
        return [dict(row) for row in rows]


def delete_budget(budget_id: int) -> None:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM budget WHERE id=?", (int(budget_id),))
        if cursor.rowcount == 0:
            raise ValueError("Budget was not found.")


def add_savings_goal(name: str, target_amount: Any, current_saved: Any, target_date: Any) -> int:
    values = (_text(name, "Goal name"), _positive_amount(target_amount, "Target amount"),
              _nonnegative_amount(current_saved, "Current saved amount"), _date(target_date, "Target date"))
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO savings_goals (name, target_amount, current_saved, target_date) VALUES (?, ?, ?, ?)", values
        )
        return int(cursor.lastrowid)


def get_savings_goals() -> list[dict[str, Any]]:
    with get_connection() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM savings_goals ORDER BY target_date, id")]


def update_savings_goal(goal_id: int, name: str, target_amount: Any, current_saved: Any, target_date: Any) -> None:
    values = (_text(name, "Goal name"), _positive_amount(target_amount, "Target amount"),
              _nonnegative_amount(current_saved, "Current saved amount"), _date(target_date, "Target date"),
              int(goal_id))
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE savings_goals SET name=?, target_amount=?, current_saved=?, target_date=? WHERE id=?", values
        )
        if cursor.rowcount == 0:
            raise ValueError("Savings goal was not found.")


def delete_savings_goal(goal_id: int) -> None:
    with get_connection() as connection:
        cursor = connection.execute("DELETE FROM savings_goals WHERE id=?", (int(goal_id),))
        if cursor.rowcount == 0:
            raise ValueError("Savings goal was not found.")


init_db()
