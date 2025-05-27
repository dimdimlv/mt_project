#!/usr/bin/env python3
"""
Baseline Comparison Analysis for PPO Reward Functions in AuctionGym

This script compares PPO reward function performance against baseline strategies:
1. Truthful Competitors (already included in experiments)
2. Average performance benchmarks
3. Statistical significance tests

For each competition level (C5, C10, C15), it:
- Extracts baseline performance from truthful competitors
- Compares PPO agents against these baselines
- Performs statistical significance testing
- Generates comprehensive comparison reports

Author: Baseline Analysis Framework for AuctionGym PPO Experiments
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
from scipy import stats
from scipy.stats import ttest_ind, mannwhitneyu
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class BaselineComparisonAnalyzer:
    """Analyzer for comparing PPO reward functions against baseline strategies"""
    
    def __init__(self, results_dir="/Users/dimdim/PycharmProjects/mt_project/results"):
        self.results_dir = Path(results_dir)
        self.configurations = {
            'C5': {
                'net_utility': 'PPO_NU_R3_I25_RPI100K_C5',
                'gross_utility': 'PPO_GU_R3_I25_RPI100K_C5',
                'penalty_wasted_spend': 'PPO_PWS_R3_I25_RPI100K_C5'
            },
            'C10': {
                'net_utility': 'PPO_NU_R3_I25_RPI100K_C10',
                'gross_utility': 'PPO_GU_R3_I25_RPI100K_C10',
                'penalty_wasted_spend': 'PPO_PWS_R3_I25_RPI100K_C10'
            },
            'C15': {
                'net_utility': 'PPO_NU_R3_I25_RPI100K_C15',
                'gross_utility': 'PPO_GU_R3_I25_RPI100K_C15',
                'penalty_wasted_spend': 'PPO_PWS_R3_I25_RPI100K_C15'
            }
        }
        
        # Store data for all configurations and baseline comparisons
        self.ppo_data = {}
        self.baseline_data = {}
        self.comparison_results = {}
        
    def load_all_data(self):
        """Load data from all PPO experiments and extract baseline information"""
        print("Loading PPO and baseline data from all configurations...")
        
        for config_name, reward_functions in self.configurations.items():
            print(f"  Loading {config_name} configuration...")
            self.ppo_data[config_name] = {}
            self.baseline_data[config_name] = {}
            
            for reward_name, folder_name in reward_functions.items():
                print(f"    Loading {reward_name} data...")
                folder_path = self.results_dir / folder_name
                
                # Load PPO data and baseline data
                ppo_data, baseline_data = self._load_experiment_data(folder_path)
                
                self.ppo_data[config_name][reward_name] = ppo_data
                self.baseline_data[config_name][reward_name] = baseline_data
    
    def _load_experiment_data(self, folder_path):
        """Load data from a single experiment folder and separate PPO vs baseline data"""
        ppo_data = {}
        baseline_data = {}
        
        # List of metrics to analyze
        metrics = [
            'net_utility', 'gross_utility', 'total_spend', 'total_clicks', 
            'cvr', 'total_sales_revenue', 'underbid_regret'
        ]
        
        for metric in metrics:
            # Look for the CSV file for this metric
            csv_pattern = f"{metric}_100000_rounds_25_iters_3_runs_5_emb_of_*.csv"
            csv_files = list(folder_path.glob(csv_pattern))
            
            if csv_files:
                csv_file = csv_files[0]  # Take the first match
                try:
                    df = pd.read_csv(csv_file)
                    
                    # Separate PPO data from baseline data
                    ppo_rows = df[df['agent_name'].str.contains('PPO', na=False)]
                    baseline_rows = df[df['agent_name'].str.contains('Truthful', na=False)]
                    
                    ppo_data[metric] = ppo_rows
                    baseline_data[metric] = baseline_rows
                    
                except Exception as e:
                    print(f"    Warning: Could not load {csv_file}: {e}")
                    ppo_data[metric] = pd.DataFrame()
                    baseline_data[metric] = pd.DataFrame()
            else:
                print(f"    Warning: No file found for metric {metric}")
                ppo_data[metric] = pd.DataFrame()
                baseline_data[metric] = pd.DataFrame()
                
        return ppo_data, baseline_data


def main():
    """Main analysis execution"""
    print("Starting PPO vs Baseline Comparison Analysis")
    print("=" * 70)
    
    try:
        # Initialize analyzer
        print("Initializing baseline analyzer...")
        analyzer = BaselineComparisonAnalyzer()
        
        # Load data
        print("Loading PPO and baseline data...")
        analyzer.load_all_data()
        
        print("Basic data loading completed successfully!")
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    main()
