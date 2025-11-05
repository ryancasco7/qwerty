"""
Utility functions for data loading and clustering
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import logging
import warnings
from config import (
    DATA_FILE, DOMAIN_NAMES, CLUSTER_INTERPRETATIONS,
    NUM_CLUSTERS, CLUSTER_RANDOM_STATE
)

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


def sanitize_df_for_arrow(df: pd.DataFrame) -> pd.DataFrame:
    """
    Try to coerce dataframe columns to Arrow-friendly dtypes.
    
    Args:
        df: DataFrame to sanitize
        
    Returns:
        Sanitized DataFrame
    """
    try:
        df = df.copy()
        for col in df.columns:
            try:
                if df[col].dtype == object:
                    s = df[col].astype(str).str.strip()
                    s_clean = s.str.replace(',', '', regex=False).str.replace('$', '', regex=False).str.replace('%', '', regex=False)
                    num = pd.to_numeric(s_clean, errors='coerce')
                    if num.notna().sum() >= max(1, int(0.5 * len(num))):
                        df[col] = num
                        continue
                    dt = pd.to_datetime(s, errors='coerce')
                    if dt.notna().sum() >= max(1, int(0.5 * len(dt))):
                        df[col] = dt
                        continue
                if pd.api.types.is_float_dtype(df[col].dtype):
                    non_null = df[col].dropna()
                    if not non_null.empty:
                        try:
                            if (non_null % 1 == 0).all():
                                df[col] = df[col].astype('Int64')
                        except Exception:
                            pass
            except Exception as e:
                logger.warning(f"Error processing column {col}: {e}")
                continue
        
        if 'Total' in df.columns and df['Total'].dtype == object:
            try:
                tot = pd.to_numeric(df['Total'].astype(str).str.replace(',', '', regex=False), errors='coerce')
                if tot.notna().any():
                    df['Total'] = tot.astype('Int64')
            except Exception as e:
                logger.warning(f"Error processing Total column: {e}")
        
        return df
    except Exception as e:
        logger.error(f"Error sanitizing DataFrame: {e}")
        return df


def get_domain_names() -> dict:
    """
    Returns mapping of domain numbers to domain names.
    
    Returns:
        Dictionary mapping domain numbers to names
    """
    return DOMAIN_NAMES.copy()


def get_cluster_interpretation(cluster_id: int) -> str:
    """
    Returns the interpretation/description for each cluster.
    
    Args:
        cluster_id: Cluster ID (0-3)
        
    Returns:
        Cluster interpretation string
    """
    return CLUSTER_INTERPRETATIONS.get(cluster_id, "Cluster interpretation not available.")


@st.cache_data
def load_data():
    """
    Load the clustering results data with error handling.
    
    Returns:
        DataFrame or None if error
    """
    try:
        if not os.path.exists(DATA_FILE):
            logger.error(f"Data file not found: {DATA_FILE}")
            st.error(f"❌ Error: '{DATA_FILE}' file not found. Please ensure the file is in the same directory as this script.")
            return None
        
        df = pd.read_excel(DATA_FILE)
        
        if df.empty:
            logger.error("Data file is empty")
            st.error("❌ Error: Data file is empty.")
            return None
        
        # Validate required columns
        required_cols = ['Cluster']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            st.error(f"❌ Error: Data file is missing required columns: {', '.join(missing_cols)}")
            return None
        
        try:
            df = sanitize_df_for_arrow(df)
        except Exception as e:
            logger.warning(f"Error sanitizing data: {e}")
        
        logger.info(f"Data loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        return df
        
    except FileNotFoundError:
        logger.error(f"File not found: {DATA_FILE}")
        st.error(f"❌ Error: '{DATA_FILE}' file not found. Please ensure the file is in the same directory as this script.")
        return None
    except pd.errors.EmptyDataError:
        logger.error("Data file is empty")
        st.error("❌ Error: Data file is empty.")
        return None
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        st.error(f"❌ Error loading data: {str(e)}. Please check the file format and try again.")
        return None


@st.cache_resource
def get_clustering_model(df):
    """
    Create and cache the KMeans clustering model.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Tuple of (kmeans_model, scaler, feature_list)
    """
    try:
        competency_cols = [col for col in df.columns if col.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.'))]
        
        if not competency_cols:
            logger.warning("No competency columns found")
        
        # Use only competency columns for clustering
        features = competency_cols
        
        # Validate features exist
        missing_features = [f for f in features if f not in df.columns]
        if missing_features:
            logger.error(f"Missing features: {missing_features}")
            raise ValueError(f"Missing required features: {missing_features}")
        
        X = df[features].copy()
        
        # Handle missing values
        X = X.fillna(X.mean(numeric_only=True))
        
        if X.empty:
            raise ValueError("Feature matrix is empty after preprocessing")
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        kmeans = KMeans(n_clusters=NUM_CLUSTERS, init='k-means++', random_state=CLUSTER_RANDOM_STATE, n_init=10)
        kmeans.fit(X_scaled)
        
        logger.info(f"Clustering model created successfully with {NUM_CLUSTERS} clusters")
        return kmeans, scaler, features
        
    except Exception as e:
        logger.error(f"Error creating clustering model: {e}")
        raise


def predict_cluster(new_data: dict, kmeans, scaler, features: list) -> int:
    """
    Predict cluster for new assessment data with validation.
    
    Args:
        new_data: Dictionary of assessment data
        kmeans: Trained KMeans model
        scaler: Trained StandardScaler
        features: List of feature names
        
    Returns:
        Predicted cluster ID
    """
    try:
        feature_dict = {}
        for feature in features:
            if feature in new_data:
                value = new_data[feature]
                # Validate numeric values
                try:
                    value = float(value)
                    # Ensure rating values are within valid range
                    if isinstance(value, (int, float)):
                        value = max(1, min(5, value))  # Rating scale is 1-5
                except (ValueError, TypeError):
                    logger.warning(f"Invalid value for {feature}: {value}")
                    value = 3  # Default rating
                feature_dict[feature] = value
            else:
                # Default value for missing competency features
                feature_dict[feature] = 3  # Default rating (middle of scale)
        
        X_new = pd.DataFrame([feature_dict])[features]
        
        # Handle missing values
        X_new = X_new.fillna(X_new.mean(numeric_only=True))
        
        X_new_scaled = scaler.transform(X_new)
        cluster = kmeans.predict(X_new_scaled)[0]
        
        logger.info(f"Cluster prediction successful: Cluster {cluster}")
        return cluster
        
    except Exception as e:
        logger.error(f"Error predicting cluster: {e}")
        raise
