"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go
from plotly.subplots import make_subplots

import ehz_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=380, legend=True):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), plot_bgcolor="rgba(0,0,0,0)", showlegend=legend,
                      legend=dict(orientation="h", y=-0.25))
    return lock_axes(fig)


def build_chain(chain, n):
    """Die Kette der besten Antworten: je k (Gegner defektiert in den letzten k Runden) die erste Runde, in der die beste Antwort defektiert,
    und ihr Wert."""
    ks = [r["k"] for r in chain]
    first = [r["first_defection"] for r in chain]
    values = [r["value"] for r in chain]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(x=[str(k) for k in ks], y=values, name="Wert der besten Antwort", marker_color="rgba(76,120,168,0.45)",
                         hovertemplate="k = %{x}: Wert %{y:.0f}<extra></extra>"), secondary_y=False)
    fig.add_trace(go.Scatter(x=[str(k) for k in ks], y=first, mode="lines+markers", name="erste Defektion der besten Antwort",
                             line=dict(color=C.COLOR_BR, width=4), hovertemplate="k = %{x}: Runde %{y}<extra></extra>"), secondary_y=True)
    fig.update_xaxes(title_text="Der Gegner defektiert in den letzten k Runden (k = 0: Tit-for-Tat, k = N: Immer-Defektieren)", type="category")
    fig.update_yaxes(title_text="Gesamtwert über N Runden", secondary_y=False, range=[0, n * C.T])
    fig.update_yaxes(title_text="Runde der ersten Defektion", secondary_y=True, range=[0, n + 1], autorange=False)
    return _base(fig, height=400)


def build_gain_curves(curves):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=curves["n"], y=curves["per_round"], mode="lines+markers", name="bekanntes Ende nach N Runden",
                             line=dict(color=C.COLOR_BR, width=4), hovertemplate="N = %{x}: %{y:.3f} je Runde<extra></extra>"))
    fig.add_trace(go.Scatter(x=curves["n"], y=curves["geometric_per_round"], mode="lines+markers", name="unbeschränktes Ende, gleiche erwartete Dauer",
                             line=dict(color=C.COLOR_UNBOUNDED, width=4, dash="dash"), hovertemplate="erwartete Dauer %{x}: %{y:.3f} je Runde<extra></extra>"))
    fig.update_xaxes(title_text="Länge N bzw. erwartete Dauer in Runden", type="log")
    fig.update_yaxes(title_text="Vorteil der besten Antwort je Runde")
    return _base(fig, height=380)


def build_window(curves):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=curves["w"], y=curves["gain"], mode="lines+markers", name="Vorteil der besten Antwort (exakt)",
                             line=dict(color=C.COLOR_BR, width=4), hovertemplate="Spanne %{x}: %{y:.3f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=curves["w"], y=curves["closed_form"], mode="lines", name="2 / (Spanne + 1)",
                             line=dict(color=C.COLOR_OTHER, width=2, dash="dot"), hovertemplate="2/(w+1) = %{y:.3f}<extra></extra>"))
    fig.update_xaxes(title_text="Spanne w: das Ende liegt gleichverteilt zwischen Runde N und Runde N + w")
    fig.update_yaxes(title_text="Vorteil der besten Antwort in Punkten")
    return _base(fig, height=360)
