import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

app = dash.Dash(__name__)
app.title = "Subte BI — Dashboard (MVP)"

# Placeholder sample until real data is loaded
sample = pd.DataFrame({
    "Line": ["A","B","C","D","E","H"]*2,
    "Month": ["2025-01"]*6 + ["2025-02"]*6,
    "Passengers": [120, 180, 90, 220, 70, 110, 140, 210, 95, 240, 80, 130]
})

fig_line = px.bar(sample.groupby("Line", as_index=False)["Passengers"].sum(),
                  x="Line", y="Passengers", title="Passengers by Line (sample)")

fig_trend = px.line(sample, x="Month", y="Passengers", color="Line",
                    markers=True, title="Monthly Trend by Line (sample)")

app.layout = html.Div(style={"fontFamily":"Inter, Arial, sans-serif", "padding":"24px"}, children=[
    html.H1("Buenos Aires Subte — BI Dashboard (MVP)"),
    html.P("Interactive insights based on GCBA open data. Week 1 skeleton."),
    html.Div([
        html.Div([dcc.Graph(figure=fig_line)], style={"width":"48%","display":"inline-block","verticalAlign":"top"}),
        html.Div([dcc.Graph(figure=fig_trend)], style={"width":"48%","display":"inline-block","marginLeft":"4%"}),
    ])
])

if __name__ == "__main__":
    app.run_server(debug=True)
