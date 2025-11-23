import streamlit as st
from data_loader import load_dataset
import student_omer
import student_mehmet
import student_ahmet

# 1. Sayfa Ayarları
st.set_page_config(
    page_title="CEN445 Data Viz Project",
    layout="wide",
    initial_sidebar_state="collapsed",
    page_icon="🗽"
)

# 2. Modern CSS Design
def apply_custom_css():
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def main():
    apply_custom_css()
    
    # Oturum Durumu Yönetimi
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"

    # Sayfa Değiştirme Fonksiyonu
    def set_page(page_name):
        st.session_state.current_page = page_name

    # --- 1. ANA SAYFA (KARŞILAMA EKRANI) ---
    if st.session_state.current_page == "Home":
        # Hero Section
        st.markdown("<h1>🗽 NYC Airbnb Analytics</h1>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>CEN445 - INTRODUCTION TO DATA VISUALIZATION</p>", unsafe_allow_html=True)
        
        # Description with Glass Effect
        col_desc1, col_desc2, col_desc3 = st.columns([1, 2, 1])
        with col_desc2:
            st.markdown("""
                <div style='background: rgba(255, 255, 255, 0.05); 
                            backdrop-filter: blur(10px); 
                            border-radius: 15px; 
                            padding: 2rem; 
                            text-align: center;
                            border: 1px solid rgba(255, 255, 255, 0.1);
                            margin-bottom: 3rem;'>
                    <p style='font-size: 1.1rem; color: #c7d2fe; line-height: 1.8;'>
                        Explore <strong>48,895 Airbnb listings</strong> across New York City through 
                        interactive visualizations. Select a student to view their unique analytical perspective.
                    </p>
                </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        
        # Student Selection Cards
        col1, col2, col3 = st.columns(3, gap="large")

        with col1:
            st.markdown("""
                <div class='student-card'>
                    <span class='icon-large'>👨‍🎓</span>
                    <p class='student-name'>Ömer Faruk Dinçoğlu<br>2021556025</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("📊 View Analysis", key="omer"):
                set_page("Ömer")
                st.rerun()

        with col2:
            st.markdown("""
                <div class='student-card'>
                    <span class='icon-large'>👨‍🎓</span>
                    <p class='student-name'>Mehmet Dora<br>2021555019</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("📊 View Analysis", key="student2"):
                set_page("Mehmet")
                st.rerun()

        with col3:
            st.markdown("""
                <div class='student-card'>
                    <span class='icon-large'>👨‍🎓</span>
                    <p class='student-name'>Ahmet Muhtar Bilal<br>2022556011</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("📊 View Analysis", key="student3"):
                set_page("Student3")
                st.rerun()
                
        st.divider()
        
        # Dataset Statistics
        st.markdown("<h3 style='text-align: center; margin-top: 3rem;'>📈 Dataset Overview</h3>", unsafe_allow_html=True)
        
        with st.expander("🔍 Explore Dataset Details", expanded=False):
            df_preview = load_dataset()
            if df_preview is not None:
                # Stats Row
                stat1, stat2, stat3, stat4 = st.columns(4)
                
                with stat1:
                    st.markdown(f"""
                        <div class='stat-box'>
                            <div class='stat-number'>{len(df_preview):,}</div>
                            <div class='stat-label'>Total Listings</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with stat2:
                    st.markdown(f"""
                        <div class='stat-box'>
                            <div class='stat-number'>{df_preview['neighbourhood_group'].nunique()}</div>
                            <div class='stat-label'>Boroughs</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with stat3:
                    st.markdown(f"""
                        <div class='stat-box'>
                            <div class='stat-number'>${df_preview['price'].mean():.0f}</div>
                            <div class='stat-label'>Avg Price/Night</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with stat4:
                    st.markdown(f"""
                        <div class='stat-box'>
                            <div class='stat-number'>{df_preview['neighbourhood'].nunique()}</div>
                            <div class='stat-label'>Neighborhoods</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.write("")
                st.dataframe(df_preview.head(10), use_container_width=True, height=300)

    # --- 2. ÖĞRENCİ SAYFALARI ---
    else:
        # Sidebar Navigation
        with st.sidebar:
            
            st.markdown("<h2 style='text-align: center;'>🧭 Navigation</h2>", unsafe_allow_html=True)
            st.write("")
            if st.button("🏠 Back to Home", use_container_width=True):
                set_page("Home")
                st.rerun()
            
            st.divider()
            
            # Mehmet Dora sayfası için gösterilmiyor bu kısım
            if st.session_state.current_page != "Mehmet":
                st.markdown("""
                    <div style='background: rgba(255, 255, 255, 0.05); 
                                padding: 1rem; 
                                border-radius: 10px; 
                                margin-top: 2rem;
                                text-align: center;'>
                        <p style='font-size: 0.9rem; color: #a5b4fc;'>
                            <strong>CEN445 Project</strong><br>
                            Data Visualization<br>
                            2025-2026
                        </p>
                    </div>
                """, unsafe_allow_html=True)
        
        # Veriyi Yükle
        df = load_dataset()
        if df is None:
            return

        # --- ÖMER'İN SAYFASI ---
        if st.session_state.current_page == "Ömer":
            st.sidebar.header("🎛️ Filters")
            all_groups = df['neighbourhood_group'].unique()
            selected_groups = st.sidebar.multiselect(
                "Neighborhood Groups", 
                all_groups, 
                default=all_groups,
                help="Filter data by NYC boroughs"
            )
            
            # Filtreleme
            df_filtered = df[df['neighbourhood_group'].isin(selected_groups)]
            
            # İstatistik Badge
            st.sidebar.markdown(f"""
                <div style='background: rgba(16, 185, 129, 0.1); 
                            border: 1px solid rgba(16, 185, 129, 0.3);
                            border-radius: 10px; 
                            padding: 1rem; 
                            margin-top: 1rem;
                            text-align: center;'>
                    <div style='font-size: 1.5rem; font-weight: 700; color: #10b981;'>
                        {len(df_filtered):,}
                    </div>
                    <div style='font-size: 0.8rem; color: #6ee7b7;'>
                        LISTINGS SELECTED
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Modülü Çalıştır
            student_omer.run_omer_module(df_filtered)



        # Mehmet Dora 
        elif st.session_state.current_page == "Mehmet": 
            st.sidebar.header("Data Filters")
            all_groups = df['neighbourhood_group'].unique()
            selected_groups = st.sidebar.multiselect(
                "Neighborhood Groups", 
                all_groups, 
                default=all_groups,
                help="Filter data by NYC boroughs"
            )
            
            # Filtreleme
            df_filtered = df[df['neighbourhood_group'].isin(selected_groups)]
            
            # İstatistik Badge
            st.sidebar.markdown(f"""
                <div style='background: rgba(16, 185, 129, 0.1); 
                            border: 1px solid rgba(16, 185, 129, 0.3);
                            border-radius: 10px; 
                            padding: 1rem; 
                            margin-top: 1rem;
                            text-align: center;'>
                    <div style='font-size: 1.5rem; font-weight: 700; color: #10b981;'>
                        {len(df_filtered):,}
                    </div>
                    <div style='font-size: 0.8rem; color: #6ee7b7;'>
                        LISTINGS SELECTED
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            student_mehmet.run_mehmet_module(df)

        # --- Student 3 SAYFASI ---
        elif st.session_state.current_page == "Student3":
            student_ahmet.run_ahmet_module(df)


if __name__ == "__main__":
    main()