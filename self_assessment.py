"""
Self Assessment module with improved validation
"""
import streamlit as st
import numpy as np
import logging
from datetime import datetime
from utils import get_domain_names, get_clustering_model, predict_cluster, get_cluster_interpretation
from config import (
    MIN_RATING, MAX_RATING
)

logger = logging.getLogger(__name__)


def show_self_assessment(df):
    """Display self assessment form and results"""
    # Mobile responsive styling
    st.markdown("""
        <style>
        /* Mobile responsive radio buttons */
        @media (max-width: 768px) {
            .stRadio > div {
                flex-direction: column !important;
            }
            
            .stRadio > div > label {
                margin-bottom: 0.5rem;
                padding: 0.75rem;
                min-height: 44px;
                display: flex;
                align-items: center;
            }
        }
        
        /* Touch-friendly form elements */
        .stButton > button {
            min-height: 44px;
            font-size: 1rem;
        }
        
        /* Word wrapping for long text */
        .stMarkdown {
            word-wrap: break-word;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("## 📝 Self Assessment")
    st.markdown("Complete this assessment to find your cluster assignment and receive personalized training recommendations.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        competency_cols = [col for col in df.columns if col.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.'))]
        
        if not competency_cols:
            st.error("Error: No competency columns found in the dataset.")
            return
        
        domain_mapping = {}
        for col in competency_cols:
            domain_num = col.split('.')[0]
            if domain_num not in domain_mapping:
                domain_mapping[domain_num] = []
            domain_mapping[domain_num].append(col)
        
        domain_names = get_domain_names()
        
        if 'assessment_submitted' not in st.session_state:
            st.session_state.assessment_submitted = False
            st.session_state.assessment_data = {}
        
        with st.form("self_assessment_form"):
            st.markdown("#### Training Needs Assessment")
            st.info("**📊 Rating Scale:** 1 = No Need | 2 = Low Need | 3 = Moderate Need | 4 = High Need | 5 = Urgent Need")
            st.markdown("<br>", unsafe_allow_html=True)
            
            ratings = {}
            
            for domain_num in sorted(domain_mapping.keys(), key=int):
                domain_cols_list = sorted(domain_mapping[domain_num])
                domain_name = domain_names.get(domain_num, f"Domain {domain_num}")
                
                with st.expander(f"📚 {domain_num}. {domain_name}", expanded=True):
                    for comp_col in domain_cols_list:
                        comp_name = comp_col.split('. ', 1)[1] if '. ' in comp_col else comp_col
                        
                        st.markdown(f"**{comp_name}**")
                        
                        # Use horizontal layout on desktop, vertical on mobile
                        rating = st.radio(
                            f"Rate: {comp_name}",
                            options=list(range(MIN_RATING, MAX_RATING + 1)),
                            index=0,
                            key=f"form_{comp_col}",
                            horizontal=True,
                            label_visibility="collapsed"
                        )
                        ratings[comp_col] = rating
                        st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button("Submit Assessment", type="primary")
            
            if submitted:
                assessment_data = {
                    'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                assessment_data.update(ratings)
                
                st.session_state.assessment_data = assessment_data
                st.session_state.assessment_submitted = True
                
                st.rerun()
        
    except Exception as e:
        logger.error(f"Error in self assessment form: {e}")
        st.error(f"An error occurred while loading the assessment form: {str(e)}")
        return
    
    if st.session_state.assessment_submitted and st.session_state.assessment_data:
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🔄 Start New Assessment"):
                st.session_state.assessment_submitted = False
                st.session_state.assessment_data = {}
                st.rerun()
        
        assessment_data = st.session_state.assessment_data.copy()
        
        kmeans, scaler, features = get_clustering_model(df)
        
        try:
            cluster = predict_cluster(assessment_data, kmeans, scaler, features)
            assessment_data['Cluster'] = cluster
            
            st.success("✅ Assessment submitted successfully!")
            st.divider()
            
            st.subheader(f"📊 Your Cluster Assignment: **Cluster {cluster}**")
            interpretation = get_cluster_interpretation(cluster)
            st.info(f"**Cluster {cluster} Profile:** {interpretation}")
            
            st.divider()
            
            st.subheader("🎯 Your Training Recommendations")
            
            recommendations = []
            
            for domain_num in sorted(domain_mapping.keys(), key=int):
                domain_cols_list = domain_mapping[domain_num]
                domain_ratings = [assessment_data[col] for col in domain_cols_list]
                domain_avg = np.mean(domain_ratings)
                overall_avg = df[domain_cols_list].mean().mean()
                gap = domain_avg - overall_avg
                
                if domain_avg >= 3.5 or gap > 0.3:
                    if domain_avg >= 4.5:
                        priority = 'URGENT'
                    elif domain_avg >= 4.0:
                        priority = 'HIGH'
                    elif domain_avg >= 3.5 or gap > 0.5:
                        priority = 'MEDIUM'
                    else:
                        priority = 'LOW'
                    
                    recommendations.append({
                        'domain': domain_num,
                        'name': domain_names.get(domain_num, f"Domain {domain_num}"),
                        'avg_rating': domain_avg,
                        'gap': gap,
                        'priority': priority
                    })
            
            if recommendations:
                priority_order = {'URGENT': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
                recommendations.sort(key=lambda x: (priority_order.get(x['priority'], 0), x['avg_rating']), reverse=True)
                
                for i, rec in enumerate(recommendations, 1):
                    if rec['priority'] == 'URGENT':
                        st.error(f"**{i}. {rec['name']}** - Priority: {rec['priority']} (Avg Rating: {rec['avg_rating']:.2f})")
                    elif rec['priority'] == 'HIGH':
                        st.warning(f"**{i}. {rec['name']}** - Priority: {rec['priority']} (Avg Rating: {rec['avg_rating']:.2f})")
                    else:
                        st.info(f"**{i}. {rec['name']}** - Priority: {rec['priority']} (Avg Rating: {rec['avg_rating']:.2f})")
                    
                    st.write(f"   - Your average rating: {rec['avg_rating']:.2f}")
                    st.write(f"   - Gap from overall average: {rec['gap']:.2f}")
                    st.write("")
            else:
                st.info("No significant training needs identified based on your assessment. Your ratings suggest you have lower training needs compared to the overall average.")
            
        except Exception as e:
            st.error(f"Error predicting cluster: {e}")
            st.write("Please check your inputs and try again.")

