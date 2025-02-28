def strip_stock_symbol(symbol: str) -> str:
    return symbol.split(":")[-1].replace('.', '-')