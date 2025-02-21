from typing import List, Union


def validate_list_str_param(
    *,
    param_name: str,
    param_value: Union[str, List[str]] | None,
    options: List[str]
) -> List[str]:
    if param_value is None:
        param_value = options
    else:
        if isinstance(param_value, str):
            param_value = [param_value]
        if isinstance(param_value, list):
            if not all(isinstance(v, str) for v in param_value):
                raise TypeError(
                    f"{[type(v).__name__ for v in param_value]}: "
                    f"`{param_name}` parameter must be a list of strings."
                )
        else:
            raise TypeError(
                f"{type(param_value).__name__}: "
                f"`{param_name}` parameter must be either None, a string, or a list of strings."
            )
    if not all(v in options for v in param_value):
        raise ValueError(
            f"Invalid values (types) for `{param_name}` parameter: "
            f"{set(param_value) - set(options)}. "
            f"Choose from {options}."
        )
    return param_value