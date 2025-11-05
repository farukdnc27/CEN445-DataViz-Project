"""
Üye 1 - Görselleştirme Modülü
Bu dosya Üye 1'in hazırladığı tüm görselleştirmeleri içerir.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np


def show_visualizations(data):
    """
    Üye 1'in tüm görselleştirmelerini gösterir
    
    Args:
        data (pd.DataFrame): Ana veri seti
    """
    
    st.markdown("## 📊 Üye 1 - Görselleştirmeler")
    st.markdown("---")
    
    # İnteraktif filtreler (sidebar veya ana sayfada)
    st.sidebar.markdown("### 🎛️ Üye 1 - Filtreler")
    
    # Görselleştirmeleri göster
    visualization_1(data)
    st.markdown("---")
    
    visualization_2(data)
    st.markdown("---")
    
    visualization_3(data)


def visualization_1(data):
    """
    Görselleştirme 1: İnteraktif Scatter Plot (Dağılım Grafiği)
    
    Özellikler:
    - Hover ile detaylı bilgi
    - Renk kodlaması
    - Zoom ve pan
    """
    st.markdown("### 📈 Görselleştirme 1: İnteraktif Dağılım Grafiği")
    
    # Örnek: Sayısal sütunları bul
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    
    if len(numeric_cols) >= 2:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            x_axis = st.selectbox("X Ekseni", numeric_cols, key="viz1_x")
        with col2:
            y_axis = st.selectbox("Y Ekseni", numeric_cols, index=1, key="viz1_y")
        with col3:
            color_by = st.selectbox("Renk", [None] + data.columns.tolist(), key="viz1_color")
        
        # Grafik oluştur
        fig = px.scatter(
            data,
            x=x_axis,
            y=y_axis,
            color=color_by if color_by else None,
            title=f"{x_axis} vs {y_axis}",
            hover_data=data.columns[:5],  # İlk 5 sütunu hover'da göster
            template="plotly_white",
            height=500
        )
        
        fig.update_traces(marker=dict(size=8, opacity=0.7))
        fig.update_layout(
            xaxis_title=x_axis,
            yaxis_title=y_axis,
            hovermode='closest'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # İçgörü
        with st.expander("💡 İçgörü ve Analiz"):
            st.write(f"""
            Bu görselleştirme **{x_axis}** ve **{y_axis}** arasındaki ilişkiyi göstermektedir.
            
            **Gözlemler:**
            - Korelasyon: {data[x_axis].corr(data[y_axis]):.3f}
            - Nokta sayısı: {len(data):,}
            - Hover ile her noktanın detaylarını görebilirsiniz
            """)
    else:
        st.warning("Yeterli sayısal sütun bulunamadı.")


def visualization_2(data):
    """
    Görselleştirme 2: İleri Düzey Treemap
    
    Özellikler:
    - Hiyerarşik görünüm
    - İnteraktif zoom
    - Renk gradyanları
    """
    st.markdown("### 🌳 Görselleştirme 2: Treemap (Ağaç Haritası)")
    
    categorical_cols = data.select_dtypes(include=['object']).columns.tolist()
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    
    if categorical_cols and numeric_cols:
        col1, col2 = st.columns(2)
        
        with col1:
            category = st.selectbox("Kategori", categorical_cols, key="viz2_cat")
        with col2:
            value = st.selectbox("Değer", numeric_cols, key="viz2_val")
        
        # Veriyi grupla
        grouped = data.groupby(category)[value].sum().reset_index()
        grouped = grouped.nlargest(20, value)  # En büyük 20 kategori
        
        # Treemap oluştur
        fig = px.treemap(
            grouped,
            path=[category],
            values=value,
            title=f"{category} Bazında {value} Dağılımı",
            color=value,
            color_continuous_scale='Viridis',
            height=500
        )
        
        fig.update_traces(
            textposition='middle center',
            textfont=dict(size=12, color='white')
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("💡 İçgörü ve Analiz"):
            st.write(f"""
            **Treemap Analizi:**
            - En büyük kategori: {grouped.iloc[0][category]} ({grouped.iloc[0][value]:,.0f})
            - Toplam değer: {grouped[value].sum():,.0f}
            - Gösterilen kategori sayısı: {len(grouped)}
            """)
    else:
        st.warning("Treemap için uygun sütunlar bulunamadı.")


def visualization_3(data):
    """
    Görselleştirme 3: İnteraktif Box Plot (Kutu Grafiği)
    
    Özellikler:
    - Aykırı değer tespiti
    - Gruplar arası karşılaştırma
    - Violin plot opsiyonu
    """
    st.markdown("### 📦 Görselleştirme 3: Box Plot (Dağılım Analizi)")
    
    numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = data.select_dtypes(include=['object']).columns.tolist()
    
    if numeric_cols:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            y_var = st.selectbox("Değişken", numeric_cols, key="viz3_y")
        with col2:
            x_var = st.selectbox("Gruplama", [None] + categorical_cols, key="viz3_x")
        with col3:
            plot_type = st.radio("Grafik Tipi", ["Box", "Violin"], key="viz3_type")
        
        # Grafik oluştur
        if plot_type == "Box":
            fig = px.box(
                data,
                x=x_var if x_var else None,
                y=y_var,
                title=f"{y_var} Dağılımı",
                color=x_var if x_var else None,
                points="outliers",  # Sadece aykırı değerleri göster
                template="plotly_white",
                height=500
            )
        else:
            fig = px.violin(
                data,
                x=x_var if x_var else None,
                y=y_var,
                title=f"{y_var} Dağılımı (Violin Plot)",
                color=x_var if x_var else None,
                box=True,  # İçinde box plot göster
                template="plotly_white",
                height=500
            )
        
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("💡 İstatistiksel Analiz"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Ortalama", f"{data[y_var].mean():.2f}")
            with col2:
                st.metric("Medyan", f"{data[y_var].median():.2f}")
            with col3:
                st.metric("Std. Sapma", f"{data[y_var].std():.2f}")
            with col4:
                st.metric("Aykırı Değer", len(data[data[y_var] > data[y_var].quantile(0.75) + 1.5 * (data[y_var].quantile(0.75) - data[y_var].quantile(0.25))]))
    else:
        st.warning("Sayısal sütun bulunamadı.")


# Yardımcı fonksiyonlar buraya eklenebilir
def calculate_statistics(data, column):
    """İstatistik hesaplama fonksiyonu"""
    return {
        'mean': data[column].mean(),
        'median': data[column].median(),
        'std': data[column].std(),
        'min': data[column].min(),
        'max': data[column].max()
    }