import streamlit as st
from utils import *
import altair as alt
import datetime
import pandas as pd
import pydeck as pdk
import numpy as np

st.set_page_config(
    page_title="Homepage",
    page_icon="🏠",
    layout="wide"
)

st.sidebar.title('TrainStats Piemonte')
st.sidebar.header(':blue[Benvenuto!]')
st.sidebar.markdown("In questo portale si possono trovare\nstatistiche e informazioni\nsulla circolazione dei treni\nin Piemonte, per le linee\nnon monitorate\ndall'Agenzia della Mobilità\n\nPer aiuto sull'utilizzo\ndel portale, visitare\nla pagina informazioni\n\n\nStato connessione DB:")

st.title("Homepage")
st.subheader('Statistiche sulle linee ferroviarie piemontesi')

tab1, tab2 = st.tabs(['📈 Statistiche e grafici', '🗺️ Mappa delle stazioni'])

conn = sql_connect('datitreni', 'sql')

with tab1:
    df = conn.query('SELECT NOMELINEA FROM LINEE;', ttl=0, show_spinner=False)
    linee_nome = df['NOMELINEA'].tolist()

    scelta_linea = st.selectbox("Seleziona la linea da visualizzare", linee_nome, index=None, placeholder='Scegli la linea...')
    with st.container(border=True):     # streamlit metric per statistiche sull'ultima settimana
        if scelta_linea != None:
            df2 = conn.query(f"SELECT CodLinea FROM LINEE WHERE NomeLinea='{scelta_linea}';", ttl=0, show_spinner=False)
            scelta_linea_codice = df2['CodLinea'][0]        # query sql per dati sull'ultima settimana \/
            puntualita, puntualita_scorsa_sett = calcola_df_puntualita_iniziali(conn, scelta_linea_codice)
            if puntualita['DATA_DA'][0] == None:
                st.warning("Nessun dato trovato.",icon='⚠️')    # controllo sull'esistenza di dati per la linea selezionata
                st.stop()
            else:
                data_da, data_a, punt_val, r5_val, r15_val, sopp_val, var_val, treni_tot_val = valori_puntualita_iniziali(puntualita)
                if puntualita_scorsa_sett['DATA_DA'][0] == None:
                    st.subheader(f"Riepilogo degli ultimi 7 giorni (dal {data_da} al {data_a}):")
                    colm1,colm2,colm3, colm4, colm5=st.columns(5)
                    colm1.metric(label="Puntualità", value=f'{round(punt_val,2)}%')
                    colm2.metric(label="n° Ritardi da 5 a 14 min", value=r5_val)
                    colm3.metric(label="n° Ritardi superiori a 15 min", value=r15_val)
                    colm4.metric(label="n° Treni soppressi", value=sopp_val)
                    colm5.metric(label="n° Treni variati", value=var_val)
                    st.markdown(f"su **:blue-background[{treni_tot_val}]** treni totali")
                else:
                    delta_or_val, delta_r5_val, delta_r15_val, delta_sopp_val, delta_var_val = valori_delta_puntualita(puntualita_scorsa_sett, punt_val, r5_val, r15_val, sopp_val, var_val)
                    st.subheader(f"Riepilogo degli ultimi 7 giorni (dal {data_da} al {data_a}):")
                    colm1,colm2,colm3, colm4, colm5=st.columns(5)
                    colm1.metric(label="Puntualità", value=f'{round(punt_val,2)}%', delta=f'{round(delta_or_val,2)}%')
                    colm2.metric(label="n° Ritardi da 5 a 14 min ", value=r5_val, delta=delta_r5_val, delta_color='inverse')
                    colm3.metric(label="n° Ritardi superiori a 15 min ", value=r15_val, delta=delta_r15_val, delta_color='inverse')
                    colm4.metric(label="n° Treni soppressi", value=sopp_val, delta=delta_sopp_val, delta_color='inverse')
                    colm5.metric(label="n° Treni variati", value=var_val, delta=delta_var_val, delta_color='inverse')
                    st.markdown(f"su **:blue-background[{treni_tot_val}]** treni totali")

    
    if scelta_linea != None:        # scelta date per visualizzazione grafici
        date=conn.query(f"SELECT MIN(DATA) AS DATAMIN, MAX(DATA) AS DATAMAX FROM CORSE, TRENI WHERE TRENI.NumTreno=CORSE.NumTreno AND LINEA={scelta_linea_codice};", ttl=0, show_spinner="Caricamento...")
        data_min = date['DATAMIN'][0]
        data_max = date['DATAMAX'][0]

        intervallo_date = st.date_input("Scegli l'intervallo di date per i grafici",value=(data_min,data_max),min_value=data_min,max_value=data_max)

    if scelta_linea != None and len(intervallo_date) != 1:
        df2 = conn.query(f"SELECT CodLinea FROM LINEE WHERE NomeLinea='{scelta_linea}';", ttl=0, show_spinner=False)    # estraggo il codice linea dal nome
        scelta_linea_codice = df2['CodLinea'][0]

        chart_media, data_media = grafico_media(conn, intervallo_date, scelta_linea_codice)
        
        if data_media.empty:
            st.warning("Nessun dato trovato.",icon='⚠️')
        else:
            with st.container(border=True):     # statistiche relative a date - calcola puntualità tra date selezionate e visualizza metric
                punt_int_val, r5_int_val, r15_int_val, sopp_int_val, var_int_val, treni_tot_int_val = metrics_intervallo(conn, intervallo_date, scelta_linea_codice)
                st.subheader('Riepilogo relativo alle date selezionate:')
                colm1,colm2,colm3, colm4, colm5 = st.columns(5)
                colm1.metric(label="Puntualità", value=f'{round(punt_int_val,2)}%')
                colm2.metric(label="n° Ritardi da 5 a 14 min", value=r5_int_val)
                colm3.metric(label="n° Ritardi superiori a 15 min", value=r15_int_val)
                colm4.metric(label="n° Treni soppressi", value=sopp_int_val)
                colm5.metric(label="n° Treni variati", value=var_int_val)
                st.markdown(f"su **:blue-background[{treni_tot_int_val}]** treni totali")

            with st.container(border=True):
                st.subheader('Puntualità e numero di ritardi/soppressioni:')
                col1, col2 = st.columns([4,1])
                chart_percent, data_percent = grafico_percent(conn, intervallo_date, scelta_linea_codice)
                with col1:
                    st.altair_chart(chart_percent, theme='streamlit', use_container_width=True)
                with col2:
                    st.dataframe(data_percent, height=400, use_container_width=True, column_config={"PERC_ORARIO": st.column_config.NumberColumn(format="%.2f")})
            
            with st.container(border=True):
                st.subheader('Media dei ritardi totali raggruppata per giorno:')
                col3, col4 = st.columns([4,1])
                with col3:
                    st.altair_chart(chart_media, theme='streamlit', use_container_width=True)
                with col4:
                    col4.dataframe(data_media, height=400, use_container_width=True, column_config={"MEDIA_RIT": st.column_config.NumberColumn(format="%.2f")})

            with st.container(border=True):
                st.subheader('Numero di ritardi/soppressioni per treno:')
                chart_rit_treno, data_rit_treno = grafico_per_num_treno(conn, intervallo_date, scelta_linea_codice)
                st.altair_chart(chart_rit_treno, theme='streamlit', use_container_width=True)

            with st.container(border=True):
                st.subheader('Media dei ritardi totali raggruppata per treno:')
                chart_media_per_num_treno, data_media_per_num_treno = grafico_media_per_num_treno(conn, intervallo_date, scelta_linea_codice)
                st.altair_chart(chart_media_per_num_treno, theme='streamlit', use_container_width=True)


