import pandas as pd
import requests
import re
import pytz
from datetime import datetime

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
    df=df.fillna(1)
    df=df.drop(columns=['Puntuación'])
    return df

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

days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

def consecutive_hours():
    df = load_data()
    for day in days:
        df[day] = df[day].apply(lambda x: ', '.join(map(str, add_consecutive_hours(list(map(int, x.split(', ')))))))
    return df

paises = [
    'Argentina', 'Bolivia', 'Brasil', 'Canadá', 'Chile', 'Colombia', 'Costa Rica',
    'Cuba', 'Ecuador', 'El Salvador', 'España', 'Estados Unidos', 'Granada',
    'Guatemala', 'Haití', 'Honduras', 'Jamaica', 'México', 'Nicaragua', 'Panamá',
    'Paraguay', 'Perú', 'República Dominicana', 'Uruguay', 'Venezuela'
]

# Diccionario con los nombres de los países y sus zonas horarias principales
paises_zonas_horarias = {
    'Argentina': 'America/Argentina/Buenos_Aires',
    'Bolivia': 'America/La_Paz',
    'Brasil': 'America/Sao_Paulo',
    'Canadá': 'America/Toronto', # Puede variar según la región
    'Chile': 'America/Santiago',
    'Colombia': 'America/Bogota',
    'Costa Rica': 'America/Costa_Rica',
    'Cuba': 'America/Havana',
    'Ecuador': 'America/Guayaquil',
    'El Salvador': 'America/El_Salvador',
    'España': 'Europe/Madrid',
    'Estados Unidos': 'America/New_York', # Puede variar según la región
    'Granada': 'America/Grenada',
    'Guatemala': 'America/Guatemala',
    'Haití': 'America/Port-au-Prince',
    'Honduras': 'America/Tegucigalpa',
    'Jamaica': 'America/Jamaica',
    'México': 'America/Mexico_City',
    'Nicaragua': 'America/Managua',
    'Panamá': 'America/Panama',
    'Paraguay': 'America/Asuncion',
    'Perú': 'America/Lima',
    'República Dominicana': 'America/Santo_Domingo',
    'Uruguay': 'America/Montevideo',
    'Venezuela': 'America/Caracas'
}

# Función para obtener el GMT actual para cada zona horaria
def obtener_gmt(paises_zonas_horarias):
    gmt_dict = {}
    for pais, zona_horaria in paises_zonas_horarias.items():
        tz = pytz.timezone(zona_horaria)
        now = datetime.now(tz)
        gmt = now.utcoffset().total_seconds() / 3600
        gmt_dict[pais] = int(gmt)
        # gmt_dict[pais] = f"GMT {gmt:+}"
    return gmt_dict

def gmt():
    df=consecutive_hours()
    gmt_paises = obtener_gmt(paises_zonas_horarias)
    df['Zona Horaria'] = df['País'].map(paises_zonas_horarias)
    df['GMT'] = df['País'].map(gmt_paises)
    return df

dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

def convertir_a_gmt(horas, zona_horaria):
    tz = pytz.timezone(zona_horaria)
    horas_gmt = []
    for hora in horas:
        # Manejar la hora '24' convirtiéndola a '00' del día siguiente
        if hora == '24':
            local_time = datetime.strptime('2024-01-02 00:00', '%Y-%m-%d %H:%M')  # Día siguiente a medianoche
        else:
            local_time = datetime.strptime(f'2024-01-01 {hora}:00', '%Y-%m-%d %H:%M')  # Fecha ficticia para la conversión

        local_dt = tz.localize(local_time)
        gmt_dt = local_dt.astimezone(pytz.utc)
        horas_gmt.append(gmt_dt.strftime('%H:%M'))
    return ', '.join(horas_gmt)

def df_final():
  df=gmt()
  for dia in dias_semana:
    df[f'{dia}'] = df.apply(lambda row: convertir_a_gmt(row[dia].split(', '), row['Zona Horaria']), axis=1)
  return df

# Función para ordenar los valores de las columnas
def data_final():
    df=df_final()
    def ordenar_horas(column):
        def convertir_y_ordenar(horas):
            horas_lista = horas.split(', ')
            horas_lista = sorted(horas_lista, key=lambda x: datetime.strptime(x, '%H:%M'))
            return ', '.join(horas_lista)
        
        df[column] = df[column].apply(convertir_y_ordenar)

    for dia in dias_semana:
        ordenar_horas(dia)  
    return df
# print(df_final()[['Nombre', 'País', 'Lunes', 'Martes', 'Miércoles']])