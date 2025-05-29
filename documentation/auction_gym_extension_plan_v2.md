# Project Plan: Extending AuctionGym with CVR & ACoS Metrics (v2)

This project plan outlines the steps to clone the original AuctionGym repository, implement CVR (Conversion Rate) and ACoS (Advertising Cost of Sales) metrics using a fixed CVR and fixed sales revenue per conversion, test these new features, and integrate new reports into the existing system.

## Phase 1: Setup and Codebase Understanding

### Step 1: Clone the Original Repository
   - **Action:** Obtain the source code for AuctionGym.
   - **Details:**
     ```bash
     git clone [https://github.com/amazon-science/auction-gym.git](https://github.com/amazon-science/auction-gym.git)
     cd auction-gym
     git remote rm origin # Remove the link to the original repository
     ```
   - **Deliverable:** A local copy of the AuctionGym repository.

### Step 2: Set Up the Python Environment
   - **Action:** Create a virtual environment and install the necessary dependencies.
   - **Details:**
     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     pip install -r requirements.txt
     pip install jupyter notebook # If you plan to use the notebooks
     ```
   - **Deliverable:** A functional Python environment for the project.

### Step 3: Understand the Existing Codebase
   - **Action:** Familiarize yourself with the key components of AuctionGym.
   - **Key Files to Review:**
     - `src/Impression.py`: Defines `ImpressionOpportunity`.
     - `src/Auction.py`: Auction simulation logic. `item_values` is used as Value Per Click (VPC) for the advertiser.
     - `src/Agent.py`: Agent behavior, logging.
     - `src/main.py`: Simulation runs, data aggregation, reporting.
     - `config/`: Simulation parameter definitions.
   - **Deliverable:** Understanding of where to make modifications.

## Phase 2: Feature Implementation (CVR & ACoS)

### Step 4: Modify `src/Impression.py`
   - **Action:** Extend `ImpressionOpportunity` for conversion and sales revenue.
   - **Details:**
     - In the `ImpressionOpportunity` dataclass:
       - Add `conversion: bool = field(default=False)`
       - Add `sales_revenue: np.float32 = field(default=0.0)`
       - Add these to `__slots__`.
       - Add method: `set_conversion_details(self, converted: bool, revenue: float)` to update these fields.
   - **Deliverable:** Updated `ImpressionOpportunity` dataclass.

### Step 5: Modify `src/Auction.py`
   - **Action:** Update the `Auction` class to simulate conversions based on a fixed CVR and log a fixed sales revenue.
   - **Details:**
     - **Constructor (`__init__`):**
       - Modify to accept `fixed_cvr: float` and `fixed_sales_revenue_per_conversion: float` from the configuration.
       - Store these as instance variables (e.g., `self.fixed_cvr`, `self.fixed_sales_revenue_per_conversion`).
     - **`simulate_opportunity` method:**
       - After determining a click (`click_outcome`):
         - If `click_outcome` is true for a winning agent:
           - Simulate conversion: `conversion_occurred = self.rng.random() < self.fixed_cvr`
           - If `conversion_occurred` is true:
             - `current_sales_revenue = self.fixed_sales_revenue_per_conversion`
           - Else:
             - `current_sales_revenue = 0.0`
         - Else (no click):
           - `conversion_occurred = False`
           - `current_sales_revenue = 0.0`
       - For the **winning agent's** last log entry (`winning_agent.logs[-1]`), call `set_conversion_details(conversion_occurred, current_sales_revenue)`.
       - For **non-winning participating agents'** last log entries, call `set_conversion_details(False, 0.0)` to ensure fields are explicitly set.
   - **Deliverable:** Modified `Auction` class.

### Step 6: Modify `src/Agent.py`
   - **Action:** Enable agents to calculate and store metrics related to CVR and ACoS.
   - **Details:**
     - Add new methods to the `Agent` class:
       - `get_total_clicks(self)`: Returns `sum(1 for opp in self.logs if opp.won and opp.outcome)`.
       - `get_total_conversions(self)`: Returns `sum(1 for opp in self.logs if opp.won and opp.conversion)`.
       - `get_total_sales_revenue(self)`: Returns `sum(opp.sales_revenue for opp in self.logs if opp.won and opp.conversion)`.
       - `get_total_spend(self)`: Returns `sum(opp.price for opp in self.logs if opp.won)`.
       - `get_CVR(self)`: Calculates `total_conversions / total_clicks`. Handle division by zero (return 0 or NaN).
       - `get_ACoS(self)`: Calculates `total_spend / total_sales_revenue`. Handle division by zero (return 0, NaN, or infinity as appropriate).
   - **Deliverable:** `Agent` class with new metric calculation methods.

### Step 7: Modify `src/main.py`
   - **Action:** Collect, log, and prepare the new metrics for reporting.
   - **Details:**
     - **`parse_config`:**
       - Ensure it reads `fixed_conversion_rate` and `fixed_sales_revenue_per_conversion` from the JSON config.
     - **`instantiate_auction`:**
       - Pass the parsed `fixed_conversion_rate` and `fixed_sales_revenue_per_conversion` to the `Auction` constructor.
     - **`simulation_run()`:**
       - After agent updates, call the new `get_...` methods from `Agent.py` (CVR, ACoS, total sales, total conversions, total clicks, total spend).
       - Store these in new dictionaries (e.g., `agent2cvr`, `agent2acos`, `agent2sales_revenue`, etc.).
     - Update `run2agent2...` dictionaries to include these new metrics.
   - **Deliverable:** `main.py` script updated to track and pass new configuration and metrics.

## Phase 3: Configuration and Testing

### Step 8: Update Configuration Files
   - **Action:** Add the new global parameters for fixed CVR and fixed sales revenue to JSON configuration files.
   - **Details:**
     - In `config/` files (e.g., `config/SP_Oracle.json`):
       ```json
       {
         // ... existing parameters ...
         "fixed_conversion_rate": 0.05, // Example: 5% CVR
         "fixed_sales_revenue_per_conversion": 50.0 // Example: $50 revenue
       }
       ```
   - **Deliverable:** Updated example configuration files.

### Step 9: Run Initial Tests & Debug
   - **Action:** Perform basic simulation runs to ensure no crashes and that new data fields are populated.
   - **Details:**
     - Use a simple config file.
     - Use print statements or a debugger to inspect `agent.logs` (specifically `conversion` and `sales_revenue` fields) and the values of newly calculated metrics in `main.py`.
   - **Deliverable:** Basic implementation confirmed working.

### Step 10: Design Test Scenarios
   - **Action:** Create scenarios to validate CVR and ACoS calculations.
   - **Details:**
     - **Scenario 1 (Zero CVR):** Set `"fixed_conversion_rate": 0.0`. Expected: CVR = 0, Total Conversions = 0, Total Sales Revenue = 0, ACoS = undefined/0.
     - **Scenario 2 (Non-Zero Fixed CVR & Sales):** Set `"fixed_conversion_rate": 0.1` and `"fixed_sales_revenue_per_conversion": 100.0`. Manually calculate expected metrics based on a small, predictable number of impressions and clicks.
   - **Deliverable:** Test scenarios with expected outcomes.

### Step 11: Execute Test Scenarios & Analyze Results
   - **Action:** Run simulations for the designed test scenarios.
   - **Details:**
     - Compare reported metrics against expected outcomes. Debug discrepancies.
   - **Deliverable:** Verified CVR and ACoS calculations.

## Phase 4: Reporting

### Step 12: Integrate New Metrics into Reporting in `main.py`
   - **Action:** Add new plots and CSV outputs for CVR, ACoS, and supporting total counts (clicks, conversions, sales revenue, spend).
   - **Details:**
     - **CSV Output:**
       - Adapt `measure_per_agent2df` to create DataFrames for: CVR, ACoS, Total Clicks, Total Conversions, Total Sales Revenue, Total Spend.
       - Save these to new CSV files (e.g., `cvr_...csv`, `acos_...csv`, `conversion_funnel_...csv`).
     - **Plotting:**
       - Adapt `plot_measure_per_agent` to generate plots for CVR and ACoS over time per agent.
       - Optionally, plot total clicks, conversions, sales revenue, and spend if insightful.
       - Save new plot files with descriptive names.
   - **Important:** Add these as *new* reports without altering existing ones.
   - **Deliverable:** `main.py` script generating reports for the new metrics.

## Phase 5: Documentation and Finalization

### Step 13: Document Changes
   - **Action:** Update documentation (e.g., a `README_extended.md` or code comments).
   - **Details:**
     - Explain the new metrics (CVR, ACoS) and how they are calculated (fixed CVR, fixed sales revenue).
     - Describe new configuration parameters (`fixed_conversion_rate`, `fixed_sales_revenue_per_conversion`).
     - Explain new reports.
   - **Deliverable:** Updated documentation.

### Step 14: Final Review and Code Cleanup
   - **Action:** Review all changes.
   - **Details:**
     - Remove debugging code. Ensure comments are clear. Verify requirements are met.
   - **Deliverable:** A clean, documented, and tested extension of AuctionGym.
