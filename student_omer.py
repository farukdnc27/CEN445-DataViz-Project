import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def run_omer_module(df):
    """
    Ömer Faruk Dinçoğlu'nun grafiklerini çizen ana fonksiyon.
    """
    st.header("Ömer Faruk Dinçoğlu's Analysis")
    st.markdown("""
    This section analyzes **Price Distribution**, **Market Hierarchy**, and **Feature Correlations** with interactive controls.
    """)
    
    st.divider()

    # --- GRAFİK 1: Fiyat Dağılım Analizi (Histogram) ---
    st.subheader("1. Price Distribution Analysis (Histogram)")
    st.info("""
    **Key Questions:**
    - How is the price distribution in New York? Are there variations at different price points?
    - What is the most common price range for Airbnb listings?
    - Are there significant outliers in pricing, and where do most listings fall?
    - How does the distribution change when filtering by room type or borough?
    """)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("**Chart Controls**")
        max_price_filter = st.slider("Max Price Filter ($)", 100, 2000, 500, step=50)
        bin_count = st.slider("Number of Bins", 10, 200, 50, help="Adjust to see general trends (low) or detailed variations (high).")
        use_log_scale = st.checkbox("Use Logarithmic Scale", help="Useful for visualizing data with a wide range of values.")
        
        
        st.markdown("**Additional Filters**")
        room_types_hist = st.multiselect(
            "Room Type:",
            options=df['room_type'].unique().tolist(),
            default=df['room_type'].unique().tolist(),
            key="hist_room",
            help="Compare price distributions across different room types"
        )
        
        selected_boroughs_hist = st.multiselect(
            "Borough:",
            options=df['neighbourhood_group'].unique().tolist(),
            default=df['neighbourhood_group'].unique().tolist(),
            key="hist_borough",
            help="Analyze price distribution by borough"
        )
        
        price_percentile = st.slider(
            "Show Top X% by Price:",
            min_value=50,
            max_value=100,
            value=100,
            step=5,
            key="hist_percentile",
            help="Filter outliers to see common price ranges"
        )

    with col2:
        # Percentile hesapla
        price_cutoff = df['price'].quantile(price_percentile / 100)
        
        df_hist = df[
            (df['price'] <= min(max_price_filter, price_cutoff)) &
            (df['room_type'].isin(room_types_hist)) &
            (df['neighbourhood_group'].isin(selected_boroughs_hist))
        ]
        
        if df_hist.empty:
            st.warning(" No data matches the selected filters. Please adjust.")
        else:
            color_seq = ['#636EFA']
        
            fig_hist = px.histogram(
                df_hist, 
                x="price", 
                nbins=bin_count, 
                log_y=use_log_scale, 
                title=f"Price Distribution for Listings under ${max_price_filter}",
                color_discrete_sequence=color_seq,
                opacity=0.8
            )
            
            fig_hist.update_layout(
                xaxis_title="Price ($)", 
                yaxis_title="Listing Count (Log Scale)" if use_log_scale else "Listing Count",
                bargap=0.1
            )
            
            
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            col_stat1.metric("Total Listings", f"{len(df_hist):,}")
            col_stat2.metric("Average Price", f"${df_hist['price'].mean():.2f}")
            col_stat3.metric("Median Price", f"${df_hist['price'].median():.2f}")
            
            st.plotly_chart(fig_hist, use_container_width=True)

    st.divider()

    # --- GRAFİK 2: Pazar Hiyerarşisi (Treemap) ---
    st.subheader("2. Market Hierarchy (Treemap)")
    st.info("""
    **Key Questions:**
    - How do neighborhoods compare in terms of volume vs. value?
    - Which boroughs have the highest concentration of listings?
    - What are the most expensive neighborhoods within each borough?
    - How does market share distribute across different areas of NYC?
    """)

    col3, col4 = st.columns([1, 3])

    with col3:
        st.markdown("**Chart Controls**")
        size_metric = st.selectbox(
            "Size Rectangles By:",
            options=["Listing Count", "Average Price"],
            index=0,
            help="'Listing Count' shows popularity. 'Average Price' shows expensive areas."
        )
        
        color_metric = st.selectbox(
            "Color Rectangles By:",
            options=["Neighbourhood Group (Categorical)", "Average Price (Sequential)"],
            index=0
        )
        
        
        st.markdown("**Additional Filters**")
        selected_boroughs = st.multiselect(
            "Select Boroughs:",
            options=df['neighbourhood_group'].unique().tolist(),
            default=df['neighbourhood_group'].unique().tolist(),
            key="tree_boroughs"
        )
        
        price_range_tree = st.slider(
            "Price Range ($):",
            min_value=int(df['price'].min()),
            max_value=int(df['price'].max()),
            value=(int(df['price'].min()), 500),
            key="tree_price",
            help="Filter by price to compare similar market segments"
        )
        
        room_type_tree = st.multiselect(
            "Room Type:",
            options=df['room_type'].unique().tolist(),
            default=df['room_type'].unique().tolist(),
            key="tree_room",
            help="Compare market hierarchy by room type"
        )
        
        min_listings_tree = st.slider(
            "Min Listings per Neighborhood:",
            min_value=1,
            max_value=50,
            value=5,
            help="Filter out small neighborhoods to focus on major markets",
            key="tree_min"
        )

    with col4:
        
        df_tree_filtered = df[
            (df['neighbourhood_group'].isin(selected_boroughs)) &
            (df['price'] >= price_range_tree[0]) &
            (df['price'] <= price_range_tree[1]) &
            (df['room_type'].isin(room_type_tree))
        ]
        
        if df_tree_filtered.empty:
            st.warning(" No data matches the selected filters. Please adjust.")
        else:
            if size_metric == "Listing Count":
                df_treemap = df_tree_filtered.groupby(['neighbourhood_group', 'neighbourhood']).size().reset_index(name='value')
                df_treemap['label_text'] = "Listings"
            else:
                df_treemap = df_tree_filtered.groupby(['neighbourhood_group', 'neighbourhood'])['price'].mean().reset_index(name='value')
                df_treemap['label_text'] = "Avg Price ($)"
            
            
            df_treemap = df_treemap[df_treemap['value'] >= min_listings_tree]
            
            if color_metric == "Neighbourhood Group (Categorical)":
                color_col = 'neighbourhood_group'
                color_scale = None
            else:
                if 'price' not in df_treemap.columns:
                    df_price = df.groupby(['neighbourhood_group', 'neighbourhood'])['price'].mean().reset_index()
                    df_treemap = pd.merge(df_treemap, df_price, on=['neighbourhood_group', 'neighbourhood'])
                color_col = 'price'
                color_scale = px.colors.sequential.Viridis

            fig_tree = px.treemap(
                df_treemap,
                path=[px.Constant("NYC"), 'neighbourhood_group', 'neighbourhood'],
                values='value',
                color=color_col,
                color_continuous_scale=color_scale,
                title=f"Market Hierarchy based on {size_metric}"
            )
            
            fig_tree.update_traces(hovertemplate='<b>%{label}</b><br>%{value}')
            fig_tree.update_layout(margin=dict(t=50, l=25, r=25, b=25))
            st.plotly_chart(fig_tree, use_container_width=True)

    st.divider()

    # --- GRAFİK 3: Korelasyon Isı Haritası (Correlation Heatmap) ---
    st.subheader("3. Feature Correlation Heatmap")
    st.info("""
    **Key Questions:**
    - How do numerical features (price, reviews, availability) correlate with each other?
    - Is there a relationship between price and number of reviews?
    - Do hosts with more listings charge different prices?
    - How does availability throughout the year relate to pricing and review patterns?
    """)

    col5, col6 = st.columns([1, 3])

    with col5:
        st.markdown("**Chart Controls**")
        
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        
        default_cols = ['price', 'number_of_reviews', 'reviews_per_month', 
                       'calculated_host_listings_count', 'availability_365', 'minimum_nights']
        default_cols = [col for col in default_cols if col in numeric_cols]
        
        selected_features = st.multiselect(
            "Select Features to Compare:",
            options=numeric_cols,
            default=default_cols[:6] if len(default_cols) >= 6 else default_cols,
            help="Choose at least 2 numerical features to see correlations."
        )
        
        color_scale_option = st.selectbox(
            "Color Scheme:",
            options=["RdBu_r", "Viridis", "Cividis", "Plasma"],
            index=0,
            help="'RdBu_r' highlights positive (red) and negative (blue) correlations."
        )
        
        show_values = st.checkbox("Show Correlation Values", value=True)
        
        
        st.markdown("**Additional Filters**")
        
        room_type_corr = st.multiselect(
            "Room Type:",
            options=df['room_type'].unique().tolist(),
            default=df['room_type'].unique().tolist(),
            key="heat_room",
            help="Analyze correlations within specific room types"
        )
        
        borough_corr = st.multiselect(
            "Borough:",
            options=df['neighbourhood_group'].unique().tolist(),
            default=df['neighbourhood_group'].unique().tolist(),
            key="heat_borough",
            help="Focus on specific boroughs for correlation analysis"
        )
        
        min_reviews_corr = st.slider(
            "Min Reviews:",
            min_value=0,
            max_value=100,
            value=0,
            step=5,
            help="Filter for established listings with review history",
            key="heat_reviews"
        )
        
        corr_threshold = st.slider(
            "Correlation Threshold:",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.1,
            help="Hide weak correlations below this absolute value",
            key="heat_threshold"
        )

    with col6:
        if len(selected_features) < 2:
            st.warning(" Please select at least 2 features to display correlations.")
        else:
            
            df_heat_filtered = df[
                (df['room_type'].isin(room_type_corr)) &
                (df['neighbourhood_group'].isin(borough_corr)) &
                (df['number_of_reviews'] >= min_reviews_corr)
            ]
            
            if df_heat_filtered.empty:
                st.warning(" No data matches the selected filters. Please adjust.")
            else:
                
                df_corr = df_heat_filtered[selected_features].corr()
                
                
                df_corr_display = df_corr.copy()
                mask = np.abs(df_corr_display) < corr_threshold
                df_corr_display[mask] = np.nan
            
                # Heatmap oluştur
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=df_corr_display.values,
                    x=df_corr_display.columns,
                    y=df_corr_display.columns,
                    colorscale=color_scale_option,
                    zmid=0,  
                    text=df_corr_display.values.round(2) if show_values else None,
                    texttemplate='%{text}' if show_values else None,
                    textfont={"size": 10},
                    colorbar=dict(title="Correlation")
                ))
                
                fig_heatmap.update_layout(
                    title="Correlation Matrix of Selected Features",
                    xaxis_title="Features",
                    yaxis_title="Features",
                    height=600,
                    xaxis={'side': 'bottom'},
                    yaxis={'autorange': 'reversed'}  
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
                
                
                st.markdown(f"**Dataset Stats:** {len(df_heat_filtered):,} listings analyzed")

    st.divider()