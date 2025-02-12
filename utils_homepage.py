import streamlit as st
from utils import *
import altair as alt
import datetime
import pandas as pd
import pydeck as pdk
import plotly.express as px
import numpy as np
import json


# TAB 2 - RICERCA PER NUMERO TRENO #

def ricerca_per_treno(conn):
    df = conn.query('SELECT NOMELINEA, CodLinea FROM LINEE ORDER BY NOMELINEA;', ttl=0, show_spinner=False)
    linee_nome = df['NOMELINEA'].tolist()
    scelta_linea = st.selectbox("**Seleziona la linea da cui scegliere il treno**", linee_nome, index=None, placeholder='Scegli la linea...')

    if scelta_linea != None:
        df2 = conn.query(f"SELECT CodLinea FROM LINEE WHERE NomeLinea='{scelta_linea}';", ttl=0, show_spinner=False)
        scelta_linea_codice = df2['CodLinea'][0]

        elenco_num_treni = conn.query(f'SELECT DISTINCT C.NumTreno FROM C_PROVV AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={scelta_linea_codice} ORDER BY C.NumTreno', ttl=0, show_spinner=False)
        num_treni_lista = elenco_num_treni['NumTreno'].tolist()
        scelta_treno = st.selectbox("**Seleziona il numero del treno**", num_treni_lista, index=None, placeholder='Scegli il numero del treno...')
        
        if scelta_treno != None:

            # grafico puntualità e medie ritardi in partenza e arrivo #

            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f"Puntualità del treno {scelta_treno}")

                    dati_grafico = conn.query(f"with TabTot AS (SELECT COUNT(NumTreno) AS NUMTOT FROM CORSE WHERE NumTreno={scelta_treno}), TabOrario AS (SELECT COUNT(Rit) AS ORARIO FROM CORSE WHERE NumTreno={scelta_treno} AND RIT IS NOT NULL AND RIT<5), TabR5 AS (SELECT COUNT(Rit) AS RIT5 FROM CORSE WHERE NumTreno={scelta_treno} AND RIT IS NOT NULL AND RIT>=5 AND RIT<=14), TabR15 AS (SELECT COUNT(Rit) AS RIT15 FROM CORSE WHERE NumTreno={scelta_treno} AND RIT IS NOT NULL AND RIT>=15), TabSopp AS (SELECT COUNT(Sopp) AS SOPP FROM CORSE WHERE NumTreno={scelta_treno} AND Sopp=1), TabVar AS (SELECT COUNT(Var) AS VAR FROM CORSE WHERE NumTreno={scelta_treno} AND Var=1) SELECT IFNULL((ORARIO/NUMTOT)*100,0) AS PUNT, IFNULL((RIT5/NUMTOT)*100,0) AS RIT5, IFNULL((RIT15/NUMTOT)*100,0) AS RIT15, IFNULL((SOPP/NUMTOT)*100,0) AS SOPP, IFNULL((VAR/NUMTOT)*100,0) AS VAR FROM TabTot AS TT, TabOrario AS TOR, TabR5 AS TR5, TabR15 AS TR15, TabSopp AS TS, TabVar AS TV;", ttl=0, show_spinner=False)

                    dati_grafico = dati_grafico.reset_index()
                    dati_grafico = pd.melt(dati_grafico, value_vars=['PUNT', 'RIT5', 'RIT15', 'SOPP', 'VAR'], var_name='LEGENDA', value_name='VALORE')
                    dati_grafico['x'] = 0

                    config = {'displayModeBar': False}
                    fig = px.bar(dati_grafico, x='VALORE', y='x', color='LEGENDA', orientation='h',
                                 color_discrete_map={'PUNT':'#4DAF4A', 'RIT5':'yellow', 'RIT15':'orange', 'SOPP':'red', 'VAR':'purple'}, hover_data={'x':False, 'VALORE':':.2f'})
                    fig.update_layout(margin=dict(t=0, b=0, l=0, r=100), height=200, xaxis_title='Valore percentuale', yaxis_visible=False, xaxis_fixedrange=True, yaxis_fixedrange=True, xaxis_showgrid=True)

                    st.plotly_chart(fig, theme="streamlit", config=config)


                with col2:
                    st.subheader("Statistiche")
                    dati_part = conn.query(f"SELECT avg(ritPartenza) as MEDIA_RIT_PART FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( ritPartenza SMALLINT(6) PATH '$.ritPartenza', tipoFermata VARCHAR(1) PATH '$.tipoFermata' ) ) AS tab_fermate WHERE C.NumTreno={scelta_treno} AND tipoFermata='P';", ttl=0, show_spinner=False)
                    dati_arr = conn.query(f"SELECT AVG(Rit) AS MEDIA_RIT_ARR FROM CORSE WHERE NumTreno={scelta_treno}", ttl=0, show_spinner=False)
                    rit_part = dati_part['MEDIA_RIT_PART'][0]
                    rit_arr = dati_arr['MEDIA_RIT_ARR'][0]
                    if rit_part != None:
                        st.metric(label="Ritardo medio alla partenza", value=f'{round(rit_part,1)} minuti')
                    else:
                        st.metric(label="Ritardo medio alla partenza", value=f'{rit_part} minuti')
                    if rit_arr != None:
                        st.metric(label="Ritardo medio all'arrivo", value=f'{round(rit_arr,1)} minuti')
                    else:
                        st.metric(label="Ritardo medio all'arrivo", value=f'{rit_arr} minuti')

                # PIE DI PAGINA BLOCCO CON GRAFICO E MEDIA RITARDI #
                date = conn.query(f"SELECT MIN(DATA) AS DATAMINIMA, MAX(DATA) AS DATAMASSIMA, COUNT(*) AS NUMTOT FROM CORSE WHERE NumTreno={scelta_treno}", ttl=0, show_spinner=False)
                giorno_min = date['DATAMINIMA'][0]
                giorno_max = date['DATAMASSIMA'][0]
                num_corse = date['NUMTOT'][0]
                date_rit_arrivo = conn.query(f"SELECT MIN(DATA) AS DATAMINIMA, MAX(DATA) AS DATAMASSIMA, COUNT(*) AS NUMTOT FROM CORSE WHERE NumTreno={scelta_treno} AND Fermate IS NOT NULL", ttl=0, show_spinner=False)
                giorno_min_2 = date_rit_arrivo['DATAMINIMA'][0]

                col3, col4 = st.columns(2)

                with col3:
                    st.markdown(f"su **:blue-background[{num_corse}]** corse totali -  dal **{giorno_min}** al **{giorno_max}**")
                with col4:
                    st.markdown(f"*Il ritardo medio alla partenza è calcolato a partire dal **{giorno_min_2}**")

                # FINE PIE DI PAGINA BLOCCO CON GRAFICO E MEDIA RITARDI #
            
            # BLOCCO STATISTICHE PER STAZIONE
            with st.expander(f"**Statistiche per stazione - treno {scelta_treno}**", icon="🚉"):
                    statistiche_per_stazione(conn, scelta_treno)

            # fine grafici e statistiche #

            df = conn.query(f"SELECT * FROM CORSE WHERE NumTreno={scelta_treno} AND Data>='2025-01-28';", ttl=0, show_spinner=False)

            # per visualizzazione dataframe
            df['Sopp'] = df['Sopp'].replace(1, "SI'").replace(0, "NO")
            df['Var'] = df['Var'].replace(1, "SI'").replace(0, "NO")

            # stampa dataframe
            event = st.dataframe(df, on_select="rerun", selection_mode="single-row", column_config={"Fermate": None, "SmartCaring": None, "NumTreno": st.column_config.NumberColumn(format="%f")}, use_container_width=True, height=300)

            selezione = event.selection.rows
                
            if len(selezione) > 0:
                st.subheader("Fermate")
                fermate = df['Fermate'][selezione[0]]
                if fermate != None:
                    json_fermate = json.loads(fermate)

                    json_fermate = pd.json_normalize(json_fermate)

                    json_fermate['partenzaTeorica'] = pd.to_datetime(json_fermate['partenzaTeorica'], unit='ms', utc=True).dt.tz_convert(tz='Europe/Brussels').dt.strftime('%H:%M:%S')
                    json_fermate['partenzaReale'] = pd.to_datetime(json_fermate['partenzaReale'], unit='ms', utc=True).dt.tz_convert(tz='Europe/Brussels').dt.strftime('%H:%M:%S')
                    json_fermate['arrivoTeorico'] = pd.to_datetime(json_fermate['arrivoTeorico'], unit='ms', utc=True).dt.tz_convert(tz='Europe/Brussels').dt.strftime('%H:%M:%S')
                    json_fermate['arrivoReale'] = pd.to_datetime(json_fermate['arrivoReale'], unit='ms', utc=True).dt.tz_convert(tz='Europe/Brussels').dt.strftime('%H:%M:%S')

                    json_fermate = json_fermate.iloc[:, [0, 8, 9, 10, 2, 3, 4, 5]]

                    json_fermate = json_fermate.rename(columns={"nomeFermata": "Stazione", "partenzaTeorica": "Partenza programmata", "partenzaReale": "Partenza effettiva", "ritPartenza": "Ritardo partenza", "arrivoTeorico": "Arrivo programmato", "arrivoReale": "Arrivo effettivo", "ritArrivo": "Ritardo arrivo", "binEffettivo": "Binario"})
                        
                    st.dataframe(json_fermate, use_container_width = True)
                else:
                    st.warning("Non sono presenti dati relativi alle fermate")


                st.subheader("Smart caring")
                smart_caring = df['SmartCaring'][selezione[0]]
                if smart_caring != None:
                    json_smart_caring = json.loads(smart_caring)

                    for avviso in json_smart_caring:
                        with st.container(border=True):
                            st.markdown(f"**{converti_data_ora(avviso['oraAvviso'])}**\n")
                            st.markdown(f"{avviso['testoAvviso']}")

                else:
                    st.info("Non sono presenti dati relativi allo smart caring")

            else:
                st.info("Seleziona un treno dalla tabella per visualizzare i dati sul percorso, clicclando sul margine sinistro della riga", icon="ℹ")


