# def prepare_member_availability(df):
#     availability = {}
#     for day in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']:
#         availability[day] = {}
#         for _, row in df.iterrows():
#             slots = process_time_slots(row[day])
#             availability[day][row['Nombre']] = slots
#     return availability

# def create_horizontal_bar_chart(day_data, day):
#     fig = go.Figure()
    
#     for member, slots in day_data.items():
#         for start, end in slots:
#             fig.add_trace(go.Bar(
#                 y=[member],
#                 x=[(end - start).total_seconds() / 3600],
#                 orientation='h',
#                 name=member,
#                 text=f"{start.strftime('%H:%M')} - {end.strftime('%H:%M')}",
#                 hoverinfo='text'
#             ))
    
#     fig.update_layout(
#         title=f"Disponibilidad para {day}",
#         xaxis_title="Horas",
#         yaxis_title="Miembros",
#         barmode='stack',
#         height=400,
#         showlegend=False
#     )
    
#     return fig

# # Preparar datos de disponibilidad
# availability = prepare_member_availability(df)

# # Crear y mostrar gráficas por día
# st.subheader("Disponibilidad por miembro y día")
# for day in ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']:
#     fig = create_horizontal_bar_chart(availability[day], day)
#     st.plotly_chart(fig, use_container_width=True)