# Personal Finance Management Dashboard

A local personal finance application for tracking income, expenses, savings, category budgets, and savings goals. Records are stored persistently in SQLite and displayed in a Streamlit dashboard with Plotly analytics. All amounts are in Indian rupees (₹).

## Features

- Dashboard KPIs for total income, expenses, savings, savings rate, and balance.
- Add, edit, search, filter, and confirmed deletion of income and expense transactions.
- Monthly income/expense and savings charts, expense categories, income sources, and spending distribution.
- Month-level summary with transaction counts and highest expense category.
- Monthly category budgets with 80% warnings and exceeded-budget alerts.
- Persistent savings goals with progress, editing, and deletion.
- CSV downloads for income, expenses, and combined transactions.
- Input validation and parameterized SQLite queries.

## Technology

Python 3, Streamlit, SQLite, Pandas, Plotly, and NumPy.

## Project structure

```text
personal_finance/
├── app.py
├── database.py
├── calculations.py
├── charts.py
├── requirements.txt
├── finance.db       # Created automatically on first launch
└── README.md
```

## Installation

Open a terminal in this directory and install the dependencies:

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Streamlit prints the local URL when the application starts. The app creates `finance.db` beside `app.py` automatically. Keep this file to retain your records; back it up like any other important personal data. The database is local and is not encrypted.

## Database information

SQLite stores income, expenses, monthly budgets, and savings goals in separate tables. Income and expense records include a creation timestamp. Updates and deletions are written directly to the database, and totals and charts are recalculated from stored records whenever a page is rendered.

## Screenshots

_Add application screenshots here._

## Future improvements

- Optional encrypted database backups and restore workflow.
- Recurring transactions and scheduled reminders.
- Multiple currency support and configurable fiscal years.
