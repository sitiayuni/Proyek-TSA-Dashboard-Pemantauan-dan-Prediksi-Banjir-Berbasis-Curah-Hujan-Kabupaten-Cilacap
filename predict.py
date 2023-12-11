import streamlit as st
import pandas as pd
import joblib
from datetime import datetime
from web_function import get_forecast_data

class SessionState:
    def __init__(self):
        self.all_data = pd.DataFrame(columns=['date', 'Kejadian', 'hujan_00', 'hujan_300', 'hujan_600', 
                                              'hujan_900', 'hujan_1200', 'hujan_1500', 'hujan_2100', 
                                              'min_hujan', 'max_hujan', 'avg_hujan'])
        self.previous_values = {}

# Inisialisasi state
state = SessionState()

# Load Model Machine Learning
def load_model():
    # model = joblib.load('models/prediksi/xgboost.sav') # Model XGboost
    model = joblib.load('models/prediksi/catboost.sav') # Model Catboost {install catboost terlebih dahulu}
    return model

# Menghitung Nilai Metriks
def calculate_metrics(rainfall_values):
    min_rainfall = min(rainfall_values)
    max_rainfall = max(rainfall_values)
    avg_rainfall = sum(rainfall_values) / len(rainfall_values)
    return min_rainfall, max_rainfall, avg_rainfall

