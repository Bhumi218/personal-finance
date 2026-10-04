"""Personal Finance Management Dashboard."""

from __future__ import annotations

import sqlite3
from datetime import date
from typing import Any

import pandas as pd
import streamlit as st

import calculations
import charts
import database

INCOME_CATEGORIES = ["Salary", "Freelance", "Business", "Scholarship", "Investment", "Other"]
EXPENSE_CATEGORIES = ["Food", "Shopping", "Travel", "Education", "Bills", "Entertainment",
                      "Healthcare", "Rent", "Groceries", "Other"]
PAYMENT_METHODS = ["Cash", "UPI", "Debit Card", "Credit Card", "Bank Transfer", "Other"]
PAGES = ["🏠 Dashboard", "💰 Add Income", "💸 Add Expense", "📋 Transactions",
         "📊 Analytics", "🎯 Budget", "🏆 Savings Goals", "📥 Export Data"]

st.set_page_config(page_title="Personal Finance Dashboard", page_icon="₹", layout="wide")
database.init_db()
st.markdown(
    """
    <style>
    :root { --ink:#eaf4ff; --muted:#9eb7d7; --line:rgba(132,183,230,.18); }
    .stApp {
        color:var(--ink);
        background-color:#06162e;
        background-image:linear-gradient(125deg,rgba(17,191,218,.14),transparent 38%),
                 linear-gradient(315deg,rgba(77,119,239,.18),transparent 42%),
                 repeating-linear-gradient(0deg,rgba(151,199,239,.045) 0,rgba(151,199,239,.045) 1px,transparent 1px,transparent 36px),
                 linear-gradient(145deg,#06172f 0%,#0b2a52 52%,#091e3e 100%);
        font-family:"Aptos","Trebuchet MS",sans-serif;
    }
    [data-testid="stAppViewContainer"] > .main { background:transparent; }
    [data-testid="stSidebar"] {
        background:linear-gradient(165deg,#061b36 0%,#0a315d 54%,#104a75 100%);
        border-right:1px solid rgba(255,255,255,.18);
        box-shadow:8px 0 28px rgba(20,51,77,.15);
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label, [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color:#f2fffc; }
    [data-testid="stSidebar"] h1 { font-size:1.4rem; }
    [data-testid="stSidebar"] [role="radiogroup"] label { border-radius:8px; padding:.2rem .45rem; }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover { background:rgba(255,255,255,.12); }
    [data-testid="stMetric"] {
        min-height:116px; padding:18px 20px; border:1px solid rgba(132,183,230,.24); border-radius:10px;
        background:linear-gradient(145deg,#143761,#0a2446);
        box-shadow:0 12px 24px rgba(0,0,0,.3),inset 0 1px 0 rgba(255,255,255,.11);
        transform:perspective(900px) rotateX(1deg);
        transition:transform .18s ease,box-shadow .18s ease;
    }
    [data-testid="stMetric"]:hover { transform:perspective(900px) translateY(-4px) rotateX(0); box-shadow:0 18px 28px rgba(0,0,0,.38),inset 0 1px 0 rgba(255,255,255,.14); }
    @keyframes panel-arrive {
        from { opacity:0; transform:perspective(1000px) translateY(14px) rotateX(-5deg) scale(.985); }
        to { opacity:1; transform:perspective(1000px) translateY(0) rotateX(0) scale(1); }
    }
    @keyframes ring-orbit {
        0% { opacity:0; transform:perspective(900px) rotateY(-38deg) rotateZ(-24deg) scale(.86); }
        72% { opacity:1; transform:perspective(900px) rotateY(7deg) rotateZ(4deg) scale(1.035); }
        100% { opacity:1; transform:perspective(900px) rotateY(0) rotateZ(0) scale(1); }
    }
    [data-testid="stMetric"], [data-testid="stPlotlyChart"] {
        transform-style:preserve-3d; animation:panel-arrive .72s cubic-bezier(.2,.75,.25,1) both;
    }
    [data-testid="stPlotlyChart"] { transition:transform .2s ease,box-shadow .2s ease; }
    [data-testid="stPlotlyChart"]:hover { transform:perspective(1100px) translateY(-3px) rotateY(-1deg); box-shadow:0 20px 34px rgba(0,0,0,.38); }
    .st-key-dashboard_savings_gauge .pielayer {
        transform-box:fill-box; transform-origin:center; animation:ring-orbit 1.5s cubic-bezier(.18,.72,.22,1) both;
    }
    [data-testid="stMetricLabel"] { color:#c1d7f2; }
    [data-testid="stMetricValue"] { color:#f5f9ff; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(1) [data-testid="stMetric"] {
        background:linear-gradient(145deg,#20bd98,#087765); box-shadow:0 12px 20px rgba(8,119,101,.27),inset 0 1px 0 rgba(255,255,255,.48);
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(2) [data-testid="stMetric"] {
        background:linear-gradient(145deg,#ff9478,#df5368); box-shadow:0 12px 20px rgba(223,83,104,.24),inset 0 1px 0 rgba(255,255,255,.48);
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(3) [data-testid="stMetric"] {
        background:linear-gradient(145deg,#648df8,#4257c8); box-shadow:0 12px 20px rgba(66,87,200,.25),inset 0 1px 0 rgba(255,255,255,.5);
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(4) [data-testid="stMetric"] {
        background:linear-gradient(145deg,#ffd66b,#f19b39); box-shadow:0 12px 20px rgba(241,155,57,.25),inset 0 1px 0 rgba(255,255,255,.55);
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(-n+4) [data-testid="stMetricLabel"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(-n+4) [data-testid="stMetricValue"] { color:#fff; }
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(4) [data-testid="stMetricLabel"],
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:nth-child(4) [data-testid="stMetricValue"] { color:#4b3515; }
    [data-testid="stForm"] {
        background:rgba(13,38,73,.92); border:1px solid rgba(132,183,230,.2); border-radius:10px;
        padding:1.1rem; box-shadow:0 14px 30px rgba(0,0,0,.27),inset 0 1px 0 rgba(255,255,255,.08);
        backdrop-filter:blur(10px);
    }
    h1, h2, h3 { color:#f1f7ff; }
    h1 { text-shadow:0 2px 12px rgba(44,183,239,.22); }
    [data-testid="stCaptionContainer"] { color:#a8c0de; }
    [data-testid="stPlotlyChart"] { border:1px solid rgba(105,166,223,.22); border-radius:10px; padding:5px; background:rgba(8,29,57,.82); box-shadow:0 14px 30px rgba(0,0,0,.28),inset 0 1px 0 rgba(255,255,255,.07); }
    [data-testid="stPlotlyChart"] .main-svg rect.bg { fill:#102b50 !important; stroke:#24466e !important; }
    [data-testid="stPlotlyChart"] .main-svg .gridlayer path { stroke:#29486b !important; }
    [data-testid="stPlotlyChart"] .main-svg .zerolinelayer path { stroke:#52759b !important; }
    [data-testid="stPlotlyChart"] .main-svg text { fill:#d7e8fb !important; }
    [data-testid="stDataFrame"] { border-radius:8px; box-shadow:0 10px 24px rgba(0,0,0,.28); }
    [data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#19b993,#4c77ed,#f1ad45); }
    .stButton > button, [data-testid="stFormSubmitButton"] > button {
        color:#fff; border:1px solid rgba(255,255,255,.35); border-radius:8px;
        background:linear-gradient(145deg,#25b7dc,#1765b6); box-shadow:0 5px 14px rgba(14,133,198,.3);
        transition:transform .16s ease,box-shadow .16s ease;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        color:#fff; border-color:rgba(255,255,255,.65); transform:translateY(-2px); box-shadow:0 9px 18px rgba(14,133,198,.4);
    }
    div[data-testid="stAlert"] { border-radius:8px; box-shadow:0 6px 14px rgba(40,65,108,.08); }
    @media (max-width:700px) {
        [data-testid="stMetric"] { min-height:96px; padding:14px; }
        [data-testid="stMetricValue"] { font-size:1.25rem; }
    }
    @media (prefers-reduced-motion:reduce) {
        [data-testid="stMetric"], [data-testid="stPlotlyChart"], .st-key-dashboard_savings_gauge .pielayer {
            animation-duration:.01ms; transition-duration:.01ms;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def money(amount: float) -> str:
    return f"₹{amount:,.2f}"


def report_error(error: Exception) -> None:
    st.error(str(error) if isinstance(error, ValueError) else "The request could not be completed. Please check the values and try again.")


def page_title(title: str, subtitle: str | None = None) -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def page_dashboard() -> None:
    page_title("Finance Dashboard", "Income, spending, and savings at a glance")
    totals = calculations.calculate_totals()
    monthly = calculations.get_monthly_data()
    categories = calculations.get_category_expenses()
    current_month = date.today().strftime("%Y-%m")
    month_summary = calculations.get_monthly_summary(current_month)

    st.markdown("### Performance")
    overview = st.columns([0.95, 1.1, 1.8], gap="small")
    with overview[0]:
        st.metric("Total Income", money(totals["income"]))
        st.metric("Total Expenses", money(totals["expenses"]))
        st.metric("Total Savings", money(totals["savings"]))
        st.metric("Savings Rate", f"{totals['savings_rate']:.1f}%")
    with overview[1]:
        st.plotly_chart(charts.savings_gauge(totals["savings_rate"]), use_container_width=True,
                        theme=None, key="dashboard_savings_gauge", height=300)
        st.caption(f"Net savings · {money(totals['savings'])}")
    with overview[2]:
        if monthly.empty:
            st.info("No financial data available yet. Add income or expenses to see analytics.")
        else:
            st.plotly_chart(charts.monthly_income_expenses(monthly), use_container_width=True,
                            theme=None, key="dashboard_monthly_performance", height=300)

    st.markdown("### Savings and spending")
    lower = st.columns([1.2, 1.1, 1.2], gap="small")
    if monthly.empty:
        lower[0].info("No monthly savings trend yet.")
    else:
        lower[0].plotly_chart(charts.savings_trend(monthly), use_container_width=True,
                              theme=None, key="dashboard_savings_trend", height=290)
    if categories.empty:
        lower[1].info("No expenses recorded yet.")
        lower[2].info("Spending breakdown appears when expenses are added.")
    else:
        lower[1].plotly_chart(charts.expense_category_chart(categories), use_container_width=True,
                              theme=None, key="dashboard_expense_categories", height=290)
        lower[2].plotly_chart(charts.spending_distribution(categories), use_container_width=True,
                              theme=None, key="dashboard_spending_distribution", height=290)

    transactions = database.get_all_transactions()
    st.markdown("### Recent transactions")
    if transactions:
        recent = pd.DataFrame(transactions[:6]).rename(columns={
            "id": "ID", "date": "Date", "type": "Type", "category": "Category",
            "source_or_method": "Source / Payment Method", "amount": "Amount", "description": "Description",
        })
        st.dataframe(recent, use_container_width=True, hide_index=True,
                     column_config={"Amount": st.column_config.NumberColumn(format="₹%.2f")})
    else:
        st.caption("No transactions recorded yet.")


def page_add_income() -> None:
    page_title("Add income")
    with st.form("income_form", clear_on_submit=True):
        transaction_date = st.date_input("Date", value=date.today())
        source = st.text_input("Income source", placeholder="Employer, client, or account")
        category = st.selectbox("Category", INCOME_CATEGORIES)
        amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0, format="%.2f")
        description = st.text_area("Description", max_chars=500)
        submitted = st.form_submit_button("Add Income", type="primary", use_container_width=True)
    if submitted:
        try:
            database.add_income(transaction_date, source, category, amount, description)
        except (ValueError, sqlite3.Error) as error:
            report_error(error)
        else:
            st.success("Income added successfully.")
            st.rerun()


def page_add_expense() -> None:
    page_title("Add expense")
    with st.form("expense_form", clear_on_submit=True):
        transaction_date = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", EXPENSE_CATEGORIES)
        amount = st.number_input("Amount (₹)", min_value=0.0, step=50.0, format="%.2f")
        payment_method = st.selectbox("Payment method", PAYMENT_METHODS)
        description = st.text_area("Description", max_chars=500)
        submitted = st.form_submit_button("Add Expense", type="primary", use_container_width=True)
    if submitted:
        try:
            database.add_expense(transaction_date, category, amount, payment_method, description)
        except (ValueError, sqlite3.Error) as error:
            report_error(error)
        else:
            st.success("Expense added successfully.")
            st.rerun()


def transaction_table(records: list[dict[str, Any]]) -> None:
    display = pd.DataFrame(records).rename(columns={
        "id": "ID", "date": "Date", "type": "Type", "category": "Category",
        "source_or_method": "Source / Payment Method", "amount": "Amount", "description": "Description",
    })
    st.dataframe(display, use_container_width=True, hide_index=True,
                 column_config={"Amount": st.column_config.NumberColumn(format="₹%.2f")})


def page_transactions() -> None:
    page_title("Transactions")
    all_records = database.get_all_transactions()
    if all_records:
        all_dates = [date.fromisoformat(row["date"]) for row in all_records]
        lower, upper = min(all_dates), max(all_dates)
    else:
        lower = upper = date.today()

    filters = st.columns([1, 1.5, 2, 1, 1, 2])
    chosen_type = filters[0].selectbox("Type", ["All", "Income", "Expense"])
    categories = sorted({row["category"] for row in all_records})
    chosen_categories = filters[1].multiselect("Category", categories, default=categories)
    date_range = filters[2].date_input("Date range", value=(lower, upper))
    min_amount = filters[3].number_input("Minimum ₹", min_value=0.0, value=0.0, step=100.0)
    max_amount = filters[4].number_input("Maximum ₹ (0 = none)", min_value=0.0, value=0.0, step=100.0)
    search = filters[5].text_input("Search", placeholder="Category, source, description...")

    filtered = all_records
    if chosen_type != "All":
        filtered = [row for row in filtered if row["type"] == chosen_type]
    filtered = [row for row in filtered if row["category"] in chosen_categories]
    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start_date, end_date = date_range
        filtered = [row for row in filtered if start_date.isoformat() <= row["date"] <= end_date.isoformat()]
    filtered = [row for row in filtered if float(row["amount"]) >= min_amount]
    if max_amount > 0:
        filtered = [row for row in filtered if float(row["amount"]) <= max_amount]
    if search.strip():
        needle = search.strip().casefold()
        filtered = [row for row in filtered if needle in " ".join(str(value) for value in row.values()).casefold()]

    st.caption(f"{len(filtered)} transaction(s)")
    if filtered:
        transaction_table(filtered)
    else:
        st.info("No transactions match these filters.")
    if not all_records:
        return

    st.divider()
    options = {f"{row['date']} · {row['type']} · {row['category']} · #{row['id']} · {money(float(row['amount']))}": row
               for row in all_records}
    with st.expander("Edit or delete a transaction"):
        selected_label = st.selectbox("Select transaction", list(options))
        selected = options[selected_label]
        current = database.get_transaction(selected["type"], selected["id"])
        if current is None:
            st.warning("This transaction no longer exists. Refresh the page.")
            return
        category_choices = INCOME_CATEGORIES if selected["type"] == "Income" else EXPENSE_CATEGORIES
        if current["category"] not in category_choices:
            category_choices = [current["category"]] + category_choices
        with st.form("edit_transaction_form"):
            edit_date = st.date_input("Date", value=date.fromisoformat(current["date"]), key="edit_date")
            if selected["type"] == "Income":
                edit_source = st.text_input("Income source", value=current["source"], key="edit_source")
                edit_category = st.selectbox("Category", category_choices,
                                             index=category_choices.index(current["category"]), key="edit_income_category")
                edit_method = ""
            else:
                edit_source = ""
                edit_category = st.selectbox("Category", category_choices,
                                             index=category_choices.index(current["category"]), key="edit_expense_category")
                methods = PAYMENT_METHODS.copy()
                if current["payment_method"] not in methods:
                    methods.insert(0, current["payment_method"])
                edit_method = st.selectbox("Payment method", methods,
                                           index=methods.index(current["payment_method"]), key="edit_method")
            edit_amount = st.number_input("Amount (₹)", min_value=0.0, value=float(current["amount"]),
                                          step=100.0, format="%.2f", key="edit_amount")
            edit_description = st.text_area("Description", value=current["description"], max_chars=500,
                                            key="edit_description")
            save_edit = st.form_submit_button("Save changes", type="primary")
        if save_edit:
            try:
                if selected["type"] == "Income":
                    database.update_income(selected["id"], edit_date, edit_source, edit_category, edit_amount, edit_description)
                else:
                    database.update_expense(selected["id"], edit_date, edit_category, edit_amount, edit_method, edit_description)
            except (ValueError, sqlite3.Error) as error:
                report_error(error)
            else:
                st.success("Transaction updated.")
                st.rerun()
        st.warning("Deleting a transaction permanently updates totals and analytics.")
        confirmed = st.checkbox("I confirm that I want to delete this transaction", key="confirm_delete_transaction")
        if st.button("Delete transaction", disabled=not confirmed, key="delete_transaction_button"):
            try:
                database.delete_transaction(selected["type"], selected["id"])
            except (ValueError, sqlite3.Error) as error:
                report_error(error)
            else:
                st.success("Transaction deleted.")
                st.rerun()


def page_analytics() -> None:
    page_title("Analytics")
    monthly = calculations.get_monthly_data()
    if monthly.empty:
        st.info("No financial data available yet. Add income or expenses to see analytics.")
        return
    left, right = st.columns(2)
    left.plotly_chart(charts.monthly_income_expenses(monthly), use_container_width=True, theme=None)
    right.plotly_chart(charts.savings_trend(monthly), use_container_width=True, theme=None)
    left, right = st.columns(2)
    categories = calculations.get_category_expenses()
    sources = calculations.get_income_sources()
    left.plotly_chart(charts.expense_category_chart(categories), use_container_width=True, theme=None)
    right.plotly_chart(charts.income_source_chart(sources), use_container_width=True, theme=None)
    st.plotly_chart(charts.spending_distribution(categories), use_container_width=True, theme=None)

    st.divider()
    st.subheader("Monthly analysis")
    chosen_month = st.selectbox("Select month", calculations.available_months())
    summary = calculations.get_monthly_summary(chosen_month)
    metrics = st.columns(4)
    metrics[0].metric("Monthly Income", money(summary["income"]))
    metrics[1].metric("Monthly Expenses", money(summary["expenses"]))
    metrics[2].metric("Monthly Savings", money(summary["savings"]))
    metrics[3].metric("Savings Rate", f"{summary['savings_rate']:.1f}%")
    details = st.columns(4)
    details[0].metric("Income transactions", summary["income_count"])
    details[1].metric("Expense transactions", summary["expense_count"])
    details[2].metric("Highest expense category", summary["highest_category"])
    details[3].metric("Highest expense", money(summary["highest_expense"]))
    selected_month_data = monthly[monthly["month"] == chosen_month]
    st.plotly_chart(charts.monthly_income_expenses(selected_month_data), use_container_width=True,
                    key="monthly_analysis_chart", theme=None)


def page_budget() -> None:
    page_title("Budget tracker")
    selected_month = st.date_input("Budget month", value=date.today().replace(day=1), key="budget_month").strftime("%Y-%m")
    with st.form("budget_form", clear_on_submit=True):
        category = st.selectbox("Category", EXPENSE_CATEGORIES)
        amount = st.number_input("Monthly budget (₹)", min_value=0.0, step=500.0, format="%.2f")
        submitted = st.form_submit_button("Save budget", type="primary")
    if submitted:
        try:
            database.upsert_budget(selected_month, category, amount)
        except (ValueError, sqlite3.Error) as error:
            report_error(error)
        else:
            st.success("Budget saved.")
            st.rerun()

    budgets = calculations.get_budget_data(selected_month)
    st.subheader(f"Budgets for {selected_month}")
    if not budgets:
        st.caption("No category budgets set for this month.")
        return
    for budget in budgets:
        with st.container(border=True):
            head = st.columns([2, 1, 1, 1, 1])
            head[0].markdown(f"**{budget['category']}**")
            head[1].caption("Budget")
            head[1].write(money(float(budget["budget_amount"])))
            head[2].caption("Spent")
            head[2].write(money(float(budget["spent"])))
            head[3].caption("Remaining")
            head[3].write(money(float(budget["remaining"])))
            head[4].caption("Used")
            head[4].write(f"{budget['percentage_used']:.1f}%")
            st.progress(min(float(budget["percentage_used"]), 100.0) / 100.0)
            if budget["percentage_used"] > 100:
                st.error("Budget exceeded!")
            elif budget["percentage_used"] >= 80:
                st.warning("You have used at least 80% of this budget.")
            if st.button("Delete budget", key=f"delete_budget_{budget['id']}"):
                try:
                    database.delete_budget(budget["id"])
                except (ValueError, sqlite3.Error) as error:
                    report_error(error)
                else:
                    st.rerun()


def page_savings_goals() -> None:
    page_title("Savings goals")
    with st.form("savings_goal_form", clear_on_submit=True):
        name = st.text_input("Goal name", placeholder="Emergency fund")
        target_amount = st.number_input("Target amount (₹)", min_value=0.0, step=1000.0, format="%.2f")
        current_saved = st.number_input("Current saved amount (₹)", min_value=0.0, step=500.0, format="%.2f")
        target_date = st.date_input("Target date", value=date.today())
        submitted = st.form_submit_button("Add savings goal", type="primary")
    if submitted:
        try:
            database.add_savings_goal(name, target_amount, current_saved, target_date)
        except (ValueError, sqlite3.Error) as error:
            report_error(error)
        else:
            st.success("Savings goal added.")
            st.rerun()

    goals = database.get_savings_goals()
    st.subheader("Your goals")
    if not goals:
        st.caption("No savings goals yet.")
        return
    for goal in goals:
        target = float(goal["target_amount"])
        saved = float(goal["current_saved"])
        progress = saved / target * 100 if target else 0.0
        with st.container(border=True):
            heading = st.columns([3, 1])
            heading[0].markdown(f"**{goal['name']}** · target {goal['target_date']}")
            heading[1].markdown(f"**{progress:.1f}%**")
            st.progress(min(progress, 100.0) / 100.0)
            stats = st.columns(3)
            stats[0].caption(f"Target: {money(target)}")
            stats[1].caption(f"Saved: {money(saved)}")
            stats[2].caption(f"Remaining: {money(target - saved)}")

    goal_options = {f"{goal['name']} · #{goal['id']}": goal for goal in goals}
    with st.expander("Edit or delete a goal"):
        selected_goal = goal_options[st.selectbox("Select goal", list(goal_options))]
        with st.form("edit_goal_form"):
            edit_name = st.text_input("Goal name", value=selected_goal["name"])
            edit_target = st.number_input("Target amount (₹)", min_value=0.0, value=float(selected_goal["target_amount"]), step=1000.0)
            edit_saved = st.number_input("Current saved amount (₹)", min_value=0.0, value=float(selected_goal["current_saved"]), step=500.0)
            edit_target_date = st.date_input("Target date", value=date.fromisoformat(selected_goal["target_date"]))
            save_goal = st.form_submit_button("Save goal changes", type="primary")
        if save_goal:
            try:
                database.update_savings_goal(selected_goal["id"], edit_name, edit_target, edit_saved, edit_target_date)
            except (ValueError, sqlite3.Error) as error:
                report_error(error)
            else:
                st.success("Savings goal updated.")
                st.rerun()
        confirmed = st.checkbox("Confirm goal deletion", key="confirm_goal_delete")
        if st.button("Delete goal", disabled=not confirmed):
            try:
                database.delete_savings_goal(selected_goal["id"])
            except (ValueError, sqlite3.Error) as error:
                report_error(error)
            else:
                st.success("Savings goal deleted.")
                st.rerun()


def page_export() -> None:
    page_title("Export data")
    income = pd.DataFrame(database.get_income(), columns=["id", "date", "source", "category", "amount", "description", "created_at"])
    expenses = pd.DataFrame(database.get_expenses(), columns=["id", "date", "category", "amount", "payment_method", "description", "created_at"])
    transactions = pd.DataFrame(database.get_all_transactions(), columns=[
        "id", "date", "type", "category", "source_or_method", "amount", "description"])
    st.write("Download the current records stored in your local finance database.")
    buttons = st.columns(3)
    buttons[0].download_button("Income CSV", income.to_csv(index=False).encode("utf-8-sig"),
                               "income.csv", "text/csv", use_container_width=True)
    buttons[1].download_button("Expense CSV", expenses.to_csv(index=False).encode("utf-8-sig"),
                               "expenses.csv", "text/csv", use_container_width=True)
    buttons[2].download_button("Complete Transaction CSV", transactions.to_csv(index=False).encode("utf-8-sig"),
                               "transactions.csv", "text/csv", use_container_width=True)
    st.subheader("Record counts")
    counts = st.columns(3)
    counts[0].metric("Income records", len(income))
    counts[1].metric("Expense records", len(expenses))
    counts[2].metric("All transactions", len(transactions))


with st.sidebar:
    st.title("₹ Finance")
    st.caption("Personal Finance Management")
    selected_page = st.radio("Navigation", PAGES, label_visibility="collapsed")
    st.divider()
    totals = calculations.calculate_totals()
    st.caption("Available balance")
    st.markdown(f"### {money(totals['balance'])}")

page_renderers = {
    PAGES[0]: page_dashboard,
    PAGES[1]: page_add_income,
    PAGES[2]: page_add_expense,
    PAGES[3]: page_transactions,
    PAGES[4]: page_analytics,
    PAGES[5]: page_budget,
    PAGES[6]: page_savings_goals,
    PAGES[7]: page_export,
}
page_renderers[selected_page]()
