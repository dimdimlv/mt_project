
# Implementation Guide: Configurable Reward Functions in AuctionGym

Generated: 2025-05-26 07:25:28

## Overview

This guide provides step-by-step instructions for implementing and using configurable reward functions in AuctionGym's PolicyLearningBidder class.

## 1. Core Implementation

### Modified PolicyLearningBidder Class

The main changes were made to `/src/Bidder.py`:

```python
class PolicyLearningBidder(Bidder):
    def __init__(self, name, true_cpc, reward_function_type="net_utility", **kwargs):
        # ... existing initialization code ...
        self.reward_function_type = reward_function_type
        
    def update(self, info):
        # ... existing code ...
        
        # Configurable reward calculation
        if self.reward_function_type == "net_utility":
            rewards = (values * outcomes - prices) * won_mask
        elif self.reward_function_type == "gross_utility":
            rewards = (values * outcomes) * won_mask
        elif self.reward_function_type == "penalty_wasted_spend":
            rewards = np.where(outcomes == 1, 
                             (values * outcomes - prices) * won_mask,
                             -prices * won_mask)
        else:
            raise ValueError(f"Unknown reward function type: {self.reward_function_type}")
```

## 2. Configuration Files

Three configuration files were created in `/config/`:

- `PolicyLearner_NetUtility.json` - Standard net utility approach
- `PolicyLearner_GrossUtility.json` - Revenue-focused approach  
- `PolicyLearner_PenaltyWastedSpend.json` - Cost-efficiency focused approach

### Configuration Template

```json
{
    "save_dir": "PolicyLearner_[REWARD_TYPE]",
    "engine": "AuctionGym",
    "rounds": 10000,
    "iterations": 5,
    "runs": 3,
    "bidders": [
        {
            "bidder_name": "PPO Bidder",
            "bidder_type": "PolicyLearningBidder",
            "bidder_kwargs": {
                "gamma": 0.99,
                "reward_function_type": "'[REWARD_TYPE]'"
            }
        }
    ]
}
```

## 3. Usage Instructions

### Running Experiments

```bash
# Navigate to project directory
cd /Users/dimdim/PycharmProjects/mt_project

# Run each configuration
python src/main.py config/PolicyLearner_NetUtility.json
python src/main.py config/PolicyLearner_GrossUtility.json  
python src/main.py config/PolicyLearner_PenaltyWastedSpend.json
```

### Analysis

```bash
# Run comprehensive analysis
python analyze_reward_functions.py
```

## 4. Key Considerations

### When to Use Each Reward Function

1. **Net Utility** (`"net_utility"`):
   - Default choice for balanced performance
   - Optimizes profit = revenue - cost
   - Best for standard campaign objectives

2. **Gross Utility** (`"gross_utility"`):
   - Focus on maximizing revenue/clicks
   - Use when budget constraints are less important
   - Good for brand awareness campaigns

3. **Penalty Wasted Spend** (`"penalty_wasted_spend"`):
   - Emphasis on cost efficiency
   - Minimizes wasted spend on non-converting impressions
   - Ideal for performance marketing with strict ROAS targets

### Implementation Notes

- The `reward_function_type` parameter must be properly quoted in JSON configs
- All reward functions maintain compatibility with existing PPO training
- Convergence behavior is similar across all reward types (typically 3 iterations)

## 5. Extension Points

To add new reward functions:

1. Add the reward type to the `if-elif` chain in `PolicyLearningBidder.update()`
2. Create corresponding configuration file
3. Test with the analysis framework

Example for adding a "bid_efficiency" reward:

```python
elif self.reward_function_type == "bid_efficiency":
    # Reward based on bid-to-price ratio efficiency
    bid_efficiency = np.where(prices > 0, bids / prices, 0)
    rewards = (values * outcomes * bid_efficiency) * won_mask
```
