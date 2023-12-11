import streamlit as st
import pandas as pd
from web_function import preprocess_dataframe, load_data
import plotly.express as px
import plotly.graph_objects as go

def plot_rainfall_line(df):
    fig = go.Figure()
    for event_type in df['Kejadian'].unique():
        event_data = df[df['Kejadian'] == event_type]
        fig.add_trace(go.Scatter(x=event_data.index, y=event_data['avg_hujan'],
                                 mode='lines', name=event_type))
    fig.update_layout(title='Average Rainfall Over Time',
                      xaxis_title='Date',
                      yaxis_title='Average Rainfall (mm)',
                      template='plotly_dark')
    return fig

def app():
    # Judul dan Informasi mengenai Dasboard
    st.title("Dashboard Pemantauan dan Prediksi Banjir Berbasis Curah Hujan di Kabupaten Cilacap :thunder_cloud_and_rain:")
    st.write("Selamat datang di Dashboard Pemantauan dan Prediksi Banjir Berbasis Curah Hujan di **Kabupaten Cilacap**! "
            "Kabupaten Cilacap, Jawa Tengah, sering mengalami masalah banjir, khususnya dalam rentang waktu tahun 2020-2023. " 
            "Dengan menggabungkan data kejadian banjir dari **BNPB** dan informasi curah hujan harian dari **WorldWeatherOnline**, " 
            "kami menciptakan solusi prediktif berupa dashboard ini. Kami menganalisis curah hujan, membuat model forecast,"
            "dan memvisualisasikannya agar dapat memberikan pemahaman yang lebih baik mengenai potensi risiko banjir. " 
            "Dengan fitur-fitur seperti data historis, forecast, dan prediksi kejadian banjir, kami berharap " 
            "dashboard ini dapat menjadi alat yang berguna dalam menghadapi tantangan banjir di **Kabupaten Cilacap**."
            )
    st.info("Semua data curah hujan diukur dalam satuan mm/jam.")

    # Load Dataset
    df = load_data("data/cilacap_hujan.csv")

    # Data Historis Banjir
    df_class = df.copy()
    df_class['date'] = pd.to_datetime(df_class['date'])
    df_class.set_index('date', inplace=True)

    # Pemfilteran Data Berdasarkan Range Waktu
    date_range = st.date_input("Pilih Rentang Waktu", [df_class.index.min(), df_class.index.max()], key="date_range")
    start_date, end_date = date_range
    filtered_df_class = df_class.loc[start_date:end_date]

    # Menampilkan Data Historis Banjir
    st.header("Data Historis Kejadian Banjir")
    st.write(filtered_df_class)

    # Menampilkan penjelasan dari struktur data
    st.markdown("Deskripsi kolom dari tabel tersebut adalah:")   
    kolomdesc = '\n1.  date\t: Merupakan kolom yang mencatat tanggal dimana data curah hujan dicatat\
                 \n2.  Kejadian\t: Merupakan status kejadian banjir atau tidak\
                 \n3.  hujan_0\t: Menunjukkan curah hujan (mm) pada jam 00:00\
                 \n4.  hujan_300\t: Menunjukkan curah hujan (mm) pada jam 03:00\
                 \n5.  hujan_600\t: Menunjukkan curah hujan (mm) pada jam 06:00\
                 \n6.  hujan_900\t: Menunjukkan curah hujan (mm) pada jam 09:00\
                 \n7.  hujan_1200\t: Menunjukkan curah hujan (mm) pada jam 12:00\
                 \n8.  hujan_1500\t: Menunjukkan curah hujan (mm) pada jam 15:00\
                 \n9.  hujan_2100\t: Menunjukkan curah hujan (mm) pada jam 21:00\
                 \n10. min_hujan\t: Menunjukkan curah hujan (mm) minimum\
                 \n10. max_hujan\t: Menunjukkan curah hujan (mm) maksimum\
                 \n10. avg_hujan\t: Menunjukkan rata-rata curah hujan (mm)'
    st.text(kolomdesc)    
    
    # Menampilkan Plot Kejadian "Banjir" dan "Tidak Banjir" 
    fig = go.Figure()
    for kejadian, color in zip(filtered_df_class['Kejadian'].unique(), ['green', 'red']):  # Choose your preferred colors
        filtered_df = filtered_df_class[filtered_df_class['Kejadian'] == kejadian]
        fig.add_trace(go.Scatter(x=filtered_df.index, y=filtered_df['max_hujan'],
                             mode='lines+markers', name=kejadian, line=dict(color=color)))
    fig.update_layout(title='Kejadian Banjir vs Tidak Banjir berdasarkan Curah Hujan Maksimum',
                  xaxis_title='Date',
                  yaxis_title='max_hujan',
                  template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True)

    # Data Historis Curah Hujan
    st.header("Data Historis Curah Hujan")
    df_time = df.drop(columns=['Kejadian','min_hujan', 'max_hujan', 'avg_hujan'])
    
    # Memberikan Opsi Resampling Frekuensi
    freq_options = {'Raw': '','Hourly': 'H', 'Daily': 'D' , 'Weekly': 'W', 'Monthly': 'M'}
    freq = st.radio("Pilih Frekuensi Resampling:", list(freq_options.keys()))

    # Menampilkan Data Historis Curah Hujan Berdasarkan Frekuensi
    df_time = preprocess_dataframe(df_time, freq_options[freq])  # Resample based on the selected frequency
    filtered_df_time = df_time.loc[start_date:end_date]

    col1, col2 = st.columns([1, 3])
    with col1:
        st.write(filtered_df_time)

    with col2:
        st.text("Dengan menghitung rata-rata dari frekuensi data yang diresample, kita dapat mendapatkan  \
            \nnilai rata-rata curah hujan untuk setiap interval waktu yang dipilih (misalnya, harian, \
            \nmingguan, atau bulanan). Perhitungan ini memberikan gambaran umum tentang kecenderungan  \
            \ncurah hujan selama interval waktu tersebut. Misalnya, rata-rata harian dapat memberikan \
            \ninformasi tentang curah hujan rata-rata setiap hari dalam satu bulan. Proses ini tidak  \
            \nhanya membantu dalam menyederhanakan data, tetapi juga memungkinkan penggunaan metrik \
            \nyang lebih mudah diinterpretasi dalam analisis. \
            \n\nDengan menggunakan nilai rata-rata ini, pengguna dapat mengidentifikasi pola, tren,  \
            \natau fluktuasi dalam curah hujan dengan lebih baik. Informasi ini kemudian dapat \
            \ndigunakan sebagai dasar untuk proses forecasting lebih lanjut atau untuk  \
            \nmengembangkan model prediksi terkait potensi banjir. Rata-rata frekuensi data \
            \nyang diresample memberikan ringkasan yang lebih mudah dipahami, yang dapat  \
            \ndigunakan sebagai dasar untuk pengambilan keputusan terkait manajemen risiko banjir."
    )    

    # Menampilkan Plot Curah Hujan
    fig = px.line(filtered_df_time, x=filtered_df_time.index, y=filtered_df_time.columns, title=f'Curah Hujan - Resampled {freq}')
    fig.update_traces(mode='lines+markers', hovertemplate='<b>Waktu</b>: %{x|%Y-%m-%d %H:%M:%S}<br><b>Curah Hujan</b>: %{y:.2f} mm')
    fig.update_layout(
        xaxis=dict(
            title_text='Waktu',
            rangeslider=dict(
                visible=True
            ),
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1h", step="hour", stepmode="backward"),
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(step="all")
                ]),
                bgcolor='#32B166',
                font=dict(color='black'),
                activecolor='gray',
                y=1
            ),
        ),
        yaxis=dict(title_text='Curah Hujan (mm)'),
        xaxis_rangeslider_visible=True,
    )
    st.plotly_chart(fig, use_container_width=True)






            