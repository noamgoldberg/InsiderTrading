from typing import List, Union, Optional

from open_insider.parameters.validate import validate_list_str_param


class TradeTypesParam:
    
    trade_types = {
        "P": "Purchase",
        "S": "Sale",
        "A": "Grant",
        "D": "Sale to Issuer",
        "G": "Gift",
        "F": "Tax",
        "M": "Option Exercise",
        "X": "Option Exercise",
        "C": "Convertible Derivative",
        "W": "Inherited"
    }
        
    @classmethod
    def validate(cls, trade_types: Optional[Union[str, List[str]]] = None) -> List[str]:
        return validate_list_str_param(
            param_name='trade_types',
            param_value=trade_types,
            options=list(cls.trade_types.keys()) 
        )
