class NumResultsParam:
    
    @staticmethod
    def validate(num_results: int) -> int:
        if not isinstance(num_results, (int, float)):
            raise TypeError(f"{num_results}: `num_results` must be an integer or float.")
        return int(min(max(num_results, 100), 5000))