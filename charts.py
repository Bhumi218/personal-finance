"""Plotly figures built only from application database calculations."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


PALETTE = {"income": "#33d6c1", "expense": "#ffae45", "savings": "#58c5ff"}
CHART_THEME = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "#102b50",
    "font": {"color": "#d7e8fb", "family": "Aptos, Trebuchet MS, sans-serif"},
}


def monthly_income_expenses(monthly: pd.DataFrame) -> go.Figure:
    figure = go.Figure()
    if not monthly.empty:
        figure.add_bar(x=monthly["month"], y=monthly["income"], name="Income", marker_color=PALETTE["income"])
        figure.add_bar(x=monthly["month"], y=monthly["expenses"], name="Expenses", marker_color=PALETTE["expense"])
    figure.update_layout(barmode="group", title="Monthly Income vs Expenses", xaxis_title="Month",
                         yaxis_title="Amount (₹)", legend_title_text="", template="plotly_dark",
                         margin={"t": 55, "r": 20, "b": 30, "l": 20}, **CHART_THEME)
    return figure


def savings_trend(monthly: pd.DataFrame) -> go.Figure:
    figure = go.Figure()
    if not monthly.empty:
        figure.add_scatter(x=monthly["month"], y=monthly["savings"], mode="lines+markers",
                           name="Savings", line={"color": PALETTE["savings"], "width": 3},
                           fill="tozeroy", fillcolor="rgba(88,197,255,0.16)")
    figure.update_layout(title="Monthly Savings Trend", xaxis_title="Month", yaxis_title="Amount (₹)",
                         showlegend=False, template="plotly_dark", margin={"t": 55, "r": 20, "b": 30, "l": 20},
                         **CHART_THEME)
    return figure


def savings_gauge(savings_rate: float) -> go.Figure:
    progress = max(0.0, min(float(savings_rate), 100.0))
    figure = go.Figure(go.Pie(
        values=[progress, 100.0 - progress],
        labels=["Savings rate", "Remaining"],
        hole=0.76,
        sort=False,
        rotation=270,
        direction="clockwise",
        textinfo="none",
        marker={"colors": ["#7cf092", "#244d80"], "line": {"color": "#0b2343", "width": 5}},
        hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
        showlegend=False,
    ))
    figure.update_layout(
        title="Savings Rate",
        annotations=[{"text": f"<b>{progress:.1f}%</b><br><span>SAVED</span>",
                      "x": 0.5, "y": 0.5, "showarrow": False,
                      "font": {"color": "#f2f8ff", "size": 24, "family": "Aptos, sans-serif"}}],
        margin={"t": 55, "r": 18, "b": 18, "l": 18},
        **CHART_THEME,
    )
    return figure


def expense_category_chart(categories: pd.DataFrame) -> go.Figure:
    if categories.empty:
        return go.Figure().update_layout(title="Expense by Category", template="plotly_dark", **CHART_THEME)
    figure = px.pie(categories, names="category", values="amount", hole=0.56,
                    color_discrete_sequence=["#33d6c1", "#ff6b76", "#ffb84d", "#638dff", "#ed8b43", "#24c5da", "#b379f7"])
    figure.update_layout(title="Expense by Category", template="plotly_dark",
                         margin={"t": 55, "r": 20, "b": 30, "l": 20}, legend_title_text="Category",
                         **CHART_THEME)
    return figure


def income_source_chart(sources: pd.DataFrame) -> go.Figure:
    figure = go.Figure()
    if not sources.empty:
        figure.add_bar(x=sources["source"], y=sources["amount"], marker_color=PALETTE["income"], name="Income")
    figure.update_layout(title="Income by Source", xaxis_title="Source", yaxis_title="Amount (₹)",
                         showlegend=False, template="plotly_dark", margin={"t": 55, "r": 20, "b": 30, "l": 20},
                         **CHART_THEME)
    return figure


def spending_distribution(categories: pd.DataFrame) -> go.Figure:
    figure = go.Figure()
    if not categories.empty:
        total = float(categories["amount"].sum())
        percentages = categories["amount"] / total * 100 if total else categories["amount"] * 0
        colors = ["#31d6d1", "#ffbc4e", "#ff7185", "#6d8dff", "#bd78f5", "#56d99c", "#42b5ed"]
        bar_colors = [colors[index % len(colors)] for index in range(len(categories))]
        figure.add_barpolar(
            r=percentages,
            theta=categories["category"],
            width=360 / max(len(categories), 1) * 0.72,
            marker={"color": bar_colors, "line": {"color": "#102b50", "width": 2}},
            opacity=0.95,
            hovertemplate="%{theta}<br>%{r:.1f}% of spending<extra></extra>",
            name="Share",
        )
    max_share = float(categories["amount"].max() / categories["amount"].sum() * 100) if not categories.empty and categories["amount"].sum() else 25
    figure.update_layout(title="Spending Distribution", showlegend=False, template="plotly_dark",
                         margin={"t": 55, "r": 24, "b": 20, "l": 24},
                         polar={"bgcolor": "#102b50",
                                "radialaxis": {"visible": False, "showticklabels": False,
                                               "range": [0, max(25, max_share * 1.2)],
                                               "gridcolor": "#29486b"},
                                "angularaxis": {"gridcolor": "#29486b", "linecolor": "#52759b",
                                                "tickfont": {"color": "#d7e8fb"}}},
                         **CHART_THEME)
    return figure