with tab2:      # mappa
    df2 = conn.query('with TabRitStazioni AS (SELECT T.STAZARRIVO, AVG(C.RIT) AS MEDIARIT FROM CORSE AS C, TRENI AS T WHERE C.NumTreno = T.NumTreno GROUP BY T.STAZARRIVO) SELECT STAZARRIVO, NomeStazione, MEDIARIT, LAT, LON FROM TabRitStazioni AS TR, STAZIONI AS S WHERE TR.STAZARRIVO = S.CodStazione;', ttl=0)
    df_l = conn.query('SELECT LINEE.NomeLinea AS name, AVG(RIT) AS MEDIARITLINEA FROM CORSE, TRENI, LINEE WHERE CORSE.NumTreno=TRENI.NumTreno AND TRENI.Linea=LINEE.CodLinea GROUP BY LINEE.NomeLinea;', ttl=0)
    percorso = pd.read_json('linee.json')
    percorso["color"] = percorso["color"].apply(hex_to_rgb)
    percorso_def = pd.merge(df_l, percorso, on='name')
    # percorso_def
    
    st.subheader('Mappa')
        
    stations_tooltip = False
    lines_tooltip = False
    map_tooltip = ''
    # scelta dei tooltip da visualizzare sulla mappa
    tooltip_choice = st.radio(
                    "Scegli cosa visualizzare sulla mappa al passaggio del mouse:",
                    ["Scheda su stazioni", "Scheda su linee"],
                    captions = ["Visualizza la media di ritardi all'arrivo per stazione", "Visualizza i dati di puntualità per linea"],
                    horizontal=True)
    
    if tooltip_choice == "Scheda su stazioni":
        stations_tooltip = True
        lines_tooltip = False
        map_tooltip = "Stazione di:\n{NomeStazione}\nMedia ritardi:\n{MEDIARIT} minuti"
    if tooltip_choice == "Scheda su linee":
        stations_tooltip = False
        lines_tooltip = True
        map_tooltip = "Linea:\n{name}\nMedia ritardi:\n{MEDIARITLINEA} minuti"

    # layer mappa
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=df2,
        pickable=stations_tooltip,
        opacity=0.8,
        stroked=True,
        filled=True,
        radius_scale=6,
        radius_min_pixels=1,
        radius_max_pixels=100,
        line_width_min_pixels=1,
        get_position='[LON, LAT]',
        get_radius=300,
        get_fill_color=[255,140,0],
        get_line_color=[0,0,0],)

    layer2 = pdk.Layer(
    type="PathLayer",
    data=percorso_def,
    pickable=lines_tooltip,
    get_color="color",
    width_scale=20,
    width_min_pixels=2,
    get_path="path",
    get_width=50,)
        
    view_state = pdk.ViewState(latitude=45.37233, longitude=8.12934, zoom=8, pitch=50)

    st.pydeck_chart(pdk.Deck(map_style=None, initial_view_state=view_state, layers=[layer, layer2], tooltip={"text": map_tooltip}))
