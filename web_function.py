import streamlit as st
import pandas as pd
import numpy as np

def preprocess_dataframe(df, freq):
    # Melt DataFrame to combine columns 'date' and 'hour' into 'waktu' and 'curah_hujan'
    df = pd.melt(df, id_vars=['date'], var_name='hour', value_name='curah_hujan')

    # Transform 'hour' into a datetime format
    df['hour'] = df['hour'].str.replace('hujan_', '')  # Remove "hujan_"
    df['hour'] = df['hour'].str.pad(width=4, side='left', fillchar='0')  # Pad 'hour' with leading zeros
    df['waktu'] = pd.to_datetime(df['date'] + ' ' + df['hour'], format='%Y-%m-%d %H%M')

    # Sort the DataFrame based on the 'waktu' column in ascending order
    df = df.sort_values(by='waktu', ascending=True)

    # Drop the 'date' and 'hour' columns that are no longer needed
    df = df.drop(columns=['date', 'hour'])

    # Reset the index
    df = df.reset_index(drop=True)

    # Convert the 'waktu' column to datetime format if it's not already
    df['waktu'] = pd.to_datetime(df['waktu'], format='%Y-%m-%d %H:%M:%S')

    # Set the 'waktu' column as the index
    df.set_index('waktu', inplace=True)

    # Check if a resampling frequency is provided
    if freq:
        # Resample the data according to the specified frequency and sum the 'curah_hujan' values
        df = df.resample(freq).mean()

        # Fill missing values with the mean of the previous and next hours
        df['curah_hujan'] = df['curah_hujan'].interpolate()

        return df
    else:
        # If resample_freq is empty, return the preprocessed DataFrame without resampling
        return df

def load_data(file_path, index_col=None):
    # index_col akan diabaikan jika None
    df = pd.read_csv(file_path, index_col=index_col)
    return df
    
# Initialize forecast_df as an empty DataFrame
forecast_df = pd.DataFrame()

def set_forecast_data(df):
    global forecast_df
    forecast_df = df.copy()

def get_forecast_data():
    global forecast_df
    return forecast_df.copy()