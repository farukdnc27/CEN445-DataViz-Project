import pandas as pd
import streamlit as st

@st.cache_data
def load_dataset():
    """
    Veri setini yükler ve temizler.
    Tüm modüller bu fonksiyonu kullanarak veriyi çeker.
    """
    try:
        df = pd.read_csv("AB_NYC_2019.csv")
        
        # Eksik verileri doldurma (Ortak temizlik kuralları)
        df.fillna({'reviews_per_month': 0}, inplace=True)
        df.fillna({'name': 'Unknown', 'host_name': 'Unknown'}, inplace=True)
        
        return df
        
    except FileNotFoundError:
        st.error("Hata: 'AB_NYC_2019.csv' dosyası bulunamadı. Lütfen proje klasörüne ekleyin.")
        return None