
import yfinance as yf
import numpy as np
import scipy.optimize as sc
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from scipy.stats import norm


class PortfolioOptimizer:

    def __init__(
        self, stocks, start, end, optimization_criterion, riskFreeRate=0.07024):
        self.stocks = [stock + ".NS" for stock in stocks]  
        self.start = start
        self.end = end
        self.optimization_criterion = optimization_criterion
        self.riskFreeRate = riskFreeRate
        self.meanReturns, self.covMatrix = self.getData()
        self.benchmark = self.benchmarkReturns()
        (
            self.optimized_returns,
            self.optimized_std,
            self.optimized_allocation,
            self.efficientList,
            self.targetReturns,
        ) = self.calculatedResults()

    def basicMetrics(self):
        if not all(s.isupper() for s in self.stocks):
            raise ValueError("Enter ticker names in Capital Letters!")
        if len(self.stocks) <= 1:
            raise ValueError("More than 1 ticker input required!")
        try:
            stockData = yf.download(self.stocks, start=self.start, end=self.end)
        except:
            raise ValueError("Unable to download data, try again later!")
        stockData = stockData["Close"]

        if len(stockData.columns) != len(self.stocks):
            raise ValueError("Unable to download data for one or more tickers!")

        returns = stockData.pct_change()
        stdIndividual = returns.std()

        return returns, stdIndividual

    def portfolioReturnsDaily(self):
        dailyIndividualReturns, dailyIndividualStd = self.basicMetrics()
        portfolioDailyReturns = np.dot(
            dailyIndividualReturns.dropna(), self.optimized_allocation
        )
        return portfolioDailyReturns

    def benchmarkReturns(self):
        try:
            benchmark_data = yf.download("^NSEI", self.start, self.end)
        except:
            raise ValueError("Unable to download data, try again later!")
        benchmark_returns = benchmark_data["Close"].pct_change().dropna()
        return benchmark_returns

    def getData(self):

        returns, stdIndividual = self.basicMetrics()
        meanReturns = (returns.mean())  
        covMatrix = (returns.cov())  

        return meanReturns, covMatrix

    def portfolioPerformance(self, weights):
        returns = (np.sum(self.meanReturns * weights) * 252)  
        std = np.sqrt(np.dot(weights.T, np.dot(self.covMatrix, weights))) * np.sqrt(252)  
        return returns, std

    def sharpe(self, weights):
        pReturns, pStd = self.portfolioPerformance(weights)  
        return (-(pReturns - self.riskFreeRate) / pStd)  

    def sortino(self, weights):
        dailyIndividualReturns, dailyIndividualStd = self.basicMetrics()
        portfolioDailyReturns = np.dot(dailyIndividualReturns.dropna(), weights)
        downsideChanges = portfolioDailyReturns[portfolioDailyReturns < 0]
        downside_deviation = downsideChanges.std(ddof=1) * np.sqrt(252)
        meanReturns = portfolioDailyReturns.mean() * 252
        sortino_ratio = (meanReturns - self.riskFreeRate) / downside_deviation

        return -sortino_ratio

    def portfolioVariance(self, weights):  
        return self.portfolioPerformance(weights)[1]

    def trackingError(self, weights):
        dailyIndividualReturns, dailyIndividualStd = self.basicMetrics()
        portfolioDailyReturns = np.array(np.dot(dailyIndividualReturns.dropna(), weights))
        benchmarkReturns = np.array(self.benchmark)

        difference_array = portfolioDailyReturns - benchmarkReturns
        trackingError = difference_array.std(ddof=1) * np.sqrt(252)

        return trackingError

    def informationRatio(self, weights):
        dailyIndividualReturns, dailyIndividualStd = self.basicMetrics()
        portfolioDailyReturns = np.array(np.dot(dailyIndividualReturns.dropna(), weights))
        benchmarkReturns = np.array(self.benchmark)
        difference_array = portfolioDailyReturns - benchmarkReturns
        portfolioPerformance = portfolioDailyReturns.mean() * 252
        benchmarkPerformance = benchmarkReturns.mean() * 252
        trackingError = difference_array.std(ddof=1) * np.sqrt(252)

        information = (portfolioPerformance - benchmarkPerformance) / trackingError

        return -information

    def conditionalVar(self, weights):
        dailyIndividualReturns, dailyIndividualStd = self.basicMetrics()
        portfolioDailyReturns = np.array(np.dot(dailyIndividualReturns.dropna(), weights))
        mu = portfolioDailyReturns.mean()
        sigma = portfolioDailyReturns.std(ddof=1)
        var = mu + sigma * norm.ppf(0.95)
        loss = portfolioDailyReturns[portfolioDailyReturns < -var]
        cvar = np.mean(loss)

        return -cvar

    def optimization_function(self, constraintSet=(0, 1)):

        numAssets = len(self.meanReturns)  ## gets the number of stocks in the portfolio
        constraints = {
            "type": "eq",
            "fun": lambda x: np.sum(x) - 1,
        }  
        bound = constraintSet  
        bounds = tuple(bound for asset in range(numAssets)) 

        if self.optimization_criterion == "Maximize Sharpe Ratio":
            return sc.minimize(
                self.sharpe,
                numAssets * [1.0 / numAssets],  
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
            )
        elif self.optimization_criterion == "Minimize Volatility":
            return sc.minimize(
                self.portfolioVariance,
                numAssets * [1.0 / numAssets],  
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
            )
        elif self.optimization_criterion == "Maximize Sortino Ratio":
            return sc.minimize(
                self.sortino,
                numAssets * [1.0 / numAssets],  
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
            )
        elif self.optimization_criterion == "Minimize Tracking Error":
            return sc.minimize(
                self.trackingError,
                numAssets * [1.0 / numAssets],  
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
            )
        elif self.optimization_criterion == "Maximize Information Ratio":
            return sc.minimize(
                self.informationRatio,
                numAssets * [1.0 / numAssets],
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
            )
        elif self.optimization_criterion == "Minimize Conditional Value-at-Risk":
            return sc.minimize(
                self.conditionalVar,
                numAssets * [1.0 / numAssets],  
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
            )

    def portfolioReturn(self, weights):  
        return self.portfolioPerformance(weights)[0]

    def efficientOpt(self, returnTarget, constraintSet=(0, 1)):  
        numAssets = len(self.meanReturns)  
        constraints = (
            {
                "type": "eq",
                "fun": lambda x: self.portfolioReturn(x) - returnTarget,
            },  
            {"type": "eq", "fun": lambda x: np.sum(x) - 1},
        )  
        bounds = tuple(constraintSet for asset in range(numAssets))  
        effOpt = sc.minimize(
            self.portfolioVariance,
            numAssets * [1.0 / numAssets],
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        return effOpt

    def calculatedResults(self):
        optimized_portfolio = (self.optimization_function())  
        optimized_returns, optimized_std = self.portfolioPerformance(
            optimized_portfolio["x"]
        )  
        optimized_allocation = pd.DataFrame(
            optimized_portfolio["x"],
            index=self.meanReturns.index,
            columns=["allocation"],
        )  #

        # Efficient Frontier
        std, ret, shar = self.simulations()
        efficientList = (
            []
        )  
        targetReturns = np.linspace(
            min(ret), max(ret), 100
        )  
        for target in targetReturns:
            efficientList.append(
                self.efficientOpt(target)["fun"]
            )  

        optimized_returns, optimized_std = round(optimized_returns * 100, 2), round(
            optimized_std * 100, 2
        )

        return (
            optimized_returns,
            optimized_std,
            optimized_allocation,
            efficientList,
            targetReturns,
        )

    def simulations(self):  
        noOfPortfolios = 10000
        numAssets = len(self.meanReturns)
        weight = np.zeros((noOfPortfolios, numAssets))
        expectedReturn = np.zeros(noOfPortfolios)
        expectedVolatility = np.zeros(noOfPortfolios)
        sharpeRatio = np.zeros(noOfPortfolios)  

        for k in range(noOfPortfolios):
            w = np.array(np.random.random(numAssets))  
            w = w / np.sum(w) 
            weight[k, :] = w  
            expectedReturn[k], expectedVolatility[k] = self.portfolioPerformance(weight[k].T)  
            sharpeRatio[k] = (expectedReturn[k] - self.riskFreeRate) / expectedVolatility[k]  

        return expectedVolatility, expectedReturn, sharpeRatio

    def EF_graph(self):

        fig, ax = plt.subplots(figsize=(10, 7))

        # Efficient Frontier
        ax.plot(
            [ef_std * 100 for ef_std in self.efficientList],
            [target * 100 for target in self.targetReturns],
            color="black",
            linestyle="-",
            linewidth=4,
            label="Efficient Frontier",
            zorder=1,
            alpha=0.9,
        )

        if self.optimization_criterion == "Maximize Sharpe Ratio":
            label_v = "Maximum Sharpe Ratio Portfolio"
        elif self.optimization_criterion == "Maximize Sortino Ratio":
            label_v = "Maximum Sortino Ratio Portfolio"
        elif self.optimization_criterion == "Minimize Volatility":
            label_v = "Minimum Volatility Portfolio"
        elif self.optimization_criterion == "Minimize Tracking Error":
            label_v = "Minimum Tracking Error Portfolio"
        elif self.optimization_criterion == "Maximize Information Ratio":
            label_v = "Maximum Information Ratio Portfolio"
        elif self.optimization_criterion == "Minimize Conditional Value-at-Risk":
            label_v = "Minimum CVaR Portfolio"

        ## Max Sharpe Ratio
        ax.scatter(
            [self.optimized_std],
            [self.optimized_returns],
            color="orange",
            marker="o",
            s=150,
            label=label_v,
            edgecolors="darkgray",
            zorder=4,
        )

        ## Plot Random Portfolios
        expectedVolatility, expectedReturn, sharpeRatio = self.simulations()
        scatter = ax.scatter(
            expectedVolatility * 100,
            expectedReturn * 100,
            c=sharpeRatio,
            cmap="Blues",
            marker="o",
            zorder=0,
            s=40,
        )
        plt.colorbar(scatter, ax=ax, label="Sharpe Ratio")
        ax.set_xlabel("Annualised Volatility (%)")
        ax.set_ylabel("Annualised Return (%)")

        ax.legend()
        st.pyplot(fig)

    def allocCharts(self):
        ## Max Sharpe Ratio allocation
        sharpeChart = px.self.optimized_allocation.allocation()
        fig = px.pie(
            sharpeChart, values="allocation", names=self.optimized_allocation.index
        )
        return fig.show()

    def frontierStats(self):
        ## Summary Stats
        returns, std = self.basicMetrics()
        tickers = [i for i in self.optimized_allocation.index]
        ExpectedReturn = [f"{round(i*252*100, 2)} %" for i in self.meanReturns]
        StandardDeviation = [f"{round(i*np.sqrt(252)*100, 2)} %" for i in std]
        sharpeRatio = []
        for i, ret in enumerate(self.meanReturns):
            sharpe = (ret * 252 - self.riskFreeRate) / (std[i] * np.sqrt(252))
            sharpeRatio.append(round(sharpe, 2))

        df = pd.DataFrame(
            {
                "Tickers": tickers,
                "Expected Return": ExpectedReturn,
                "Standard Deviation": StandardDeviation,
                "Sharpe Ratio": sharpeRatio,
            }
        )

        ## Correlation Matrix

        matrix = returns.corr().round(decimals=2)
        matrix[""] = matrix.index
        matrix = matrix[[""] + [col for col in matrix.columns if col != ""]]
        matrix.columns = [stock.replace(".NS", "") for stock in matrix.columns]
        matrix[""] = [stock.replace(".NS", "") for stock in matrix[""]]

        return df, matrix