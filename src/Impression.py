import numpy as np
from dataclasses import dataclass, field


class _ImpressionSlotsBase:
    """Base class to define slots that are not dataclass fields."""
    __slots__ = 'winning_bid', # 'winning_bid' was in __slots__ but not a typed field

@dataclass(slots=True) # Let dataclass manage slots for its fields
class ImpressionOpportunity(_ImpressionSlotsBase):
    # Manual __slots__ removed. Dataclass will generate slots for fields below
    # and inherit 'winning_bid' from _ImpressionSlotsBase.
    context: np.array
    item: np.uint32
    value: np.float32
    bid: np.float32
    best_expected_value: np.float32
    true_CTR: np.float32
    estimated_CTR: np.float32
    price: np.float32
    second_price: np.float32
    # If 'winning_bid' was intended as a dataclass field, it should be defined here with a type.
    # e.g., winning_bid: np.float32 = field(default=0.0)
    # Since it was only in __slots__ before, we keep it as an inherited slot for now.
    outcome: np.bool_
    won: np.bool_
    conversion: bool = field(default=False)
    sales_revenue: np.float32 = field(default=0.0)

    def set_true_CTR(self, best_expected_value, true_CTR):
        self.best_expected_value = best_expected_value  # Best possible CTR (to compute regret from ad allocation)
        self.true_CTR = true_CTR  # True CTR for the chosen ad

    def set_price_outcome(self, price, second_price, outcome, won=True):
        self.price = price
        self.second_price = second_price
        self.outcome = outcome
        self.won = won

    def set_price(self, price):
        self.price = price

    def set_conversion_details(self, converted: bool, revenue: float):
        self.conversion = converted
        self.sales_revenue = revenue
