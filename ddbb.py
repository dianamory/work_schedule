import streamlit as st
import pandas as pd
import re
import requests

days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

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
    for day in days:
        df[day] = df[day].apply(lambda x: ', '.join(map(str, add_consecutive_hours(list(map(int, x.split(', ')))))))
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


# La función para procesar las listas de horas
def add_consecutive_hours(hour_list):
    if not hour_list:
        return hour_list
    
    hour_list = sorted(hour_list)
    new_list = []

    for i in range(len(hour_list)):
        new_list.append(hour_list[i])
        # Verificar si el número actual no es el último y no tiene consecutivo
        if (i < len(hour_list) - 1 and hour_list[i] + 1 != hour_list[i + 1]) or (i == len(hour_list) - 1):
            next_hour = hour_list[i] + 1
            if next_hour == 25:  # Si la hora es 24, reiniciar a 1
                next_hour = 1
            new_list.append(next_hour)
    
    return sorted(set(new_list))

print(load_data())