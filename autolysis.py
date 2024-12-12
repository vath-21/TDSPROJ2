#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# Dependencies
# pip install pandas numpy seaborn matplotlib scikit-learn scipy requests
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
from datetime import datetime
import requests
import sys
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.stats import normaltest

# Ensure all necessary libraries are installed
REQUIRED_LIBRARIES = [
    "pandas",
    "numpy",
    "seaborn",
    "matplotlib",
    "scikit-learn",
    "scipy",
    "requests"
]

def check_and_install_libraries():
    """Check and install missing libraries."""
    import subprocess
    import importlib
    for library in REQUIRED_LIBRARIES:
        try:
            importlib.import_module(library)
        except ImportError:
            print(f"Library {library} not found. Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", library])
            except Exception as e:
                print(f"Failed to install {library}: {e}")
                sys.exit(1)

check_and_install_libraries()

# Ensure AIPROXY_TOKEN is set in the environment
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    print("Error: AIPROXY_TOKEN environment variable is not set.")
    sys.exit(1)

API_BASE = "https://aiproxy.sanand.workers.dev/openai/v1"

def generate_llm_story(analysis, images, key_insights):
    """
    Generate a narrative about the data analysis using GPT-4o-mini via direct REST API.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {AIPROXY_TOKEN}"
    }

    prompt = f"""
    You received a dataset with {analysis['rows']} rows and {analysis['columns']} columns.
    The dataset includes columns: {', '.join(analysis['column_names'])}.

    Based on this dataset, the following analyses were performed:
    - Outlier Detection
    - Correlation Analysis
    - Clustering
    - Normality Test

    Key insights:
    {key_insights}

    Visualizations:
    - Correlation Heatmap: {images['correlation']}
    - Clustering Visualization: {images['clustering']}

    Please write a data story that includes:
    1. A brief description of the dataset.
    2. Explanation of each analysis and the methods used.
    3. Key insights from the findings.
    4. Implications and actionable recommendations.

    Use an engaging narrative tone suitable for a professional report.
    """

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a data analyst summarizing analysis results into a report."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1000
    }

    try:
        response = requests.post(f"{API_BASE}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Error with OpenAI API: {e}")
        sys.exit(1)

def create_visualizations(df):
    """
    Generate visualizations for the dataset.
    """
    # Correlation heatmap
    plt.figure(figsize=(12, 8))
    correlation_matrix = df.select_dtypes(include=[np.number]).corr()
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', linewidths=0.5)
    correlation_path = 'correlation_heatmap.png'
    plt.title('Correlation Heatmap', fontsize=16)
    plt.xlabel('Features')
    plt.ylabel('Features')
    plt.tight_layout()
    plt.savefig(correlation_path)
    plt.close()

    # Clustering visualization
    numeric_data = df.select_dtypes(include=[np.number]).dropna()
    clustering_path = None
    if numeric_data.shape[1] >= 2:
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_data)
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(scaled_data)

        plt.figure(figsize=(10, 8))
        plt.scatter(scaled_data[:, 0], scaled_data[:, 1], c=clusters, cmap='viridis', s=50)
        plt.title('K-Means Clustering Visualization', fontsize=16)
        plt.xlabel(numeric_data.columns[0])
        plt.ylabel(numeric_data.columns[1])
        plt.colorbar(label='Cluster')
        clustering_path = 'clustering_visualization.png'
        plt.tight_layout()
        plt.savefig(clustering_path)
        plt.close()

    return correlation_path, clustering_path

def perform_statistical_analysis(df):
    """
    Perform statistical analyses including normality tests and outlier detection.
    """
    insights = []

    # Normality test for numeric columns
    numeric_data = df.select_dtypes(include=[np.number])
    for column in numeric_data.columns:
        stat, p_value = normaltest(numeric_data[column].dropna())
        if p_value < 0.05:
            insights.append(f"Column '{column}' does not follow a normal distribution (p={p_value:.3f}).")
        else:
            insights.append(f"Column '{column}' follows a normal distribution (p={p_value:.3f}).")

    # Outlier detection summary
    outlier_counts = (np.abs((numeric_data - numeric_data.mean()) / numeric_data.std()) > 3).sum()
    for column, count in outlier_counts.items():
        if count > 0:
            insights.append(f"Column '{column}' has {count} outlier(s).")

    return insights

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python enhanced_autolysis.py <path_to_csv_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        sys.exit(1)

    # Load the dataset
    df = pd.read_csv(file_path)

    # Create visualizations
    correlation_path, clustering_path = create_visualizations(df)

    # Perform analysis
    analysis = {
        'rows': len(df),
        'columns': len(df.columns),
        'column_names': df.columns.tolist(),
        'summary_statistics': df.describe().to_string()
    }

    # Perform statistical analysis
    insights = perform_statistical_analysis(df)
    key_insights = "\n".join(insights)

    # Images dictionary for the story
    images = {
        'correlation': correlation_path,
        'clustering': clustering_path if clustering_path else "N/A"
    }

    # Generate the LLM story
    story = generate_llm_story(analysis, images, key_insights)

    # Generate README content
    readme_content = f"""# Data Analysis Report

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Story of the Analysis
{story}

## Visualizations
- ![Correlation Heatmap]({correlation_path})
- {f'![Clustering Visualization]({clustering_path})' if clustering_path else 'Clustering visualization not generated.'}

## Notes
- For detailed data and visualizations, please refer to the files generated.
"""

    # Save README
    readme_path = 'README.md'
    with open(readme_path, 'w') as f:
        f.write(readme_content)

    print("Generated files:")
    print("- correlation_heatmap.png")
    if clustering_path:
        print("- clustering_visualization.png")
    print("- README.md")
