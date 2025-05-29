# AuctionGym Extended Functionality: CVR & ACoS Metrics + Configurable Reward Functions

This document describes the comprehensive extensions made to the original [AuctionGym](auction-gym/README.md) to incorporate:
1. **CVR & ACoS Metrics**: Conversion Rate and Advertising Cost of Sales tracking
2. **Configurable Reward Functions**: Three distinct reward calculation methods for PolicyLearningBidder

These enhancements provide deeper insights into advertising performance and enable optimization for different campaign objectives.

## Setup and Installation

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### Installation Steps

1. **Clone and Setup Environment**
   ```bash
   git clone <your-repository>
   cd mt_project
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Verify Installation**
   ```bash
   # Test basic functionality
   python src/main.py config/Test01_5_5_10K.json
   ```

## New Features Overview

### 1. CVR & ACoS Metrics

Enhanced auction simulation with post-click conversion tracking and sales revenue calculation.

**Core Configuration Parameters:**
- `fixed_conversion_rate`: Probability of conversion per click (e.g., 0.1 for 10%)
- `fixed_sales_revenue_per_conversion`: Revenue amount per conversion (e.g., 100.0)

### 2. Configurable Reward Functions

Three distinct reward calculation methods for PolicyLearningBidder optimization:

#### Net Utility (Default)
```python
rewards = (values * outcomes - prices) * won_mask
```
- **Objective**: Maximize profit (revenue - cost)
- **Use Case**: Balanced campaigns with profit focus

#### Gross Utility
```python
rewards = (values * outcomes) * won_mask
```
- **Objective**: Maximize revenue/clicks without cost penalty
- **Use Case**: Brand awareness, volume maximization

#### Penalty for Wasted Spend
```python
rewards = np.where(outcomes == 1, 
                  (values * outcomes - prices) * won_mask,
                  -prices * won_mask)
```
- **Objective**: Minimize wasted spend on non-converting impressions
- **Use Case**: Performance marketing with strict efficiency targets

## Configuration Guide

### CVR & ACoS Configuration

Add to your JSON configuration files:
```json
{
  "fixed_conversion_rate": 0.1,
  "fixed_sales_revenue_per_conversion": 100.0
}
```

### Reward Function Configuration

Configure PolicyLearningBidder with desired reward type:
```json
{
  "bidders": [
    {
      "bidder_name": "PPO Bidder",
      "bidder_type": "PolicyLearningBidder",
      "bidder_kwargs": {
        "reward_function_type": "net_utility"
      }
    }
  ]
}
```

**Available reward types:**
- `"net_utility"` (default)
- `"gross_utility"`
- `"penalty_wasted_spend"`

## Usage and Reproduction

### Running Basic Experiments

```bash
# CVR & ACoS experiment
python src/main.py config/Test01_5_5_10K.json

# Reward function experiments
python src/main.py config/PPO_NU_R3_I25_RPI100K_C10.json
python src/main.py config/PPO_GU_R3_I25_RPI100K_C10.json
python src/main.py config/PPO_PWS_R3_I25_RPI100K_C10.json
```

### Comprehensive Analysis

```bash
# Analyze reward functions performance
python analyze_reward_functions.py

# Compare baseline performance
python analyze_baseline_comparison.py

