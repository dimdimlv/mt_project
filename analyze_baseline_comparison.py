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
        
        # List of metrics to analyze with their CSV column names
        metrics_mapping = {
            'net_utility': 'Net Utility',
            'gross_utility': 'Gross Utility', 
            'total_spend': 'Total Spend',
            'total_clicks': 'Total Clicks',
            'cvr': 'CVR',
            'total_sales_revenue': 'Total Sales Revenue',
            'underbid_regret': 'Underbid Regret'
        }
        
        for metric, column_name in metrics_mapping.items():
            # Look for the CSV file for this metric
            csv_pattern = f"{metric}_100000_rounds_25_iters_3_runs_5_emb_of_*.csv"
            csv_files = list(folder_path.glob(csv_pattern))
            
            if csv_files:
                csv_file = csv_files[0]  # Take the first match
                try:
                    df = pd.read_csv(csv_file)
                    
                    # Check if the expected columns exist
                    if 'Agent' in df.columns and column_name in df.columns:
                        # Rename columns to standard format
                        df = df.rename(columns={
                            'Agent': 'agent_name',
                            'Iteration': 'iter',
                            column_name: 'value'
                        })
                        
                        # Separate PPO data from baseline data
                        ppo_rows = df[df['agent_name'].str.contains('PPO', na=False)]
                        baseline_rows = df[df['agent_name'].str.contains('Truthful', na=False)]
                        
                        ppo_data[metric] = ppo_rows
                        baseline_data[metric] = baseline_rows
                        
                        print(f"    Loaded {metric}: {len(ppo_rows)} PPO rows, {len(baseline_rows)} baseline rows")
                    else:
                        print(f"    Warning: Expected columns not found in {csv_file}")
                        print(f"    Available columns: {list(df.columns)}")
                        ppo_data[metric] = pd.DataFrame()
                        baseline_data[metric] = pd.DataFrame()
                    
                except Exception as e:
                    print(f"    Warning: Could not load {csv_file}: {e}")
                    ppo_data[metric] = pd.DataFrame()
                    baseline_data[metric] = pd.DataFrame()
            else:
                print(f"    Warning: No file found for metric {metric}")
                ppo_data[metric] = pd.DataFrame()
                baseline_data[metric] = pd.DataFrame()
                
        return ppo_data, baseline_data
    
    def calculate_baseline_statistics(self):
        """Calculate statistics for baseline performance across all configurations"""
        print("Calculating baseline statistics...")
        
        self.baseline_stats = {}
        
        for config_name in self.configurations.keys():
            print(f"  Processing {config_name}...")
            self.baseline_stats[config_name] = {}
            
            # For each configuration, we'll aggregate baseline data across all reward function experiments
            aggregated_baselines = {}
            
            for reward_name in self.configurations[config_name].keys():
                baseline_data = self.baseline_data[config_name][reward_name]
                
                for metric, df in baseline_data.items():
                    if not df.empty:
                        if metric not in aggregated_baselines:
                            aggregated_baselines[metric] = []
                        
                        # Get final iteration performance (iteration 24)
                        final_data = df[df['iter'] == 24]
                        if not final_data.empty:
                            aggregated_baselines[metric].extend(final_data['value'].tolist())
            
            # Calculate statistics for each metric
            for metric, values in aggregated_baselines.items():
                if values:
                    self.baseline_stats[config_name][metric] = {
                        'mean': np.mean(values),
                        'std': np.std(values),
                        'median': np.median(values),
                        'min': np.min(values),
                        'max': np.max(values),
                        'q25': np.percentile(values, 25),
                        'q75': np.percentile(values, 75),
                        'count': len(values),
                        'values': values  # Store all values for statistical tests
                    }
    
    def compare_ppo_vs_baselines(self):
        """Compare PPO performance against baseline statistics"""
        print("Comparing PPO performance vs baselines...")
        
        self.comparison_results = {}
        
        for config_name in self.configurations.keys():
            print(f"  Processing {config_name}...")
            self.comparison_results[config_name] = {}
            
            for reward_name in self.configurations[config_name].keys():
                print(f"    Analyzing {reward_name}...")
                self.comparison_results[config_name][reward_name] = {}
                
                ppo_data = self.ppo_data[config_name][reward_name]
                
                for metric in ['net_utility', 'gross_utility', 'total_spend', 'total_clicks', 'cvr']:
                    ppo_df = ppo_data.get(metric, pd.DataFrame())
                    
                    if not ppo_df.empty and metric in self.baseline_stats[config_name]:
                        # Get PPO final performance (iteration 24)
                        ppo_final = ppo_df[ppo_df['iter'] == 24]
                        
                        if not ppo_final.empty:
                            ppo_values = ppo_final['value'].tolist()
                            baseline_stats = self.baseline_stats[config_name][metric]
                            baseline_values = baseline_stats['values']
                            
                            # Calculate comparison metrics
                            ppo_mean = np.mean(ppo_values)
                            baseline_mean = baseline_stats['mean']
                            improvement = ((ppo_mean - baseline_mean) / baseline_mean) * 100
                            
                            # Perform statistical tests
                            try:
                                # t-test
                                t_stat, t_pvalue = ttest_ind(ppo_values, baseline_values)
                                
                                # Mann-Whitney U test (non-parametric)
                                u_stat, u_pvalue = mannwhitneyu(ppo_values, baseline_values, alternative='two-sided')
                                
                                # Effect size (Cohen's d)
                                pooled_std = np.sqrt(((len(ppo_values) - 1) * np.var(ppo_values, ddof=1) + 
                                                    (len(baseline_values) - 1) * np.var(baseline_values, ddof=1)) / 
                                                   (len(ppo_values) + len(baseline_values) - 2))
                                cohens_d = (ppo_mean - baseline_mean) / pooled_std if pooled_std > 0 else 0
                                
                            except Exception as e:
                                print(f"      Warning: Statistical test failed for {metric}: {e}")
                                t_stat, t_pvalue = 0, 1
                                u_stat, u_pvalue = 0, 1
                                cohens_d = 0
                            
                            self.comparison_results[config_name][reward_name][metric] = {
                                'ppo_mean': ppo_mean,
                                'ppo_std': np.std(ppo_values),
                                'baseline_mean': baseline_mean,
                                'baseline_std': baseline_stats['std'],
                                'improvement_percent': improvement,
                                't_statistic': t_stat,
                                't_pvalue': t_pvalue,
                                'u_statistic': u_stat,
                                'u_pvalue': u_pvalue,
                                'cohens_d': cohens_d,
                                'significant': t_pvalue < 0.05
                            }
    
    def create_baseline_comparison_plots(self):
        """Generate comprehensive baseline comparison visualizations"""
        print("Generating baseline comparison plots...")
        
        # Create a comprehensive figure with multiple subplots
        fig = plt.figure(figsize=(20, 24))
        
        metrics_to_plot = ['net_utility', 'gross_utility', 'total_spend', 'total_clicks', 'cvr']
        metric_titles = ['Net Utility', 'Gross Utility', 'Total Spend', 'Total Clicks', 'Conversion Rate']
        
        plot_idx = 1
        
        for i, (metric, title) in enumerate(zip(metrics_to_plot, metric_titles)):
            # Plot 1: Improvement percentages
            plt.subplot(5, 3, plot_idx)
            self._plot_improvement_percentages(metric, title)
            plot_idx += 1
            
            # Plot 2: Absolute values comparison
            plt.subplot(5, 3, plot_idx)
            self._plot_absolute_comparison(metric, title)
            plot_idx += 1
            
            # Plot 3: Statistical significance
            plt.subplot(5, 3, plot_idx)
            self._plot_statistical_significance(metric, title)
            plot_idx += 1
        
        plt.tight_layout()
        
        # Save plots
        output_path = self.results_dir / "baseline_comparison_analysis.png"
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Baseline comparison plots saved to: {output_path}")
        
        output_path_pdf = self.results_dir / "baseline_comparison_analysis.pdf"
        plt.savefig(output_path_pdf, bbox_inches='tight')
        print(f"Baseline comparison plots saved to: {output_path_pdf}")
        
        plt.close()
    
    def _plot_improvement_percentages(self, metric, title):
        """Plot improvement percentages vs baseline"""
        data = []
        configs = []
        rewards = []
        improvements = []
        
        for config in ['C5', 'C10', 'C15']:
            for reward in ['net_utility', 'gross_utility', 'penalty_wasted_spend']:
                if (config in self.comparison_results and 
                    reward in self.comparison_results[config] and
                    metric in self.comparison_results[config][reward]):
                    
                    improvement = self.comparison_results[config][reward][metric]['improvement_percent']
                    configs.append(config)
                    rewards.append(reward.replace('_', ' ').title())
                    improvements.append(improvement)
        
        if improvements:
            df_plot = pd.DataFrame({
                'Configuration': configs,
                'Reward Function': rewards,
                'Improvement (%)': improvements
            })
            
            sns.barplot(data=df_plot, x='Configuration', y='Improvement (%)', hue='Reward Function')
            plt.title(f'{title} - Improvement vs Baseline')
            plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
            plt.xticks(rotation=45)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    def _plot_absolute_comparison(self, metric, title):
        """Plot absolute values: PPO vs Baseline"""
        configs = []
        values = []
        types = []
        reward_funcs = []
        
        for config in ['C5', 'C10', 'C15']:
            for reward in ['net_utility', 'gross_utility', 'penalty_wasted_spend']:
                if (config in self.comparison_results and 
                    reward in self.comparison_results[config] and
                    metric in self.comparison_results[config][reward]):
                    
                    result = self.comparison_results[config][reward][metric]
                    
                    # PPO values
                    configs.append(config)
                    values.append(result['ppo_mean'])
                    types.append('PPO')
                    reward_funcs.append(reward.replace('_', ' ').title())
                    
                    # Baseline values
                    configs.append(config)
                    values.append(result['baseline_mean'])
                    types.append('Baseline')
                    reward_funcs.append(reward.replace('_', ' ').title())
        
        if values:
            df_plot = pd.DataFrame({
                'Configuration': configs,
                'Value': values,
                'Type': types,
                'Reward Function': reward_funcs
            })
            
            sns.barplot(data=df_plot, x='Configuration', y='Value', hue='Type')
            plt.title(f'{title} - Absolute Values')
            plt.xticks(rotation=45)
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    def _plot_statistical_significance(self, metric, title):
        """Plot statistical significance indicators"""
        data = []
        
        for config in ['C5', 'C10', 'C15']:
            for reward in ['net_utility', 'gross_utility', 'penalty_wasted_spend']:
                if (config in self.comparison_results and 
                    reward in self.comparison_results[config] and
                    metric in self.comparison_results[config][reward]):
                    
                    result = self.comparison_results[config][reward][metric]
                    
                    data.append({
                        'Configuration': config,
                        'Reward Function': reward.replace('_', ' ').title(),
                        'P-value': result['t_pvalue'],
                        'Effect Size': abs(result['cohens_d']),
                        'Significant': result['significant']
                    })
        
        if data:
            df_plot = pd.DataFrame(data)
            
            # Create scatter plot with p-value vs effect size
            colors = ['red' if sig else 'blue' for sig in df_plot['Significant']]
            scatter = plt.scatter(df_plot['Effect Size'], df_plot['P-value'], c=colors, alpha=0.7)
            
            plt.axhline(y=0.05, color='black', linestyle='--', alpha=0.5, label='p=0.05')
            plt.xlabel('Effect Size (|Cohen\'s d|)')
            plt.ylabel('P-value')
            plt.title(f'{title} - Statistical Significance')
            plt.yscale('log')
            
            # Add legend
            red_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='r', markersize=8, label='Significant')
            blue_patch = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='b', markersize=8, label='Not Significant')
            plt.legend(handles=[red_patch, blue_patch])
    
    def generate_baseline_comparison_report(self):
        """Generate a comprehensive baseline comparison report"""
        print("Generating baseline comparison report...")
        
        report_path = self.results_dir / "baseline_comparison_report.txt"
        
        with open(report_path, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("BASELINE COMPARISON ANALYSIS OF PPO REWARD FUNCTIONS\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("EXPERIMENT OVERVIEW:\n")
            f.write("-" * 30 + "\n")
            f.write("This analysis compares PPO reward functions against truthful competitor baselines:\n")
            f.write("• Net Utility (NU): (VPC * click) - price_paid\n")
            f.write("• Gross Utility (GU): VPC * click\n")
            f.write("• Penalty Wasted Spend (PWS): reward if click, penalty if no click\n\n")
            
            f.write("Baselines: Truthful bidders (truth-telling strategy)\n")
            f.write("Statistical Tests: t-test, Mann-Whitney U, Cohen's d effect size\n")
            f.write("Significance Level: p < 0.05\n\n")
            
            # Configuration-wise analysis
            for config_name in ['C5', 'C10', 'C15']:
                f.write(f"{config_name} CONFIGURATION RESULTS:\n")
                f.write("-" * 40 + "\n\n")
                
                # Baseline statistics
                if config_name in self.baseline_stats:
                    f.write("Baseline Performance Statistics:\n")
                    for metric, stats in self.baseline_stats[config_name].items():
                        f.write(f"  {metric}:\n")
                        f.write(f"    mean: {stats['mean']:.2f}\n")
                        f.write(f"    std: {stats['std']:.2f}\n")
                        f.write(f"    median: {stats['median']:.2f}\n")
                        f.write(f"    count: {stats['count']}\n\n")
                
                # PPO vs Baseline comparisons
                if config_name in self.comparison_results:
                    for reward_name in ['net_utility', 'gross_utility', 'penalty_wasted_spend']:
                        if reward_name in self.comparison_results[config_name]:
                            f.write(f"{reward_name.replace('_', ' ').title()} vs Baseline:\n")
                            
                            for metric, result in self.comparison_results[config_name][reward_name].items():
                                f.write(f"  {metric}:\n")
                                f.write(f"    PPO: {result['ppo_mean']:.2f} ± {result['ppo_std']:.2f}\n")
                                f.write(f"    Baseline: {result['baseline_mean']:.2f} ± {result['baseline_std']:.2f}\n")
                                f.write(f"    Improvement: {result['improvement_percent']:.1f}%\n")
                                f.write(f"    P-value: {result['t_pvalue']:.4f}\n")
                                f.write(f"    Effect size: {result['cohens_d']:.3f}\n")
                                f.write(f"    Significant: {'Yes' if result['significant'] else 'No'}\n\n")
                            
                            f.write("\n")
                
                f.write("\n")
            
            # Summary section
            f.write("SUMMARY OF KEY FINDINGS:\n")
            f.write("-" * 30 + "\n")
            
            # Find best performing configurations
            best_improvements = {}
            significant_improvements = {}
            
            for config in ['C5', 'C10', 'C15']:
                for reward in ['net_utility', 'gross_utility', 'penalty_wasted_spend']:
                    if (config in self.comparison_results and 
                        reward in self.comparison_results[config]):
                        
                        for metric, result in self.comparison_results[config][reward].items():
                            key = f"{config}_{reward}_{metric}"
                            best_improvements[key] = result['improvement_percent']
                            
                            if result['significant']:
                                significant_improvements[key] = result['improvement_percent']
            
            # Top improvements
            if best_improvements:
                sorted_improvements = sorted(best_improvements.items(), key=lambda x: x[1], reverse=True)
                f.write("Top 5 Improvements vs Baseline:\n")
                for i, (key, improvement) in enumerate(sorted_improvements[:5]):
                    config, reward, metric = key.split('_', 2)
                    f.write(f"  {i+1}. {config} {reward.replace('_', ' ').title()} - {metric}: {improvement:.1f}%\n")
                f.write("\n")
            
            # Significant improvements
            if significant_improvements:
                f.write("Statistically Significant Improvements:\n")
                sig_sorted = sorted(significant_improvements.items(), key=lambda x: x[1], reverse=True)
                for key, improvement in sig_sorted:
                    config, reward, metric = key.split('_', 2)
                    f.write(f"  • {config} {reward.replace('_', ' ').title()} - {metric}: {improvement:.1f}%\n")
                f.write("\n")
        
        print(f"Baseline comparison report saved to: {report_path}")
    
    def create_summary_comparison_table(self):
        """Create a summary table comparing all configurations against baselines"""
        print("Creating baseline comparison summary table...")
        
        summary_data = []
        
        for config in ['C5', 'C10', 'C15']:
            for reward in ['net_utility', 'gross_utility', 'penalty_wasted_spend']:
                if (config in self.comparison_results and 
                    reward in self.comparison_results[config]):
                    
                    # Get net utility comparison (primary metric)
                    if 'net_utility' in self.comparison_results[config][reward]:
                        result = self.comparison_results[config][reward]['net_utility']
                        
                        summary_data.append({
                            'Configuration': config,
                            'Competitors': config[1:],  # Extract number from C5, C10, C15
                            'Reward Function': reward.replace('_', ' ').title(),
                            'PPO Net Utility': f"{result['ppo_mean']:.2f}",
                            'Baseline Net Utility': f"{result['baseline_mean']:.2f}",
                            'Improvement (%)': f"{result['improvement_percent']:.1f}%",
                            'P-value': f"{result['t_pvalue']:.4f}",
                            'Effect Size': f"{result['cohens_d']:.3f}",
                            'Significant': 'Yes' if result['significant'] else 'No'
                        })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            
            # Save to CSV
            summary_path = self.results_dir / "baseline_comparison_summary_table.csv"
            summary_df.to_csv(summary_path, index=False)
            
            # Print summary
            print("\nBaseline Comparison Summary Table:")
            print("=" * 100)
            print(summary_df.to_string(index=False))
            print(f"\nSummary table saved to: {summary_path}")
            
            return summary_df


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
        
        # Calculate baseline statistics
        print("Calculating baseline statistics...")
        analyzer.calculate_baseline_statistics()
        
        # Compare PPO vs baselines
        print("Performing PPO vs baseline comparisons...")
        analyzer.compare_ppo_vs_baselines()
        
        # Create visualizations
        print("Creating baseline comparison visualizations...")
        analyzer.create_baseline_comparison_plots()
        
        # Generate report
        print("Generating baseline comparison report...")
        analyzer.generate_baseline_comparison_report()
        
        # Create summary table
        print("Creating baseline comparison summary table...")
        analyzer.create_summary_comparison_table()
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\nBaseline comparison analysis completed successfully!")
    print("Generated outputs:")
    print("- baseline_comparison_analysis.pdf")
    print("- baseline_comparison_analysis.png")
    print("- baseline_comparison_report.txt")
    print("- baseline_comparison_summary_table.csv")

if __name__ == "__main__":
    main()
