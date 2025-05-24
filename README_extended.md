# AuctionGym Extended Functionality: CVR & ACoS Metrics

This document describes the extensions made to the original AuctionGym to incorporate Conversion Rate (CVR) and Advertising Cost of Sales (ACoS) metrics. These metrics provide deeper insights into advertising performance beyond click-through rates and utility.

## Core Changes

The primary modification involves simulating conversion events post-click and associating a sales revenue with each conversion. This is achieved using two new global configuration parameters:

1.  `fixed_conversion_rate`: This floating-point value (e.g., `0.05` for 5%) represents the probability that a click on an ad will result in a conversion. The simulation uses this rate to stochastically determine if a conversion occurs for each click.
2.  `fixed_sales_revenue_per_conversion`: This floating-point value (e.g., `50.0`) represents the amount of revenue generated when a conversion occurs.

## New Metrics Implemented

Based on these new simulation capabilities, the following metrics have been added:

### 1. Total Clicks
   - **Definition:** The total number of times an agent's ad was clicked after winning an auction.
   - **Calculation:** Sum of all clicks for a specific agent.

### 2. Total Conversions
   - **Definition:** The total number of conversions achieved by an agent from their clicks.
   - **Calculation:** Sum of all conversion events for a specific agent. Each conversion is determined probabilistically based on `fixed_conversion_rate` after a click occurs.

### 3. Total Sales Revenue
   - **Definition:** The total revenue generated from all conversions for an agent.
   - **Calculation:** `Total Conversions` * `fixed_sales_revenue_per_conversion`.

### 4. Total Spend
   - **Definition:** The total amount an agent spent to win the auctions that resulted in impressions (and potentially clicks/conversions).
   - **Calculation:** Sum of the prices paid by the agent for all won auctions.

### 5. Conversion Rate (CVR)
   - **Definition:** The rate at which clicks turn into conversions.
   - **Calculation:** `Total Conversions` / `Total Clicks`.
   - **Handling Edge Cases:** If `Total Clicks` is 0, CVR is reported as 0.0.

### 6. Advertising Cost of Sales (ACoS)
   - **Definition:** The ratio of advertising spend to the revenue generated from those advertisements. It measures the efficiency of the ad spend.
   - **Calculation:** `Total Spend` / `Total Sales Revenue`.
   - **Handling Edge Cases:**
     - If `Total Sales Revenue` is 0:
       - If `Total Spend` is also 0, ACoS is 0.0.
       - If `Total Spend` > 0, ACoS is `infinity` (represented as `inf` in CSVs).
   - **Reporting in Plots:** In the generated PDF plots, ACoS is displayed as a percentage (e.g., 0.25 is shown as 25%).

## Configuration Updates

To use the new CVR and ACoS features, you must add the following parameters to your JSON configuration files (e.g., `config/SP_Oracle.json`):

```json
{
  // ... existing parameters ...
  "fixed_conversion_rate": 0.1, // Example: 10% probability of conversion per click
  "fixed_sales_revenue_per_conversion": 100.0 // Example: $100 revenue per conversion
}
```

If these parameters are not present, they will default to `0.0`, effectively disabling the conversion and sales revenue calculations.

## New Reports

The `main.py` script has been updated to generate new reports for these metrics. These are saved in the specified `output_dir`.

### CSV Outputs:

For each simulation run, the following CSV files are generated, containing per-agent, per-iteration data:

-   `total_clicks_...csv`: Contains the total clicks for each agent.
-   `total_conversions_...csv`: Contains the total conversions for each agent.
-   `total_sales_revenue_...csv`: Contains the total sales revenue for each agent.
-   `total_spend_...csv`: Contains the total spend for each agent.
-   `cvr_...csv`: Contains the calculated CVR for each agent.
-   `acos_...csv`: Contains the calculated ACoS for each agent (as a decimal ratio).

### PDF Plot Outputs:

The following new plots are generated, showing the metric over time (iterations) for each agent:

-   `CVR_...pdf`: Plots the Conversion Rate.
-   `ACoS_...pdf`: Plots the Advertising Cost of Sales. **Note:** In this plot, ACoS is displayed as a percentage.

These new reports are generated in addition to the existing reports from the original AuctionGym.

## Code Modifications Summary

-   **`src/Impression.py`**: `ImpressionOpportunity` was extended to store `conversion` (bool) and `sales_revenue` (float).
-   **`src/Auction.py`**: The `Auction` class now accepts `fixed_cvr` and `fixed_sales_revenue_per_conversion` from the config. The `simulate_opportunity` method was updated to:
    - Probabilistically determine if a conversion occurs after a click based on `fixed_cvr`.
    - Assign `fixed_sales_revenue_per_conversion` if a conversion happens.
    - Log these details in the `ImpressionOpportunity` for the winning agent.
-   **`src/Agent.py`**: The `Agent` class was augmented with new methods to calculate total clicks, total conversions, total sales revenue, total spend, CVR, and ACoS based on its logs.
-   **`src/main.py`**:
    - Updated to parse the new configuration parameters.
    - Collects the new metrics from each agent after each iteration.
    - Generates the new CSV files and PDF plots as described above.
    - Modified the plotting function to display ACoS as a percentage in the ACoS-specific plot.
