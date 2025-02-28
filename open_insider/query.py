from typing import List, Union, Optional, Dict, Any

from open_insider.url_builder import URLBuilder
from open_insider.parameters.job_titles import JobTitlesParam
from open_insider.parameters.trade_value import TradeValueParams
from open_insider.parameters.num_results import NumResultsParam


class Query:
    
    def __init__(
        self,
        job_titles: Optional[Union[str, List[str]]] = None,
        trade_val_min: Optional[int] = None,
        trade_val_max: Optional[int] = None,
        num_results: int = 1000,
    ):
        self.job_titles = JobTitlesParam.validate(job_titles)
        self.trade_val_min, self.trade_val_max = TradeValueParams.validate(trade_val_min, trade_val_max)
        self.num_results = NumResultsParam.validate(num_results)
        
    @property
    def params(self) -> str:
        return dict(
            job_titles=self.job_titles,
            trade_val_min=self.trade_val_min,
            trade_val_max=self.trade_val_max,
            num_results=self.num_results,
        )

    def describe(self) -> Dict[str, Any]:
        return self.params

    @property
    def url(self) -> str:
        return URLBuilder(**self.params).build()