def process_data():
    global state  # Mendeklarasikan variabel all_data sebagai variabel global

    # Memanggil Model
    model = load_model()

    # Judul Halaman
    st.title("Prediksi Kejadian Banjir")

    # Membuat Inputan Data
    col1, col2 = st.columns(2)

    with col1:
        selected_date = st.date_input('Pilih Tanggal', datetime.today())

        # Mengisi ulang nilai formulir jika tanggal berubah
        if selected_date not in state.previous_values:
            state.previous_values[selected_date] = {
                'rainfall_00': None,
                'rainfall_300': None,
                'rainfall_600': None,
                'rainfall_900': None,
                'rainfall_1200': None,
                'rainfall_1500': None,
                'rainfall_2100': None
            }

        # Menetapkan Parameter Kunci untuk Inputan Baru
        key_00 = f"rainfall_00_{selected_date}"
        key_300 = f"rainfall_300_{selected_date}"
        key_600 = f"rainfall_600_{selected_date}"
        
        rainfall_00 = st.text_input('Input Nilai Curah Hujan 00:00', key=key_00, value=state.previous_values[selected_date]['rainfall_00'])
        rainfall_300 = st.text_input('Input Nilai Curah Hujan 03:00', key=key_300, value=state.previous_values[selected_date]['rainfall_300'])
        rainfall_600 = st.text_input('Input Nilai Curah Hujan 06:00', key=key_600, value=state.previous_values[selected_date]['rainfall_600'])
    
    with col2:
        # Menetapkan Parameter Kunci untuk Inputan Baru
        key_900 = f"rainfall_900_{selected_date}"
        key_1200 = f"rainfall_1200_{selected_date}"
        key_1500 = f"rainfall_1500_{selected_date}"
        key_2100 = f"rainfall_2100_{selected_date}"

        rainfall_900 = st.text_input('Input Nilai Curah Hujan 09:00', key=key_900, value=state.previous_values[selected_date]['rainfall_900'])
        rainfall_1200 = st.text_input('Input Nilai Curah Hujan 12:00', key=key_1200, value=state.previous_values[selected_date]['rainfall_1200'])
        rainfall_1500 = st.text_input('Input Nilai Curah Hujan 15:00', key=key_1500, value=state.previous_values[selected_date]['rainfall_1500'])
        rainfall_2100 = st.text_input('Input Nilai Curah Hujan 21:00', key=key_2100, value=state.previous_values[selected_date]['rainfall_2100'])

    # Menampilkan Hasil Prediksi Banjir
    hasil_prediksi = ""

    if st.button("Prediksi Banjir"):
        try:
            rainfall_values = [float(rainfall_00), float(rainfall_300), float(rainfall_600),
                                float(rainfall_900), float(rainfall_1200), float(rainfall_1500),
                                float(rainfall_2100)]

            min_rainfall, max_rainfall, avg_rainfall = calculate_metrics(rainfall_values)

            # Menggabungkan Nilai min_rainfall, max_rainfall, avg_rainfall
            input_features = [float(rainfall_00), float(rainfall_300), float(rainfall_600),
                              float(rainfall_900), float(rainfall_1200), float(rainfall_1500),
                              float(rainfall_2100), min_rainfall, max_rainfall, avg_rainfall]

            # Model Melakukan Prediksi
            hasil_prediksi = model.predict([input_features])
            hasil_prediksi = "Banjir" if hasil_prediksi[0] == 1 else "Tidak Banjir"

            # Menambahkan hasil prediksi ke DataFrame
            new_data = {'date': [selected_date.strftime('%Y-%m-%d')],
                        'Kejadian': [hasil_prediksi],
                        'hujan_00': [float(rainfall_00)],
                        'hujan_300': [float(rainfall_300)],
                        'hujan_600': [float(rainfall_600)],
                        'hujan_900': [float(rainfall_900)],
                        'hujan_1200': [float(rainfall_1200)],
                        'hujan_1500': [float(rainfall_1500)],
                        'hujan_2100': [float(rainfall_2100)],
                        'min_hujan': [min_rainfall],
                        'max_hujan': [max_rainfall],
                        'avg_hujan': [avg_rainfall]}           

            state.all_data = pd.concat([state.all_data, pd.DataFrame(new_data)], ignore_index=True)

            # Memperbarui nilai-nilai sebelumnya
            state.previous_values[selected_date]['rainfall_00'] = rainfall_00
            state.previous_values[selected_date]['rainfall_300'] = rainfall_300
            state.previous_values[selected_date]['rainfall_600'] = rainfall_600
            state.previous_values[selected_date]['rainfall_900'] = rainfall_900
            state.previous_values[selected_date]['rainfall_1200'] = rainfall_1200
            state.previous_values[selected_date]['rainfall_1500'] = rainfall_1500
            state.previous_values[selected_date]['rainfall_2100'] = rainfall_2100

        except ValueError:
            st.warning("Please enter valid numeric values for rainfall.")
            hasil_prediksi = ""

    # Menampilkan Alert Sukses bila Berhasil
    st.success(hasil_prediksi)

    # Menampilkan DataFrame hasil prediksi
    state.all_data = state.all_data.sort_values(by=['date'], ascending=True)
    state.all_data = state.all_data.reset_index(drop=True)
    st.table(state.all_data)

    # Membuat Tombol untuk Download Dataframe ke Bentuk CSV
    if not state.all_data.empty:
        csv_data = state.all_data.to_csv(index=False)
        st.download_button(label="Download CSV", data=csv_data, file_name='output.csv', key='download_button')

    # Menampilkan penjelasan dari data diatas
    st.text("Setelah mendapatkan forecast curah hujan, model prediksi mengambil nilai-nilai ini sebagai input untuk menentukan potensi \
             \nterjadinya banjir. Dengan demikian, pengguna dapat dengan cepat mengetahui risiko banjir pada hari-hari yang diforecast. \
             \nHasil dari model prediksi ini memberikan informasi yang sangat berharga bagi pihak terkait untuk mengambil langkah-langkah  \
             \nmitigasi bencana yang efektif. Dengan memahami potensi risiko banjir, pihak terkait dapat bersiap-siap dan \
             \nmengimplementasikan tindakan pencegahan guna mengurangi dampak bencana di Kabupaten Cilacap."
    )    

