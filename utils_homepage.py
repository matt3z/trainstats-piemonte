import streamlit as st
from utils import *
import altair as alt
import datetime
import pandas as pd
import pydeck as pdk
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

        elenco_num_treni = conn.query(f'SELECT DISTINCT C.NumTreno FROM C_PROVV AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={scelta_linea_codice} ORDER BY C.NumTreno')
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
                    dati_part = conn.query(f"SELECT avg(ritPartenza) as MEDIA_RIT_PART FROM C_PROVV AS C, JSON_TABLE(Fermate, '$[*]' COLUMNS ( ritPartenza SMALLINT(6) PATH '$.ritPartenza', tipoFermata VARCHAR(1) PATH '$.tipoFermata' ) ) AS tab_fermate WHERE C.NumTreno={scelta_treno} AND tipoFermata='P';", ttl=0, show_spinner=False)
                    dati_arr = conn.query(f"SELECT AVG(Rit) AS MEDIA_RIT_ARR FROM C_PROVV WHERE NumTreno={scelta_treno}", ttl=0, show_spinner=False)
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

            # fine grafico e statistiche #

            df = conn.query(f"SELECT * FROM C_PROVV WHERE NumTreno={scelta_treno};", ttl=0)

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

                    json_fermate['partenzaTeorica'] = pd.to_datetime(json_fermate['partenzaTeorica'], unit='ms').dt.strftime('%H:%M:%S')
                    json_fermate['partenzaReale'] = pd.to_datetime(json_fermate['partenzaReale'], unit='ms').dt.strftime('%H:%M:%S')
                    json_fermate['arrivoTeorico'] = pd.to_datetime(json_fermate['arrivoTeorico'], unit='ms').dt.strftime('%H:%M:%S')
                    json_fermate['arrivoReale'] = pd.to_datetime(json_fermate['arrivoReale'], unit='ms').dt.strftime('%H:%M:%S')

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
                st.info("Seleziona un treno dalla tabella per visualizzare i dati sul percorso", icon="ℹ")









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
