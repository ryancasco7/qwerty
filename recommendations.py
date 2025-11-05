import streamlit as st
from utils import get_domain_names, get_cluster_interpretation


def show_recommendations(df):
    st.markdown("## 🎯 Training Program Recommendations")
    st.markdown("<br>", unsafe_allow_html=True)
    
    domain_names = get_domain_names()
    
    if 'selected_cluster_rec' not in st.session_state:
        st.session_state.selected_cluster_rec = sorted(df['Cluster'].unique())[0]
    
    st.markdown("**Select Cluster:**")
    clusters = sorted(df['Cluster'].unique())
    cols = st.columns(len(clusters))
    
    for i, cluster in enumerate(clusters):
        with cols[i]:
            if st.button(
                f"Cluster {cluster}",
                key=f"cluster_rec_btn_{cluster}",
                use_container_width=True,
                type="primary" if st.session_state.selected_cluster_rec == cluster else "secondary"
            ):
                st.session_state.selected_cluster_rec = cluster
                st.rerun()
    
    selected_cluster = st.session_state.selected_cluster_rec
    cluster_data = df[df['Cluster'] == selected_cluster]
    
    st.markdown("---")
    
    interpretation = get_cluster_interpretation(selected_cluster)
    st.info(f"**Cluster {selected_cluster} Profile:** {interpretation}")
    st.divider()
    
    domain_mapping = {}
    for col in df.columns:
        if col.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.')):
            domain_num = col.split('.')[0]
            if domain_num not in domain_mapping:
                domain_mapping[domain_num] = []
            domain_mapping[domain_num].append(col)
    
    recommendations = []
    for domain, cols in sorted(domain_mapping.items(), key=lambda x: int(x[0])):
        cluster_avg = cluster_data[cols].mean().mean()
        overall_avg = df[cols].mean().mean()
        gap = cluster_avg - overall_avg
        
        if gap > 0.3 or cluster_avg >= 3.5:
            if cluster_avg >= 4.5:
                priority = 'URGENT'
            elif cluster_avg >= 4.0:
                priority = 'HIGH'
            elif cluster_avg >= 3.5 or gap > 0.5:
                priority = 'MEDIUM'
            else:
                priority = 'LOW'
            
            recommendations.append({
                'domain': domain,
                'name': domain_names.get(domain, f"Domain {domain}"),
                'cluster_avg': cluster_avg,
                'gap': gap,
                'priority': priority,
                'competencies': cols
            })
    
    if recommendations:
        st.markdown(f"### Recommended Training Programs for Cluster {selected_cluster}")
        st.caption("📋 Based on training need ratings: 1=No Need, 2=Low Need, 3=Moderate Need, 4=High Need, 5=Urgent Need")
        st.markdown("<br>", unsafe_allow_html=True)
        
        recommendations_sorted = sorted(recommendations, key=lambda x: (x['cluster_avg'], x['gap']), reverse=True)
        
        for i, rec in enumerate(recommendations_sorted, 1):
            with st.expander(f"{i}. {rec['name']} - Priority: {rec['priority']} (Rating: {rec['cluster_avg']:.2f})", expanded=(i <= 3)):
                st.write(f"**Average Training Need Rating:** {rec['cluster_avg']:.2f}")
                st.write(f"**Gap vs Overall Average:** {rec['gap']:.2f} (Higher = More Need)")
                st.write(f"**Recommended Focus Areas:**")
                
                comp_needs = []
                for col in rec['competencies']:
                    cluster_avg = cluster_data[col].mean()
                    overall_avg = df[col].mean()
                    comp_needs.append((col, cluster_avg, cluster_avg - overall_avg))
                
                comp_needs_sorted = sorted(comp_needs, key=lambda x: x[1], reverse=True)
                for comp, comp_avg, gap_val in comp_needs_sorted[:5]:
                    if comp_avg >= 3.0:
                        comp_name = comp.split('. ', 1)[1] if '. ' in comp else comp
                        if comp_avg >= 4.5:
                            need_level = "URGENT"
                            st.error(f"- {comp_name} (Rating: {comp_avg:.2f} - {need_level})")
                        elif comp_avg >= 4.0:
                            need_level = "HIGH"
                            st.warning(f"- {comp_name} (Rating: {comp_avg:.2f} - {need_level})")
                        else:
                            need_level = "MODERATE"
                            st.info(f"- {comp_name} (Rating: {comp_avg:.2f} - {need_level})")
                
                st.write("**Suggested Training Programs:**")
                if rec['domain'] == '1':
                    st.write("- Inquiry-Based Learning Workshop")
                    st.write("- Project-Based Learning Implementation")
                    st.write("- Contextualized Teaching Strategies")
                elif rec['domain'] == '2':
                    st.write("- Classroom Management Techniques")
                    st.write("- Positive Behavior Support Systems")
                    st.write("- Time Management Strategies")
                elif rec['domain'] == '5':
                    st.write("- Digital Literacy Training")
                    st.write("- LMS Implementation Workshop")
                    st.write("- Blended Learning Strategies")
                else:
                    st.write(f"- Training program for {rec['name']}")
                    st.write("- Skill development workshops")
                    st.write("- Hands-on practice sessions")
    else:
        st.info("No significant training needs identified for this cluster. This group reports lower training needs compared to the overall average.")

