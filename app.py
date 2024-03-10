import os

import altair as alt
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import yfinance as yf
from datetime import datetime
import time

t0 = time.time()

# SETTING PAGE CONFIG TO WIDE MODE AND ADDING A TITLE AND FAVICON
st.set_page_config(layout="wide", page_title="Market Watch", page_icon=":money:")


# LOAD DATA ONCE
@st.cache_resource
def load_data(download_new_data,exchanges,indexes,start_date,end_date):
    download_new_data = download_new_data

    exchanges = exchanges
    indexes = indexes
    data_list = exchanges + indexes

    # start_date = start_date
    start_date = '1900-01-01'
    end_date = datetime.today().strftime('%Y-%m-%d')
    # st.sidebar.write(end_date)
    file_out = 'raw_data.xlsx'
    sheet_out = 'df_raw' 
    # Definiton of Dataframes
    df_raw = pd.DataFrame()

    if download_new_data == 1:
        for data in data_list:
            if data == 'BSE':
                x = '^BSESN'   
            if data == 'DJI':
                x = '^DJI'
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

download_new_data = 0
if st.sidebar.button('Update Database'):
    download_new_data = 1
    st.sidebar.write('Last updated on '+str(datetime.today()))

st.sidebar.button('Refresh')

gain_toggle = st.sidebar.toggle('Gain %')

year = st.sidebar.slider('Year',1991,2024,(2020,2024))
# month = st.sidebar.slider('Month',1,12,2)
# date = st.sidebar.slider('Date',1,31,5)


col1s, col2s = st.sidebar.columns(2)
with col1s:
    month = st.sidebar.number_input('Month',1,12,1,1)
with col2s:
    date = st.sidebar.number_input('Date',1,31,1,1)


exchanges = ['BSE','DJI','Hong Kong','Dax40']
indexes = ['Nasdaq100','S&P500','FTSE100','Nifty50','DAX40','Euronext100']

indian_market = ['BSE','Nifty50']
world_market = ['DJI','Nasdaq100','S&P500','FTSE100','DAX40','Euronext100']

data_list = []
# indian_market = []
# world_market = []

st.sidebar.text('Stock Exchanges')
if st.sidebar.checkbox('Bombay Stock Exchange'):
    data_list.append('BSE')
if st.sidebar.checkbox('Dow Jones Industrial'):
    data_list.append('DJI')
if st.sidebar.checkbox('DAX40'):
    data_list.append('DAX40')
if st.sidebar.checkbox('Hong Kong'):
    data_list.append('Hong Kong')

st.sidebar.text('Indexes')
if st.sidebar.checkbox('Nasdaq 100'):
    data_list.append('Nasdaq100')
if st.sidebar.checkbox('Nifty 50'):
    data_list.append('Nifty50')
if st.sidebar.checkbox('S&P500'):
    data_list.append('S&P500')
if st.sidebar.checkbox('FTSE100'):
    data_list.append('FTSE100')

if st.sidebar.checkbox('Euronext100'):
    data_list.append('Euronext100')


# data_list = indexes

s_year, e_year = year
s_month, e_month = month, month
s_date, e_date = date, date
s_month, e_month, s_date, e_date = "{:02d}".format(s_month), "{:02d}".format(e_month), "{:02d}".format(s_date), "{:02d}".format(e_date)


start_date = str(s_year)+'-'+str(s_month)+'-'+str(s_date)
end_date = str(e_year)+'-'+str(e_month)+'-'+str(e_date)

abs_gain_date = start_date

# Calculate the moving average with a window size of 3
window_mov_avg = st.sidebar.slider('Average over days:',1,100,1)



# Definiton of Dataframes
df_raw_main = pd.DataFrame()
df_raw = pd.DataFrame()
df_mav = pd.DataFrame()
df_normperyear = pd.DataFrame()
df_normmax = pd.DataFrame()
df_diff = pd.DataFrame()
df_gain = pd.DataFrame()
df_raw_re = pd.DataFrame()


df_raw_main, file_out, sheet_out = load_data(download_new_data,exchanges,indexes,start_date,end_date)
df_raw_main.iloc[0] = df_raw_main.iloc[0].combine_first(df_raw_main.dropna().iloc[0])
df_raw = df_raw_main.loc[start_date:end_date]
df_raw.iloc[0] = df_raw.iloc[0].combine_first(df_raw.dropna().iloc[0])


ymd_abs_gain_start_val = abs_gain_date.split('-')[0]+abs_gain_date.split('-')[1]+abs_gain_date.split('-')[2]


for data in data_list:
    df_normperyear[data] = df_raw[data]/df_raw.groupby('Year')[data].transform('max')
    df_normmax[data] = df_raw[data]/max(df_raw[data].dropna())
    df_normmax[data] = df_normmax[data].rolling(window=window_mov_avg).mean()
    df_mav[data] = df_raw[data].rolling(window=window_mov_avg).mean()
    df_diff[data] = np.diff(df_raw[data])
    df_gain[data] = ((df_raw[data] - df_raw[data][0])/df_raw[data][0]*100).rolling(window=window_mov_avg).mean()
    df_raw_re[data] = df_raw[data]


# Export data to excel
if download_new_data == 1:
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(file_out, engine='xlsxwriter')
    # Write each dataframe to a different worksheet.
    df_raw_main.to_excel(writer, sheet_name=sheet_out)
    # df2.to_excel(writer, sheet_name='Sheet2')
    # Close the Pandas Excel writer and output the Excel file.
    writer.save()



st.title(abs_gain_date+' to '+end_date)

if gain_toggle == 1:
    st.header('Gain (%)')
    st.line_chart(df_gain)
else:
    st.header('Data')
    st.line_chart(df_raw_re)



col1, col2 = st.columns(2)

with col1:
   st.header("Indian Market")
   df_gain_sub = pd.DataFrame()
   df_raw_sub = df_raw[indian_market]
   for data in data_list and indian_market:
       df_gain_sub[data] = ((df_raw[data] - df_raw[data][0])/df_raw[data][0]*100).rolling(window=window_mov_avg).mean()

   if gain_toggle == 1:   
       st.line_chart(df_gain_sub)
   else:
       st.line_chart(df_raw_sub)
   
with col2:
   st.header("World Market")
   df_gain_sub = pd.DataFrame()
   df_raw_sub = df_raw[world_market]
   for data in data_list and world_market:
       df_gain_sub[data] = ((df_raw[data] - df_raw[data][0])/df_raw[data][0]*100).rolling(window=window_mov_avg).mean()

   if gain_toggle == 1:   
       st.line_chart(df_gain_sub)
   else:
       st.line_chart(df_raw_sub)



if st.sidebar.toggle('Table shows chart data'):
    st.dataframe(df_raw_re)
else:
    st.dataframe(df_raw_main)


# st.dataframe(df_gain)
fin = time.time()
st.write('Took ',np.round(fin-t0,2),' s to load.')
st.write(np.random.randint(0,10))