from enum import StrEnum


class SummaryStrategy(StrEnum):
    SMALL = "small"
    MAP_REDUCE = "map_reduce"


class SummaryStrategySelector:
    def __init__(self, small_document_token_limit: int = 4000) -> None:
        self.small_document_token_limit = small_document_token_limit

    def select(self, text: str) -> SummaryStrategy:
        estimated_tokens = self.estimate_tokens(text)

        if estimated_tokens <= self.small_document_token_limit:
            return SummaryStrategy.SMALL

        return SummaryStrategy.MAP_REDUCE

    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 3)