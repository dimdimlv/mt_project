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
        -   `Total Clicks` for the agent = 50 (observed from simulation).
    -   The simulation is configured such that the cost per click (or total spend) is also predictable. Let's assume:
        -   `Total Spend` for the agent = 250.0 (observed from simulation).
-   **Expected Outcomes (for the specific agent based on the above assumptions):**
    -   The `fixed_conversion_rate` (e.g., 0.1) is treated as the probability of a single click event resulting in a conversion. Therefore, the `Total Conversions` will be a random variable following a binomial distribution B(n, p), where n is `Total Clicks` and p is `fixed_conversion_rate`.
    -   Expected `Total Conversions`: `Total Clicks` * `fixed_conversion_rate` = 50 * 0.1 = 5. The actual observed number of conversions in a simulation run may vary around this expected value.
    -   `Total Sales Revenue`: Actual `Total Conversions` (observed from simulation) * `fixed_sales_revenue_per_conversion`. For an expected 5 conversions, this would be 5 * 100.0 = 500.0.
    -   `CVR (Conversion Rate)`: Actual `Total Conversions` (observed) / `Total Clicks` (observed). This should be close to the `fixed_conversion_rate`.
    -   `ACoS (Advertising Cost of Sales)`: `Total Spend` (observed) / Actual `Total Sales Revenue` (calculated from observed conversions). For an expected 5 conversions and 250.0 spend, this would be 250.0 / 500.0 = 0.5.

## Notes for Execution:

-   These scenarios should be tested by running the `main.py` script with appropriately modified configuration files (e.g., a copy of `SP_Oracle.json`).
-   The actual number of clicks and spend will depend on the simulation dynamics (number of agents, bidding strategies, etc.).
-   For Scenario 2, it is necessary to:
    -   Observe the actual `Total Clicks` and `Total Spend` from the simulation output for an agent.
    -   The `fixed_conversion_rate` acts as a per-click probability. Thus, the actual `Total Conversions` will be a result of a stochastic process (e.g., a binomial distribution based on the number of clicks and the conversion rate).
    -   Calculate the expected `Total Conversions` (mean of the distribution) as `Total Clicks` * `fixed_conversion_rate`.
    -   Then, calculate `Total Sales Revenue`, `CVR`, and `ACoS` based on the *actual observed* `Total Conversions` from the simulation and the observed `Total Clicks` and `Total Spend`.
-   Verify that the reported metrics in the CSV files and plots are internally consistent (e.g., reported CVR = reported Conversions / reported Clicks) and that the observed CVR is statistically consistent with the `fixed_conversion_rate` given the number of clicks.
