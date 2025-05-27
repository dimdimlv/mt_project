#!/usr/bin/env python3
"""
Comprehensive Analysis of PPO Reward Functions in AuctionGym (C15 Configuration)

This script analyzes the behavioral differences between three PPO reward function configurations:
1. PPO_NU_R3_I25_RPI100K_C15: Net Utility (VPC * click) - price_paid
2. PPO_GU_R3_I25_RPI100K_C15: Gross Utility VPC * click  
3. PPO_PWS_R3_I25_RPI100K_C15: Penalty for Wasted Spend

Author: Analysis Framework for AuctionGym PPO Experiments
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class RewardFunctionAnalyzer:
    """Comprehensive analyzer for comparing reward function behaviors"""
    
    def __init__(self, results_dir="/Users/dimdim/PycharmProjects/mt_project/results"):
        self.results_dir = Path(results_dir)
        self.reward_functions = {
            'net_utility': 'PPO_NU_R3_I25_RPI100K_C15',
            'gross_utility': 'PPO_GU_R3_I25_RPI100K_C15', 
            'penalty_wasted_spend': 'PPO_PWS_R3_I25_RPI100K_C15'
        }
        self.data = {}
        self.metrics = {}
        
    def load_data(self):
        """Load CSV data for all reward function types"""
        print("Loading data from all reward function experiments...")
        
        for rf_name, folder_name in self.reward_functions.items():
            folder_path = self.results_dir / folder_name
            if folder_path.exists():
                print(f"  Loading data for {rf_name}...")
                self.data[rf_name] = {}
                
                # Load key metrics CSV files
                csv_files = {
                    'results': 'results_100000_rounds_25_iters_3_runs_5_emb_of_5.csv',
                    'net_utility': 'net_utility_100000_rounds_25_iters_3_runs_5_emb_of_5.csv',
                    'gross_utility': 'gross_utility_100000_rounds_25_iters_3_runs_5_emb_of_5.csv',
                    'total_spend': 'total_spend_100000_rounds_25_iters_3_runs_5_emb_of_5.csv',
                    'total_clicks': 'total_clicks_100000_rounds_25_iters_3_runs_5_emb_of_5.csv',
                    'acos': 'acos_100000_rounds_25_iters_3_runs_5_emb_of_5.csv',
                    'overbid_regret': 'overbid_regret_100000_rounds_25_iters_3_runs_5_emb_of_5.csv',
                    'underbid_regret': 'underbid_regret_100000_rounds_25_iters_3_runs_5_emb_of_5.csv'
                }
                
                for metric_name, csv_file in csv_files.items():
                    csv_path = folder_path / csv_file
                    if csv_path.exists():
                        try:
                            self.data[rf_name][metric_name] = pd.read_csv(csv_path)
                        except Exception as e:
                            print(f"    Warning: Could not load {csv_file}: {e}")
            else:
                print(f"  Warning: Folder {folder_name} not found")
    
    def calculate_summary_metrics(self):
        """Calculate summary statistics for comparison"""
        print("\nCalculating summary metrics...")
        
        for rf_name in self.data.keys():
            print(f"  Processing {rf_name}...")
            self.metrics[rf_name] = {}
            
            # Extract metrics from individual CSV files
            metric_files = {
                'net_utility': 'Net Utility',
                'gross_utility': 'Gross Utility', 
                'total_spend': 'Total Spend',
                'total_clicks': 'Total Clicks',
                'acos': 'ACoS'
            }
            
            for csv_key, metric_name in metric_files.items():
                if csv_key in self.data[rf_name]:
                    df = self.data[rf_name][csv_key]
                    
                    # Filter to PPO Bidder only and get final iteration (24)
                    ppo_data = df[df['Agent'].str.contains('PPO Bidder', na=False)]
                    final_iter_data = ppo_data[ppo_data['Iteration'] == 24]
                    
                    if len(final_iter_data) > 0:
                        # Get the metric column name (should be the last column)
                        metric_col = df.columns[-1]
                        avg_value = final_iter_data[metric_col].mean()
                        self.metrics[rf_name][f'final_{csv_key}'] = avg_value
                        
                        # Also calculate learning curve slope for this metric
                        self.metrics[rf_name][f'{csv_key}_learning_slope'] = self._calculate_slope_from_agent_data(ppo_data, metric_col)
            
            # Calculate overall learning metrics based on net utility
            if 'net_utility' in self.data[rf_name]:
                net_util_df = self.data[rf_name]['net_utility']
                ppo_net_data = net_util_df[net_util_df['Agent'].str.contains('PPO Bidder', na=False)]
                
                self.metrics[rf_name]['learning_curve_slope'] = self._calculate_slope_from_agent_data(ppo_net_data, 'Net Utility')
                self.metrics[rf_name]['convergence_iteration'] = self._find_convergence_from_agent_data(ppo_net_data, 'Net Utility')
                
            # Regret analysis - handle the specific CSV format
            if 'overbid_regret' in self.data[rf_name] and 'underbid_regret' in self.data[rf_name]:
                overbid_df = self.data[rf_name]['overbid_regret']
                underbid_df = self.data[rf_name]['underbid_regret']
                
                if len(overbid_df) > 0 and len(underbid_df) > 0:
                    # Filter to PPO Bidder only and calculate mean regret
                    ppo_overbid = overbid_df[overbid_df['Agent'].str.contains('PPO Bidder', na=False)]
                    ppo_underbid = underbid_df[underbid_df['Agent'].str.contains('PPO Bidder', na=False)]
                    
                    if len(ppo_overbid) > 0:
                        self.metrics[rf_name]['avg_overbid_regret'] = ppo_overbid['Overbid Regret'].mean()
                    else:
                        self.metrics[rf_name]['avg_overbid_regret'] = 0
                        
                    if len(ppo_underbid) > 0:
                        self.metrics[rf_name]['avg_underbid_regret'] = ppo_underbid['Underbid Regret'].mean()
                    else:
                        self.metrics[rf_name]['avg_underbid_regret'] = 0
                    
                    self.metrics[rf_name]['total_regret'] = (
                        self.metrics[rf_name]['avg_overbid_regret'] + 
                        self.metrics[rf_name]['avg_underbid_regret']
                    )
    
    def _calculate_slope_from_agent_data(self, agent_df, metric_col):
        """Calculate learning curve slope from agent-specific data"""
        if len(agent_df) < 2:
            return 0
        
        # Group by iteration and calculate mean across runs
        iteration_means = agent_df.groupby('Iteration')[metric_col].mean()
        
        if len(iteration_means) < 2:
            return 0
        
        iterations = np.array(iteration_means.index)
        values = iteration_means.values
        
        # Remove any NaN or infinite values
        valid_mask = np.isfinite(values)
        if np.sum(valid_mask) < 2:
            return 0
            
        iterations = iterations[valid_mask]
        values = values[valid_mask]
        
        # Calculate slope using linear regression
        slope = np.polyfit(iterations, values, 1)[0]
        return slope
    
    def _find_convergence_from_agent_data(self, agent_df, metric_col, threshold=50.0):
        """Find convergence point from agent-specific data"""
        if len(agent_df) < 3:
            return 25
        
        # Group by iteration and calculate mean across runs
        iteration_means = agent_df.groupby('Iteration')[metric_col].mean()
        
        if len(iteration_means) < 3:
            return 25
        
        values = iteration_means.values
        
        # Calculate moving average of rate of change
        rates_of_change = np.abs(np.diff(values))
        
        # Find first point where rate of change consistently stays below threshold
        for i in range(1, len(rates_of_change)):
            if np.mean(rates_of_change[max(0, i-2):i+1]) < threshold:
                return i
        
        return len(iteration_means)
    
    def _calculate_learning_slope_from_results(self, results_df, measure_name='Net Utility'):
        """Calculate the learning curve slope for a given measure from results format"""
        # Filter data for the specific measure
        measure_data = results_df[results_df['Measure Name'] == measure_name]
        
        if len(measure_data) < 2:
            return 0
        
        # Group by iteration and calculate mean across runs
        iteration_means = measure_data.groupby('Iteration')['Measure'].mean()
        
        if len(iteration_means) < 2:
            return 0
        
        iterations = np.array(iteration_means.index)
        values = iteration_means.values
        
        # Remove any NaN or infinite values
        valid_mask = np.isfinite(values)
        if np.sum(valid_mask) < 2:
            return 0
            
        iterations = iterations[valid_mask]
        values = values[valid_mask]
        
        # Calculate slope using linear regression
        slope = np.polyfit(iterations, values, 1)[0]
        return slope
    
    def _find_convergence_point_from_results(self, results_df, measure_name='Net Utility', threshold=0.01):
        """Find when the learning curve converges from results format"""
        # Filter data for the specific measure
        measure_data = results_df[results_df['Measure Name'] == measure_name]
        
        if len(measure_data) < 3:
            return 25
        
        # Group by iteration and calculate mean across runs
        iteration_means = measure_data.groupby('Iteration')['Measure'].mean()
        
        if len(iteration_means) < 3:
            return 25
        
        values = iteration_means.values
        
        # Calculate moving average of rate of change
        rates_of_change = np.abs(np.diff(values))
        
        # Find first point where rate of change consistently stays below threshold
        for i in range(1, len(rates_of_change)):
            if np.mean(rates_of_change[max(0, i-2):i+1]) < threshold:
                return i
        
        return len(iteration_means)
    
    def _calculate_learning_slope(self, results_df, metric='net_utility'):
        """Calculate the learning curve slope for a given metric"""
        if metric not in results_df.columns or len(results_df) < 2:
            return 0
        
        iterations = np.arange(len(results_df))
        values = results_df[metric].values
        
        # Remove any NaN or infinite values
        valid_mask = np.isfinite(values)
        if np.sum(valid_mask) < 2:
            return 0
            
        iterations = iterations[valid_mask]
        values = values[valid_mask]
        
        # Calculate slope using linear regression
        slope = np.polyfit(iterations, values, 1)[0]
        return slope
    
    def _find_convergence_point(self, results_df, metric='net_utility', threshold=0.01):
        """Find when the learning curve converges (rate of change falls below threshold)"""
        if metric not in results_df.columns or len(results_df) < 3:
            return len(results_df)
        
        values = results_df[metric].values
        
        # Calculate moving average of rate of change
        rates_of_change = np.abs(np.diff(values))
        
        # Find first point where rate of change consistently stays below threshold
        for i in range(1, len(rates_of_change)):
            if np.mean(rates_of_change[max(0, i-2):i+1]) < threshold:
                return i
        
        return len(results_df)
    
    def create_comparison_plots(self):
        """Create comprehensive comparison plots"""
        print("\nGenerating comparison plots...")
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(20, 15))
        
        # 1. Learning Curves Comparison
        ax1 = plt.subplot(3, 3, 1)
        self._plot_learning_curves(ax1, 'net_utility', 'Net Utility Learning Curves')
        
        ax2 = plt.subplot(3, 3, 2)
        self._plot_learning_curves(ax2, 'gross_utility', 'Gross Utility Learning Curves')
        
        ax3 = plt.subplot(3, 3, 3)
        self._plot_learning_curves(ax3, 'total_spend', 'Total Spend Learning Curves')
        
        # 2. Final Performance Comparison
        ax4 = plt.subplot(3, 3, 4)
        self._plot_final_performance_comparison(ax4)
        
        # 3. Regret Analysis
        ax5 = plt.subplot(3, 3, 5)
        self._plot_regret_comparison(ax5)
        
        # 4. Learning Efficiency
        ax6 = plt.subplot(3, 3, 6)
        self._plot_learning_efficiency(ax6)
        
        # 5. Risk-Return Analysis
        ax7 = plt.subplot(3, 3, 7)
        self._plot_risk_return_analysis(ax7)
        
        # 6. Click Efficiency
        ax8 = plt.subplot(3, 3, 8)
        self._plot_click_efficiency(ax8)
        
        # 7. Cost Management
        ax9 = plt.subplot(3, 3, 9)
        self._plot_cost_management(ax9)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'ppo_reward_functions_c15_comprehensive_analysis.pdf', 
                   dpi=300, bbox_inches='tight')
        plt.savefig(self.results_dir / 'ppo_reward_functions_c15_comprehensive_analysis.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def _plot_learning_curves(self, ax, metric_key, title):
        """Plot learning curves for all reward functions"""
        for rf_name in self.data.keys():
            if metric_key in self.data[rf_name]:
                df = self.data[rf_name][metric_key]
                
                # Filter to PPO Bidder data
                ppo_data = df[df['Agent'].str.contains('PPO Bidder', na=False)]
                
                if len(ppo_data) > 0:
                    # Group by iteration and calculate mean across runs
                    metric_col = df.columns[-1]  # Last column should be the metric
                    iteration_means = ppo_data.groupby('Iteration')[metric_col].mean()
                    
                    ax.plot(iteration_means.index, iteration_means.values, 
                           label=rf_name.replace('_', ' ').title(), 
                           linewidth=2, marker='o', markersize=4)
        
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Iteration')
        ax.set_ylabel(title.split(' ')[0] + ' ' + title.split(' ')[1])
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_final_performance_comparison(self, ax):
        """Plot final performance metrics comparison"""
        metrics_to_compare = ['final_net_utility', 'final_gross_utility', 'final_total_spend']
        
        x = np.arange(len(self.reward_functions))
        width = 0.25
        
        for i, metric in enumerate(metrics_to_compare):
            values = [self.metrics[rf_name].get(metric, 0) for rf_name in self.reward_functions.keys()]
            ax.bar(x + i*width, values, width, 
                  label=metric.replace('final_', '').replace('_', ' ').title())
        
        ax.set_title('Final Performance Comparison', fontsize=12, fontweight='bold')
        ax.set_xlabel('Reward Function Type')
        ax.set_ylabel('Final Value')
        ax.set_xticks(x + width)
        ax.set_xticklabels([rf.replace('_', ' ').title() for rf in self.reward_functions.keys()], 
                          rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_regret_comparison(self, ax):
        """Plot regret comparison"""
        rf_names = list(self.reward_functions.keys())
        overbid_regrets = [self.metrics[rf].get('avg_overbid_regret', 0) for rf in rf_names]
        underbid_regrets = [self.metrics[rf].get('avg_underbid_regret', 0) for rf in rf_names]
        
        x = np.arange(len(rf_names))
        width = 0.35
        
        ax.bar(x - width/2, overbid_regrets, width, label='Overbid Regret', alpha=0.8)
        ax.bar(x + width/2, underbid_regrets, width, label='Underbid Regret', alpha=0.8)
        
        ax.set_title('Regret Analysis Comparison', fontsize=12, fontweight='bold')
        ax.set_xlabel('Reward Function Type')
        ax.set_ylabel('Average Regret')
        ax.set_xticks(x)
        ax.set_xticklabels([rf.replace('_', ' ').title() for rf in rf_names], rotation=45)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_learning_efficiency(self, ax):
        """Plot learning efficiency metrics"""
        rf_names = list(self.reward_functions.keys())
        convergence_iterations = [self.metrics[rf].get('convergence_iteration', 25) for rf in rf_names]
        learning_slopes = [self.metrics[rf].get('learning_curve_slope', 0) for rf in rf_names]
        
        # Normalize learning slopes for comparison
        max_slope = max(abs(s) for s in learning_slopes) if learning_slopes else 1
        normalized_slopes = [s/max_slope if max_slope > 0 else 0 for s in learning_slopes]
        
        x = np.arange(len(rf_names))
        width = 0.35
        
        ax.bar(x - width/2, convergence_iterations, width, label='Convergence Iteration', alpha=0.8)
        ax2 = ax.twinx()
        ax2.bar(x + width/2, normalized_slopes, width, label='Learning Rate (normalized)', 
               alpha=0.8, color='orange')
        
        ax.set_title('Learning Efficiency Comparison', fontsize=12, fontweight='bold')
        ax.set_xlabel('Reward Function Type')
        ax.set_ylabel('Convergence Iteration')
        ax2.set_ylabel('Normalized Learning Rate')
        ax.set_xticks(x)
        ax.set_xticklabels([rf.replace('_', ' ').title() for rf in rf_names], rotation=45)
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
    
    def _plot_risk_return_analysis(self, ax):
        """Plot risk-return analysis"""
        rf_names = list(self.reward_functions.keys())
        returns = [self.metrics[rf].get('final_net_utility', 0) for rf in self.reward_functions.keys()]
        risks = [self.metrics[rf].get('total_regret', 0) for rf in rf_names]
        
        colors = ['blue', 'green', 'red']
        for i, rf_name in enumerate(rf_names):
            ax.scatter(risks[i], returns[i], s=100, c=colors[i], 
                      label=rf_name.replace('_', ' ').title(), alpha=0.7)
            ax.annotate(rf_name.replace('_', ' ').title(), 
                       (risks[i], returns[i]), xytext=(5, 5), 
                       textcoords='offset points', fontsize=10)
        
        ax.set_title('Risk-Return Analysis', fontsize=12, fontweight='bold')
        ax.set_xlabel('Total Regret (Risk)')
        ax.set_ylabel('Final Net Utility (Return)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_click_efficiency(self, ax):
        """Plot click efficiency analysis"""
        rf_names = list(self.reward_functions.keys())
        clicks = [self.metrics[rf].get('final_total_clicks', 1) for rf in rf_names]
        spend = [self.metrics[rf].get('final_total_spend', 1) for rf in rf_names]
        
        # Calculate cost per click
        cpc = [s/c if c > 0 else 0 for s, c in zip(spend, clicks)]
        
        x = np.arange(len(rf_names))
        width = 0.35
        
        ax.bar(x - width/2, clicks, width, label='Total Clicks', alpha=0.8)
        ax2 = ax.twinx()
        ax2.bar(x + width/2, cpc, width, label='Cost Per Click', alpha=0.8, color='red')
        
        ax.set_title('Click Efficiency Analysis', fontsize=12, fontweight='bold')
        ax.set_xlabel('Reward Function Type')
        ax.set_ylabel('Total Clicks')
        ax2.set_ylabel('Cost Per Click')
        ax.set_xticks(x)
        ax.set_xticklabels([rf.replace('_', ' ').title() for rf in rf_names], rotation=45)
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
    
    def _plot_cost_management(self, ax):
        """Plot cost management analysis"""
        rf_names = list(self.reward_functions.keys())
        spend = [self.metrics[rf].get('final_total_spend', 0) for rf in rf_names]
        acos = [self.metrics[rf].get('final_acos', float('inf')) for rf in rf_names]
        
        # Cap ACOS at reasonable values for visualization
        acos = [min(a, 10) if a != float('inf') else 10 for a in acos]
        
        x = np.arange(len(rf_names))
        width = 0.35
        
        ax.bar(x - width/2, spend, width, label='Total Spend', alpha=0.8)
        ax2 = ax.twinx()
        ax2.bar(x + width/2, acos, width, label='ACOS', alpha=0.8, color='purple')
        
        ax.set_title('Cost Management Analysis', fontsize=12, fontweight='bold')
        ax.set_xlabel('Reward Function Type')
        ax.set_ylabel('Total Spend')
        ax2.set_ylabel('ACOS (capped at 10)')
        ax.set_xticks(x)
        ax.set_xticklabels([rf.replace('_', ' ').title() for rf in rf_names], rotation=45)
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
    
    def generate_detailed_report(self):
        """Generate a detailed text report of findings"""
        print("\nGenerating detailed analysis report...")
        
        report_path = self.results_dir / 'ppo_reward_functions_c15_analysis_report.txt'
        
        with open(report_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("COMPREHENSIVE ANALYSIS OF PPO REWARD FUNCTIONS IN AUCTIONSGYM (C15)\n")
            f.write("="*80 + "\n\n")
            
            f.write("EXPERIMENT OVERVIEW:\n")
            f.write("-" * 20 + "\n")
            f.write("This analysis compares three PPO reward function configurations (C15):\n")
            f.write("1. PPO_NU_R3_I25_RPI100K_C15: Net Utility (VPC * click) - price_paid\n")
            f.write("2. PPO_GU_R3_I25_RPI100K_C15: Gross Utility VPC * click\n")
            f.write("3. PPO_PWS_R3_I25_RPI100K_C15: Penalty for Wasted Spend\n")
            f.write("All experiments: 100K rounds, 25 iterations, 3 runs, 15 competitors\n\n")
            
            f.write("SUMMARY METRICS:\n")
            f.write("-" * 20 + "\n")
            for rf_name in self.reward_functions.keys():
                f.write(f"\n{rf_name.replace('_', ' ').title()}:\n")
                metrics = self.metrics.get(rf_name, {})
                for metric_name, value in metrics.items():
                    if isinstance(value, float):
                        f.write(f"  {metric_name}: {value:.4f}\n")
                    else:
                        f.write(f"  {metric_name}: {value}\n")
            
            f.write("\nKEY FINDINGS:\n")
            f.write("-" * 20 + "\n")
            
            # Performance comparison
            net_utils = [self.metrics[rf].get('final_net_utility', 0) for rf in self.reward_functions.keys()]
            best_net_utility = max(net_utils) if net_utils else 0
            best_performer = list(self.reward_functions.keys())[net_utils.index(best_net_utility)] if net_utils else "N/A"
            
            f.write(f"1. Best Final Net Utility: {best_performer.replace('_', ' ').title()} ({best_net_utility:.4f})\n")
            
            # Learning efficiency
            convergence_times = [self.metrics[rf].get('convergence_iteration', 25) for rf in self.reward_functions.keys()]
            fastest_learner = list(self.reward_functions.keys())[convergence_times.index(min(convergence_times))] if convergence_times else "N/A"
            
            f.write(f"2. Fastest Convergence: {fastest_learner.replace('_', ' ').title()} ({min(convergence_times)} iterations)\n")
            
            # Regret analysis
            total_regrets = [self.metrics[rf].get('total_regret', 0) for rf in self.reward_functions.keys()]
            lowest_regret = list(self.reward_functions.keys())[total_regrets.index(min(total_regrets))] if total_regrets else "N/A"
            
            f.write(f"3. Lowest Total Regret: {lowest_regret.replace('_', ' ').title()} ({min(total_regrets):.4f})\n")
            
            f.write("\nBEHAVIORAL INSIGHTS:\n")
            f.write("-" * 20 + "\n")
            f.write("• Net Utility: Balanced approach considering both revenue and costs\n")
            f.write("• Gross Utility: More aggressive bidding, potentially higher spend\n")
            f.write("• Penalty Wasted Spend: Conservative approach, focuses on click efficiency\n")
            
            f.write(f"\nReport generated: {pd.Timestamp.now()}\n")
            f.write("="*80 + "\n")
        
        print(f"Detailed report saved to: {report_path}")
    
    def create_summary_table(self):
        """Create a summary comparison table"""
        print("\nCreating summary comparison table...")
        
        # Prepare data for the summary table
        table_data = []
        for rf_name in self.reward_functions.keys():
            metrics = self.metrics.get(rf_name, {})
            row = {
                'Reward Function': rf_name.replace('_', ' ').title(),
                'Final Net Utility': f"{metrics.get('final_net_utility', 0):.2f}",
                'Final Gross Utility': f"{metrics.get('final_gross_utility', 0):.2f}",
                'Total Spend': f"{metrics.get('final_total_spend', 0):.2f}",
                'Total Clicks': f"{metrics.get('final_total_clicks', 0):.0f}",
                'ACOS': f"{metrics.get('final_acos', float('inf')):.2f}" if metrics.get('final_acos', float('inf')) != float('inf') else "∞",
                'Convergence Iteration': f"{metrics.get('convergence_iteration', 25):.0f}",
                'Total Regret': f"{metrics.get('total_regret', 0):.4f}"
            }
            table_data.append(row)
        
        # Create DataFrame and save
        summary_df = pd.DataFrame(table_data)
        summary_path = self.results_dir / 'ppo_reward_functions_c15_summary_table.csv'
        summary_df.to_csv(summary_path, index=False)
        
        print("Summary Table:")
        print("=" * 100)
        print(summary_df.to_string(index=False))
        print(f"\nSummary table saved to: {summary_path}")
        
        return summary_df

def main():
    """Main analysis execution"""
    print("Starting Comprehensive PPO Reward Functions Analysis (C15)")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = RewardFunctionAnalyzer()
    
    # Load data
    analyzer.load_data()
    
    # Calculate metrics
    analyzer.calculate_summary_metrics()
    
    # Create visualizations
    analyzer.create_comparison_plots()
    
    # Generate reports
    analyzer.generate_detailed_report()
    analyzer.create_summary_table()
    
    print("\nAnalysis completed successfully!")
    print("Generated outputs:")
    print("- ppo_reward_functions_c15_comprehensive_analysis.pdf")
    print("- ppo_reward_functions_c15_comprehensive_analysis.png")
    print("- ppo_reward_functions_c15_analysis_report.txt")
    print("- ppo_reward_functions_c15_summary_table.csv")


if __name__ == "__main__":
    main()