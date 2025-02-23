import plotly.express as px
import plotly.graph_objects as go


def create_time_series_chart(df_plot, x, aggregation_option, gb_selected) -> go.Figure:
    """Generates a time series chart for temporal groupings."""
    df_plot.sort_values(by=x, inplace=True)
    if gb_selected == "Month":
        df_plot[x] = df_plot[x].astype(str)  # Ensure categorical ordering
        fig = px.bar(
            df_plot, x=x, y=aggregation_option,
            title=f"{aggregation_option} of Trades Over Time",
            labels={x: gb_selected, aggregation_option: aggregation_option},
        )
        fig.update_xaxes(type="category")  # Prevents unnecessary intermediate months
    else:
        fig = px.line(
            df_plot, x=x, y=aggregation_option,
            title=f"{aggregation_option} of Trades Over Time",
            labels={x: gb_selected, aggregation_option: aggregation_option},
        )
    return fig

def create_categorical_chart(df_plot, x, aggregation_option, gb_selected, top_n) -> go.Figure:
    """Generates a bar chart for categorical groupings."""
    if top_n:
        df_plot = df_plot.head(top_n)
    orientation = "h" if gb_selected not in ["Year"] else "v"
    fig = px.bar(
        df_plot.sort_values(by=aggregation_option, ascending=True),
        x=aggregation_option, y=x,
        title=f"{aggregation_option} of Trades by {gb_selected} (Top {top_n})",
        labels={x: gb_selected, aggregation_option: aggregation_option},
        orientation=orientation,
    )
    chart_height = max(400, 40 + df_plot.shape[0] * 20)
    fig.update_layout(height=chart_height)
    return fig
