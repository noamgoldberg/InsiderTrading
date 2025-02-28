from typing import Union, Iterable, Optional, Callable, Any, Dict
import yfinance as yf
import pandas as pd
import streamlit as st

from yahoo_finance.formatting_utils import strip_stock_symbol
from utils.wrapper_utils import wrapper


class StocksDataLoader:
    
    def __init__(
        self,
        symbols: Union[str, Iterable[str]],
        start_date: str,
        end_date: Optional[str] = None,
        verbose: int = 0
    ):
        self.symbols = self.obj2list(symbols)
        [symbols] if isinstance(symbols, str) else list(symbols)
        self.symbols = list(map(strip_stock_symbol, self.symbols))
        invalid_tickers = [symbol for symbol in self.symbols if not self.is_ticker_valid(symbol)]
        if len(invalid_tickers) > 0:
            error = f"The following tickers are invalid: {invalid_tickers}"
            st.error(error)
            raise Exception(error)
        self.start_date = start_date
        self.end_date = end_date
        self.verbose = verbose
        self._data = None
    
    @staticmethod
    def obj2list(obj: Any) -> list:
        return [obj] if isinstance(obj, str) else list(obj)
    
    @staticmethod
    def is_ticker_valid(ticker: str):
        """
        Checks if a ticker is available via the Yahoo Finance API.
        """
        info = yf.Ticker(ticker).history(
            period='7d',
            interval='1d'
        )
        return len(info) > 0

    def download_and_clean_data(
        self,
        symbols: Union[str, Iterable[str]],
        start_date: str,
        end_date: Optional[str] = None,
        batch_size: Optional[int] = 10,
    ) -> pd.DataFrame:
        symbols = self.obj2list(symbols)
        all_data = []
        for i in range(0, len(symbols), batch_size):
            batch_symbols = symbols[i:i + batch_size]
            data: pd.DataFrame = yf.download(batch_symbols, start=start_date, end=end_date, progress=bool(self.verbose))
            data.columns = data.columns.swaplevel(0, 1)
            data.sort_index(axis=1, level=0, inplace=True)
            all_data.append(data)
        
        return pd.concat(all_data, axis=1) if all_data else pd.DataFrame()
    
    @property
    def data(self) -> pd.DataFrame:
        if self._data is None:
            self._data = self.download_and_clean_data(self.symbols, self.start_date, end_date=self.end_date)
        return self._data

    def get_data(
        self,
        return_dict: bool = True,
        _callable: bool = False
    ) -> Union[Dict[str, Callable], pd.DataFrame]:
        if return_dict:
            def _get_ticker_data(ticker: str) -> Callable:
                return self.data[ticker]
            partitions = {
                ticker: (wrapper(_get_ticker_data, ticker) if _callable else _get_ticker_data(ticker))
                for ticker in self.data.columns.get_level_values('Ticker').unique()
            }
            return partitions
        return self.data