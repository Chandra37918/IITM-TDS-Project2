# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pandas",
#   "seaborn",
#   "matplotlib",
#   "numpy",
#   "scipy",
#   "openai",
#   "scikit-learn",
#   "requests",
#   "ipykernel",  # Added ipykernel
# ]
# ///

import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
import requests
import json
import openai  # Make sure you install this library: pip install openai

# Function to analyze the data (basic summary stats, missing values, correlation matrix)
def analyze_data(df):
    print("Analyzing the data...")  # Debugging line
    # Summary statistics for numerical columns
    summary_stats = df.describe()

    # Check for missing values
    missing_values = df.isnull().sum()

    # Select only numeric columns for correlation matrix
    numeric_df = df.select_dtypes(include=[np.number])

    # Correlation matrix for numerical columns
    corr_matrix = numeric_df.corr() if not numeric_df.empty else pd.DataFrame()

    print("Data analysis complete.")  # Debugging line
    return summary_stats, missing_values, corr_matrix


# Function to detect outliers using the IQR method
def detect_outliers(df):
    print("Detecting outliers...")  # Debugging line
    # Select only numeric columns
    df_numeric = df.select_dtypes(include=[np.number])

    # Apply the IQR method to find outliers in the numeric columns
    Q1 = df_numeric.quantile(0.25)
    Q3 = df_numeric.quantile(0.75)
    IQR = Q3 - Q1
    outliers = ((df_numeric < (Q1 - 1.5 * IQR)) | (df_numeric > (Q3 + 1.5 * IQR))).sum()

    print("Outliers detection complete.")  # Debugging line
    return outliers


# Function to generate visualizations (correlation heatmap, outliers plot, and distribution plot)
def visualize_data(corr_matrix, outliers, df, output_dir):
    print("Generating visualizations...")  # Debugging line
    # Generate a heatmap for the correlation matrix
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Correlation Matrix')
    heatmap_file = os.path.join(output_dir, 'correlation_matrix.png')
    plt.savefig(heatmap_file)
    plt.close()

    # Check if there are outliers to plot
    if not outliers.empty and outliers.sum() > 0:
        # Plot the outliers
        plt.figure(figsize=(10, 6))
        outliers.plot(kind='bar', color='red')
        plt.title('Outliers Detection')
        plt.xlabel('Columns')
        plt.ylabel('Number of Outliers')
        outliers_file = os.path.join(output_dir, 'outliers.png')
        plt.savefig(outliers_file)
        plt.close()
    else:
        print("No outliers detected to visualize.")
        outliers_file = None  # No file created for outliers

    # Generate a distribution plot for the first numeric column
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) > 0:
        first_numeric_column = numeric_columns[0]  # Get the first numeric column
        plt.figure(figsize=(10, 6))
        sns.histplot(df[first_numeric_column], kde=True, color='blue', bins=30)
        plt.title(f'Distribution')
        dist_plot_file = os.path.join(output_dir, f'distribution_.png')
        plt.savefig(dist_plot_file)
        plt.close()
    else:
        dist_plot_file = None  # No numeric columns to plot

    print("Visualizations generated.")  # Debugging line
    return heatmap_file, outliers_file, dist_plot_file


# Function to create the README.md with a narrative and visualizations
def create_readme(summary_stats, missing_values, corr_matrix, outliers, output_dir):
    print("Creating README file...")  # Debugging line
    readme_file = os.path.join(output_dir, 'README.md')
    try:
        with open(readme_file, 'w') as f:
            f.write("# Automated Data Analysis Report\n\n")
            f.write("## Introduction\n")
            f.write("This is an automated analysis of the dataset, providing summary statistics, visualizations, and insights.\n\n")

            # Summary Statistics
            f.write("## Summary Statistics\n")
            f.write("| Column | Mean | Std Dev | Min | 25% | Median | 75% | Max |\n")
            f.write("|--------|------|---------|-----|-----|--------|-----|-----|\n")
            for column in summary_stats.columns:
                f.write(f"| {column} | {summary_stats.loc['mean', column]:.2f} | {summary_stats.loc['std', column]:.2f} | "
                        f"{summary_stats.loc['min', column]:.2f} | {summary_stats.loc['25%', column]:.2f} | "
                        f"{summary_stats.loc['50%', column]:.2f} | {summary_stats.loc['75%', column]:.2f} | "
                        f"{summary_stats.loc['max', column]:.2f} |\n")

            # Missing Values
            f.write("\n## Missing Values\n")
            f.write("| Column | Missing Values |\n|--------|-----------------|\n")
            for column, count in missing_values.items():
                f.write(f"| {column} | {count} |\n")

            # Outliers
            f.write("\n## Outliers Detection\n")
            f.write("| Column | Outliers Count |\n|--------|----------------|\n")
            for column, count in outliers.items():
                f.write(f"| {column} | {count} |\n")

            # Visualizations
            f.write("\n## Visualizations\n")
            f.write("### Correlation Matrix\n")
            f.write("![Correlation Matrix](correlation_matrix.png)\n")
            f.write("### Outliers\n")
            f.write("![Outliers](outliers.png)\n")
            f.write("### Distribution Plot\n")
            f.write("![Distribution](distribution_.png)\n")
        print(f"README file created: {readme_file}")
        return readme_file
    except Exception as e:
        print(f"Error writing to README.md: {e}")
        return None


# Main function to execute the script
def main():
    parser = argparse.ArgumentParser(description="Automated Data Analysis Tool")
    parser.add_argument("--input", type=str, required=True, help="Input CSV file path")
    parser.add_argument("--output", type=str, required=True, help="Output directory path")
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)

    # Read input CSV file
    df = pd.read_csv(args.input)
    print("Dataset loaded successfully.")

    # Analyze data
    summary_stats, missing_values, corr_matrix = analyze_data(df)
    outliers = detect_outliers(df)

    # Visualize data
    visualize_data(corr_matrix, outliers, df, args.output)

    # Generate README
    create_readme(summary_stats, missing_values, corr_matrix, outliers, args.output)


if __name__ == "__main__":
    main()
