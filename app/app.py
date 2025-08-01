import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'config')))

import dash
from dash import html, dcc, Input, Output
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from events import EVENTS, EVENT_COLOURS

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Generate markers for all events
event_markers = [
    dl.CircleMarker(
        center=(event['location']['lat'], event['location']['lon']),
        radius=5,
        color=EVENT_COLOURS.get(event['type'], 'gray'),
        fill=True,
        fillOpacity=0.7,
        children=dl.Tooltip(event['name']),
        id=f"marker-{key}"
    )
    for key, event in EVENTS.items()
]

# event_markers = [
#     dl.Marker(
#         position=(event['location']['lat'], event['location']['lon']),
#         children=dl.Tooltip(event['name']),
#         id=f"marker-{key}"
#     )
#     for key, event in EVENTS.items()
# ]

# Extract unique event types for cross-event analysis
event_types = sorted(set(event['type'] for event in EVENTS.values()))

def layout():
    return dbc.Container([
        html.H1("Climate-Driven Financial Event Study Viewer"),

        dbc.Row([
            dbc.Col([
                html.Label("Select Analysis Type:"),
                dcc.RadioItems(
                    id='analysis-type',
                    options=[
                        {'label': 'Single Event', 'value': 'single'},
                        {'label': 'Cross-Event', 'value': 'cross'}
                    ],
                    value='single',
                    inline=True
                )
            ])
        ], className="my-2"),

        dbc.Row([
            dbc.Col([
                html.Label(id='event-selector-label'),
                dcc.Dropdown(id='event-selector')
            ])
        ], className="my-2"),

        html.Hr(),

        dl.Map([
            dl.TileLayer(),
            dl.LayerGroup(event_markers)
        ], style={'width': '100%', 'height': '500px'}, center=[39.8283, -98.5795], zoom=3, id='event-map'),

        html.Div([
            html.H6("Event Type Legend:"),
            html.Ul([
                html.Li([
                    html.Span(style={'display': 'inline-block', 'width': '12px', 'height': '12px',
                                     'backgroundColor': color, 'marginRight': '8px'}),
                    etype.title()
                ]) for etype, color in EVENT_COLOURS.items()
            ], style={'listStyleType': 'none', 'padding': 0})
        ], style={'marginTop': '1rem'}),

        html.Hr(),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='ar-car-plot')
            ], width=6),
            dbc.Col([
                dcc.Graph(id='model-performance-plot')
            ], width=6),
        ])
    ], fluid=True)

app.layout = layout

@app.callback(
    Output('event-selector-label', 'children'),
    Output('event-selector', 'options'),
    Input('analysis-type', 'value')
)
def update_event_selector(analysis_type):
    if analysis_type == 'single':
        return "Select Event:", [{'label': v['name'], 'value': k} for k, v in EVENTS.items()]
    else:
        return "Select Event Type:", [{'label': t.title(), 'value': t} for t in event_types]

# Placeholder callbacks for rendering plots
@app.callback(
    Output('ar-car-plot', 'figure'),
    Output('model-performance-plot', 'figure'),
    Input('event-selector', 'value'),
    Input('analysis-type', 'value')
)
def update_plots(selected, analysis_type):
    fig1 = go.Figure()
    fig2 = go.Figure()
    if selected:
        fig1.update_layout(title="AR/CAR Placeholder")
        fig2.update_layout(title="Model Performance Placeholder")
    return fig1, fig2

if __name__ == '__main__':
    app.run(debug=True,port=8050)