import dash
from dash import html
dash.register_page(__name__, path="/kpis", title="KPIs")

layout = html.Div([
    html.H4("KPIs (placeholder)"),
    html.Ul([
        html.Li("Passengers per dispatched train (requires formations_2024 join)"),
        html.Li("Peak / off-peak ratios"),
        html.Li("Station utilization percentiles")
    ])
])
