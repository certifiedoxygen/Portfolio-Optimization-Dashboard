from portfolio_optimizer import PortfolioOptimizer
import numpy as np
from scipy.stats import norm
import pandas as pd
import plotly.express as px
import streamlit as st


class RiskMetrics(PortfolioOptimizer):
    def __init__(self, stocks, start, end, optimization_criterion, riskFreeRate=0.07024):
        super().__init__(stocks, start, end, optimization_criterion, riskFreeRate)
        self.portfolioDaily = np.array(self.portfolioReturnsDaily())
        self.mu, self.sigma = self.muSigma()

    def muSigma(self):
        mu = self.portfolioDaily.mean()
        sigma = self.portfolioDaily.std(ddof=1)

        return mu, sigma

    def Rvar(self):
        confidence_levels = [0.9, 0.95, 0.99]
        var_values = []
        for lvl in confidence_levels:
            var = self.mu + self.sigma * norm.ppf(lvl)
            var_values.append(var)

        return var_values

    def RCvar(self):
        var_values = self.Rvar()
        cvar_values = []
        for var in var_values:
            loss = self.portfolioDaily[self.portfolioDaily < -var]
            cvar = np.mean(loss)
            cvar_values.append(-cvar)

        return cvar_values

    def riskTable(self):
        var_values = self.Rvar()
        cvar_values = self.RCvar()

        var_dict = {
            "90%": [
                "90%",
                f"{round(var_values[0]*100, 2)}%",
                f"{round(cvar_values[0]*100, 2)}%",
            ],
            "95%": [
                "95%",
                f"{round(var_values[1]*100, 2)}%",
                f"{round(cvar_values[1]*100, 2)}%",
            ],
            "99%": [
                "99%",
                f"{round(var_values[2]*100, 2)}%",
                f"{round(cvar_values[2]*100, 2)}%",
            ],
        }

        var_df = pd.DataFrame(
            var_dict, index=["Confidence Level", "VaR(%)", "CVaR(%)"]
        ).T

        return var_df

    def varXReturns(self):
        portfolio = np.array(self.portfolioDaily).flatten()
        ret, std = self.basicMetrics()
        portfolio_dates = ret.index

        if len(portfolio) == len(portfolio_dates):
            portfolio_series = pd.Series(portfolio, index=portfolio_dates)
        else:
            # Handle length mismatch: truncate or pad the shorter array
            min_length = min(len(portfolio), len(portfolio_dates))
            portfolio_series = pd.Series(
                portfolio[:min_length], index=portfolio_dates[:min_length]
            )

        daily_returns_df = pd.DataFrame(
            {
                "Date": portfolio_series.index,
                "Daily Return (%)": portfolio_series.values * 100,
            }
        )

        ymin = np.min(portfolio_series.values * 100)
        ymax = np.max(portfolio_series.values * 100)

        var_list = self.Rvar()
        var_95 = var_list[1]

        breach_points = daily_returns_df[
            daily_returns_df["Daily Return (%)"] < -var_95 * 100
        ]
        fig = px.line(daily_returns_df, "Date", "Daily Return (%)")
        scatter = fig.add_scatter(
            x=breach_points["Date"],
            y=breach_points["Daily Return (%)"],
            mode="markers",
            marker_color="#0D2A63",
            name="VaR 95% Breaches",
        )

        fig.update_yaxes(tickformat=".0f", ticksuffix="%")
        fig.update_yaxes(range=[ymin * 1.4, ymax * 1.4])
        fig.update_traces(line_color="#86caff")

        fig.update_layout(
            legend_title_text="",
            legend=dict(orientation="h", yanchor="top", y=1.02, xanchor="right", x=1),
        )

        st.plotly_chart(fig)