"""
Plotly chart helpers — all themed to match the dashboard (dark/light).
"""

from __future__ import annotations

from typing import Dict, List

import plotly.graph_objects as go


def _get_common() -> dict:
    text_color = "#f3f4f6"
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=text_color, family="'Space Grotesk', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif", size=13),
        margin=dict(t=40, l=10, r=10, b=10),
        transition=dict(duration=500, easing="cubic-in-out")
    )


def radar_chart(dimensions: Dict[str, dict]) -> go.Figure:
    gridcolor = "rgba(255,255,255,0.08)"
    radial_color = "#9ca3af"
    angular_color = "#f3f4f6"
    
    names = [d["name"] for d in dimensions.values()]
    scores = [d["score"] for d in dimensions.values()]
    # close the loop
    names.append(names[0]); scores.append(scores[0])

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=scores, theta=names, fill="toself",
            line=dict(color="#8b5cf6", width=2),
            fillcolor="rgba(139, 92, 246, 0.25)",
            name="Score",
        )
    )
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(255,255,255,0.01)",
            radialaxis=dict(visible=True, range=[0, 10], gridcolor=gridcolor, color=radial_color),
            angularaxis=dict(gridcolor=gridcolor, color=angular_color),
        ),
        showlegend=False, height=380, **_get_common(),
    )
    return fig


def rubric_bar_chart(dimensions: Dict[str, dict]) -> go.Figure:
    gridcolor = "rgba(255,255,255,0.05)"
    
    names = [d["name"] for d in dimensions.values()]
    weighted = [d["weighted"] for d in dimensions.values()]
    weights = [d["weight"] for d in dimensions.values()]

    text = [f"{w:.1f} / {wt}" for w, wt in zip(weighted, weights)]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=names, y=weighted,
            text=text, textposition="outside",
            marker=dict(
                color=weighted,
                colorscale=[[0, "#ef4444"], [0.5, "#f59e0b"], [1, "#10b981"]],
                line=dict(color="rgba(255,255,255,0.08)", width=1),
            ),
        )
    )
    # add weight cap line
    fig.add_trace(
        go.Scatter(
            x=names, y=weights, mode="markers",
            marker=dict(symbol="line-ew", size=24, color="#9ca3af", line=dict(width=3, color="#9ca3af")),
            name="Max weight", showlegend=False,
        )
    )
    fig.update_layout(
        height=360, showlegend=False,
        yaxis=dict(title="Weighted contribution", gridcolor=gridcolor, zerolinecolor=gridcolor),
        xaxis=dict(gridcolor=gridcolor),
        **_get_common(),
    )
    return fig


def ranking_bar_chart(candidates: List[dict]) -> go.Figure:
    gridcolor = "rgba(255,255,255,0.05)"
    
    candidates = sorted(candidates, key=lambda r: r["total_score"])
    names = [
        (r["payload"].get("candidate", {}).get("name") or f"Candidate {r['id']}")[:28]
        for r in candidates
    ]
    scores = [r["total_score"] for r in candidates]
    recs = [r["recommendation"] for r in candidates]
    color_map = {
        "Strong Hire": "#10b981",
        "Shortlist":   "#3b82f6",
        "Consider":    "#f59e0b",
        "Reject":      "#ef4444",
    }
    colors = [color_map.get(r, "#8b5cf6") for r in recs]
    fig = go.Figure(
        go.Bar(
            x=scores, y=names, orientation="h",
            marker=dict(color=colors, line=dict(color="rgba(255,255,255,0.05)", width=1)),
            text=[f"{s:.1f}" for s in scores], textposition="outside",
            hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>",
        )
    )
    fig.update_layout(
        height=max(280, 38 * len(names) + 60),
        xaxis=dict(title="Total score (/100)", range=[0, max(100, max(scores or [0]) + 8)],
                   gridcolor=gridcolor),
        yaxis=dict(gridcolor=gridcolor),
        **_get_common(),
    )
    return fig


def confidence_gauge(value: float) -> go.Figure:
    text_color = "#f3f4f6"
    tick_color = "#9ca3af"
    bg_color = "rgba(255,255,255,0.02)"
    
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "%", "font": {"color": text_color, "size": 28}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": tick_color},
                "bar": {"color": "#8b5cf6"},
                "bgcolor": bg_color,
                "steps": [
                    {"range": [0, 50],  "color": "rgba(239, 68, 68, 0.15)"},
                    {"range": [50, 75], "color": "rgba(245, 158, 11, 0.15)"},
                    {"range": [75, 100],"color": "rgba(16, 185, 129, 0.15)"},
                ],
                "threshold": {"line": {"color": text_color, "width": 2}, "thickness": 0.85, "value": value},
            },
        )
    )
    gauge_layout = {**_get_common(), "margin": dict(t=20, l=10, r=10, b=10)}
    fig.update_layout(height=240, **gauge_layout)
    return fig