# funzione per blocco statistiche aggiuntive per stazione #
def statistiche_per_stazione(conn, scelta_treno):

    stazioni = conn.query(f"SELECT tab_fermate.nomeFermata FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( nomeFermata VARCHAR(32) PATH '$.nomeFermata', ritArrivo SMALLINT(6) PATH '$.ritArrivo', ritPartenza SMALLINT(6) PATH '$.ritPartenza' ) ) AS tab_fermate WHERE C.Data=(SELECT MAX(Data) FROM CORSE WHERE NumTreno={scelta_treno} AND Fermate IS NOT NULL) AND C.NumTreno={scelta_treno};", ttl=0, show_spinner=False)
    stazioni_lista = stazioni['nomeFermata'].tolist()
    scelta_stazione = st.selectbox("**Seleziona una stazione**", stazioni_lista, index=None, placeholder='Scegli una stazione...')

    date = conn.query(f"SELECT MIN(Data) AS DATAMIN, MAX(Data) AS DATAMAX FROM CORSE WHERE NumTreno={scelta_treno} AND Fermate IS NOT NULL", ttl=0, show_spinner=False)
    data_min = date['DATAMIN'][0]
    data_max = date['DATAMAX'][0]
    intervallo_date = st.date_input("**Scegli l'intervallo di date per le statistiche**",value=(data_min, data_max),min_value=data_min,max_value=data_max)
                
    if len(intervallo_date) != 1:
                
        giorno_1 = intervallo_date[0]
        giorno_2 = intervallo_date[1]

                    
        if scelta_stazione != None:
            
            dati_box_plot = conn.query(f"SELECT C.Data, tab_fermate.nomeFermata, ritArrivo, ritPartenza FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( nomeFermata VARCHAR(32) PATH '$.nomeFermata', ritArrivo SMALLINT(6) PATH '$.ritArrivo', ritPartenza SMALLINT(6) PATH '$.ritPartenza' ) ) AS tab_fermate WHERE nomeFermata='{scelta_stazione}' AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND C.NumTreno={scelta_treno};", ttl=0)

            if dati_box_plot['ritArrivo'].isnull().all():
                scelta_arr_part = st.radio("**Scegli se visualizzare il ritardo di arrivo o di partenza**", options=['Arrivo', 'Partenza'], index=1, disabled=True, horizontal=True)
            elif dati_box_plot['ritPartenza'].isnull().all():
                scelta_arr_part = st.radio("**Scegli se visualizzare il ritardo di arrivo o di partenza**", options=['Arrivo', 'Partenza'], index=0, disabled=True, horizontal=True)
            else:
                scelta_arr_part = st.radio("**Scegli se visualizzare il ritardo di arrivo o di partenza**", options=['Arrivo', 'Partenza'], disabled=False, horizontal=True)
                    
            if scelta_arr_part == 'Arrivo':
                tipo_rit = 'ritArrivo'
            elif scelta_arr_part == 'Partenza':
                tipo_rit = 'ritPartenza'
                    
        col1, col2, col3 = st.columns(3, gap="medium")
    
        with col1:
            if scelta_stazione != None:

                st.markdown("**Grafico:**")

                config = {'displayModeBar': False}
                fig_box = px.box(dati_box_plot, y=tipo_rit, points='all')
                fig_box.update_traces(quartilemethod="linear", boxmean=True)
                # fig_box.update_layout(yaxis_tickformat="d")
                fig_box.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=400, xaxis_title=f"{scelta_treno}", yaxis_visible=True, xaxis_fixedrange=True, yaxis_fixedrange=True, xaxis_showgrid=False)

                st.plotly_chart(fig_box, theme="streamlit", config=config)

        with col2:
            if scelta_stazione != None:

                punt_df = conn.query(f"with TabTotArrivo AS (SELECT count(ritArrivo) AS TOTARR FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( nomeFermata VARCHAR(32) PATH '$.nomeFermata', ritArrivo SMALLINT(6) PATH '$.ritArrivo' ) ) AS tab_fermate WHERE nomeFermata='{scelta_stazione}' AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND C.NumTreno={scelta_treno}), TabTotPartenza AS (SELECT count(ritPartenza) AS TOTPART FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( nomeFermata VARCHAR(32) PATH '$.nomeFermata', ritPartenza SMALLINT(6) PATH '$.ritPartenza' ) ) AS tab_fermate WHERE nomeFermata='{scelta_stazione}' AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND C.NumTreno={scelta_treno}), TabPuntArrivo AS (SELECT count(ritArrivo) AS ORARIOARR FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( nomeFermata VARCHAR(32) PATH '$.nomeFermata', ritArrivo SMALLINT(6) PATH '$.ritArrivo' ) ) AS tab_fermate WHERE nomeFermata='{scelta_stazione}' AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND C.NumTreno={scelta_treno} AND ritArrivo<5), TabPuntPartenza AS (SELECT count(ritPartenza) AS ORARIOPART FROM CORSE AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( nomeFermata VARCHAR(32) PATH '$.nomeFermata', ritPartenza SMALLINT(6) PATH '$.ritPartenza' ) ) AS tab_fermate WHERE nomeFermata='{scelta_stazione}' AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND C.NumTreno={scelta_treno} AND ritPartenza<5) SELECT IFNULL((ORARIOARR/TOTARR)*100,0) AS PUNTARRIVO, IFNULL((ORARIOPART/TOTPART)*100,0) AS PUNTPARTENZA FROM TabTotArrivo, TabTotPartenza, TabPuntArrivo, TabPuntPartenza;", ttl=0, show_spinner=False)
                if scelta_arr_part == 'Arrivo':
                    punt = punt_df['PUNTARRIVO'][0]
                elif scelta_arr_part == 'Partenza':
                    punt = punt_df['PUNTPARTENZA'][0]
                avg = dati_box_plot[tipo_rit].mean()
                std = dati_box_plot[tipo_rit].std()
                med = dati_box_plot[tipo_rit].median()
                q1 = dati_box_plot[tipo_rit].quantile(q=0.25, interpolation='hazen') 
                q3 = dati_box_plot[tipo_rit].quantile(q=0.75, interpolation='hazen')

                st.markdown("**Statistiche aggiuntive:**")

                col4, col5 = st.columns(2)
                col4.metric("Puntualità su treni effettuati", f"{round(punt,2)}%")
                col5.metric("Media", f"{round(avg,1)} min")
                            
                col6, col7 = st.columns(2)
                col6.metric("Mediana", f"{med} min")
                col7.metric("Deviazione Standard", f"{round(std,1)} min")
                            
                col8, col9 = st.columns(2)
                col8.metric("1° quartile", f"{q1} min")
                col9.metric("3° quartile", f"{q3} min")

        with col3:
            if scelta_stazione != None:
                st.markdown("**Dettaglio per singoli giorni:**")
                st.dataframe(dati_box_plot, column_config={"nomeFermata": None}, height=400, use_container_width=True)

    else:
        st.info("Seleziona un intervallo di date per visualizzare le statistiche", icon="ℹ")



# TAB 3 - MAPPA #

def visualizza_mappa_stazioni(conn):
    df2 = conn.query('with TabRitStazioni AS (SELECT T.STAZARRIVO, AVG(C.RIT) AS MEDIARIT FROM CORSE AS C, TRENI AS T WHERE C.NumTreno = T.NumTreno GROUP BY T.STAZARRIVO) SELECT STAZARRIVO, NomeStazione, MEDIARIT, LAT, LON FROM TabRitStazioni AS TR, STAZIONI AS S WHERE TR.STAZARRIVO = S.CodStazione;', ttl=0, show_spinner="Caricamento...")
    df2 = df2.round({'MEDIARIT':2})

    # layer mappa
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=df2,
        pickable=True,
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
        
    view_state = pdk.ViewState(latitude=45.37233, longitude=8.12934, zoom=7, bearing=0, pitch=None)

    st.pydeck_chart(pdk.Deck(initial_view_state=view_state, layers=[layer], tooltip={"text": "Stazione di:\n{NomeStazione}\nMedia ritardi:\n{MEDIARIT} minuti"}), height=700)
