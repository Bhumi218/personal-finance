"""Database-backed financial calculations and analytics datasets."""

from __future__ import annotations

from datetime import date
from typing import Any

import numpy as np
import pandas as pd

import database


def calculate_totals() -> dict[str, float]:
    income = sum(float(row["amount"]) for row in database.get_income())
    expenses = sum(float(row["amount"]) for row in database.get_expenses())
    savings = income - expenses
    rate = float(np.divide(savings * 100, income)) if income else 0.0
    return {"income": income, "expenses": expenses, "savings": savings,
            "savings_rate": rate, "balance": savings}


def _transaction_frame() -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for row in database.get_income():
        records.append({"date": row["date"], "type": "Income", "category": row["category"],
                        "source_or_method": row["source"], "amount": float(row["amount"]),
                        "description": row["description"]})
    for row in database.get_expenses():
        records.append({"date": row["date"], "type": "Expense", "category": row["category"],
                        "source_or_method": row["payment_method"], "amount": float(row["amount"]),
                        "description": row["description"]})
    frame = pd.DataFrame(records)
    if not frame.empty:
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        frame["month"] = frame["date"].dt.strftime("%Y-%m")
    return frame


def get_monthly_data() -> pd.DataFrame:
    frame = _transaction_frame()
    if frame.empty:
        return pd.DataFrame(columns=["month", "income", "expenses", "savings"])
    monthly = frame.pivot_table(index="month", columns="type", values="amount", aggfunc="sum", fill_value=0)
    for column in ("Income", "Expense"):
        if column not in monthly.columns:
            monthly[column] = 0.0
    monthly = monthly.rename(columns={"Income": "income", "Expense": "expenses"})
    monthly["savings"] = monthly["income"] - monthly["expenses"]
    return monthly.reset_index().sort_values("month")


def get_monthly_summary(month: str) -> dict[str, Any]:
    frame = _transaction_frame()
    selected = frame[frame["month"] == month] if not frame.empty else frame
    income_rows = selected[selected["type"] == "Income"] if not selected.empty else selected
    expense_rows = selected[selected["type"] == "Expense"] if not selected.empty else selected
    income = float(income_rows["amount"].sum()) if not income_rows.empty else 0.0
    expenses = float(expense_rows["amount"].sum()) if not expense_rows.empty else 0.0
    category_spend = expense_rows.groupby("category")["amount"].sum() if not expense_rows.empty else pd.Series(dtype=float)
    top_category = str(category_spend.idxmax()) if not category_spend.empty else "None"
    top_amount = float(category_spend.max()) if not category_spend.empty else 0.0
    return {"income": income, "expenses": expenses, "savings": income - expenses,
            "savings_rate": float(np.divide((income - expenses) * 100, income)) if income else 0.0,
            "income_count": int(len(income_rows)), "expense_count": int(len(expense_rows)),
            "highest_category": top_category, "highest_expense": top_amount}


def get_category_expenses() -> pd.DataFrame:
    frame = _transaction_frame()
    if frame.empty:
        return pd.DataFrame(columns=["category", "amount"])
    expenses = frame[frame["type"] == "Expense"]
    if expenses.empty:
        return pd.DataFrame(columns=["category", "amount"])
    return expenses.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)


def get_income_sources() -> pd.DataFrame:
    frame = _transaction_frame()
    if frame.empty:
        return pd.DataFrame(columns=["source", "amount"])
    income = frame[frame["type"] == "Income"]
    if income.empty:
        return pd.DataFrame(columns=["source", "amount"])
    return income.groupby("source_or_method", as_index=False)["amount"].sum().rename(
        columns={"source_or_method": "source"}).sort_values("amount", ascending=False)


def get_budget_data(month: str) -> list[dict[str, Any]]:
    budgets = database.get_budgets(month)
    expenses = database.get_expenses()
    spent_by_category: dict[str, float] = {}
    for expense in expenses:
        if str(expense["date"]).startswith(month):
            category = str(expense["category"])
            spent_by_category[category] = spent_by_category.get(category, 0.0) + float(expense["amount"])
    result = []
    for budget in budgets:
        limit = float(budget["budget_amount"])
        spent = spent_by_category.get(str(budget["category"]), 0.0)
        result.append({**budget, "spent": spent, "remaining": limit - spent,
                       "percentage_used": spent / limit * 100 if limit else 0.0})
    return result


def available_months() -> list[str]:
    monthly = get_monthly_data()
    current = date.today().strftime("%Y-%m")
    months = monthly["month"].astype(str).tolist() if not monthly.empty else []
    return sorted(set(months + [current]), reverse=True)
