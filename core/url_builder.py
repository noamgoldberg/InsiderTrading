from typing import List, Union, Optional

from core.parameters.job_titles import JobTitlesParam
from core.parameters.num_results import NumResultsParam
from core.parameters.trade_value import TradeValueParams
from consts import OI_URL


class URLBuilder:
    BASE_URL = f"{OI_URL}/screener"
    
    def __init__(
        self,
        num_results: int = 1000,
        job_titles: Optional[Union[str, List[str]]] = None,
        trade_val_min: Optional[int] = None,
        trade_val_max: Optional[int] = None,
    ) -> None:
        self.num_results = NumResultsParam.validate(num_results)
        self.job_titles = JobTitlesParam.validate(job_titles)
        self.trade_val_min, self.trade_val_max = TradeValueParams.validate(trade_val_min, trade_val_max)
    
    def build(self) -> str:
        job_titles_params = JobTitlesParam.to_url_params(self.job_titles)
        trade_val_params = TradeValueParams.to_url_params(self.trade_val_min, self.trade_val_max)
        return f"{self.BASE_URL}?cnt={self.num_results}&{job_titles_params}&{trade_val_params}".rstrip("&")