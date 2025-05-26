# Project Plan: Implementing Configurable Reward Functions in AuctionGym

This plan outlines the steps to modify the AuctionGym environment to support three distinct reward functions for the `PolicyLearningBidder`:
1.  **Net Utility per Impression** (current default)
2.  **Gross Utility per Impression**
3.  **Penalty for Wasted Spend** (if no click occurs on a won impression)

---

## Phase 1: Setup & Initial Code Review

**Step 1: Ensure AuctionGym is Set Up**
   - **Action:** If not already done, clone the AuctionGym repository from GitHub and set up the Python virtual environment with all necessary dependencies as per the original `requirements.txt`.
   - **Reference:** Initial setup steps from previous project plans.
   - **Deliverable:** A local, functional copy of the AuctionGym project.

**Step 2: Review Key Files**
   - **Action:** Thoroughly review the structure and logic of the following key files to understand the current reward calculation and agent update mechanisms.
        - `src/Bidder.py`: Focus on the `PolicyLearningBidder` class, specifically its `__init__` method (for adding configuration) and `update` method (where rewards are calculated and used for policy updates).
        - `src/Agent.py`: Understand how the `Agent` class collects data (like `values`, `outcomes`, `prices`, `won_mask`) and passes it to the `bidder.update()` method.
        - `config/` directory: Examine existing JSON configuration files (e.g., `Test01_5_5_10K.json` or any that use a learning bidder) to see how bidder types and their keyword arguments (`kwargs`) are specified. This will inform how to add the new reward function configuration.
   - **Deliverable:** Clear understanding of the existing code related to bidders, rewards, and configuration.

---

## Phase 2: Implementing Configurable Rewards in `PolicyLearningBidder`

**Step 3: Modify `PolicyLearningBidder` in `src/Bidder.py`**
   - **Action:** Enhance the `PolicyLearningBidder` to accept a configuration parameter for the reward function type and implement the logic to calculate rewards based on this parameter.
   - **Details:**
        1.  **Update `__init__` method:**
            - Add a new parameter `reward_function_type: str` to the constructor with a default value (e.g., `"net_utility"`).
            - Store this parameter as an instance variable: `self.reward_function_type = reward_function_type`.
            ```python
            # Example snippet for __init__ in PolicyLearningBidder
            class PolicyLearningBidder(Bidder):
                def __init__(self, rng, learning_rate=0.001, C=1.0, reward_function_type="net_utility"): # New parameter
                    super().__init__(rng)
                    # ... existing initializations ...
                    self.reward_function_type = reward_function_type
                    # ...
            ```

        2.  **Update `update` method:**
            - Locate the section where the `rewards` tensor is currently calculated: `rewards = torch.Tensor((values * outcomes - prices) * won_mask)`.
            - Replace this with conditional logic based on `self.reward_function_type` to compute `raw_rewards`.
            ```python
            # Example snippet for reward calculation in update method
            # Inputs: values (VPC), outcomes (clicks), prices, won_mask

            raw_rewards_np = np.zeros(len(values)) # Use NumPy for easier conditional assignment initially

            if self.reward_function_type == "net_utility":
                # Scenario 1: Net Utility = (VPC * click) - price_paid (if won)
                raw_rewards_np = (values * outcomes - prices) * won_mask
            elif self.reward_function_type == "gross_utility":
                # Scenario 2: Gross Utility = VPC * click (if won)
                raw_rewards_np = (values * outcomes) * won_mask
            elif self.reward_function_type == "penalty_wasted_spend":
                # Scenario 3: (VPC * click) - price_paid if click; -price_paid if no click (but won)
                # Ensure 'outcomes' is boolean or 0/1 for correct indexing/logic
                is_click = outcomes.astype(bool) 
                
                # Calculate rewards for impressions with a click
                clicked_rewards = (values * outcomes - prices)
                
                # Calculate penalties for impressions without a click (but won)
                no_click_penalties = -prices
                
                # Combine based on whether a click occurred, for won impressions only
                # Using np.where for conditional assignment
                rewards_for_won_impressions = np.where(is_click, clicked_rewards, no_click_penalties)
                raw_rewards_np = rewards_for_won_impressions * won_mask # Apply won_mask
            else:
                raise ValueError(f"Unknown reward_function_type: {self.reward_function_type}")

            rewards = torch.Tensor(raw_rewards_np) # Convert to PyTorch Tensor

            # Normalize rewards (existing logic)
            if len(rewards[won_mask.astype(bool)]) > 1:
                rewards_norm = torch.clone(rewards)
                # Ensure won_mask is boolean for indexing PyTorch tensors
                won_mask_bool = won_mask.astype(bool)
                rewards_norm[won_mask_bool] = (rewards[won_mask_bool] - rewards[won_mask_bool].mean()) / (rewards[won_mask_bool].std() + 1e-5)
            else:
                rewards_norm = rewards
            
            # ... rest of the update method using rewards_norm ...
            ```
            *Note: Ensure `values`, `outcomes`, `prices`, and `won_mask` are NumPy arrays when performing NumPy operations before converting to `torch.Tensor`.*
   - **Deliverable:** An updated `PolicyLearningBidder` class in `src/Bidder.py` capable of using one of the three specified reward functions based on its configuration.

---

## Phase 3: Configuration and Simulation Setup

