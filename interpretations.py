import streamlit as st
from risk import RiskMetrics

def metric_info():
    st.write("")
    st.markdown("##### 1. Mean Return (Monthly and Annualized)")
    st.markdown("**Interpretation**: Mean Return indicates the average return the portfolio generates over a specific period. It shows how much the portfolio is earning on average every month or year.")
    st.markdown("**Ideal Range**: Positive values are desirable. Higher mean returns indicate better performance. However, returns must be evaluated relative to the risk taken to achieve them.")
    
    st.markdown("##### 2. Standard Deviation (Monthly and Annualized)")
    st.markdown("**Interpretation**: Standard Deviation measures the portfolio's volatility or risk. It shows how much the portfolio’s returns deviate from the average return. Higher values indicate more significant fluctuations.")
    st.markdown("**Ideal Range**: Lower values are generally preferred as they indicate lower risk. However, in a high-return portfolio, slightly higher volatility might be acceptable.")
    
    st.markdown("##### 3. Downside Standard Deviation")
    st.markdown("**Interpretation**: Downside Standard Deviation measures the portfolio's volatility concerning negative returns only, providing a more focused view of the risk of losses.")
    st.markdown("**Ideal Range**: Lower values are better, indicating fewer and less severe downside deviations.")
    
    st.markdown("##### 4. Maximum Drawdown")
    st.markdown("**Interpretation**: Maximum Drawdown is the largest peak-to-trough decline in the portfolio’s value, representing the worst loss from a historical peak before a recovery occurs. It measures the risk of a portfolio experiencing significant losses.")
    st.markdown("**Ideal Range**: Lower values are preferred, indicating less severe losses. Investors often seek to minimize Maximum Drawdown to protect capital.")
    
    st.markdown("##### 5. Beta")
    st.markdown("**Interpretation**: Beta measures the portfolio's sensitivity to market movements. A beta greater than 1 indicates that the portfolio is more volatile than the market, while a beta less than 1 indicates it is less volatile.")
    st.markdown("**Ideal Range**: A beta close to 1 indicates that the portfolio's volatility is similar to the market's. Lower values (less than 1) suggest lower risk, but potentially lower returns. Higher values (greater than 1) suggest higher risk, but potentially higher returns.")

    st.markdown("##### 6. Alpha")
    st.markdown("**Interpretation**: Alpha represents the portfolio's excess return over the benchmark, considering the risk taken. A positive alpha indicates outperformance relative to the market, while a negative alpha indicates underperformance.")
    st.markdown("**Ideal Range**: Positive values are desirable, as they indicate that the portfolio is outperforming the benchmark after adjusting for risk.")

    st.markdown("##### 7. Sharpe Ratio")
    st.markdown("**Interpretation**: The Sharpe Ratio measures the risk-adjusted return of the portfolio. It shows how much excess return is generated for each unit of risk.")
    st.markdown("**Ideal Range**: Higher values are better, indicating that the portfolio is generating higher returns for each unit of risk taken. A Sharpe Ratio above 1 is generally considered good.")

    st.markdown("##### 8. Sortino Ratio")
    st.markdown("**Interpretation**: The Sortino Ratio is similar to the Sharpe Ratio but focuses only on downside risk. It measures the portfolio's risk-adjusted return, considering only the negative deviations.")
    st.markdown("**Ideal Range**: Higher values are preferred, indicating better returns per unit of downside risk. A Sortino Ratio above 2 is considered excellent.")

    st.markdown("##### 9. Treynor Ratio")
    st.markdown("**Interpretation**: The Treynor Ratio measures the portfolio's risk-adjusted return relative to its beta (systematic risk). It shows how much excess return is generated for each unit of market risk.")
    st.markdown("**Ideal Range**: Higher values are better, indicating that the portfolio is generating higher returns per unit of market risk.")

    st.markdown("##### 10. Calmar Ratio")
    st.markdown("**Interpretation**: The Calmar Ratio measures the portfolio's risk-adjusted return relative to its maximum drawdown. It provides insight into how well the portfolio compensates for drawdowns.")
    st.markdown("**Ideal Range**: Higher values are preferred, indicating better performance relative to the drawdown risk. A Calmar Ratio above 1 is considered good.")

    st.markdown("##### 11. Tracking Error")
    st.markdown("**Interpretation**: Tracking Error measures the standard deviation of the portfolio's excess returns relative to its benchmark. It shows how closely the portfolio follows its benchmark.")
    st.markdown("**Ideal Range**: Lower values are better if the goal is to closely track the benchmark. Higher values might be acceptable in actively managed portfolios aiming for higher returns.")

    st.markdown("##### 12.Information Ratio")
    st.markdown("**Interpretation**: The Information Ratio measures the portfolio's excess return relative to the benchmark, adjusted for the tracking error. It assesses the consistency of the portfolio’s outperformance.")
    st.markdown("**Ideal Range**: Higher values are preferred, indicating consistent outperformance relative to the benchmark. An Information Ratio above 0.5 is generally considered good.")

    st.markdown("##### 13. Skewness")
    st.markdown("**Interpretation**: Skewness measures the asymmetry of the return distribution. A positive skew indicates a distribution with more frequent small gains and a few large losses, while a negative skew indicates the opposite.")
    st.markdown("**Ideal Range**: Positive skewness is generally preferred, indicating the potential for more frequent small gains and fewer large losses.")

    st.markdown("##### 14. Excess Kurtosis")
    st.markdown("**Interpretation**: Excess Kurtosis measures the \"tailedness\" of the return distribution. Higher kurtosis indicates more frequent extreme returns (both positive and negative), while lower kurtosis suggests fewer extreme returns.")
    st.markdown("**Ideal Range**: Lower values are generally preferred, indicating fewer extreme returns and a more stable return distribution.")

    st.markdown("##### 15. Positive Periods")
    st.markdown("**Interpretation**: Positive Periods refers to the number of periods where the portfolio experienced positive returns. It provides insight into the consistency of the portfolio's performance.")
    st.markdown("**Ideal Range**: Higher percentages are better, indicating that the portfolio experiences positive returns in more periods. However, this metric should be considered in conjunction with other risk and return metrics.")


