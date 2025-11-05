import streamlit as st
import pandas as pd


def show_admin_tools(df):
    st.markdown("## ⚙️ Administrative Tools")
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["Data Management", "Export Visualizations", "Data Statistics"])
    
    with tab1:
        st.subheader("Dataset Information")
        st.write(f"**Total Records:** {len(df)}")
        st.write(f"**Total Features:** {len(df.columns)}")
        st.write(f"**Clusters:** {df['Cluster'].nunique()}")
        
        st.divider()
        
        st.subheader("Preview Data")
        num_rows = st.number_input("Number of rows to display", min_value=1, max_value=100, value=10, key="admin_rows")
        st.dataframe(df.head(num_rows), use_container_width=True)
        
        st.subheader("Download Data")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="clustering_results.csv",
            mime="text/csv",
            key="download_main_csv"
        )
    
    with tab2:
        st.subheader("Export Visualizations")
        
        export_format = st.selectbox("Export Format", ["PNG", "PDF", "HTML"], key="export_format_select")
        
        if st.button("Generate All Visualizations", key="generate_viz_btn"):
            st.info("📊 Visualization export feature - implementation in progress")
            st.write("This feature will allow you to export:")
            st.write("- Cluster distribution charts")
            st.write("- PCA visualizations")
            st.write("- Domain comparison graphs")
            st.write("- Training needs heatmaps")
    
    with tab3:
        st.subheader("Detailed Statistics")
        
        st.write("**Cluster Distribution:**")
        cluster_stats = pd.DataFrame({
            'Cluster': df['Cluster'].value_counts().sort_index(),
            'Percentage': (df['Cluster'].value_counts(normalize=True).sort_index() * 100).round(2)
        })
        st.dataframe(cluster_stats, use_container_width=True)
        
        st.divider()
        
        st.write("**Missing Values Check:**")
        missing = df.isnull().sum()
        if missing.sum() > 0:
            st.dataframe(missing[missing > 0], use_container_width=True)
        else:
            st.success("✅ No missing values in the dataset!")
        
        st.divider()
        
        st.write("**Competency Ratings Summary:**")
        competency_cols = [col for col in df.columns if col.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.'))]
        if competency_cols:
            comp_stats = df[competency_cols].describe().round(2)
            st.dataframe(comp_stats, use_container_width=True)