# Generate final documentation
python final_analysis.py
```

### Jupyter Notebooks

Explore interactive examples:
```bash
jupyter notebook
# Navigate to src/ and open:
# - Getting Started with AuctionGym (1. Effects of Competition).ipynb
# - Getting Started with AuctionGym (2. Effects of Bid Shading).ipynb
```

## New Metrics Implemented

### CVR & ACoS Metrics

1. **Total Clicks**: Sum of all clicks for an agent
2. **Total Conversions**: Conversions achieved from clicks (probabilistic based on CVR)
3. **Total Sales Revenue**: Revenue from conversions (`conversions * revenue_per_conversion`)
4. **Total Spend**: Amount spent on won auctions
5. **Conversion Rate (CVR)**: `Total Conversions / Total Clicks`
6. **Advertising Cost of Sales (ACoS)**: `Total Spend / Total Sales Revenue`

### Performance Metrics

All reward functions are evaluated on:
- Learning curve convergence
- Final performance metrics
- Bidding behavior patterns
- Cost efficiency measures

## Generated Reports

### CSV Outputs
**CVR & ACoS:**
- `total_clicks_*.csv`, `total_conversions_*.csv`
- `total_sales_revenue_*.csv`, `total_spend_*.csv`
- `cvr_*.csv`, `acos_*.csv`

**Reward Functions:**
- `gross_utility_*.csv`, `net_utility_*.csv`
- `learning_curves_*.csv`, `performance_metrics_*.csv`

### Visualizations
**CVR & ACoS:**
- `CVR_*.pdf`: Conversion rate over time
- `ACoS_*.pdf`: Advertising cost of sales (displayed as percentage)

**Reward Functions:**
- `reward_functions_analysis.pdf`: Comprehensive 15-subplot comparison
- `reward_functions_comparison.png`: High-resolution performance plots

## Code Modifications Summary

### Core Extensions

1. **[`src/Impression.py`](src/Impression.py)**: Extended `ImpressionOpportunity` with conversion tracking
2. **[`src/Auction.py`](src/Auction.py)**: Added conversion simulation logic
3. **[`src/Agent.py`](src/Agent.py)**: New metric calculation methods
4. **[`src/Bidder.py`](src/Bidder.py)**: Configurable reward functions in PolicyLearningBidder
5. **[`src/main.py`](src/main.py)**: Enhanced reporting and configuration parsing

### Analysis Framework

- **[`analyze_reward_functions.py`](analyze_reward_functions.py)**: Comprehensive reward function analysis
- **[`analyze_baseline_comparison.py`](analyze_baseline_comparison.py)**: Performance comparison tools
- **[`final_analysis.py`](final_analysis.py)**: Documentation generation

### Configuration Files

Available configuration files in `/config` folder:
- **[`config/Test01_5_5_10K.json`](config/Test01_5_5_10K.json)**: Basic CVR & ACoS experiment
- **[`config/PPO_NU_R3_I25_RPI100K_C*.json`](config/)**: Net Utility reward experiments (C5, C10, C15)
- **[`config/PPO_GU_R3_I25_RPI100K_C*.json`](config/)**: Gross Utility reward experiments (C5, C10, C15)
- **[`config/PPO_PWS_R3_I25_RPI100K_C*.json`](config/)**: Penalty Wasted Spend experiments (C5, C10, C15)


## Key Findings

### Reward Function Performance
- **Net Utility**: Balanced bidding with ~3 iteration convergence
- **Gross Utility**: Aggressive bidding, higher volume, increased costs
- **Penalty Wasted Spend**: Conservative bidding, strong cost control

### CVR & ACoS Insights
- Enables performance marketing optimization
- Provides actionable efficiency metrics
- Supports campaign ROI analysis

## Extensions and Future Work

The framework is designed for extensibility:

1. **Additional Reward Functions**: Easy to add new optimization objectives
2. **Dynamic CVR**: Replace fixed rates with learned conversion models
3. **Multi-Objective Optimization**: Combine multiple reward signals
4. **Advanced Metrics**: Attribution modeling, lifetime value tracking

## Documentation

Comprehensive documentation available:
- **[Implementation Guide](documentation/implementation_guide.md)**: Technical implementation details
- **[Complete Documentation](documentation/complete_documentation.md)**: Full project analysis
- **[Reward Functions Documentation](documentation/REWARD_FUNCTIONS_DOCUMENTATION.md)**: Detailed performance analysis

## Original AuctionGym

This project extends the original [AuctionGym](auction-gym/README.md) framework. For the base functionality and original research, please refer to:

```bibtex
@inproceedings{10.1145/3580305.3599877,
    author = {Jeunen, Olivier and Murphy, Sean and Allison, Ben},
    title = {Off-Policy Learning-to-Bid with AuctionGym},
    year = {2023},
    publisher = {Association for Computing Machinery},
    booktitle = {Proceedings of the 29th ACM SIGKDD Conference on Knowledge Discovery and Data Mining},
    pages = {4219–4228}
}
```

## License

This project maintains the Apache-2.0 License from the original AuctionGym. See [LICENSE](auction-gym/LICENSE) for details.