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

    # Scatter Plot: Fiyat - Popülarite İlişkisi
    st.subheader("1. Price vs Popularity (Scatter Plot)")
    st.info("""
                **İlgili Sorular:**

                - Ucuz evlerde yorum sayısı daha yüksek mi?
                - Fiyat arttıkça yorumlar azalıyor mu?
                - Bazı bölgeler hem pahalı hem popüler mi?
                - Aykırı değerler var mı? (Örneğin 1000$ olup 0 yorumlu ilanlar)
            """)    
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("**Chart Data Filter**")
        
        selected_groups_scatter = st.multiselect(
            "Neighbourhood Group:",
            options=sorted(df['neighbourhood_group'].dropna().unique().tolist()),
            default=sorted(df['neighbourhood_group'].dropna().unique().tolist()),
            key="scatter_groups"
        )
        
        max_price_scatter = st.slider(
            "Max Price Filter ($)",
            min_value=50,
            max_value=int(min(2000, df['price'].max())),
            value=500,
            step=50
        )
        
        min_reviews_scatter = st.slider(
            "Min Reviews:",
            min_value=0,
            max_value=int(df['number_of_reviews'].max()),
            value=0,
            step=5
        )
        
        use_log_y = st.checkbox(
            "Use Log Scale for Reviews",
            value=False,
            help="Log scale helps when some listings have very large review counts."
        )

        

        # Kullanmaktan vazgeçildi   
        """show_trendline = st.checkbox(
            "Show Trendline (OLS)",
            value=True,
            help="Adds a regression line to see overall correlation."
        )"""

    with col2:
        # Filtrelenmiş veri
        df_scatter = df[
            (df['price'] <= max_price_scatter) &
            (df['number_of_reviews'] >= min_reviews_scatter) &
            (df['neighbourhood_group'].isin(selected_groups_scatter))
        ]

        if df_scatter.empty:
            st.warning("No data matches the selected filters. Please adjust the filters.")
        else:
            #trend_arg = "ols" if show_trendline else None

            fig_scatter = px.scatter(
                df_scatter,
                x="price",
                y="number_of_reviews",
                color="neighbourhood_group",
                hover_data=["name", "room_type", "neighbourhood"],
                title=f"Price vs Number of Reviews (≤ ${max_price_scatter})",
                opacity=0.7,
                #trendline=trend_arg
            )

            fig_scatter.update_layout(
                xaxis_title="Price ($)",
                yaxis_title="Number of Reviews (log scale)" if use_log_y else "Number of Reviews",
                legend_title="Neighbourhood Group"
            )

            if use_log_y:
                fig_scatter.update_yaxes(type="log")

            # Basit istatistikler
            col_stat1, col_stat2, col_stat3 = st.columns(3)
            col_stat1.metric("Total Listings", f"{len(df_scatter):,}")
            col_stat2.metric("Avg Price", f"${df_scatter['price'].mean():.2f}")
            col_stat3.metric("Avg Reviews", f"{df_scatter['number_of_reviews'].mean():.2f}")

            st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    # Parallel Coordinates: Çok Boyutlu Özellik Karşılaştırması
    st.subheader("2. Multidimensional Feature Profile (Parallel Coordinates)")
    st.info("""
                **İlgili Sorular:**

                - Entire home → genelde pahalı + yüksek minimum geceli mi?
                - Private room → ucuz ama çok mu müsait?
                - Shared room → düşük fiyat ama düşük review sayısı mı?
                - Hangi oda tipi “ağır çizgi kümelerine” sahip?
            """)
    
    col3, col4 = st.columns([1, 3])

    with col3:
        st.markdown("**Chart Data Filter**")

        # Kullanılabilecek kolonlar
        candidate_dims = [
            col for col in ["price", "minimum_nights", "availability_365", "number_of_reviews"]
            if col in df.columns
        ]
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        selected_dims = st.multiselect(
            "Select Dimensions:",
            options=numeric_cols,
            default=candidate_dims if len(candidate_dims) >= 3 else numeric_cols[:4],
            help="Choose at least 3 numerical features to compare."
        )

        selected_room_types_pc = st.multiselect(
            "Room Types:",
            options=sorted(df['room_type'].dropna().unique().tolist()),
            default=sorted(df['room_type'].dropna().unique().tolist()),
            key="pc_room_types"
        )

        max_rows_pc = st.slider(
            "Max Number of Listings (sampling):",
            min_value=100,
            max_value=3000,
            value=1000,
            step=100,
            help="To avoid clutter, the data will be randomly sampled if it exceeds this number."
        )

        min_reviews_pc = st.slider(
            "Min Reviews (filter):",
            min_value=0,
            max_value=int(df['number_of_reviews'].max()),
            value=0,
            step=5,
            key="pc_min_reviews"
        )

    with col4:
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
                # Sadece seçilen numeric kolonları ve room_type'ı al
                df_pc = df_pc[selected_dims + ["room_type"]].dropna()

                # Sampling
                if len(df_pc) > max_rows_pc:
                    df_pc = df_pc.sample(n=max_rows_pc, random_state=42)

                # Eğer yine de tek room_type kalıyorsa bilgin olsun
                unique_room_types = df_pc["room_type"].unique().tolist()

                # room_type -> numeric kodlama
                room_type_map = {rt: i for i, rt in enumerate(unique_room_types)}
                df_pc["room_type_code"] = df_pc["room_type"].map(room_type_map)

                num_types = len(room_type_map)

                # Keskin (gradient değil) renkler için qualitative palette
                qualitative_colors = px.colors.qualitative.Set1  # oldukça kontrastlı
                color_scale = []
                for i, (rt, code) in enumerate(room_type_map.items()):
                    color = qualitative_colors[i % len(qualitative_colors)]
                    t0 = code / max(num_types - 1, 1)
                    t1 = code / max(num_types - 1, 1)
                    # Aynı noktaya aynı rengi veriyoruz (keskin geçiş)
                    color_scale.append([t0, color])
                    color_scale.append([t1, color])

                # Parallel Coordinates grafiği (go.Parcoords ile)
                fig_pc = go.Figure(
                    data=go.Parcoords(
                        line=dict(
                            color=df_pc["room_type_code"],
                            colorscale=color_scale,
                            cmin=0,
                            cmax=max(num_types - 1, 1),
                            showscale=False  # parcoords.Line için geçerli, parcoords trace için değil
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

                # Layout: kenar boşluklarını büyüt -> eksen isimleri kesilmesin
                fig_pc.update_layout(
                    margin=dict(l=80, r=80, t=60, b=50)
                )

                # Label ve değer fontlarını biraz büyüt
                fig_pc.update_traces(
                    labelfont=dict(size=12),
                    rangefont=dict(size=10),
                    tickfont=dict(size=10),
                )

                # Üstte kendi legend
                legend_items = []
                for i, (rt, code) in enumerate(room_type_map.items()):
                    color = qualitative_colors[i % len(qualitative_colors)]
                    legend_items.append(f"""
                        <span style="display:inline-flex;align-items:center;margin-right:10px;margin-bottom:4px;">
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

    st.divider()

    # Sankey Diagram: Bölge → Oda Tipi 
    st.subheader("3. Category Flow: Neighbourhood Group → Room Type (Sankey Diagram)")
    st.info("Manhattan’da Entire Home baskın mı? Brooklyn’de Private Room yoğun mu? Queens’de Shared Room oranı düşük mü?")

    col5, col6 = st.columns([1, 3])

    with col5:
        st.markdown("**Chart Data Filter**")

        selected_groups_sankey = st.multiselect(
            "Neighbourhood Group:",
            options=sorted(df['neighbourhood_group'].dropna().unique().tolist()),
            default=sorted(df['neighbourhood_group'].dropna().unique().tolist()),
            key="sankey_groups"
        )

        selected_room_types_sankey = st.multiselect(
            "Room Types:",
            options=sorted(df['room_type'].dropna().unique().tolist()),
            default=sorted(df['room_type'].dropna().unique().tolist()),
            key="sankey_room_types"
        )

        max_price_sankey = st.slider(
            "Max Price Filter ($):",
            min_value=50,
            max_value=int(min(1500, df['price'].max())),
            value=int(min(500, df['price'].max())),
            step=50,
            help="Helps to focus on more 'typical' listings and remove extreme outliers."
        )

        min_count_sankey = st.slider(
            "Min Listings per Flow:",
            min_value=1,
            max_value=100,
            value=5,
            step=1,
            help="Hide very thin flows with very few listings."
        )

    with col6:
        df_sankey = df[
            (df['neighbourhood_group'].isin(selected_groups_sankey)) &
            (df['room_type'].isin(selected_room_types_sankey)) &
            (df['price'] <= max_price_sankey)
        ]

        if df_sankey.empty:
            st.warning("No data matches the selected filters. Please adjust the filters.")
        else:
            # Group by neighbourhood_group & room_type
            grouped = (
                df_sankey
                .groupby(["neighbourhood_group", "room_type"])
                .size()
                .reset_index(name="count")
            )

            # Min count filtresi
            grouped = grouped[grouped["count"] >= min_count_sankey]

            if grouped.empty:
                st.warning("All flows were filtered out by 'Min Listings per Flow'. "
                           "Try lowering the threshold.")
            else:
                # Node label listesi: önce neighbourhood_group, sonra room_type
                groups = sorted(grouped["neighbourhood_group"].unique().tolist())
                room_types = sorted(grouped["room_type"].unique().tolist())
                labels = groups + room_types

                # Label -> index map
                label_to_index = {label: i for i, label in enumerate(labels)}

                sources = []
                targets = []
                values = []

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
                st.markdown(f"**Total Flows:** {len(values):,} | **Total Listings (after filters):** {len(df_sankey):,}")

    st.divider()
