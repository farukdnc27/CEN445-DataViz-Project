import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def run_mehmet_module(df):
    st.header("Mehmet Dora's Analysis")
    st.markdown("""
    This section analyzes **Price vs Popularity**, **Multidimensional Feature Profiles**, 
    and **Category Flows** with interactive controls.
    """)
    st.divider()
    
    st.markdown("""
        <style>
        div[data-baseweb="tab-list"] {
            justify-content: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Navbar
    tab1, tab2, tab3 = st.tabs([
        "Price vs Popularity",
        "Multidimensional Profile",
        "Category Flow"
    ])
    
    # scatter plot
    with tab1:
        st.subheader("1. Price vs Popularity (Scatter Plot)")
        st.info("""
            **Related Questions:**
            - Do cheaper properties have higher review counts?
            - Does the number of reviews decrease as price increases?
            - Are some neighborhoods both expensive and popular?
            - Are there outliers? (For example, listings at $1000 with 0 reviews)
        """)    
        
        st.markdown("**Chart Data Filter**")
        col_f1, col_f2 = st.columns(2)
        
        with col_f1:
            selected_groups_scatter = st.multiselect(
                "Neighbourhood Group:",
                options=sorted(df['neighbourhood_group'].dropna().unique().tolist()),
                default=sorted(df['neighbourhood_group'].dropna().unique().tolist()),
                key="scatter_groups",
                help=(
                    "Select which neighborhoods to include in the scatter plot. "
                    "By removing certain neighbourhood_group values, you can focus on "
                    "the price-review relationship for specific areas."
                )
            )
        
        with col_f2:
            max_price_scatter = st.slider(
                "Max Price Filter ($)",
                min_value=50,
                max_value=int(min(2000, df['price'].max())),
                value=500,
                step=50,
                help=(
                    "This value determines the maximum price displayed in the chart. "
                    "Listings with prices above this threshold are filtered out. "
                    "Use this to exclude extremely expensive (outlier) listings."
                )
            )
        
        min_reviews_scatter = st.slider(
            "Min Reviews:",
            min_value=0,
            max_value=int(df['number_of_reviews'].max()),
            value=0,
            step=5,
            help=(
                "Sets the minimum number of reviews that listings must have to be displayed. "
                "Listings with fewer reviews than this value are filtered out. "
                "This allows you to focus on more popular listings."
            )
        )
        
        use_log_y = st.checkbox(
            "Use Log Scale for Reviews",
            value=False,
            help=(
                "Converts the Y-axis (review count) to a logarithmic scale. "
                "When some listings have very high and others have very low review counts, "
                "this makes the differences more readable. It doesn't change the data, "
                "only the axis scale."
            )
        )
        
        st.divider()
        
        df_scatter = df[
            (df['price'] <= max_price_scatter) &
            (df['number_of_reviews'] >= min_reviews_scatter) &
            (df['neighbourhood_group'].isin(selected_groups_scatter))
        ]
        
        if df_scatter.empty:
            st.warning("No data matches the selected filters. Please adjust the filters.")
        else:
            fig_scatter = px.scatter(
                df_scatter,
                x="price",
                y="number_of_reviews",
                color="neighbourhood_group",
                hover_data=["name", "room_type", "neighbourhood"],
                title=f"Price vs Number of Reviews (≤ ${max_price_scatter})",
                opacity=0.7,
            )
            fig_scatter.update_layout(
                xaxis_title="Price ($)",
                yaxis_title="Number of Reviews (log scale)" if use_log_y else "Number of Reviews",
                legend_title="Neighbourhood Group"
            )
            
            if use_log_y:
                fig_scatter.update_yaxes(type="log")
            
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Statistics
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            col_stat1.metric("Total Listings", f"{len(df_scatter):,}")
            col_stat2.metric("Avg Price", f"${df_scatter['price'].mean():.2f}")
            col_stat3.metric("Avg Reviews", f"{df_scatter['number_of_reviews'].mean():.2f}")
    
    # paralell coordinates
    with tab2:
        st.subheader("2. Multidimensional Feature Profile (Parallel Coordinates)")
        st.info("""
            **Related Questions:**
            - Entire home → generally expensive + high minimum nights?
            - Private room → cheap but highly available?
            - Shared room → low price but low review count?
            - Which room type has "heavy line clusters"?
        """)
        
        st.markdown("**Chart Data Filter**")
        col_f1, col_f2, col_f3 = st.columns(3)
        
        candidate_dims = [
            col for col in ["price", "minimum_nights", "availability_365", "number_of_reviews"]
            if col in df.columns
        ]
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        with col_f1:
            selected_dims = st.multiselect(
                "Select Dimensions:",
                options=numeric_cols,
                default=candidate_dims if len(candidate_dims) >= 3 else numeric_cols[:4],
                help=(
                    "Choose numerical columns to compare in the Parallel Coordinates chart.\n"
                    "- You must select at least **3 columns**.\n"
                    "- These form the vertical axes that the lines pass through.\n"
                    "- Example: price, minimum_nights, availability_365, number_of_reviews."
                )
            )
        
        with col_f2:
            selected_room_types_pc = st.multiselect(
                "Room Types:",
                options=sorted(df['room_type'].dropna().unique().tolist()),
                default=sorted(df['room_type'].dropna().unique().tolist()),
                key="pc_room_types",
                help=(
                    "Select which room types to display in the chart.\n"
                    "- Each room type is shown in a different color.\n"
                    "- Example: Entire home, Private room, Shared room.\n"
                    "This filter lets you examine the multidimensional profile of specific room types."
                )
            )
        
        with col_f3:
            max_rows_pc = st.slider(
                "Max Listings (sampling):",
                min_value=100,
                max_value=3000,
                value=1000,
                step=100,
                help=(
                    "Maximum number of listings displayed in the chart.\n"
                    "- Parallel Coordinates can become cluttered with too many lines.\n"
                    "- If data exceeds this number, random sampling is applied.\n"
                    "- Example: If data has 6000 records and you select 1000, "
                    "1000 random records will be shown."
                )
            )
        
        min_reviews_pc = st.slider(
            "Min Reviews:",
            min_value=0,
            max_value=int(df['number_of_reviews'].max()),
            value=0,
            step=5,
            key="pc_min_reviews",
            help=(
                "Minimum review count filter.\n"
                "- Listings with fewer reviews than this value are filtered out.\n"
                "- This lets you examine the multidimensional profile of more popular listings."
            )
        )
        
        st.divider()
        
        if len(selected_dims) < 3:
            st.warning("Please select at least 3 numerical dimensions.")
        else:
            df_pc = df[
                (df['room_type'].isin(selected_room_types_pc)) &
                (df['number_of_reviews'] >= min_reviews_pc)
            ]
            
            if df_pc.empty:
                st.warning("No data matches the selected filters. Please adjust the filters.")
            else:
                df_pc = df_pc[selected_dims + ["room_type"]].dropna()
                
                if len(df_pc) > max_rows_pc:
                    df_pc = df_pc.sample(n=max_rows_pc, random_state=42)
                
                unique_room_types = df_pc["room_type"].unique().tolist()
                room_type_map = {rt: i for i, rt in enumerate(unique_room_types)}
                df_pc["room_type_code"] = df_pc["room_type"].map(room_type_map)
                
                num_types = len(room_type_map)
                qualitative_colors = px.colors.qualitative.Set1
                color_scale = []
                
                for i, (rt, code) in enumerate(room_type_map.items()):
                    color = qualitative_colors[i % len(qualitative_colors)]
                    t0 = code / max(num_types - 1, 1)
                    t1 = code / max(num_types - 1, 1)
                    color_scale.append([t0, color])
                    color_scale.append([t1, color])
                
                fig_pc = go.Figure(
                    data=go.Parcoords(
                        line=dict(
                            color=df_pc["room_type_code"],
                            colorscale=color_scale,
                            cmin=0,
                            cmax=max(num_types - 1, 1),
                            showscale=False
                        ),
                        dimensions=[
                            dict(
                                label=dim.replace("_", " ").title(),
                                values=df_pc[dim]
                            )
                            for dim in selected_dims
                        ]
                    )
                )
                
                fig_pc.update_layout(
                    margin=dict(l=80, r=80, t=60, b=50)
                )
                fig_pc.update_traces(
                    labelfont=dict(size=12),
                    rangefont=dict(size=10),
                    tickfont=dict(size=10),
                )
                
                legend_items = []
                for i, (rt, code) in enumerate(room_type_map.items()):
                    color = qualitative_colors[i % len(qualitative_colors)]
                    legend_items.append(f"""
                        <span style="display:inline-flex;align-items:center;
                                    margin-right:10px;margin-bottom:4px;">
                            <span style="width:14px;height:14px;background:{color};
                                        display:inline-block;margin-right:5px;
                                        border:1px solid #333;border-radius:3px;"></span>
                            <span>{rt}</span>
                        </span>
                    """)
                
                st.markdown("**Color Encoding (room_type):**", unsafe_allow_html=True)
                st.markdown("".join(legend_items), unsafe_allow_html=True)
                st.plotly_chart(fig_pc, use_container_width=True)
                st.markdown(f"**Listings Visualized:** {len(df_pc):,}")
    

    # sankey
    with tab3:
        st.subheader("3. Category Flow: Neighbourhood Group → Room Type (Sankey Diagram)")
        st.info("""
            **Related Questions:**
            - Is Entire home dominant in Manhattan?
            - Is Private room prevalent in Brooklyn?
            - Is Shared room proportion low in Queens?
        """)
        
        st.markdown("**Chart Data Filter**")
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            selected_groups_sankey = st.multiselect(
                "Neighbourhood Group:",
                options=sorted(df['neighbourhood_group'].dropna().unique().tolist()),
                default=sorted(df['neighbourhood_group'].dropna().unique().tolist()),
                key="sankey_groups",
                help=(
                    "Select which boroughs (neighbourhood_group) to display in the Sankey diagram.\n"
                    "- Only flows from the selected neighborhoods to room types are drawn.\n"
                    "- For example, if you select only Manhattan and Brooklyn, "
                    "flows from other boroughs are hidden."
                )
            )
        
        with col_f2:
            selected_room_types_sankey = st.multiselect(
                "Room Types:",
                options=sorted(df['room_type'].dropna().unique().tolist()),
                default=sorted(df['room_type'].dropna().unique().tolist()),
                key="sankey_room_types",
                help=(
                    "Select which room types to display in the Sankey diagram.\n"
                    "- Each room type appears as a target node receiving flows from boroughs.\n"
                    "- For example, if you select only Entire home and Private room, "
                    "Shared room flows are hidden."
                )
            )
        
        with col_f3:
            max_price_sankey = st.slider(
                "Max Price ($):",
                min_value=50,
                max_value=int(min(1500, df['price'].max())),
                value=int(min(500, df['price'].max())),
                step=50,
                help=(
                    "Sets the maximum price to include in the Sankey diagram.\n"
                    "- Listings with prices above this threshold are completely filtered out.\n"
                    "- This prevents extremely expensive (outlier) listings from skewing "
                    "the flow distribution, and helps you focus on more 'typical' price ranges."
                )
            )
        
        min_count_sankey = st.slider(
            "Min Listings per Flow:",
            min_value=1,
            max_value=100,
            value=5,
            step=1,
            help=(
                "Sets the minimum number of listings required for a borough → room_type "
                "flow to be drawn.\n"
                "- Flows with fewer listings than this value are removed from the diagram.\n"
                "- This makes the diagram cleaner and lets you focus on strong flows "
                "(important combinations)."
            )
        )
        
        st.divider()
        
        df_sankey = df[
            (df['neighbourhood_group'].isin(selected_groups_sankey)) &
            (df['room_type'].isin(selected_room_types_sankey)) &
            (df['price'] <= max_price_sankey)
        ]
        
        if df_sankey.empty:
            st.warning("No data matches the selected filters. Please adjust the filters.")
        else:
            grouped = (
                df_sankey
                .groupby(["neighbourhood_group", "room_type"])
                .size()
                .reset_index(name="count")
            )
            grouped = grouped[grouped["count"] >= min_count_sankey]
            
            if grouped.empty:
                st.warning(
                    "All flows were filtered out by 'Min Listings per Flow'. "
                    "Try lowering the threshold."
                )
            else:
                groups = sorted(grouped["neighbourhood_group"].unique().tolist())
                room_types = sorted(grouped["room_type"].unique().tolist())
                labels = groups + room_types
                
                label_to_index = {label: i for i, label in enumerate(labels)}
                
                sources, targets, values = [], [], []
                for _, row in grouped.iterrows():
                    s = label_to_index[row["neighbourhood_group"]]
                    t = label_to_index[row["room_type"]]
                    v = int(row["count"])
                    sources.append(s)
                    targets.append(t)
                    values.append(v)
                
                fig_sankey = go.Figure(data=[go.Sankey(
                    node=dict(
                        pad=15,
                        thickness=20,
                        label=labels
                    ),
                    link=dict(
                        source=sources,
                        target=targets,
                        value=values
                    )
                )])
                
                fig_sankey.update_layout(
                    title_text="Flow of Listings from Neighbourhood Group to Room Type",
                    font_size=12,
                    height=600
                )
                
                st.plotly_chart(fig_sankey, use_container_width=True)
                
                # Statistics
                col_stat1, col_stat2 = st.columns(2)
                col_stat1.metric("Total Flows", f"{len(values):,}")
                col_stat2.metric("Total Listings (after filters)", f"{len(df_sankey):,}")
    
    st.divider()