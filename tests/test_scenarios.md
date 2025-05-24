# Test Scenarios for CVR and ACoS Metrics

This document outlines test scenarios designed to validate the correct implementation and calculation of Conversion Rate (CVR) and Advertising Cost of Sales (ACoS) metrics in the extended AuctionGym.

## Scenario 1: Zero CVR

-   **Objective:** Verify that when the fixed conversion rate is zero, all conversion-related metrics are zero, and ACoS is handled appropriately (e.g., undefined or zero).
-   **Configuration:**
    -   Set `"fixed_conversion_rate": 0.0` in the simulation configuration file.
    -   Set `"fixed_sales_revenue_per_conversion": 100.0` (or any value, as it shouldn't affect the outcome if CVR is 0).
-   **Assumptions:**
    -   The simulation runs for a number of rounds, generating impressions and clicks for at least one agent.
-   **Expected Outcomes (for any agent with clicks):**
    -   `Total Conversions`: 0
    -   `Total Sales Revenue`: 0.0
    -   `CVR (Conversion Rate)`: 0.0
    -   `ACoS (Advertising Cost of Sales)`: Undefined (or reported as 0 or NaN, depending on implementation for division by zero). If spend is > 0 and sales revenue is 0, ACoS is effectively infinite. The implementation should handle this gracefully.

## Scenario 2: Non-Zero Fixed CVR & Sales Revenue

-   **Objective:** Verify that CVR and ACoS are calculated correctly when both fixed conversion rate and fixed sales revenue per conversion are non-zero.
-   **Configuration:**
    -   Set `"fixed_conversion_rate": 0.1` (i.e., 10% CVR).
    -   Set `"fixed_sales_revenue_per_conversion": 100.0`.
-   **Assumptions for Manual Calculation (for a specific agent):**
    -   The agent wins and secures a click for a predictable number of opportunities. Let's assume:
        -   `Total Clicks` for the agent = 50.
    -   The simulation is configured such that the cost per click (or total spend) is also predictable. For simplicity in this scenario, let's assume:
        -   `Total Spend` for the agent = 250.0 (e.g., 50 clicks at an average cost of 5.0 per click).
-   **Expected Outcomes (for the specific agent based on the above assumptions):**
    -   `Total Conversions`: `Total Clicks` * `fixed_conversion_rate` = 50 * 0.1 = 5.
    -   `Total Sales Revenue`: `Total Conversions` * `fixed_sales_revenue_per_conversion` = 5 * 100.0 = 500.0.
    -   `CVR (Conversion Rate)`: `Total Conversions` / `Total Clicks` = 5 / 50 = 0.1.
    -   `ACoS (Advertising Cost of Sales)`: `Total Spend` / `Total Sales Revenue` = 250.0 / 500.0 = 0.5.

## Notes for Execution:

-   These scenarios should be tested by running the `main.py` script with appropriately modified configuration files (e.g., a copy of `SP_Oracle.json`).
-   The actual number of clicks and spend will depend on the simulation dynamics (number of agents, bidding strategies, etc.). For Scenario 2, it might be necessary to:
    -   Run a simulation with a very simple setup (e.g., one dominant agent).
    -   Or, observe the actual `Total Clicks` and `Total Spend` from the simulation output for an agent, and then calculate the expected `Total Conversions`, `Total Sales Revenue`, `CVR`, and `ACoS` based on those observed values and the fixed configuration parameters.
-   Verify that the reported metrics in the CSV files and plots match these expected outcomes.