def var_info():
    st.markdown("##### Value at Risk (VaR)")
    st.markdown("**Interpretation**: VaR measures the maximum potential loss of the portfolio over a specified time period at different confidence levels. For example, at a 95% confidence level, VaR would indicate the maximum loss expected with a 5% chance of occurring over the period.")
    st.markdown("**Ideal Range**: Lower VaR values indicate less risk, as they suggest smaller potential losses. The acceptable range depends on the investor's risk tolerance, but generally, the goal is to keep VaR values as low as possible without sacrificing too much return.")

    st.markdown("##### Conditional Value at Risk (CVaR)")
    st.markdown("**Interpretation**: CVaR estimates the average loss in the worst-case scenarios beyond the VaR threshold. If the portfolio experiences losses exceeding the VaR, CVaR indicates the expected average loss in those extreme cases.")
    st.markdown("**Ideal Range**: Lower CVaR values are preferable as they indicate smaller average losses in extreme situations. Minimizing CVaR helps in managing tail risk and protecting against severe market downturns.")

def appinfo():
    st.markdown("This app optimizes a stock portfolio using a range of optimization techniques to identify the most efficient allocation based on the selected criteria. Simply enter your stock tickers, choose a historical date range, and watch as the app analyzes performance and delivers tailored allocation recommendations to help you achieve your investment goals.")

def optimization_strategies_info():
    st.write("")
    st.markdown("**Sharpe Ratio**: Measures the return per unit of total risk taken. This metric is ideal for investors seeking to maximize returns relative to risk. A higher Sharpe Ratio indicates more effective risk management alongside return generation.")
    st.markdown( "**Volatility**: Represented by the standard deviation of portfolio returns, this metric is crucial for investors focused on reducing fluctuations in their portfolio's value. Lower volatility signifies a more stable investment, aligning with conservative investment strategies.")
    st.markdown("**Sortino Ratio**: This ratio emphasizes downside risk by measuring returns per unit of negative volatility. It’s beneficial for investors who prioritize capital preservation and want to avoid significant losses. A higher Sortino Ratio indicates better performance in adverse market conditions.")
    st.markdown("**Tracking Error**: This metric measures how closely a portfolio's returns follow its benchmark. It’s suitable for investors who want to ensure their portfolio closely aligns with a benchmark index. A lower Tracking Error indicates consistency with benchmark performance.")
    st.markdown("**Information Ratio**: This ratio evaluates returns above a benchmark relative to the active risk taken. It’s ideal for active investors who seek to outperform a benchmark while managing risk. A higher Information Ratio indicates successful active management.")
    st.markdown("**Conditional Value-at-Risk (CVaR)**: This metric estimates potential losses in extreme market conditions, focusing on worst-case scenarios. It's essential for risk-averse investors looking to safeguard their capital against severe downturns. Lower CVaR values indicate better risk protection.")
    st.markdown("*Benchmark: NIFTY50*")