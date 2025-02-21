from typing import Optional, Tuple


class TradeValueParams:
        
    @staticmethod
    def _validate_single(param_name: str, param_value: int | None) -> int | None:
        if param_value is not None:
            if not isinstance(param_value, (int, float)):
                raise TypeError(f"{param_value}: `{param_name}` must be an integer, float, or None.")
            if isinstance(param_value, float) and param_value != int(param_value):
                raise ValueError(f"{param_value}: `{param_name}` must be a whole number if provided as a float.")
            if param_value < 0:
                raise ValueError(f"{param_value}: `{param_name}` must be a non-negative value.")
        return int(param_value) if param_value is not None else None

    @classmethod
    def validate(
        cls,
        trade_val_min: Optional[int] = None,
        trade_val_max: Optional[int] = None
    ) -> Tuple[int | None, int | None]:
        return (
            cls._validate_single('trade_val_min', trade_val_min),
            cls._validate_single('trade_val_max', trade_val_max)
        )
    
    @staticmethod
    def to_url_params(
        trade_val_min: Optional[int] = None,
        trade_val_max: Optional[int] = None
    ) -> str:
        params = []
        if trade_val_min is not None:
            params.append(f"vl={trade_val_min}")
        if trade_val_max is not None:
            params.append(f"vh={trade_val_max}")
        return "&".join(params)