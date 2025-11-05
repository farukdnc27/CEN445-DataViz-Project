import streamlit as st
import pandas as pd
from pathlib import Path

# Sayfa ayarları
st.set_page_config(
    page_title="CEN445 Veri Görselleştirme Projesi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    st.markdown("# 📊 CEN445 Veri Görselleştirme Projesi")    


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

def main():
    data = load_data()
    
    
    # ana sayfayı ilk başlamada göster
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "🏠 Ana Sayfa"
    
    col_left, col_center, col_right = st.columns([12, 6, 8])
    with col_center:
        if st.button("🏠 Ana Sayfa", key="merkez_btn"):
            st.session_state.centered_clicked = True
            st.session_state.current_page = "🏠 Ana Sayfa"
                
    
    st.markdown("---")
    
    PAGE_INFO = {
        "👤 Üye 1": "Veri ön işleme ve Bölgesel Analizler.",
        "👤 Üye 2": "Fiyat ve Yorum İlişkisi Görselleştirmeleri.",
        "👤 Üye 3": "Zaman Serileri ve Gelişmiş Grafik Tipleri."
    }
    
    PAGE_OPTIONS = list(PAGE_INFO.keys())
    N_PAGES = len(PAGE_OPTIONS)

    # Ortalamak için
    padding_left, main_area, padding_right = st.columns([1, 4, 1]) # 4, 1, 4 daha çok boşluk bırakır

    with main_area:
        # Butonları yatayda hizalamak için yeni bir columns grubu oluşturun
        cols_for_buttons = st.columns(N_PAGES)
        
        for i, page_name in enumerate(PAGE_OPTIONS):
            
            with cols_for_buttons[i]:
                # --- Buton Oluşturma ---
                if st.button(
                    page_name, 
                    key=f"tab_btn_{i}",
                    use_container_width=True,
                ):
                    st.session_state.current_page = page_name
                    
                # --- Açıklama Ekleme ---
                st.caption(PAGE_INFO[page_name])
                
                

    st.markdown("---") 

    active_page = st.session_state.current_page
    if active_page != "🏠 Ana Sayfa":
        with st.sidebar:
            if active_page == "👤 Üye 1":
                st.markdown("### Üye 1 Filtreleri")
                st.info("Bölge filtreleri, Fiyat aralığı vb. buraya gelecek.")
                # Örnek:
                if data is not None:
                    st.multiselect(
                        "Bölge Seçin:",
                        data['neighbourhood_group'].unique(),
                        key="member1_regions"
                    )

            elif active_page == "👤 Üye 2":
                st.markdown("### Üye 2 Filtreleri")
                st.info("Kullanıcı Tipi, Yorum Sayısı filtreleri vb. buraya gelecek.")
                
            elif active_page == "👤 Üye 3":
                st.markdown("### Üye 3 Filtreleri")
                st.info("Kullanıcı Tipi, Yorum Sayısı filtreleri vb. buraya gelecek.")
            

    # Ana Sayfa 
    if active_page == "🏠 Ana Sayfa":
        show_home_page(data)
    
    elif active_page == "👤 Üye 1":
        st.markdown("# 👤 Üye 1 - Görselleştirmeler")
        # Filtreleri session_state'den alıp görselleştirme fonksiyonuna iletme
        # filter_values = st.session_state.get("member1_regions", [])
        
        if data is not None:
             # from member1.visualizations import show_visualizations
             # show_visualizations(data, filter_values)
             st.warning("Üye 1 görselleştirme çağrısı...")
    elif active_page == "👤 Üye 2":
        st.markdown("# 👤 Üye 2 - Görselleştirmeler")
        if data is not None:
             st.warning("Üye 2 görselleştirme çağrısı...")
             
    elif active_page == "👤 Üye 3":
        st.markdown("# 👤 Üye 3 - Görselleştirmeler")
        if data is not None:
             st.warning("Üye 3 görselleştirme çağrısı...")
        


if __name__ == "__main__":
    main()