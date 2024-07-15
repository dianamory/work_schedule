import streamlit as st
import pandas as pd
import re
import requests


@st.cache_data(ttl=600)
def load_data():
    gsheetid = '13RwOemvOpn1g3SkWZoN_y_fbXfzdHJdVh1vlqgFqeX0'
    sheetid = '1140708899'
    url = f'https://docs.google.com/spreadsheets/d/{gsheetid}/export?format=csv&gid={sheetid}'

    try:
        df = pd.read_csv(url)
        # print(df)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Google Sheets: {e}")

    for col in df.columns:
      if col.startswith("Horas disponibles"):
        df[col] = df[col].apply(eliminar_franjas)
    df.rename(columns={col: renombrar_columna(col) for col in df.columns if col.startswith("Horas disponibles")}, inplace=True)
    return df

def eliminar_franjas(franjas):
    if pd.isna(franjas):
        return franjas
    franjas_list = franjas.split(', ')
    franjas_limpias = [re.sub(r'-\d+', '', franja).strip() for franja in franjas_list]
    franjas_limpias = [franja for franja in franjas_limpias if franja]
    return ', '.join(franjas_limpias)

def renombrar_columna(col):
    match = re.search(r'\[(.*?)\]', col)
    return match.group(1) if match else col

# print(load_data())