**Step 4: Update Configuration Files**
   - **Action:** Create or modify JSON configuration files in the `config/` directory to test each reward function scenario.
   - **Details:**
        - For each agent that will use the `PolicyLearningBidder`, add the `reward_function_type` key to the `bidder`'s `kwargs` dictionary.
        - Create three separate configuration files (or modify existing ones that are suitable for `PolicyLearningBidder`), each specifying one of the reward types:
            - **Config 1 (Net Utility):** e.g., `FP_PolicyLearner_NetUtility.json`
              ```json
              // ...
              "bidder": {
                "type": "PolicyLearningBidder",
                "kwargs": {
                  "reward_function_type": "net_utility"
                  // ... other PolicyLearningBidder kwargs like learning_rate, C ...
                }
              }
              // ...
              ```
            - **Config 2 (Gross Utility):** e.g., `FP_PolicyLearner_GrossUtility.json`
              ```json
              // ...
              "bidder": {
                "type": "PolicyLearningBidder",
                "kwargs": {
                  "reward_function_type": "gross_utility"
                  // ...
                }
              }
              // ...
              ```
            - **Config 3 (Penalty Wasted Spend):** e.g., `FP_PolicyLearner_PenaltyWastedSpend.json`
              ```json
              // ...
              "bidder": {
                "type": "PolicyLearningBidder",
                "kwargs": {
                  "reward_function_type": "penalty_wasted_spend"
                  // ...
                }
              }
              // ...
              ```
        - Ensure the `output_dir` in each config file points to a unique directory to store results for that scenario.
   - **Deliverable:** Three distinct JSON configuration files, each set up for one reward function scenario.

**Step 5: Verify Parameter Passing in `src/main.py`**
   - **Action:** Confirm that the `reward_function_type` (and other `kwargs`) from the JSON config files are correctly passed to the `PolicyLearningBidder` constructor when agents are instantiated.
   - **Details:**
        The existing `instantiate_agents` function in `main.py` uses:
        `eval(f"{agent_config['bidder']['type']}(rng=rng{parse_kwargs(agent_config['bidder']['kwargs'])})")`
        This dynamic instantiation should automatically handle the new `reward_function_type` from the `kwargs` in the config. A quick check or a print statement during instantiation can verify this.
   - **Deliverable:** Confirmation that the new configuration parameter is correctly passed to the bidder.

---

## Phase 4: Testing and Analysis

**Step 6: Design Test Scenarios and Verification Steps**
   - **Action:** Outline how to test each reward function to ensure correctness and observe its impact.
   - **Details:**
        - **Correctness Verification (Debugging):**
            - For each reward scenario, run a short simulation (e.g., few iterations, few rounds per iteration).
            - Add temporary `print()` statements within the `PolicyLearningBidder.update` method to output the input `values`, `outcomes`, `prices`, `won_mask`, and the calculated `raw_rewards_np` for a few sample impressions.
            - Manually calculate the expected reward for these samples based on the active reward function's formula and verify against the printed output.
        - **Behavioral Observation (Qualitative):**
            - **Net Utility:** Expect the agent to learn a balance between bidding to win valuable clicks and managing costs.
            - **Gross Utility:** Expect the agent to potentially bid more aggressively to win impressions with high VPC, possibly at a higher cost (leading to lower net utility but potentially higher gross utility).
            - **Penalty for Wasted Spend:** Expect the agent to be more conservative, potentially bidding lower or less frequently on impressions where click probability is uncertain or low, to avoid the penalty for paying for unclicked ads.
   - **Deliverable:** A checklist for verification and a set of expected qualitative behaviors for each reward function.

**Step 7: Execute Simulations and Analyze Results**
   - **Action:** Run full simulations for each of the three configurations and analyze the generated reports.
   - **Details:**
        - Execute `src/main.py` with each of the three configuration files:
          ```bash
          python src/main.py config/FP_PolicyLearner_NetUtility.json
          python src/main.py config/FP_PolicyLearner_GrossUtility.json
          python src/main.py config/FP_PolicyLearner_PenaltyWastedSpend.json
          ```
        - Examine the output CSV files and plots generated in the respective `results/` subdirectories.
        - **Comparative Analysis:** Compare key agent performance metrics across the three scenarios. Focus on:
            - `Net Utility` (as reported by AuctionGym)
            - `Gross Utility` (as reported by AuctionGym)
            - `Auction Revenue` (for the auctioneer)
            - `Shading Factors` (if the bidder learns them)
            - `CTR RMSE` and `CTR Bias` (if an allocator is also learning)
            - Number of bids, win rate (these might need to be inferred or added to logging if not standard).
        - Note how the different reward functions influence these metrics and the overall bidding strategy learned by the agent.
   - **Deliverable:** Simulation results (CSVs, plots) for each scenario and a written summary comparing the observed agent behaviors and performance.

---

## Phase 5: Documentation (Optional but Recommended)

**Step 8: Document the Implementation and Findings**
   - **Action:** Create or update project documentation to reflect the new configurable reward function feature.
   - **Details:**
        - Explain the `reward_function_type` parameter added to `PolicyLearningBidder`.
        - Clearly define the calculation logic for each of the three implemented reward functions.
        - Summarize the key findings from the comparative analysis in Step 7, highlighting how each reward function affected the agent's learning and performance.
   - **Deliverable:** Internal documentation or notes detailing the configurable reward function implementation and experimental observations.
