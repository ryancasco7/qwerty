import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from utils import get_cluster_interpretation


def show_dashboard(df):
    st.header("📈 Overview Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Participants", len(df))
    
    with col2:
        st.metric("Number of Clusters", df['Cluster'].nunique())
    
    st.divider()
    
    st.markdown('<h2 style="color: #0D47A1; margin-bottom: 1.5rem; text-align: center; word-wrap: break-word;">📋 Cluster Interpretations</h2>', unsafe_allow_html=True)
    
    # Enhanced styling for cluster interpretations with mobile responsiveness
    st.markdown("""
        <style>
        .cluster-card {
            background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-left: 5px solid;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .cluster-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.15);
        }
        
        .cluster-card::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 100px;
            height: 100px;
            background: radial-gradient(circle, rgba(0,0,0,0.03) 0%, transparent 70%);
            border-radius: 50%;
            transform: translate(30px, -30px);
        }
        
        .cluster-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid rgba(0,0,0,0.05);
            flex-wrap: wrap;
        }
        
        .cluster-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            flex-wrap: wrap;
        }
        
        .cluster-badge {
            display: inline-block;
            padding: 0.35rem 0.85rem;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-left: 0.5rem;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        
        .cluster-profile {
            font-size: 1.1rem;
            font-weight: 600;
            color: #424242;
            margin-bottom: 0.75rem;
            padding: 0.5rem 0;
            word-wrap: break-word;
        }
        
        .cluster-description {
            font-size: 1rem;
            line-height: 1.8;
            color: #555;
            text-align: justify;
            padding: 0.5rem 0;
            word-wrap: break-word;
        }
        
        .cluster-0 { border-left-color: #4CAF50; }
        .cluster-0 .cluster-badge { background: #4CAF50; color: white; }
        
        .cluster-1 { border-left-color: #2196F3; }
        .cluster-1 .cluster-badge { background: #2196F3; color: white; }
        
        .cluster-2 { border-left-color: #FF9800; }
        .cluster-2 .cluster-badge { background: #FF9800; color: white; }
        
        .cluster-icon {
            font-size: 2rem;
            margin-right: 0.5rem;
        }
        
        /* Mobile responsive */
        @media (max-width: 768px) {
            .cluster-card {
                padding: 1rem;
                border-radius: 12px;
            }
            
            .cluster-title {
                font-size: 1.25rem;
            }
            
            .cluster-profile {
                font-size: 1rem;
            }
            
            .cluster-description {
                font-size: 0.9rem;
                line-height: 1.6;
            }
            
            .cluster-icon {
                font-size: 1.5rem;
            }
            
            .cluster-header {
                flex-direction: column;
                align-items: flex-start;
            }
        }
        
        @media (max-width: 480px) {
            .cluster-card {
                padding: 0.75rem;
            }
            
            .cluster-title {
                font-size: 1.1rem;
            }
            
            .cluster-badge {
                font-size: 0.75rem;
                padding: 0.25rem 0.5rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)
    
    cluster_counts = df['Cluster'].value_counts().sort_index()
    cluster_icons = {
        0: "🌟",
        1: "📚",
        2: "🔧"
    }
    
    cluster_colors = {
        0: ("#4CAF50", "High Engagement - Active Users"),
        1: ("#2196F3", "Moderate - Neutral Stance"),
        2: ("#FF9800", "Low Engagement - Traditional Methods")
    }
    
    # Display clusters in a grid layout
    clusters = sorted(df['Cluster'].unique())
    
    for cluster_id in clusters:
        cluster_size = cluster_counts[cluster_id]
        interpretation = get_cluster_interpretation(cluster_id)
        icon = cluster_icons.get(cluster_id, "📊")
        color, tag = cluster_colors.get(cluster_id, ("#666", "Cluster"))
        
        # Extract profile title from interpretation
        if "**" in interpretation and ":" in interpretation:
            # Format: **Title**: Description
            parts = interpretation.split("**", 2)
            if len(parts) >= 3:
                profile_title = parts[1].strip()
                description = parts[2].replace(":", "").strip()
            else:
                profile_title = "Cluster Profile"
                description = interpretation.replace("**", "").strip()
        elif ":" in interpretation:
            profile_title = interpretation.split(":")[0].replace("**", "").strip()
            description = interpretation.split(":", 1)[1].replace("**", "").strip()
        else:
            profile_title = "Cluster Profile"
            description = interpretation.replace("**", "").strip()
        
        st.markdown(f'''
            <div class="cluster-card cluster-{cluster_id}">
                <div class="cluster-header">
                    <div>
                        <h3 class="cluster-title">
                            <span class="cluster-icon">{icon}</span>
                            Cluster {cluster_id}
                            <span class="cluster-badge">n={cluster_size}</span>
                        </h3>
                    </div>
                    <div style="font-size: 0.9rem; color: #666; font-weight: 500;">{tag}</div>
                </div>
                <div class="cluster-profile">Profile: {profile_title}</div>
                <div class="cluster-description">{description}</div>
            </div>
        ''', unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Cluster Distribution")
        cluster_counts = df['Cluster'].value_counts().sort_index()
        fig_pie = px.pie(
            values=cluster_counts.values,
            names=[f"Cluster {i}" for i in cluster_counts.index],
            title="Participants per Cluster"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("Cluster Size Comparison")
        fig_bar = px.bar(
            x=[f"Cluster {i}" for i in cluster_counts.index],
            y=cluster_counts.values,
            title="Number of Participants per Cluster",
            labels={"x": "Cluster", "y": "Count"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    st.subheader("Cluster Visualization (PCA)")
    if st.checkbox("Show PCA Visualization"):
        feature_cols = [col for col in df.columns if col not in ['Cluster']]
        
        if len(feature_cols) > 0:
            X = df[feature_cols].values
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            pca = PCA(n_components=2)
            principal_components = pca.fit_transform(X_scaled)
            
            pca_df = pd.DataFrame(
                principal_components,
                columns=['PC1', 'PC2']
            )
            pca_df['Cluster'] = df['Cluster'].values
            
            fig_scatter = px.scatter(
                pca_df,
                x='PC1',
                y='PC2',
                color='Cluster',
                color_discrete_sequence=['#4CAF50', '#2196F3', '#FF9800'],
                title="2D PCA Visualization of Clusters",
                labels={"PC1": f"Principal Component 1 ({pca.explained_variance_ratio_[0]:.2%})",
                       "PC2": f"Principal Component 2 ({pca.explained_variance_ratio_[1]:.2%})"}
            )
            fig_scatter.update_layout(
                font=dict(size=12),
                title_font=dict(size=16, color='#0D47A1')
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            st.info(f"PCA explains {sum(pca.explained_variance_ratio_):.2%} of the variance")