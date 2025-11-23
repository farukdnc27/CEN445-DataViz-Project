import streamlit as st
import plotly.express as px
import pydeck as pdk
import pandas as pd
import numpy as np


def run_ahmet_module(data):
    """


    1. Bar Chart
    2. Violin Plot
    3. 3D Hexagon Map
    """

    # Veri kopyalama
    df = data.copy()

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("Filters")
        selected_groups = st.multiselect(
            "Choose borough",
            options=df['neighbourhood_group'].unique(),
            default=df['neighbourhood_group'].unique(),
            key="u3_region_select"
        )

    # Filtreleme
    filtered_df = df[df['neighbourhood_group'].isin(selected_groups)]

    if filtered_df.empty:
        st.warning("Veri yok.")
        return

    st.markdown("Airbnb market analysis")
    compact_margin = dict(l=0, r=0, t=30, b=0)

    # ---------------------------------------------------------
    # GRAFİK 1: En Pahalı Semtler (BAR CHART)
    # ---------------------------------------------------------
    st.markdown("#### 1. Which Neighborhoods Are the Most Expensive? ")
    st.caption("Sorting neighborhoods by average nightly prices.")

    top_expensive = filtered_df.groupby('neighbourhood')['price'].mean().sort_values(ascending=False).head(
        10).reset_index()

    fig1 = px.bar(
        top_expensive,
        x='price',
        y='neighbourhood',
        orientation='h',
        text_auto='.0f',
        color='price',
        color_continuous_scale='Reds',
        labels={'price': 'Ortalama Fiyat ($)', 'neighbourhood': 'Semt'},
        height=500
    )
    fig1.update_layout(yaxis=dict(autorange="reversed"), margin=compact_margin)
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # GRAFİK 2: Fiyat Dağılımı (VIOLIN PLOT)
    # ---------------------------------------------------------
    st.markdown("#### 2.Price distribution by room tpyes. 🎻")
    st.caption("Ranges where prices are concentrated (Violin Chart).")

    # Outlier temizliği (500$ altı)
    violin_df = filtered_df[filtered_df['price'] < 500]

    fig2 = px.violin(
        violin_df,
        x="room_type",
        y="price",
        color="room_type",
        box=True,
        points=False,
        hover_data=violin_df.columns
    )

    fig2.update_layout(
        yaxis_title="Gecelik Fiyat ($)",
        xaxis_title="Oda Tipi",
        showlegend=False,
        height=550,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    # ---------------------------------------------------------
    # GRAFİK 3: 3D Bölgesel Doluluk Haritası (PYDECK HEXAGON)
    # ---------------------------------------------------------
    st.markdown("#### 3. 3D Borough Demand/Occupancy Map 🧊")



    # 1. Doluluk Hesabı
    filtered_df['occupied_days'] = 365 - filtered_df['availability_365']

    # 2. NaN Temizliği
    filtered_df['occupied_days'] = filtered_df['occupied_days'].fillna(0)

    # 3. Veri Tipi Zorlama
    filtered_df['occupied_days'] = filtered_df['occupied_days'].astype(float)

    # Harita Başlangıç Açısı
    view_state = pdk.ViewState(
        latitude=40.7128,
        longitude=-74.0060,
        zoom=9,
        pitch=60,
        bearing=30
    )


    layer = pdk.Layer(
        "HexagonLayer",
        data=filtered_df,
        get_position='[longitude, latitude]',
        radius=200,

        # Yükseklik Ayarları
        get_elevation_weight='occupied_days',
        elevation_aggregation='SUM',

        elevation_scale=300,


        extruded=True,
        pickable=True,
        auto_highlight=True,
    )

    st.pydeck_chart(pdk.Deck(
        map_style=None,  #
        initial_view_state=view_state,
        layers=[layer],
    ))
