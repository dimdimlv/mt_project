#!/usr/bin/env python3
"""
Cross-Configuration Analysis of PPO Reward Functions in AuctionGym

This script provides a comprehensive comparison across all competition levels:
- C5: 5 competitors
- C10: 10 competitors  
- C15: 15 competitors

For each competition level, it compares three reward functions:
1. Net Utility (NU): (VPC * click) - price_paid
2. Gross Utility (GU): VPC * click
3. Penalty for Wasted Spend (PWS): reward if click, penalty if no click but won

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

class CrossConfigurationAnalyzer:
    """Analyzer for comparing reward functions across different competition levels"""
    
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
        self.data = {}
        self.metrics = {}
        
    def load_all_data(self):
        """Load data for all configurations and reward functions"""
        print("Loading data from all PPO configurations...")
        
        for config_name, reward_functions in self.configurations.items():
            print(f"\n  Loading {config_name} configuration...")
            self.data[config_name] = {}
            
            for rf_name, folder_name in reward_functions.items():
                folder_path = self.results_dir / folder_name
                if folder_path.exists():
                    print(f"    Loading {rf_name} data...")
                    self.data[config_name][rf_name] = {}
                    
                    # Load key metrics CSV files
                    csv_files = {
                        'net_utility': 'net_utility_100000_rounds_25_iters_3_runs_5_emb_of_5.csv',
                        'gross_utility': 'gross_utility_100000_rounds_25_iters_3_runs_5_emb_of_5.csv',
                        'total_spend': 'total_spend_100000_rounds_25_iters_3_runs_5_emb_of_5.csv',
                        'total_clicks': 'total_clicks_100000_rounds_25_iters_3_runs_5_emb_of_5.csv',
                        'acos': 'acos_100000_rounds_25_iters_3_runs_5_emb_of_5.csv'
                    }
                    
                    for metric_name, csv_file in csv_files.items():
                        csv_path = folder_path / csv_file
                        if csv_path.exists():
                            try:
                                self.data[config_name][rf_name][metric_name] = pd.read_csv(csv_path)
                            except Exception as e:
                                print(f"      Warning: Could not load {csv_file}: {e}")
                else:
                    print(f"    Warning: Folder {folder_name} not found")
    
    def calculate_summary_metrics(self):
        """Calculate summary metrics for all configurations"""
        print("\nCalculating summary metrics...")
        
        for config_name in self.configurations.keys():
            print(f"  Processing {config_name}...")
            self.metrics[config_name] = {}
            
            for rf_name in self.configurations[config_name].keys():
                if config_name in self.data and rf_name in self.data[config_name]:
                    self.metrics[config_name][rf_name] = {}
                    
                    # Calculate final metrics for each reward function
                    for metric_key in ['net_utility', 'gross_utility', 'total_spend', 'total_clicks', 'acos']:
                        if metric_key in self.data[config_name][rf_name]:
                            df = self.data[config_name][rf_name][metric_key]
                            
                            # Filter to PPO Bidder only and get final iteration (24)
                            ppo_data = df[df['Agent'].str.contains('PPO Bidder', na=False)]
                            final_iter_data = ppo_data[ppo_data['Iteration'] == 24]
                            
                            if len(final_iter_data) > 0:
                                metric_col = df.columns[-1]
                                avg_value = final_iter_data[metric_col].mean()
                                self.metrics[config_name][rf_name][f'final_{metric_key}'] = avg_value
    
    def create_cross_configuration_plots(self):
        """Create comprehensive cross-configuration comparison plots"""
        print("\nGenerating cross-configuration comparison plots...")
        
        # Create figure with multiple subplots
        fig = plt.figure(figsize=(20, 15))
        
        # 1. Net Utility across configurations
        ax1 = plt.subplot(2, 3, 1)
        self._plot_metric_across_configs(ax1, 'final_net_utility', 'Net Utility Across Configurations')
        
        # 2. Gross Utility across configurations
        ax2 = plt.subplot(2, 3, 2)
        self._plot_metric_across_configs(ax2, 'final_gross_utility', 'Gross Utility Across Configurations')
        
        # 3. Total Spend across configurations
        ax3 = plt.subplot(2, 3, 3)
        self._plot_metric_across_configs(ax3, 'final_total_spend', 'Total Spend Across Configurations')
        
        # 4. Total Clicks across configurations
        ax4 = plt.subplot(2, 3, 4)
        self._plot_metric_across_configs(ax4, 'final_total_clicks', 'Total Clicks Across Configurations')
        
        # 5. ACOS across configurations
        ax5 = plt.subplot(2, 3, 5)
        self._plot_metric_across_configs(ax5, 'final_acos', 'ACOS Across Configurations')
        
        # 6. Competition impact analysis
        ax6 = plt.subplot(2, 3, 6)
        self._plot_competition_impact(ax6)
        
        plt.tight_layout()
        plt.savefig(self.results_dir / 'cross_configuration_analysis.pdf', 
                   dpi=300, bbox_inches='tight')
        plt.savefig(self.results_dir / 'cross_configuration_analysis.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def _plot_metric_across_configs(self, ax, metric_key, title):
        """Plot a specific metric across all configurations"""
        configs = list(self.configurations.keys())
        reward_functions = ['net_utility', 'gross_utility', 'penalty_wasted_spend']
        
        x = np.arange(len(configs))
        width = 0.25
        
        colors = ['blue', 'green', 'red']
        
        for i, rf_name in enumerate(reward_functions):
            values = []
            for config in configs:
                if (config in self.metrics and 
                    rf_name in self.metrics[config] and 
                    metric_key in self.metrics[config][rf_name]):
                    values.append(self.metrics[config][rf_name][metric_key])
                else:
                    values.append(0)
            
            ax.bar(x + i*width, values, width, 
                  label=rf_name.replace('_', ' ').title(), 
                  color=colors[i], alpha=0.8)
        
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Competition Level')
        ax.set_ylabel(metric_key.replace('final_', '').replace('_', ' ').title())
        ax.set_xticks(x + width)
        ax.set_xticklabels(configs)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_competition_impact(self, ax):
        """Plot the impact of competition level on performance"""
        configs = list(self.configurations.keys())
        competitor_counts = [5, 10, 15]
        
        # Get net utility for each reward function across configurations
        for rf_name in ['net_utility', 'gross_utility', 'penalty_wasted_spend']:
            net_utilities = []
            for config in configs:
                if (config in self.metrics and 
                    rf_name in self.metrics[config] and 
                    'final_net_utility' in self.metrics[config][rf_name]):
                    net_utilities.append(self.metrics[config][rf_name]['final_net_utility'])
                else:
                    net_utilities.append(0)
            
            ax.plot(competitor_counts, net_utilities, 
                   label=rf_name.replace('_', ' ').title(), 
                   marker='o', linewidth=2, markersize=8)
        
        ax.set_title('Competition Impact on Net Utility', fontsize=12, fontweight='bold')
        ax.set_xlabel('Number of Competitors')
        ax.set_ylabel('Final Net Utility')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def generate_cross_configuration_report(self):
        """Generate a comprehensive cross-configuration report"""
        print("\nGenerating cross-configuration analysis report...")
        
        report_path = self.results_dir / 'cross_configuration_analysis_report.txt'
        
        with open(report_path, 'w') as f:
            f.write("="*80 + "\n")
            f.write("CROSS-CONFIGURATION ANALYSIS OF PPO REWARD FUNCTIONS\n")
            f.write("="*80 + "\n\n")
            
            f.write("EXPERIMENT OVERVIEW:\n")
            f.write("-" * 20 + "\n")
            f.write("This analysis compares three reward functions across three competition levels:\n")
            f.write("• Net Utility (NU): (VPC * click) - price_paid\n")
            f.write("• Gross Utility (GU): VPC * click\n")
            f.write("• Penalty Wasted Spend (PWS): reward if click, penalty if no click\n\n")
            f.write("Competition Levels:\n")
            f.write("• C5: 5 competitors\n")
            f.write("• C10: 10 competitors\n")
            f.write("• C15: 15 competitors\n\n")
            
            # Summary table for each configuration
            for config_name in self.configurations.keys():
                f.write(f"{config_name} CONFIGURATION RESULTS:\n")
                f.write("-" * 30 + "\n")
                
                if config_name in self.metrics:
                    for rf_name in ['net_utility', 'gross_utility', 'penalty_wasted_spend']:
                        if rf_name in self.metrics[config_name]:
                            f.write(f"\n{rf_name.replace('_', ' ').title()}:\n")
                            metrics = self.metrics[config_name][rf_name]
                            for metric_name, value in metrics.items():
                                if isinstance(value, float):
                                    f.write(f"  {metric_name}: {value:.2f}\n")
                                else:
                                    f.write(f"  {metric_name}: {value}\n")
                f.write("\n")
            
            # Cross-configuration insights
            f.write("CROSS-CONFIGURATION INSIGHTS:\n")
            f.write("-" * 30 + "\n")
            
            # Find best performers across configurations
            best_performers = {}
            for metric in ['final_net_utility', 'final_gross_utility']:
                best_value = -float('inf')
                best_config = None
                best_rf = None
                
                for config_name in self.configurations.keys():
                    if config_name in self.metrics:
                        for rf_name in self.metrics[config_name]:
                            if metric in self.metrics[config_name][rf_name]:
                                value = self.metrics[config_name][rf_name][metric]
                                if value > best_value:
                                    best_value = value
                                    best_config = config_name
                                    best_rf = rf_name
                
                if best_config and best_rf:
                    f.write(f"Best {metric.replace('final_', '').replace('_', ' ').title()}: ")
                    f.write(f"{best_rf.replace('_', ' ').title()} in {best_config} ({best_value:.2f})\n")
            
            # Competition impact analysis
            f.write("\nCOMPETITION IMPACT ANALYSIS:\n")
            f.write("-" * 30 + "\n")
            for rf_name in ['net_utility', 'gross_utility', 'penalty_wasted_spend']:
                f.write(f"\n{rf_name.replace('_', ' ').title()} performance trend:\n")
                for config in ['C5', 'C10', 'C15']:
                    if (config in self.metrics and 
                        rf_name in self.metrics[config] and 
                        'final_net_utility' in self.metrics[config][rf_name]):
                        value = self.metrics[config][rf_name]['final_net_utility']
                        f.write(f"  {config}: {value:.2f}\n")
            
            f.write(f"\nReport generated: {pd.Timestamp.now()}\n")
            f.write("="*80 + "\n")
        
        print(f"Cross-configuration report saved to: {report_path}")
    
    def create_summary_comparison_table(self):
        """Create a comprehensive summary table"""
        print("\nCreating comprehensive summary table...")
        
        # Prepare data for comprehensive table
        table_data = []
        for config_name in self.configurations.keys():
            if config_name in self.metrics:
                for rf_name in self.metrics[config_name]:
                    metrics = self.metrics[config_name][rf_name]
                    row = {
                        'Configuration': config_name,
                        'Competitors': config_name[1:],  # Extract number from C5, C10, C15
                        'Reward Function': rf_name.replace('_', ' ').title(),
                        'Net Utility': f"{metrics.get('final_net_utility', 0):.2f}",
                        'Gross Utility': f"{metrics.get('final_gross_utility', 0):.2f}",
                        'Total Spend': f"{metrics.get('final_total_spend', 0):.2f}",
                        'Total Clicks': f"{metrics.get('final_total_clicks', 0):.0f}",
                        'ACOS': f"{metrics.get('final_acos', 0):.3f}"
                    }
                    table_data.append(row)
        
        # Create DataFrame and save
        summary_df = pd.DataFrame(table_data)
        summary_path = self.results_dir / 'cross_configuration_summary_table.csv'
        summary_df.to_csv(summary_path, index=False)
        
        print("Cross-Configuration Summary Table:")
        print("=" * 120)
        print(summary_df.to_string(index=False))
        print(f"\nSummary table saved to: {summary_path}")
        
        return summary_df

def main():
    """Main analysis execution"""
    print("Starting Cross-Configuration PPO Reward Functions Analysis")
    print("=" * 70)
    
    try:
        # Initialize analyzer
        print("Initializing analyzer...")
        analyzer = CrossConfigurationAnalyzer()
        
        # Load data
        print("Loading data...")
        analyzer.load_all_data()
        
        # Calculate metrics
        print("Calculating metrics...")
        analyzer.calculate_summary_metrics()
        
        # Create visualizations
        print("Creating visualizations...")
        analyzer.create_cross_configuration_plots()
        
        # Generate reports
        print("Generating reports...")
        analyzer.generate_cross_configuration_report()
        analyzer.create_summary_comparison_table()
        
    except Exception as e:
        print(f"Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\nCross-configuration analysis completed successfully!")
    print("Generated outputs:")
    print("- cross_configuration_analysis.pdf")
    print("- cross_configuration_analysis.png")
    print("- cross_configuration_analysis_report.txt")
    print("- cross_configuration_summary_table.csv")

if __name__ == "__main__":
    main()
