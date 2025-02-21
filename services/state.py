# services/state.py

from enum import Enum

class State(Enum):
    HOME = 1
    VIEW_CATEGORIES = 2
    FIND_BEST_DEAL_AWAITING_LINK = 3
    UNKNOWN = 9999
