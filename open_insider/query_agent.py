import time
from typing import Dict, Any, List, Union, Optional
import pandas as pd
import numpy as np

from open_insider.query import Query
from open_insider.parameters.trade_types import TradeTypesParam


def get_current_time() -> str:
    return time.strftime('%Y-%m-%d %H:%M:%S')


class QueryAgent:

    def __init__(self, remember: Union[bool, int] = True, max_rows: int = 5000) -> None:
        self.remember = int(np.abs(remember)) if isinstance(remember, (int, float)) else remember
        self.max_rows = max_rows
        self.data = []
        print(f"[{get_current_time()}] QueryAgent initialized with max_rows={max_rows}")

    def remember_data(self, params: Dict[str, Any], df: pd.DataFrame) -> None:
        if self.remember:
            self.data.append((params, df))  # Store the scraped data
            if isinstance(self.remember, int):
                self.data = self.data[-self.remember:]

    def get_existing_data(
        self,
        job_titles: Optional[Union[str, List[str]]] = None,
        trade_val_min: Optional[int] = None,
        trade_val_max: Optional[int] = None,
    ) -> None | pd.DataFrame:
        """Returns cached data if the current query is fully contained in an existing dataset."""
        job_titles = job_titles or []  # Ensure job_titles is a list
        print(f"[{get_current_time()}] Checking cache for job_titles={job_titles}, "
              f"trade_val_min={trade_val_min}, trade_val_max={trade_val_max}")
        for params, df in self.data:
            params: Dict[str, Any]
            prev_job_titles = set(params.get("job_titles") or [])
            prev_trade_val_min = params.get("trade_val_min") or float('-inf')
            prev_trade_val_max = params.get("trade_val_max") or float('inf')
            prev_num_results = params.get("num_results") or 0
            if (
                prev_job_titles == set(job_titles) and
                prev_trade_val_min <= (trade_val_min or float('-inf')) and
                prev_trade_val_max >= (trade_val_max or float('inf')) and
                prev_num_results < self.max_rows
            ):
                print(f"[{get_current_time()}] Cache hit! Reusing existing data.")
                return df  # Safe to reuse the cached data
        print(f"[{get_current_time()}] Cache miss. No suitable cached data found.")
        return None

    @staticmethod
    def filter_df(
        df: pd.DataFrame,
        trade_types: Optional[Union[str, List[str]]] = None,
        trade_val_min: Optional[int] = None,
        trade_val_max: Optional[int] = None,
    ) -> pd.DataFrame:
        """Filters the dataframe based on the given parameters."""
        print(f"[{get_current_time()}] Filtering DataFrame with trade_types={trade_types}, "
              f"trade_val_min={trade_val_min}, trade_val_max={trade_val_max}")
        if trade_types:
            trade_types = TradeTypesParam.validate(trade_types)
            df = df[df["Trade Type"].apply(lambda tt: tt.split(' - ')[0]).isin(trade_types)]
        if trade_val_min is not None:
            df = df[df["Value"] >= trade_val_min]
        if trade_val_max is not None:
            df = df[df["Value"] <= trade_val_max]
        print(f"[{get_current_time()}] Filtering complete. Resulting DataFrame shape: {df.shape}")
        return df

    @staticmethod
    def preprocess_data(
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        df.columns = df.columns.str.replace("\xa0", " ")
        df.drop(columns=["1d", "1w", "1m", "6m"], inplace=True)
        df.rename(columns={"X": "Filing Type", "Qty": "Quantity"}, inplace=True)
        df["Filing Type"] = df["Filing Type"].astype("category")
        df["Quantity"] = df["Quantity"].astype(int)
        df["Filing Date"] = pd.to_datetime(df["Filing Date"])
        df["Price"] = df["Price"].str.replace(r'[\$,+]', '', regex=True).astype(float)
        df["Value"] = df["Value"].str.replace(r'[\$,+]', '', regex=True).astype(float)
        df["Owned"] = df["Owned"].astype(int)
        df["ΔOwn"] = df["ΔOwn"].replace("New", np.nan).str.replace(r'[\$,+%>]', '', regex=True).astype(float) / 100
        df["Title"] = df["Title"].str.split(", ")
        return df

    def scrape(
        self,
        trade_types: Optional[Union[str, List[str]]] = ["P", "S"],
        job_titles: Optional[Union[str, List[str]]] = None,
        trade_val_min: Optional[int] = None,
        trade_val_max: Optional[int] = None,
        num_results: int = 1000
    ) -> pd.DataFrame:
        """Executes a query by scraping OpenInsider, reusing cached data when possible."""
        print(f"\n[{get_current_time()}] Initiating scrape request with parameters:")
        print(f"\tTrade Types: {trade_types}")
        print(f"\tJob Titles: {job_titles}")
        print(f"\tTrade Volume Min: {trade_val_min}")
        print(f"\tTrade Volume Max: {trade_val_max}")
        print(f"\tNumber of Results: {num_results}\n")
        existing_data = self.get_existing_data(
            job_titles=job_titles,
            trade_val_min=trade_val_min,
            trade_val_max=trade_val_max,
        )
        if existing_data is None:
            query = Query(
                job_titles=job_titles,
                trade_val_min=trade_val_min,
                trade_val_max=trade_val_max,
                num_results=num_results,
            )
            start_time = time.time()
            print(f"[{get_current_time()}] Scraping new data with query:\n")
            print(f"\t{query.describe()}")
            print(f"\tURL: {query.url}\n")
            try:
                df = pd.read_html(query.url)[11]  # Fetch the 11th table from the webpage
                print(f"[{get_current_time()}] Scraping successfully completed in {time.time() - start_time:.2f} seconds")
            except Exception as e:
                print(f"[{get_current_time()}] Error during scraping: {e}")
                return pd.DataFrame()  # Return empty DataFrame in case of failure
            df = self.preprocess_data(df)
            if self.remember:
                self.remember_data(query.params, df)
        else:
            df = existing_data
            print(f"[{get_current_time()}] Using cached data. No scraping needed.")
        return self.filter_df(
            df,
            trade_types=trade_types,
            trade_val_min=trade_val_min,
            trade_val_max=trade_val_max,
        )

    def clear(self) -> None:
        """Clears all cached data."""
        print(f"[{get_current_time()}] Clearing cached data...")
        self.data.clear()
        print(f"[{get_current_time()}] Cache cleared successfully.")
