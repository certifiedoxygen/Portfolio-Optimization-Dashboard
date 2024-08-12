
import datetime as dt
import pandas as pd
import streamlit as st
import plotly.express as px
import streamlit_shadcn_ui as ui
from PIL import Image
from interpretations import metric_info, var_info, optimization_strategies_info, appinfo
from portfolio_optimizer import PortfolioOptimizer
from metrics import MetricsCalculator
from risk import RiskMetrics


def main():
    im = Image.open("EfficientFrontier.png")

    st.set_page_config(page_title="Portfolio Optimization Dashboard", page_icon=im)

    st.markdown("## Portfolio Optimization Dashboard")
    col1, col2 = st.columns([0.14, 0.86], gap="small")
    col1.write("`Created by:`")
    linkedin_url = "https://www.linkedin.com/in/yashkhaitan/"
    col2.markdown(
        f'<a href="{linkedin_url}" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="15" height="15" style="vertical-align: middle; margin-right: 10px;">`Yash Khaitan`</a>',
        unsafe_allow_html=True,
    )
    
    appinfo()

    with st.expander("View Optimization Strategies"):
        optimization_strategies_info()

    # Using sidebar for inputs

    if "stocks" not in st.session_state:
        st.session_state.stocks_list = ["TCS, CAMS, ITC, INFY"]  # Initialize empty list

    default_tickers_str = ", ".join(st.session_state.stocks_list)

    cont1 = st.container(border=True)
    cont1.markdown("### Input Parameters")
    stocks = cont1.text_input(
        "Enter Tickers (separated by commas)", value=default_tickers_str
    )
    start, end = cont1.columns(2)
    start_date = start.date_input(
        "Start Date",
        max_value=dt.date.today() - dt.timedelta(days=1),
        min_value=dt.date.today() - dt.timedelta(days=1250),
        value=dt.date.today() - dt.timedelta(days=365),
    )
    end_date = end.date_input(
        "End Date",
        max_value=dt.date.today(),
        min_value=start_date + dt.timedelta(days=1),
        value=dt.date.today(),
    )
    col1, col2 = cont1.columns(2)
    optimization_criterion = col1.selectbox(
        "Optimization Objective",
        options=[
            "Maximize Sharpe Ratio",
            "Minimize Volatility",
            "Maximize Sortino Ratio",
            "Minimize Tracking Error",
            "Maximize Information Ratio",
            "Minimize Conditional Value-at-Risk",
        ],
    )
    riskFreeRate_d = col2.number_input(
        "Risk Free Rate (%)",
        min_value=0.00,
        max_value=100.00,
        step=0.001,
        format="%0.3f",
        value=6.880,
        help = "10 Year Bond Yield"
    )
    calc = cont1.button("Calculate")
    riskFreeRate = riskFreeRate_d / 100

    st.session_state.stocks_list = [s.strip() for s in stocks.split(",")]

    if calc:
        try:
            with st.spinner("Buckle Up! Financial Wizardry in Progress...."):
                stocks_list = st.session_state.stocks_list
                optimizer = PortfolioOptimizer(
                    stocks_list,
                    start_date,
                    end_date,
                    optimization_criterion,
                    riskFreeRate,
                )
                optimizer.optimized_allocation.index = [
                    stock.replace(".NS", "")
                    for stock in optimizer.optimized_allocation.index
                ]
                ret, std = optimizer.basicMetrics()
                if not (len(ret.columns) == len(stocks_list)):
                    missing_tickers = set(stocks_list) - set(ret.columns)
                    raise ValueError(
                        f"Data for the following tickers could not be retrieved: {', '.join(missing_tickers)}"
                    )

                optimizer.optimized_allocation.columns = ["Allocation (%)"]
                optimizer.optimized_allocation["Allocation (%)"] = [
                    round(i * 100, 2)
                    for i in optimizer.optimized_allocation["Allocation (%)"]
                ]

                metrics = MetricsCalculator(
                    stocks_list,
                    start_date,
                    end_date,
                    optimization_criterion,
                    riskFreeRate,
                )
                
                metric_df = metrics.metricDf()
                metric_df = pd.DataFrame(list(metric_df.items()))
                metric_df.columns = ["Metric", "Value"]

                riskM = RiskMetrics(
                    stocks_list,
                    start_date,
                    end_date,
                    optimization_criterion,
                    riskFreeRate,
                )

        except ValueError as e:
            st.error(str(e))
            return
        except Exception as e:
            st.error(str(e))
            return

        with st.container(border=True):
            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                [
                    "Summary",
                    "Efficient Frontier",
                    "Metrics",
                    "Portfolio Returns",
                    "Risk Analysis",
                ]
            )
            with tab1:
                st.markdown("#### Optimized Portfolio Performance")
                col1, col2 = st.columns(2)
                col1.markdown(f"**Returns**: {optimizer.optimized_returns}%")
                col1.markdown(f"**Volatility**: {optimizer.optimized_std}%")
                sharpe = (
                    optimizer.optimized_returns - (optimizer.riskFreeRate * 100)
                ) / optimizer.optimized_std
                col1.markdown(f"**Sharpe Ratio**: {round(sharpe, 2)}")
                col1.markdown(f"**Sortino Ratio**: {round(metrics.MSortinoRatio(), 2)}")
                col2.markdown(f"**Time Period**: {(end_date - start_date).days} days")
                st.markdown("#### Optimized Portfolio Allocation")
                alocCol, pieCol = st.columns(2)
                with alocCol:
                    allocations = optimizer.optimized_allocation
                    allocations["Tickers"] = allocations.index
                    allocations = allocations[["Tickers", "Allocation (%)"]]
                    ui.table(allocations)
                with pieCol:
                    sharpeChart = optimizer.optimized_allocation[
                        optimizer.optimized_allocation["Allocation (%)"] != 0
                    ]
                    fig = px.pie(
                        sharpeChart, values="Allocation (%)", names=sharpeChart.index
                    )
                    fig.update_layout(
                        width=180,
                        height=200,
                        showlegend=False,
                        margin=dict(t=20, b=0, l=0, r=0),
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.markdown("#### Efficient Frontier Assets")
                frontierAssets, matrix = optimizer.frontierStats()
                ui.table(frontierAssets)
                st.markdown("#### Asset Correlations")
                ui.table(matrix)
                st.markdown("*(Higher Value Represents Higher Correlation)*")
                st.markdown("#### Efficient Frontier Graph")
                optimizer.EF_graph()

            with tab3:
                st.markdown("#### Risk and Return Metrics")
                ui.table(metric_df)
                with st.expander("Metric Interpretations:"):
                    metric_info()

            with tab4:
                st.markdown("#### Cumulative Portfolio Returns")
                metrics.portfolioReturnsGraph()

            with tab5:
                st.markdown("#### VaR and CVaR")
                var = riskM.riskTable()
                ui.table(var)
                with st.expander("VaR and CVar Interpretation"):
                    var_info()
                st.markdown("#### VaR Breaches")
                riskM.varXReturns()


if __name__ == "__main__":
    main()
