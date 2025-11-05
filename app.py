import streamlit as st
import pandas as pd
from pathlib import Path

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="CEN445 Veri Görselleştirme Projesi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Veri yükleme fonksiyonu
@st.cache_data
def load_data():
    """Veri setini yükler ve önbelleğe alır"""
    try:
        # Veri dosyanızın yolunu buraya 
        data = pd.read_csv('data/AB_NYC_2019.csv')
        return data
    except FileNotFoundError:
        st.error("⚠️ Veri dosyası bulunamadı! Lütfen 'data/dataset.csv' dosyasının mevcut olduğundan emin olun.")
        return None

# Ana sayfa içeriği
def show_home_page(data):
    """Ana sayfa - Proje ve veri seti hakkında genel bilgiler"""
    st.markdown('<p class="main-header">📊 CEN445 Veri Görselleştirme Projesi</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Interaktif Keşifsel Veri Analizi Dashboard\'u</p>', unsafe_allow_html=True)
    
    # Proje bilgileri
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("## 🎯 Proje Hakkında")
        st.markdown("""
        Bu proje, **CEN445 Introduction to Data Visualization** dersi kapsamında hazırlanmıştır.
        
        ### Amaç
        - Kapsamlı bir veri setini interaktif olarak keşfetmek
        - Anlamlı ve ileri düzey görselleştirmeler oluşturmak
        - Veriden içgörüler ve desenler çıkarmak
        - Kullanıcı dostu bir dashboard geliştirmek
        
        ### Özellikler
        - ✅ 9+ farklı görselleştirme tekniği
        - ✅ İnteraktif bileşenler (filtreler, sliderlar, seçim kutuları)
        - ✅ İleri düzey grafikler (treemap, sankey, network, vs.)
        - ✅ Modüler ve genişletilebilir kod yapısı
        """)
    
    with col2:
        st.markdown("## 👥 Takım Üyeleri")
        st.info("""
        **Üye 1:** [İsim Soyisim]
        - Veri ön işleme
        - 3 görselleştirme
        
        **Üye 2:** [İsim Soyisim]
        - İnteraktif bileşenler
        - 3 görselleştirme
        
        **Üye 3:** [İsim Soyisim]
        - Dashboard tasarımı
        - 3 görselleştirme
        """)
    
    # Veri seti bilgileri
    if data is not None:
        st.markdown("---")
        st.markdown("## 📁 Veri Seti Bilgileri")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Toplam Satır", f"{len(data):,}")
        with col2:
            st.metric("Toplam Sütun", len(data.columns))
        with col3:
            st.metric("Sayısal Sütunlar", len(data.select_dtypes(include=['number']).columns))
        with col4:
            st.metric("Kategorik Sütunlar", len(data.select_dtypes(include=['object']).columns))
        
        # Veri seti önizlemesi
        st.markdown("### 🔍 Veri Seti Önizlemesi")
        st.dataframe(data.head(10), use_container_width=True)
        
        # Temel istatistikler
        with st.expander("📊 Temel İstatistikler"):
            st.dataframe(data.describe(), use_container_width=True)
        
        # Veri tipleri
        with st.expander("🔤 Sütun Bilgileri"):
            col_info = pd.DataFrame({
                'Sütun Adı': data.columns,
                'Veri Tipi': data.dtypes.astype(str).values,
                'Null Değer': data.isnull().sum().values,
                'Null %': (data.isnull().sum().values / len(data) * 100).round(2)
            })
            st.dataframe(col_info, use_container_width=True)

# Ana uygulama
def main():
    # Veriyi yükle
    data = load_data()
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x150.png?text=Logo", width=150)
        st.markdown("## 📌 Navigasyon")
        st.markdown("Üst kısımdaki tab'lardan takım üyelerinin çalışmalarını inceleyebilirsiniz.")
        
        if data is not None:
            st.markdown("---")
            st.markdown("## ⚙️ Genel Ayarlar")
            st.checkbox("Koyu Tema", value=False, key="dark_theme")
            st.slider("Grafik Yüksekliği", 300, 800, 500, key="chart_height")
    
    # Tab sistemi
    tab1, tab2= st.tabs(["🏠 Ana Sayfa", "👤 Üye 1"])
    
    with tab1:
        show_home_page(data)
    
    with tab2:
        st.markdown("# 👤 Üye 1 - Görselleştirmeler")
        if data is not None:
            try:
                from member1.visualizations import show_visualizations
                show_visualizations(data)
            except ImportError:
                st.warning("⚠️ Üye 1'in görselleştirme modülü henüz hazır değil.")
                st.code("""
                    # member1/visualizations.py dosyası oluşturulmalı
                    # Örnek içerik için aşağıya bakın
                """)
        else:
            st.error("Veri yüklenemedi!")
    
"""     with tab3:
        st.markdown("# 👤 Üye 2 - Görselleştirmeler")
        if data is not None:
            try:
                from member2.visualizations import show_visualizations
                show_visualizations(data)
            except ImportError:
                st.warning("⚠️ Üye 2'nin görselleştirme modülü henüz hazır değil.")
        else:
            st.error("Veri yüklenemedi!")
    
    with tab4:
        st.markdown("# 👤 Üye 3 - Görselleştirmeler")
        if data is not None:
            try:
                from member3.visualizations import show_visualizations
                show_visualizations(data)
            except ImportError:
                st.warning("⚠️ Üye 3'ün görselleştirme modülü henüz hazır değil.")
        else:
            st.error("Veri yüklenemedi!") """

if __name__ == "__main__":
    main()