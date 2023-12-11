import streamlit as st
import pandas as pd
from web_function import load_data, set_forecast_data
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import joblib

# Load model machine learning
def load_model(model_path):
    model = joblib.load('models/forecast/' + model_path)
    return model

def app():
    
    # Judul Halaman
    st.title("Forecast Curah Hujan")

    ## Memanggil Model
    # Update the paths to your model files
    model_paths = ['hujan_0_model.pkl', 'hujan_300_model.pkl', 'hujan_600_model.pkl',
                   'hujan_900_model.pkl',
                   'hujan_1200_model.pkl', 'hujan_1500_model.pkl', 'hujan_2100_model.pkl'
                   ] 

    models = [load_model(path) for path in model_paths]

    # Data Historis Banjir
    df = load_data("data/cilacap_hujan.csv")
    df['date'] = pd.to_datetime(df['date'])
    df.set_index(['date'], inplace=True)

    columns = ['hujan_0', 'hujan_300', 'hujan_600', 'hujan_900', 'hujan_1200', 'hujan_1500', 'hujan_2100']

    # Membuat Tabel Kosong untuk Menampung Semua Hasil Forecast
    concatenated_df = pd.DataFrame()
    
    # Menentukan Jumlah Hari yang ingin Diforecast
    n_days = st.slider("Tentukan Jumlah Hari Forecast:", 1, 365, step=1)
    st.write("Forecast untuk {} hari kedepan".format(n_days))

    # When the "Predict" button is clicked
    if st.button("Predict"):
        for col, model_path in zip(columns, model_paths):
            # Get the corresponding DataFrame
            df_hujan = df[col]

            # Load the corresponding model
            model = load_model(model_path)

            # Perform the forecast
            pred = abs(model.forecast(n_days))  # Replace 'forecast' with the actual method in your model
            pred = pd.DataFrame(pred, columns=['curah_hujan'])

            # # Menggabungkan Data Kedalam Tabel Kosong
            concatenated_df[col] = pred['curah_hujan']
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.subheader(f"Hasil Forecast - {col}")
                st.write(pred)

            with col2:
                # Append the forecasted values to the historical data
                df_hujan = pd.concat([df_hujan, pred['curah_hujan']])
                df_hujan.index = pd.date_range(start=df.index[-1], periods=len(df_hujan))

                fig = make_subplots(rows=1, cols=1, subplot_titles=[f'Curah Hujan - {col}'])
                trace = go.Scatter(x=df.index, y=df_hujan.iloc[:-n_days], mode='lines', name='Historical Data')
                trace_pred = go.Scatter(x=pd.date_range(start=df.index[-1], periods=n_days+1, freq='D')[1:],
                                       y=pred['curah_hujan'], mode='lines', name='Forecast')

                trace.marker.line.color = 'blue'
                trace_pred.marker.line.color= 'red'

                fig.add_trace(trace)
                fig.add_trace(trace_pred)

                fig.update_layout(
                    showlegend=True,
                    xaxis_rangeslider_visible=True,
                    hovermode='x',
                    xaxis=dict(title_text='Waktu'),
                    yaxis=dict(title_text='Curah Hujan (mm)'),
                )

                fig.update_traces(
                    hovertemplate='<b>Waktu</b>: %{x}<br><b>Curah Hujan</b>: %{y:.2f} mm',
                )

                st.plotly_chart(fig, use_container_width=True)

  
     # Menghitung nilai minimum, maksimum, dan rata-rata curah hujan per tanggal
    concatenated_df['min_hujan'] = concatenated_df.min(axis=1)
    concatenated_df['max_hujan'] = concatenated_df.max(axis=1)
    concatenated_df['avg_hujan'] = concatenated_df.iloc[:, 0:7].mean(axis=1)

    concatenated_df = concatenated_df.reset_index()
    concatenated_df = concatenated_df.rename(columns={'index': 'date'})

    # Menampilkan Tabel Hasil Concatenated
    st.subheader("Tabel Hasil Forecast Curah Hujan untuk {} Hari Kedepan".format(n_days))
    st.write(concatenated_df)

    # Membuat Tombol untuk Download Dataframe ke Bentuk CSV
    if not concatenated_df.empty:
        csv_data = concatenated_df.to_csv(index=False)
        st.download_button(label="Download CSV", data=csv_data, file_name='forecast.csv', key='download_button')

    set_forecast_data(concatenated_df)

    # Menampilkan penjelasan dari data diatas
    st.text("Setelah melakukan forecasting curah hujan, nilai-nilai hasil prediksi tersebut dapat dijadikan sebagai input\
             \nuntuk model prediksi yang lebih lanjut. Data forecasting ini mencakup estimasi jumlah curah hujan untuk interval waktu\
             \ntertentu di masa depan, yang diperoleh melalui metode forecasting yang telah diimplementasikan sebelumnya."
    )    

