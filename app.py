import os

import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import yfinance as yf
from datetime import datetime
import time


# SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
st.set_page_config(layout="wide", page_title="Market Watch", page_icon=":money:")


# LOAD DATA ONCE
@st.cache_resource
def load_data(download_new_data,exchanges,indexes,start_date,end_date):
    download_new_data = download_new_data

    stock_exchanges = exchanges
    indexes = indexes
    data_list = indexes

    start_date = start_date
    end_date = end_date

    file_out = 'raw_data.xlsx'
    sheet_out = 'df_raw' 
    # Definiton of Dataframes
    df_raw = pd.DataFrame()

    if download_new_data == 1:
        for data in data_list:
            if data == 'BSE':
                x = '^BSESN'   
            if data == 'Hong Kong':
                x = '^HSI'
            if data == 'Nasdaq100':
                x = '^NDX'
            if data == 'S&P500':
                x = '^GSPC'       
            if data == 'Nifty50':
                x = '^NSEI'
            if data == 'FTSE100':
                x = '^FTSE'
            if data == 'DAX40':
                x = '^GDAXI'
            if data == 'Euronext100':
                x = '^N100'
            if data == 'CSI300':
                x = '000300.SS'

                
            df_raw[data] = yf.download(x, start=start_date, end=end_date)['Close']

    else:
        df_raw = pd.read_excel(file_out,sheet_out)

    df_raw = df_raw.reset_index()
    df_raw['Year'], df_raw['Month'], df_raw['Date_n'] = df_raw['Date'].astype(str).str.split('-', 2).str
    df_raw['ymd']=df_raw['Year'].astype(str)+df_raw['Month'].astype(str)+df_raw['Date_n'].astype(str)
    # df_raw['ymd'] = df_raw['ymd'].astype(int)
    df_raw = df_raw.set_index('Date')
    
    return df_raw, file_out, sheet_out


download_new_data = 1

exchanges = ['BSE','Hong Kong']
indexes = ['BSE','Nasdaq100','S&P500','FTSE100','Nifty50','DAX40','Euronext100']
data_list = indexes

st.sidebar.button('Refresh')
st.sidebar.button('Update Database')

year = st.sidebar.slider('Year',1950,2024,(2020,2024))
# st.sidebar.year = st.slider('Year',1950,2024,(2020,2024))
month = st.sidebar.slider('Month',1,12,(2,3))
date = st.sidebar.slider('Date',1,31,(5,7))

s_year, e_year = year
s_month, e_month = month
s_date, e_date = date
s_month, e_month, s_date, e_date = "{:02d}".format(s_month), "{:02d}".format(e_month), "{:02d}".format(s_date), "{:02d}".format(e_date)


# start_date = '1986-01-01'
start_date = str(s_year)+'-'+str(s_month)+'-'+str(s_date)
end_date = str(e_year)+'-'+str(e_month)+'-'+str(e_date)

abs_gain_date = start_date

# Calculate the moving average with a window size of 3
window_mov_avg = 7



# Definiton of Dataframes

df_raw = pd.DataFrame()
df_mav = pd.DataFrame()
df_normperyear = pd.DataFrame()
df_normmax = pd.DataFrame()
df_diff = pd.DataFrame()
df_gain = pd.DataFrame()





df_raw, file_out, sheet_out = load_data(download_new_data,exchanges,indexes,start_date,end_date)




ymd_abs_gain_start_val = abs_gain_date.split('-')[0]+abs_gain_date.split('-')[1]+abs_gain_date.split('-')[2]


for data in data_list:
    df_normperyear[data] = df_raw[data]/df_raw.groupby('Year')[data].transform('max')
    df_normmax[data] = df_raw[data]/max(df_raw[data].dropna())
    df_normmax[data] = df_normmax[data].rolling(window=window_mov_avg).mean()
    df_mav[data] = df_raw[data].rolling(window=window_mov_avg).mean()
    df_diff[data] = np.diff(df_raw[data])
    df_gain[data] = ((df_raw[data] - df_raw.query('ymd==@ymd_abs_gain_start_val')[data][0])/df_raw.query('ymd==@ymd_abs_gain_start_val')[data][0]*100).rolling(window=window_mov_avg).mean()


sub_list = ['Nasdaq100','Nifty50']

df_gain_sub = df_gain[sub_list]

# Export data to excel

if download_new_data == 1:
    
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(file_out, engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet.
    df_raw.to_excel(writer, sheet_name=sheet_out)
    # df2.to_excel(writer, sheet_name='Sheet2')
    
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()

st.title('Gain (%) from '+abs_gain_date+' to '+end_date)
st.line_chart(df_gain)


st.dataframe(df_raw)
st.dataframe(df_gain)