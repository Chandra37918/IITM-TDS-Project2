# -*- coding: utf-8 -*-
"""autolysis - Corrected Code"""

import os
import sys
import subprocess

# Helper function to check and install missing libraries
def install_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing missing package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Check for required packages
required_packages = ["pandas", "matplotlib", "seaborn", "httpx", "chardet"]
for package in required_packages:
    install_package(package)

# Import modules after ensuring installation
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import httpx
import chardet

# Constants
API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
AIPROXY_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjIwMDA1OTBAZHMuc3R1ZHkuaWl0bS5hYy5pbiJ9.kX5xjtFCGnivrfSatvDuvFFR5RPJ_jcDFB1XqaxfzW4"

def load_data(file_path):
    """Load CSV data with encoding detection."""
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        encoding = result['encoding']
        print(f"Detected file encoding: {encoding}")
        return pd.read_csv(file_path, encoding=encoding)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading file: {e}")
        sys.exit(1)

def analyze_data(df):
    """Perform basic data analysis."""
    numeric_df = df.select_dtypes(include=['number'])  # Select only numeric columns
    analysis = {
        'summary': df.describe(include='all').to_dict(),
        'missing_values': df.isnull().sum().to_dict(),
        'correlation': numeric_df.corr().to_dict()  # Compute correlation only on numeric columns
    }
    return analysis

def visualize_data(df):
    """Generate and save visualizations."""
    sns.set(style="whitegrid")
    numeric_columns = df.select_dtypes(include=['number']).columns
    if len(numeric_columns) == 0:
        print("No numeric columns to visualize.")
        return
    for column in numeric_columns:
        try:
            plt.figure()
            sns.histplot(df[column].dropna(), kde=True)
            plt.title(f'Distribution of {column}')
            plt.savefig(f'{column}_distribution.png')
            plt.close()
            print(f"Saved visualization: {column}_distribution.png")
        except Exception as e:
            print(f"Error generating visualization for {column}: {e}")

def generate_narrative(analysis):
    """Generate narrative using LLM."""
    headers = {
        'Authorization': f'Bearer {AIPROXY_TOKEN}',
        'Content-Type': 'application/json'
    }
    prompt = f"Provide a detailed analysis based on the following data summary: {analysis}"
    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    try:
        response = httpx.post(API_URL, headers=headers, json=data, timeout=30.0)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return "Narrative generation failed due to an error."

def main(file_path):
    print("Starting data analysis...")
    df = load_data(file_path)
    print("Data loaded successfully.")

    print("Analyzing data...")
    analysis = analyze_data(df)
    print("Data analysis completed.")

    print("Generating visualizations...")
    visualize_data(df)
    print("Visualizations saved.")

    print("Generating narrative report...")
    narrative = generate_narrative(analysis)
    print("Narrative report generated.")

    with open('README.md', 'w') as f:
        f.write(narrative)
    print("README.md created with the narrative report.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python autolysis.py <dataset.csv>")
        sys.exit(1)
    main(sys.argv[1])
