from typing import Tuple, List
import pandas as pd
from datetime import datetime

from yahoo_finance.stocks_data_loader import StocksDataLoader


def load_stocks_data(
    tickers: str | List[str],
    st_date: str,
    end_date: str = datetime.today().strftime("%Y-%m-%d")
) -> pd.DataFrame:
    tickers = [tickers] if isinstance(tickers, str) else tickers
    loader = StocksDataLoader(
        tickers,
        pd.to_datetime(st_date).strftime("%Y-%m-%d"),
        pd.to_datetime(end_date).strftime("%Y-%m-%d"),
    )
    stock_dict = loader.get_data()
    return pd.concat(
        stock_dict.values(),
        keys=stock_dict.keys(),
        names=["Ticker", "Date"]
    ).reset_index().drop(columns="Ticker").set_index("Date")


def get_ticker_trades_and_stock_data(
    trading_data: pd.DataFrame,
    ticker: str,
    window: int = 180 # days (lb - window, ub + window)
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    ticker_trading_data = trading_data[trading_data["Ticker"] == ticker]
    ticker_trading_data["Trade Date"] = pd.to_datetime(ticker_trading_data["Trade Date"])
    min_date = ticker_trading_data["Trade Date"].min()
    min_date = min_date - pd.Timedelta(days=window)
    max_date = ticker_trading_data["Trade Date"].max()
    max_date = min(
        min(max_date, max_date + pd.Timedelta(days=30)),
        datetime.today()
    )
    ticker_stock_data = load_stocks_data(
        ticker,
        min_date.strftime("%Y-%m-%d"),
        max_date.strftime("%Y-%m-%d"),
    )
    return ticker_trading_data, ticker_stock_data