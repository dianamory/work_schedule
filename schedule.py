import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
from collections import defaultdict
import data as data

st.set_page_config(page_title="schedule", page_icon="📅", layout="wide")
df = data.data_final()

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'group' not in st.session_state:
    st.session_state.group = None

def check_password(password):
    if group == 1:
        return password == "Diana"
    if group == 2:
        return password == "Leo"
    if group == 3:
        return password == "Cleses"
    if group == 4:
        return password == "Zerberus"

if not st.session_state.authenticated:
    st.title("Bienvenido al Planificador de Horarios")
    group = st.radio("Selecciona tu grupo:", df['Grupo'].unique())
    password = st.text_input("Ingresa la clave de acceso:", type="password")

    if st.button("Acceder"):
        if check_password(password):
            st.session_state.authenticated = True
            st.session_state.group = group
            st.experimental_rerun()
        else:
            st.error("Clave de acceso incorrecta. Intenta de nuevo.")

if st.session_state.authenticated:
      df = df[df['Grupo'] == st.session_state.group]
      grupo = int(df.Grupo.unique()[0])

      def process_time_slots(time_slots):
         intervals = time_slots.split(', ')
         result = []
         for interval in intervals:
            if interval.strip() == '24:00':
                  interval = '00:00'
            start = datetime.strptime(interval.strip(), '%H:%M')
            end = start + timedelta(hours=1)
            result.append((start, end))
         return result
      
      def find_common_time_slots(df, min_members=2):
         common_slots = defaultdict(list)
         for day in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']:
            day_data = []
            for _, row in df.iterrows():
                  slots = process_time_slots(row[day])
                  for slot in slots:
                     day_data.append((slot, row['Nombre']))
            day_data.sort()

            start_time = None
            current_count = 0
            current_members = []

            for time, member in day_data:
                  if start_time is None:
                     start_time = time[0]
                     current_count = 1
                     current_members = [member]
                  else:
                     if time[0] < start_time + timedelta(hours=1):
                        current_count += 1
                        current_members.append(member)
                     else:
                        if current_count >= min_members:
                              common_slots[day].append({
                                 'start': start_time,
                                 'end': start_time + timedelta(hours=1),
                                 'count': current_count,
                                 'members': current_members.copy()
                              })
                        start_time = time[0]
                        current_count = 1
                        current_members = [member]

            if current_count >= min_members:
                  common_slots[day].append({
                     'start': start_time,
                     'end': start_time + timedelta(hours=1),
                     'count': current_count,
                     'members': current_members.copy()
                  })

         return common_slots

      st.markdown("""<style>
      #root > div:nth-child(1) > div.withScreencast > div > div > div > section.main.st-emotion-cache-bm2z3a.ea3mdgi8 > div.block-container.st-emotion-cache-1jicfl2.ea3mdgi5{
      padding:.5rem 1rem 1rem 1rem !important;
      }
      #root > div:nth-child(1) > div.withScreencast > div > div > div > section.st-emotion-cache-1itdyc2.eczjsme18{
      width: 10rem !important;
      }                    
      </style>""", unsafe_allow_html=True)

      st.sidebar.subheader('Filtrar por cantidad')
      num_unique_names = df['Nombre'].nunique()
      min_members = st.sidebar.number_input(label='', min_value=2, max_value=num_unique_names, value=min(2, num_unique_names), step=1, label_visibility='collapsed')

      st.sidebar.subheader('Filtrar por Miembro')
      selected_members = []
      for member in sorted(df['Nombre'].unique()):
         if st.sidebar.checkbox(member, value=True):
               selected_members.append(member)

      if selected_members:
         df = df[df['Nombre'].isin(selected_members)]

      common_slots = find_common_time_slots(df, min_members)

      fig = go.Figure()

      days_order = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
      colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692']

      for i, day in enumerate(days_order):
         if day in common_slots:
               for slot in common_slots[day]:
                  members_text = ', '.join(slot['members'])
                  fig.add_trace(go.Bar(
                     x=[day],
                     y=[(slot['end'] - slot['start']).total_seconds() / 3600],
                     base=[slot['start'].hour + slot['start'].minute / 60],
                     marker_color=colors[i % len(colors)],
                     name=f"{day} {slot['start'].strftime('%H:%M')} - {slot['end'].strftime('%H:%M')}",
                     text=f"{len(set(members_text.split(', ')))} miembros<br>" + "<br>".join(list(set(members_text.split(', ')))),
                     hoverinfo='text',
                     hovertemplate="<b>%{x}</b><br>"
                                    "Inicio: %{base:.2f}<br>"
                                    "Fin: %{y:.2f}<br>"
                                    "<extra></extra>"
                  ))

      title_format = {
         'text': f'Grupo {grupo}: Franjas horarias comunes GMT',
         'font': {'size': 35, 'color': '#1f77b4'},
         'xref': 'paper',
         'x': 0.5,
         'y': 0.95,
         'xanchor': 'center',
         'yanchor': 'top'
      }

      fig.update_layout(
         title=title_format,
         xaxis_title='',
         yaxis_title='',
         barmode='stack',
         height=750,
         yaxis=dict(
               tickmode='array',
               tickvals=list(range(24)),
               ticktext=[f"{h:02d}:00 hs" for h in range(24)]
         ),
         hovermode='closest',
         showlegend=False
      )

      st.plotly_chart(fig, use_container_width=True)
      st.dataframe(df[['Nombre', 'País', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']])

      if selected_members:
         filtered_df = df[df['Nombre'].isin(selected_members)]
         st.sidebar.markdown("<h3 style='text-align: center;'>Miembros</h3>", unsafe_allow_html=True)

         st.sidebar.table(filtered_df[['Nombre', 'País', 'GMT']].style
                           .set_properties(**{'text-align': 'left'})
                           .set_table_styles([
                              {'selector': 'th', 'props': [('text-align', 'left'), ('font-weight', 'bold')]},
                              {'selector': '.row_heading, .blank', 'props': [('display', 'none')]},
                              {'selector': 'td', 'props': [('text-align', 'left')]},
                              {'selector': 'td:nth-child(2)', 'props': [('font-size', '0.8em')]},
                              {'selector': 'td:nth-child(3)', 'props': [('font-size', '0.8em')]},
                              {'selector': 'td:nth-child(4)', 'props': [('font-size', '0.8em')]}

                           ])
                           .highlight_max(color='lightgreen', axis=0, subset=['GMT'])
                           .highlight_min(color='lightcoral', axis=0, subset=['GMT']))
      else:
         st.subheader('Datos de disponibilidad originales')
         st.dataframe(df[['Nombre', 'País', 'GMT']])

      st.sidebar.subheader('Si es 15:00 GMT y estás en un huso horario GMT-5, la hora local es 10:00 (15:00 - 5 horas)')
