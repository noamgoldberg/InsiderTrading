import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def create_time_series_chart(
    *,
    df_plot: pd.DataFrame,
    x: str,
    aggregation: str,
    groupby: str,
    title: str
) -> go.Figure:
    """Generates a time series chart for temporal groupings."""
    df_plot.sort_values(by=x, inplace=True)
    if groupby == "Month":
        df_plot[x] = df_plot[x].astype(str)  # Ensure categorical ordering
        fig = px.bar(
            df_plot, x=x, y=aggregation,
            title=title,
            labels={x: groupby, aggregation: aggregation},
        )
        fig.update_xaxes(type="category")  # Prevents unnecessary intermediate months
    else:
        fig = px.line(
            df_plot, x=x, y=aggregation,
            title=title,
            labels={x: groupby, aggregation: aggregation},
        )
    return fig

def create_categorical_chart(
    *,
    df_plot: pd.DataFrame,
    x: str,
    aggregation: str,
    groupby: str,
    top_n: int | None,
    title: str | None
) -> go.Figure:
    """Generates a bar chart for categorical groupings."""
    if top_n:
        df_plot = df_plot.sort_values(by=aggregation, ascending=False).head(top_n)
    df_plot = df_plot.sort_values(by=aggregation, ascending=True)
    df_plot.sort_values(by=aggregation, ascending=False)
    orientation = "h" if groupby not in ["Year"] else "v"
    fig = px.bar(
        df_plot,
        x=aggregation, y=x,
        title=title,
        labels={x: groupby, aggregation: aggregation},
        orientation=orientation,
    )
    chart_height = max(400, 40 + df_plot.shape[0] * 20)
    fig.update_layout(height=chart_height)
    return fig
