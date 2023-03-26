from enum import Enum


class TradeStage(Enum):
    NOT_STARTED = 1
    MAIN = 2
    BETWEEN_MAIN_AND_ADD = 3
    ADD = 4
    FINISHED = 5
