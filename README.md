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
├── .devcontainer/
│   └── devcontainer.json
├── .gitignore
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

## Run in GitHub Codespaces

GitHub displays this repository's files but does not run Streamlit by itself. To open the working app in a browser, use [Open in GitHub Codespaces](https://github.com/codespaces/new?repo=Bhumi218/personal-finance&ref=main). Codespaces installs `requirements.txt`, starts Streamlit, and forwards port `8501`; open that forwarded port in the browser if it does not open automatically.

The forwarded app is available while the Codespace is running and is private by default. Its `finance.db` stays inside the Codespace and is ignored by Git, so it is not uploaded to GitHub. Back up or export records before deleting the Codespace. Codespaces usage may consume your included quota or incur charges according to your GitHub plan.

## Database information

SQLite stores income, expenses, monthly budgets, and savings goals in separate tables. Income and expense records include a creation timestamp. Updates and deletions are written directly to the database, and totals and charts are recalculated from stored records whenever a page is rendered.

## Screenshots

_Add application screenshots here._

## Future improvements

- Optional encrypted database backups and restore workflow.
- Recurring transactions and scheduled reminders.
- Multiple currency support and configurable fiscal years.