def process_forecast_data(forecast_data):
 
    # Memanggil Model
    model = load_model()

    # Judul Halaman
    st.title("Prediksi Kejadian Banjir")

    # Membuat Inputan Data
    col1, col2 = st.columns(2)

    with col1:
        selected_date = st.date_input('Pilih Tanggal', datetime.today())

        # Mengisi ulang nilai formulir jika tanggal berubah
        if selected_date not in state.previous_values:
            state.previous_values[selected_date] = {
                'rainfall_00': None,
                'rainfall_300': None,
                'rainfall_600': None,
                'rainfall_900': None,
                'rainfall_1200': None,
                'rainfall_1500': None,
                'rainfall_2100': None
            }
        
        # Check if the formatted selected_date is in forecast_data
        formatted_forecast_dates = forecast_data['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
        selected_date_str = selected_date.strftime('%Y-%m-%d %H:%M:%S')

        # Check apakah selected_date ada dalam forecast_data
        if selected_date_str in formatted_forecast_dates.values:
            hujan_0_value = round(forecast_data.loc[formatted_forecast_dates == selected_date_str, 'hujan_0'].values[0], 2)
            state.previous_values[selected_date]['rainfall_00'] = hujan_0_value

            hujan_300_value = round(forecast_data.loc[formatted_forecast_dates == selected_date_str, 'hujan_300'].values[0], 2)
            state.previous_values[selected_date]['rainfall_300'] = hujan_300_value

            hujan_600_value = round(forecast_data.loc[formatted_forecast_dates == selected_date_str, 'hujan_600'].values[0], 2)
            state.previous_values[selected_date]['rainfall_600'] = hujan_600_value

            hujan_900_value = round(forecast_data.loc[formatted_forecast_dates == selected_date_str, 'hujan_900'].values[0], 2)
            state.previous_values[selected_date]['rainfall_900'] = hujan_900_value

            hujan_1200_value = round(forecast_data.loc[formatted_forecast_dates == selected_date_str, 'hujan_1200'].values[0], 2)
            state.previous_values[selected_date]['rainfall_1200'] = hujan_1200_value

            hujan_1500_value = round(forecast_data.loc[formatted_forecast_dates == selected_date_str, 'hujan_1500'].values[0], 2)
            state.previous_values[selected_date]['rainfall_1500'] = hujan_1500_value

            hujan_2100_value = round(forecast_data.loc[formatted_forecast_dates == selected_date_str, 'hujan_2100'].values[0], 2)
            state.previous_values[selected_date]['rainfall_2100'] = hujan_2100_value
            
        else:
            hujan_0_value = None
            hujan_300_value = None
            hujan_600_value = None
            hujan_900_value = None
            hujan_1200_value = None
            hujan_1500_value = None
            hujan_2100_value = None
    
        # Menetapkan Parameter Kunci untuk Inputan Baru
        key_00 = f"rainfall_00_{selected_date}"
        key_300 = f"rainfall_300_{selected_date}"
        key_600 = f"rainfall_600_{selected_date}"
        
        rainfall_00 = st.text_input('Input Nilai Curah Hujan 00:00', key=key_00, value=state.previous_values[selected_date]['rainfall_00'] if state.previous_values[selected_date]['rainfall_00'] is not None else hujan_0_value)
        rainfall_300 = st.text_input('Input Nilai Curah Hujan 03:00', key=key_300, value=state.previous_values[selected_date]['rainfall_300'] if state.previous_values[selected_date]['rainfall_300'] is not None else hujan_300_value)
        rainfall_600 = st.text_input('Input Nilai Curah Hujan 06:00', key=key_600, value=state.previous_values[selected_date]['rainfall_600'] if state.previous_values[selected_date]['rainfall_600'] is not None else hujan_600_value)
    
    with col2:
        # Menetapkan Parameter Kunci untuk Inputan Baru
        key_900 = f"rainfall_900_{selected_date}"
        key_1200 = f"rainfall_1200_{selected_date}"
        key_1500 = f"rainfall_1500_{selected_date}"
        key_2100 = f"rainfall_2100_{selected_date}"

        rainfall_900 = st.text_input('Input Nilai Curah Hujan 09:00', key=key_900, value=state.previous_values[selected_date]['rainfall_900'] if state.previous_values[selected_date]['rainfall_900'] is not None else hujan_900_value)
        rainfall_1200 = st.text_input('Input Nilai Curah Hujan 12:00', key=key_1200, value=state.previous_values[selected_date]['rainfall_1200'] if state.previous_values[selected_date]['rainfall_1200'] is not None else hujan_1200_value)
        rainfall_1500 = st.text_input('Input Nilai Curah Hujan 15:00', key=key_1500, value=state.previous_values[selected_date]['rainfall_1500'] if state.previous_values[selected_date]['rainfall_1500'] is not None else hujan_1500_value)
        rainfall_2100 = st.text_input('Input Nilai Curah Hujan 21:00', key=key_2100, value=state.previous_values[selected_date]['rainfall_2100'] if state.previous_values[selected_date]['rainfall_2100'] is not None else hujan_2100_value)

    # Menampilkan Hasil Prediksi Banjir
    hasil_prediksi = ""

    if st.button("Prediksi Banjir"):
        try:
            rainfall_values = [float(rainfall_00), float(rainfall_300), float(rainfall_600),
                                float(rainfall_900), float(rainfall_1200), float(rainfall_1500),
                                float(rainfall_2100)]

            min_rainfall, max_rainfall, avg_rainfall = calculate_metrics(rainfall_values)

            # Menggabungkan Nilai min_rainfall, max_rainfall, avg_rainfall
            input_features = [float(rainfall_00), float(rainfall_300), float(rainfall_600),
                            float(rainfall_900), float(rainfall_1200), float(rainfall_1500),
                            float(rainfall_2100), min_rainfall, max_rainfall, avg_rainfall]

            # Model Melakukan Prediksi
            hasil_prediksi = model.predict([input_features])
            hasil_prediksi = "Banjir" if hasil_prediksi[0] == 1 else "Tidak Banjir"

            # Menambahkan hasil prediksi ke DataFrame
            new_data = {'date': [selected_date.strftime('%Y-%m-%d')],
                        'Kejadian': [hasil_prediksi],
                        'hujan_00': [float(rainfall_00)],
                        'hujan_300': [float(rainfall_300)],
                        'hujan_600': [float(rainfall_600)],
                        'hujan_900': [float(rainfall_900)],
                        'hujan_1200': [float(rainfall_1200)],
                        'hujan_1500': [float(rainfall_1500)],
                        'hujan_2100': [float(rainfall_2100)],
                        'min_hujan': [min_rainfall],
                        'max_hujan': [max_rainfall],
                        'avg_hujan': [avg_rainfall]}           

            state.all_data = pd.concat([state.all_data, pd.DataFrame(new_data)], ignore_index=True)

            # Memperbarui nilai-nilai sebelumnya
            state.previous_values[selected_date]['rainfall_00'] = rainfall_00
            state.previous_values[selected_date]['rainfall_300'] = rainfall_300
            state.previous_values[selected_date]['rainfall_600'] = rainfall_600
            state.previous_values[selected_date]['rainfall_900'] = rainfall_900
            state.previous_values[selected_date]['rainfall_1200'] = rainfall_1200
            state.previous_values[selected_date]['rainfall_1500'] = rainfall_1500
            state.previous_values[selected_date]['rainfall_2100'] = rainfall_2100

        except ValueError:
            st.warning("Please enter valid numeric values for rainfall.")
            hasil_prediksi = ""

    # Menampilkan Alert Sukses bila Berhasil
    st.success(hasil_prediksi)

    # Menampilkan DataFrame hasil prediksi
    state.all_data = state.all_data.sort_values(by=['date'], ascending=True)
    state.all_data = state.all_data.reset_index(drop=True)
    st.table(state.all_data)

    # Membuat Tombol untuk Download Dataframe ke Bentuk CSV
    if not state.all_data.empty:
        csv_data = state.all_data.to_csv(index=False)
        st.download_button(label="Download CSV", data=csv_data, file_name='prediction.csv', key='download_button')

    # Menampilkan penjelasan dari data di atas
    st.text("Setelah mendapatkan prediksi curah hujan, model prediksi mengambil nilai-nilai ini sebagai input untuk menentukan potensi \
            \nterjadinya banjir. Dengan demikian, pengguna dapat dengan cepat mengetahui risiko banjir pada hari-hari yang diforecast. \
            \nHasil dari model prediksi ini memberikan informasi yang sangat berharga bagi pihak terkait untuk mengambil langkah-langkah  \
            \nmitigasi bencana yang efektif. Dengan memahami potensi risiko banjir, pihak terkait dapat bersiap-siap dan \
            \nmengimplementasikan tindakan pencegahan guna mengurangi dampak bencana di Kabupaten Cilacap."
    )

def app():
    global state  # Mendeklarasikan variabel state sebagai variabel global

    # Mengambil nilai forecast_df dari modul forecast_module
    forecast_data = get_forecast_data()

    # Check if forecast_data is empty
    if forecast_data.empty:
        process_data()
    else:
        # Jika forecast_data tidak kosong, panggil fungsi process_forecast_data
        process_forecast_data(forecast_data)
