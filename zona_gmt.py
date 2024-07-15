from datetime import datetime
from datetime import datetime
import pytz
import ddbb as con

paises = [
    'Argentina', 'Bolivia', 'Brasil', 'Canadá', 'Chile', 'Colombia', 'Costa Rica', 
    'Cuba', 'Ecuador', 'El Salvador', 'España', 'Estados Unidos', 'Granada', 
    'Guatemala', 'Haití', 'Honduras', 'Jamaica', 'México', 'Nicaragua', 'Panamá', 
    'Paraguay', 'Perú', 'República Dominicana', 'Uruguay', 'Venezuela'
]

paises_zonas_horarias = {
    'Argentina': 'America/Argentina/Buenos_Aires',
    'Bolivia': 'America/La_Paz',
    'Brasil': 'America/Sao_Paulo',
    'Canadá': 'America/Toronto',
    'Chile': 'America/Santiago',
    'Colombia': 'America/Bogota',
    'Costa Rica': 'America/Costa_Rica',
    'Cuba': 'America/Havana',
    'Ecuador': 'America/Guayaquil',
    'El Salvador': 'America/El_Salvador',
    'España': 'Europe/Madrid',
    'Estados Unidos': 'America/New_York',
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

def obtener_gmt(paises_zonas_horarias):
    gmt_dict = {}
    for pais, zona_horaria in paises_zonas_horarias.items():
        tz = pytz.timezone(zona_horaria)
        now = datetime.now(tz)
        gmt = now.utcoffset().total_seconds() / 3600
        gmt_dict[pais] = int(gmt)
    return gmt_dict

def df_gmt():
      df = con.load_data()
      gmt_paises = obtener_gmt(paises_zonas_horarias)
      df['Zona Horaria'] = df['País'].map(paises_zonas_horarias)
      df['GMT'] = df['País'].map(gmt_paises)
      return df

def convertir_a_gmt(horas, zona_horaria):
    tz = pytz.timezone(zona_horaria)
    horas_gmt = []
    for hora in horas:
        local_time = datetime.strptime(f'2024-01-01 {hora}:00', '%Y-%m-%d %H:%M')  # Fecha ficticia para la conversión
        local_dt = tz.localize(local_time)
        gmt_dt = local_dt.astimezone(pytz.utc)
        horas_gmt.append(gmt_dt.strftime('%H:%M'))
    return ', '.join(horas_gmt)

def df_final():
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        df=df_gmt()
        for dia in dias_semana:
            df[f'{dia}'] = df.apply(lambda row: convertir_a_gmt(row[dia].split(', '), row['Zona Horaria']), axis=1)
        # df_zona_gmt=df[[f'{dia}' for dia in dias_semana]]
        return df
