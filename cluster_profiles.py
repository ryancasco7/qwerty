import streamlit as st
import plotly.graph_objects as go
from utils import get_domain_names, get_cluster_interpretation


def show_cluster_profiles(df):
    st.header("🔍 Cluster Profiles & Analysis")
    
    if 'selected_cluster' not in st.session_state:
        st.session_state.selected_cluster = sorted(df['Cluster'].unique())[0]
    
    st.markdown("**Select Cluster:**")
    clusters = sorted(df['Cluster'].unique())
    cols = st.columns(len(clusters))
    
    for i, cluster in enumerate(clusters):
        with cols[i]:
            if st.button(
                f"Cluster {cluster}",
                key=f"cluster_btn_{cluster}",
                use_container_width=True,
                type="primary" if st.session_state.selected_cluster == cluster else "secondary"
            ):
                st.session_state.selected_cluster = cluster
                st.rerun()
    
    selected_cluster = st.session_state.selected_cluster
    cluster_data = df[df['Cluster'] == selected_cluster]
    
    st.markdown("---")
    
    st.subheader(f"Cluster {selected_cluster} Profile")
    
    interpretation = get_cluster_interpretation(selected_cluster)
    st.info(f"**Cluster {selected_cluster} Interpretation:** {interpretation}")
    
    st.markdown("**Key Characteristics:**")
    competency_cols = [col for col in cluster_data.columns if col.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.'))]
    if competency_cols:
        avg_rating = cluster_data[competency_cols].mean().mean()
        st.write(f"**Avg Training Need Rating:** {avg_rating:.2f}")
    
    st.divider()
    
    st.metric("Participants", len(cluster_data))
    
    st.divider()
    
    st.subheader("Training Needs Analysis by Domain")
    
    competency_cols = [col for col in cluster_data.columns if col.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.'))]
    if len(competency_cols) > 0:
        st.markdown("**Key Competency Highlights:**")
        top_needs = cluster_data[competency_cols].mean().sort_values(ascending=False).head(5)
        st.write("**Highest Training Needs (Top 5):**")
        for comp, rating in top_needs.items():
            comp_name = comp.split('. ', 1)[1] if '. ' in comp else comp
            if rating >= 4.0:
                st.error(f"- {comp_name}: {rating:.2f} (High/Urgent Need)")
            elif rating >= 3.0:
                st.warning(f"- {comp_name}: {rating:.2f} (Moderate Need)")
            else:
                st.info(f"- {comp_name}: {rating:.2f} (Low Need)")
    
    st.divider()
    
    domain_mapping = {}
    for col in df.columns:
        if col.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.')):
            domain_num = col.split('.')[0]
            if domain_num not in domain_mapping:
                domain_mapping[domain_num] = []
            domain_mapping[domain_num].append(col)
    
    domain_avgs = {}
    for domain, cols in domain_mapping.items():
        cluster_avg = cluster_data[cols].mean().mean()
        overall_avg = df[cols].mean().mean()
        domain_avgs[domain] = {
            'cluster_avg': cluster_avg,
            'overall_avg': overall_avg,
            'gap': cluster_avg - overall_avg
        }
    
    domain_names = get_domain_names()
    domains = [domain_names.get(d, f"Domain {d}") for d in sorted(domain_mapping.keys(), key=int)]
    cluster_scores = [domain_avgs[d]['cluster_avg'] for d in sorted(domain_mapping.keys(), key=int)]
    overall_scores = [domain_avgs[d]['overall_avg'] for d in sorted(domain_mapping.keys(), key=int)]
    
    fig_domain = go.Figure()
    fig_domain.add_trace(go.Bar(
        name='Cluster Average',
        x=domains,
        y=cluster_scores,
        marker_color='#1E88E5'
    ))
    fig_domain.add_trace(go.Bar(
        name='Overall Average',
        x=domains,
        y=overall_scores,
        marker_color='#90CAF9'
    ))
    fig_domain.update_layout(
        title="Training Needs by Domain Comparison",
        xaxis_title="Competency Domain",
        yaxis_title="Average Training Need Rating (1=No Need, 5=Urgent Need)",
        barmode='group',
        yaxis=dict(range=[1, 5]),
        height=500,
        font=dict(size=12),
        title_font=dict(size=16, color='#0D47A1')
    )
    st.plotly_chart(fig_domain, use_container_width=True)
    
    st.caption("Rating Scale: 1=No Need, 2=Low Need, 3=Moderate Need, 4=High Need, 5=Urgent Need")
    
    st.subheader("Identified Training Needs")
    gaps = [(d, domain_avgs[d]['gap']) for d in sorted(domain_mapping.keys(), key=int)]
    gaps_sorted_high = sorted(gaps, key=lambda x: x[1], reverse=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔴 High Priority Areas")
        st.markdown("*(Above overall average)*")
        high_needs_count = 0
        for domain, gap in gaps_sorted_high:
            if gap > 0:
                avg_rating = domain_avgs[domain]['cluster_avg']
                domain_name = domain_names.get(domain, f"Domain {domain}")
                if avg_rating >= 4:
                    priority = "URGENT"
                    st.error(f"**{domain_name}**\n\n+{gap:.2f} above average | Rating: {avg_rating:.2f} - {priority}")
                elif avg_rating >= 3:
                    priority = "HIGH"
                    st.warning(f"**{domain_name}**\n\n+{gap:.2f} above average | Rating: {avg_rating:.2f} - {priority}")
                else:
                    st.info(f"**{domain_name}**\n\n+{gap:.2f} above average | Rating: {avg_rating:.2f}")
                high_needs_count += 1
                if high_needs_count >= 5:
                    break
        
        if high_needs_count == 0:
            st.success("✅ No areas above overall average. This cluster shows lower training needs.")
    
    with col2:
        st.markdown("#### 🟢 Lower Priority Areas")
        st.markdown("*(Below overall average)*")
        low_needs_count = 0
        for domain, gap in gaps_sorted_high[::-1]:
            if gap < 0:
                domain_name = domain_names.get(domain, f"Domain {domain}")
                avg_rating = domain_avgs[domain]['cluster_avg']
                st.success(f"**{domain_name}**\n\n{gap:.2f} below average | Rating: {avg_rating:.2f}")
                low_needs_count += 1
                if low_needs_count >= 3:
                    break

