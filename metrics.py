from portfolio_optimizer import PortfolioOptimizer
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import skew, kurtosis
import streamlit as st
import plotly.express as px


class MetricsCalculator(PortfolioOptimizer):
    def __init__(
        self, stocks, start, end, optimization_criterion, riskFreeRate=0.07024
    ):
        super().__init__(stocks, start, end, optimization_criterion, riskFreeRate)
        self.portfolioDaily = self.portfolioReturnsDaily()
        self.annual_return = self.MMeanReturn("annual") / 100

    def MMeanReturn(self, frequency):
        if frequency == "monthly":
            return self.portfolioDaily.mean() * 21 * 100
        if frequency == "annual":
            return self.portfolioDaily.mean() * 252 * 100

    def MStandardDeviation(self, frequency):
        if frequency == "monthly":
            return self.portfolioDaily.std(ddof=1) * np.sqrt(21) * 100
        if frequency == "annual":
            return self.portfolioDaily.std(ddof=1) * np.sqrt(252) * 100

    def MDownsideDeviation(self):
        downsideChanges = self.portfolioDaily[self.portfolioDaily < 0]
        return downsideChanges.std(ddof=1) * np.sqrt(252) * 100

    def MMaxDrawdown(self):
        returns = np.array(self.portfolioDaily)
        cumulative_returns = np.cumprod(1 + returns) - 1
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = cumulative_returns - running_max
        max_drawdown = np.min(drawdown) * 100

        ## Fix this calculation

        return max_drawdown

    def MBeta(self):
        portfolio = np.array(self.portfolioDaily).flatten()
        benchmark = np.array(self.benchmark).flatten()
        portfolio_dates = pd.date_range(
            start=self.start, periods=len(portfolio), freq="D"
        )
        benchmark_dates = pd.date_range(
            start=self.start, periods=len(benchmark), freq="D"
        )

        portfolio_series = pd.Series(portfolio, index=portfolio_dates)
        benchmark_series = pd.Series(benchmark, index=benchmark_dates)

        common_dates = portfolio_series.index.intersection(benchmark_series.index)

        aligned_portfolio = portfolio_series[common_dates]
        aligned_benchmark = benchmark_series[common_dates]

        portfolio = aligned_portfolio.tolist()
        benchmark = aligned_benchmark.tolist()

        returns_data = pd.DataFrame(
            {"Portfolio": portfolio, "Benchmark": benchmark}
        ).dropna()
        X = sm.add_constant(returns_data["Benchmark"])
        model = sm.OLS(returns_data["Portfolio"], X).fit()
        beta = model.params["Benchmark"]

        return beta

    def MAlpha(self):
        market_return = self.benchmark.mean() * 252
        alpha = (self.annual_return) - (
            self.riskFreeRate + self.MBeta() * (market_return - self.riskFreeRate)
        )
        return alpha * 100

    def MSharpeRatio(self):
        annual_std = self.MStandardDeviation("annual") / 100
        sharpe = (self.annual_return - self.riskFreeRate) / annual_std

        ## fix sharpe ratio
        return sharpe

    def MSortinoRatio(self):
        downside_std = self.MDownsideDeviation() / 100
        sortino = (self.annual_return - self.riskFreeRate) / downside_std
        return sortino

    def MTrackingError(self):
        portfolioDailyReturns = np.array(self.portfolioReturnsDaily())
        benchmarkReturns = np.array(self.benchmark)

        difference_array = portfolioDailyReturns - benchmarkReturns
        trackingError = difference_array.std(ddof=1) * np.sqrt(252)

        return trackingError

    def MInformationRatio(self):
        trackingError = self.MTrackingError()
        portfolioDailyReturns = np.array(self.portfolioReturnsDaily())
        benchmarkReturns = np.array(self.benchmark)

        mean_portfolio = portfolioDailyReturns.mean() * 252
        mean_benchmark = benchmarkReturns.mean() * 252

        information_ratio = (mean_portfolio - mean_benchmark) / trackingError

        return information_ratio

    def MTreynorRatio(self):
        treynor = (self.annual_return - self.riskFreeRate) / self.MBeta()
        return treynor

    def MCalmarRatio(self):
        calmar = (self.annual_return - self.riskFreeRate) / (-self.MMaxDrawdown() / 100)
        return calmar

    def MSkewness(self):
        skewness = skew(self.portfolioDaily)[0]
        return skewness

    def MKurtosis(self):
        kurtos = kurtosis(self.portfolioDaily)[0]
        return 3 - kurtos

    def MPositivePeriods(self):
        positive = self.portfolioDaily[self.portfolioDaily > 0]
        total = len(self.portfolioDaily)

        positive_periods = len(positive)
        ratio = round((positive_periods / (total)) * 100, 2)

        return f"{positive_periods} out of {total} ({ratio}%)"

    def portfolioReturnsGraph(self):
        portfolio = np.array(self.portfolioDaily).flatten()
        benchmark = np.array(self.benchmark).flatten()
        ret, std = self.basicMetrics()
        portfolio_dates = ret.index

        if len(portfolio) and len(benchmark) == len(portfolio_dates):
            portfolio_series = pd.Series(portfolio, index=portfolio_dates)
            benchmark_series = pd.Series(benchmark, index=portfolio_dates)
        else:
            # Handle length mismatch: truncate or pad the shorter array
            min_length = min(len(benchmark), len(portfolio), len(portfolio_dates))
            portfolio_series = pd.Series(
                portfolio[:min_length], index=portfolio_dates[:min_length]
            )
            benchmark_series = pd.Series(
                benchmark[:min_length], index=portfolio_dates[:min_length]
            )

        cumulative_returns_p = 100 * ((1 + portfolio_series).cumprod() - 1)
        cumulative_returns_b = 100 * ((1 + benchmark_series).cumprod() - 1)

        cumulative_returns_p = cumulative_returns_p.reindex(portfolio_dates)
        cumulative_returns_p.fillna(method="ffill", inplace=True)

        cumulative_returns_b = cumulative_returns_b.reindex(portfolio_dates)
        cumulative_returns_b.fillna(method="ffill", inplace=True)

        returns_df = pd.DataFrame(
            {
                "Date": cumulative_returns_p.index,
                "Nifty Cumulative Return (%)": cumulative_returns_b.values,
                "Portfolio Cumulative Return (%)": cumulative_returns_p.values,
            }
        )

        returns_df.dropna(inplace=True)

        fig = px.line(
            returns_df,
            x="Date",
            y=["Portfolio Cumulative Return (%)", "Nifty Cumulative Return (%)"],
            labels={"value": "Cumulative Return (%)", "variable": "Legend"},
        )

        fig.update_yaxes(tickformat=".0f", ticksuffix="%")
        fig.update_layout(
            legend_title_text="",
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5
            ),
        )

        st.markdown(f'**Portfolio Returns**: {round(cumulative_returns_p.values[-1], 2)}% ')
        st.markdown(f'**NIFTY Returns**: {round(cumulative_returns_b.values[-1], 2)}% ')
        st.plotly_chart(fig)

    def metricDf(self):
        metric_df = {
                    "Mean Return (Monthly)": f'{round(self.MMeanReturn("monthly"), 2)}%',
                    "Mean Return (Annualised)": f'{round(self.MMeanReturn("annual"), 2)}%',
                    "Standard Deviation (Monthly)": f'{round(self.MStandardDeviation("monthly"), 2)}%',
                    "Standard Deviation (Annualised)": f'{round(self.MStandardDeviation("annual"), 2)}%',
                    "Downside Standard Deviation": f"{round(self.MDownsideDeviation(), 2)}%",
                    "Maximum Drawdown": f"{round(self.MMaxDrawdown(), 2)}%",
                    "Beta": round(self.MBeta(), 2),
                    "Alpha": f"{round(self.MAlpha(), 2)}%",
                    "Sharpe Ratio": round(self.MSharpeRatio(), 2),
                    "Sortino Ratio": round(self.MSortinoRatio(), 2),
                    "Treynor Ratio": round(self.MTreynorRatio(), 2),
                    "Calmar Ratio": round(self.MCalmarRatio(), 2),
                    "Tracking Error": round(self.MTrackingError(), 2),
                    "Information Ratio": round(self.MInformationRatio(), 2),
                    "Skewness": round(self.MSkewness(), 2),
                    "Excess Kurtosis": round(self.MKurtosis(), 2),
                    "Positive Periods": self.MPositivePeriods(),
                }
        return metric_df
        