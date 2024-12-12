# /// script
[tool.uv]
requires-python = ">=3.11"
dependencies = [
    "numpy",
    "pandas",
    "scikit-learn",
    "chardet",
    "requests",
    "seaborn",
    "matplotlib",
    "python-dotenv",
    "missingno",
]
# ///

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys
import requests
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from scipy.stats import zscore
import missingno as msno
import argparse
import chardet

# Set the AIPROXY_TOKEN environment variable if not already set
if "AIPROXY_TOKEN" not in os.environ:
    api_key = input("Please enter your OpenAI API key: ")
    os.environ["AIPROXY_TOKEN"] = api_key

api_key = os.environ["AIPROXY_TOKEN"]
API_BASE = "https://aiproxy.sanand.workers.dev/openai/v1"

# Function to detect file encoding
def detect_encoding(filename):
    with open(filename, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    
    # Handle UTF-16 without BOM
    if result['encoding'] == 'UTF-16' and not raw_data.startswith(b'\xff\xfe') and not raw_data.startswith(b'\xfe\xff'):
        result['encoding'] = 'utf-16'  # Assume UTF-16 if BOM is missing
        print("Warning: File is UTF-16 but lacks BOM. Using 'utf-16' encoding.")
    
    return result['encoding']

# Function to preprocess files with missing BOM (optional, adds BOM)
def add_bom_if_missing(filename):
    with open(filename, 'rb') as f:
        raw_data = f.read()
    if raw_data.startswith(b'\xff\xfe') or raw_data.startswith(b'\xfe\xff'):
        return filename  # BOM exists; no changes needed
    # Add BOM and save as a new file
    new_filename = filename.replace('.csv', '_with_bom.csv')
    with open(new_filename, 'wb') as f:
        f.write(b'\xff\xfe' + raw_data)
    print(f"BOM added to the file. Saved as {new_filename}.")
    return new_filename

def load_and_clean_data(filename):
    try:
        # Optionally add BOM if missing
        filename = add_bom_if_missing(filename)
        encoding = detect_encoding(filename)
        df = pd.read_csv(filename, encoding=encoding)

        # Drop rows with all NaN values
        df.dropna(axis=0, how='all', inplace=True)

        # Fill missing values in numeric columns with the mean of the column
        numeric_columns = df.select_dtypes(include='number')
        df[numeric_columns.columns] = numeric_columns.fillna(numeric_columns.mean())

        # Handle missing values in non-numeric columns (e.g., fill with 'Unknown')
        non_numeric_columns = df.select_dtypes(exclude='number')
        df[non_numeric_columns.columns] = non_numeric_columns.fillna('Unknown')

        return df

    except UnicodeDecodeError as e:
        print(f"Error: Could not decode the file. Ensure it is properly encoded. Details: {e}")
        sys.exit(1)

# Function to summarize the dataset
def summarize_data(df):
    summary = {
        'shape': df.shape,
        'columns': df.columns.tolist(),
        'types': df.dtypes.to_dict(),
        'descriptive_statistics': df.describe().to_dict(),
        'missing_values': df.isnull().sum().to_dict()
    }
    return summary

# Outlier detection function using Z-Score
def detect_outliers(df):
    numeric_df = df.select_dtypes(include=[np.number])
    z_scores = np.abs(zscore(numeric_df))
    outliers = (z_scores > 3).sum(axis=0)
    outlier_info = {
        column: int(count) for column, count in zip(numeric_df.columns, outliers)
    }
    return outlier_info

# Correlation analysis function
def correlation_analysis(df):
    numeric_df = df.select_dtypes(include='number')
    correlation_matrix = numeric_df.corr()
    return correlation_matrix.to_dict()

# Cluster analysis using KMeans
def perform_clustering(df, n_clusters=3):
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df.select_dtypes(include=[np.number]))
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['Cluster'] = kmeans.fit_predict(df_scaled)
    return df, kmeans

# PCA for dimensionality reduction (optional)
def perform_pca(df):
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df.select_dtypes(include=[np.number]))
    pca = PCA(n_components=2)
    pca_components = pca.fit_transform(df_scaled)
    df['PCA1'] = pca_components[:, 0]
    df['PCA2'] = pca_components[:, 1]
    return df

# Function to create visualizations
def create_visualizations(df):
    visualizations = []  # Initialize an empty list to store image paths

    # Visualization for missing data
    try:
        msno.matrix(df)
        missing_img = 'missing_data.png'
        plt.savefig(missing_img, dpi=100)  # Low resolution
        plt.close()
        visualizations.append(missing_img)
    except Exception as e:
        print(f"Failed to generate missing data visualization: {e}")

    # Correlation heatmap
    try:
        numeric_df = df.select_dtypes(include='number')
        if numeric_df.shape[1] > 1:
            plt.figure(figsize=(10, 6), constrained_layout=True)
            sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
            plt.title("Correlation Matrix")
            correlation_img = 'correlation_matrix.png'
            plt.savefig(correlation_img, dpi=100)  # Low resolution
            plt.close()
            visualizations.append(correlation_img)
    except Exception as e:
        print(f"Failed to generate correlation heatmap: {e}")

    # Cluster visualization (after performing PCA)
    try:
        if 'PCA1' in df.columns and 'Cluster' in df.columns:
            plt.figure(figsize=(8, 6), constrained_layout=True)
            sns.scatterplot(x='PCA1', y='PCA2', hue='Cluster', data=df, palette='Set1')
            plt.title("Cluster Analysis (PCA)")
            cluster_img = 'cluster_analysis.png'
            plt.savefig(cluster_img, dpi=100)  # Low resolution
            plt.close()
            visualizations.append(cluster_img)
    except Exception as e:
        print(f"Failed to generate cluster analysis visualization: {e}")

    return visualizations  # Always return the list, even if empty

# Main function
def main():
    parser = argparse.ArgumentParser(description="Automated Dataset Analysis")
    parser.add_argument("csv_filename", help="Path to the CSV file to analyze")
    args = parser.parse_args()

    df = load_and_clean_data(args.csv_filename)
    summary = summarize_data(df)
    outliers = detect_outliers(df)
    correlation_matrix = correlation_analysis(df)
    df, _ = perform_clustering(df)
    df = perform_pca(df)
    visualizations = create_visualizations(df)  # Capture visualizations here
    print("Analysis complete. Results saved in README.md.")

if __name__ == "__main__":
    main()
