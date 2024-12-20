import streamlit as st
import altair as alt
import plotly.express as px

def metrics_sfm_tot_ieri(conn):
    data_max = conn.query("SELECT MAX(DATA) AS DATAMASSIMA FROM CORSE", ttl=3600, show_spinner=False)
    giorno = data_max['DATAMASSIMA'][0]

    dati = conn.query(f"with TabTot AS (SELECT COUNT(C.NumTreno) AS NUMTOT FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data='{giorno}'), TabOrario AS (SELECT COUNT(C.Rit) AS ORARIO FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data='{giorno}' AND RIT IS NOT NULL AND RIT<5), TabR5 AS (SELECT COUNT(C.Rit) AS RIT5 FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data='{giorno}' AND RIT IS NOT NULL AND RIT>=5 AND RIT<=14), TabR15 AS (SELECT COUNT(C.Rit) AS RIT15 FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data='{giorno}' AND RIT IS NOT NULL AND RIT>=15), TabSopp AS (SELECT COUNT(C.Rit) AS SOPP FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data='{giorno}' AND Sopp=1), TabVar AS (SELECT COUNT(C.Rit) AS VAR FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data='{giorno}' AND Var=1) SELECT IFNULL((ORARIO/NUMTOT)*100,0) AS PUNT, IFNULL(RIT5,0) AS RIT5, IFNULL(RIT15,0) AS RIT15, IFNULL(SOPP,0) AS SOPP, IFNULL(VAR,0) AS VAR, NUMTOT, ORARIO FROM TabTot AS TT, TabOrario AS TOR, TabR5 AS TR5, TabR15 AS TR15, TabSopp AS TS, TabVar AS TV;", ttl=0, show_spinner="Caricamento...")
    dati_ieri = conn.query(f"with TabTot AS (SELECT COUNT(C.NumTreno) AS NUMTOT FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data=DATE_SUB('{giorno}', INTERVAL 1 DAY)), TabOrario AS (SELECT COUNT(C.Rit) AS ORARIO FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data=DATE_SUB('{giorno}', INTERVAL 1 DAY) AND RIT IS NOT NULL AND RIT<5), TabR5 AS (SELECT COUNT(C.Rit) AS RIT5 FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data=DATE_SUB('{giorno}', INTERVAL 1 DAY) AND RIT IS NOT NULL AND RIT>=5 AND RIT<=14), TabR15 AS (SELECT COUNT(C.Rit) AS RIT15 FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data=DATE_SUB('{giorno}', INTERVAL 1 DAY) AND RIT IS NOT NULL AND RIT>=15), TabSopp AS (SELECT COUNT(C.Rit) AS SOPP FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data=DATE_SUB('{giorno}', INTERVAL 1 DAY) AND Sopp=1), TabVar AS (SELECT COUNT(C.Rit) AS VAR FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data=DATE_SUB('{giorno}', INTERVAL 1 DAY) AND Var=1) SELECT IFNULL((ORARIO/NUMTOT)*100,0) AS PUNT, IFNULL(RIT5,0) AS RIT5, IFNULL(RIT15,0) AS RIT15, IFNULL(SOPP,0) AS SOPP, IFNULL(VAR,0) AS VAR, NUMTOT, ORARIO FROM TabTot AS TT, TabOrario AS TOR, TabR5 AS TR5, TabR15 AS TR15, TabSopp AS TS, TabVar AS TV;", ttl=0, show_spinner="Caricamento...")
    
    punt_val = dati['PUNT'][0]
    r5_val = int(dati['RIT5'][0])
    r15_val = int(dati['RIT15'][0])
    sopp_val = int(dati['SOPP'][0])
    var_val = int(dati['VAR'][0])
    treni_tot_val = int(dati['NUMTOT'][0])

    delta_punt_val = punt_val-dati_ieri['PUNT'][0]
    delta_r5_val = int(r5_val-dati_ieri['RIT5'][0])
    delta_r15_val = int(r15_val-dati_ieri['RIT15'][0])
    delta_sopp_val = int(sopp_val-dati_ieri['SOPP'][0])
    delta_var_val = int(var_val-dati_ieri['VAR'][0])
    
    col1, col2 = st.columns([1.5,1])
    with col1:
        if dati_ieri['NUMTOT'][0] == None:
            st.subheader(f"Statistiche intera rete del {giorno}:")
            colm1,colm2,colm3, colm4, colm5=st.columns(5)
            colm1.metric(label="Puntualità", value=f'{round(punt_val,2)}%')
            colm2.metric(label="n° Rit. da 5 a 14 min", value=r5_val)
            colm3.metric(label="n° Rit. superiori a 15 min", value=r15_val)
            colm4.metric(label="n° Treni soppressi", value=sopp_val)
            colm5.metric(label="n° Treni variati", value=var_val)
            st.markdown(f"su **:blue-background[{treni_tot_val}]** treni totali")
        else:
            st.subheader(f"Statistiche intera rete del {giorno}")
            colm1,colm2,colm3=st.columns(3)
            colm1.metric(label="Puntualità", value=f'{round(punt_val,2)}%', delta=f'{round(delta_punt_val,2)}%')
            colm2.metric(label="n° Rit. da 5 a 14 min ", value=r5_val, delta=delta_r5_val, delta_color='inverse')
            colm3.metric(label="n° Rit. superiori a 15 min ", value=r15_val, delta=delta_r15_val, delta_color='inverse')
            colm4,colm5,coml6=st.columns(3)
            colm4.metric(label="n° Treni soppressi", value=sopp_val, delta=delta_sopp_val, delta_color='inverse')
            colm5.metric(label="n° Treni variati", value=var_val, delta=delta_var_val, delta_color='inverse')
            st.markdown(f"su **:blue-background[{treni_tot_val}]** treni totali")

    with col2:
        dati_2 = conn.query(f"with TabTot AS (SELECT T.Linea, COUNT(C.NumTreno) AS NUMTOT FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data='{giorno}' GROUP BY T.Linea), TabOrario AS (SELECT T.Linea, COUNT(C.Rit) AS ORARIO FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data='{giorno}' AND RIT IS NOT NULL AND RIT<5 GROUP BY T.Linea) SELECT TT.Linea, IFNULL((ORARIO/NUMTOT)*100,0) AS PUNT FROM TabTot AS TT LEFT JOIN TabOrario AS TOR ON TT.Linea=TOR.Linea;", ttl=0, show_spinner="Caricamento...")
        linee={901:'sfm1', 902:'sfm2', 903:'sfm3', 904:'sfm4', 906:'sfm6', 907:'sfm7', 913:'sfm3b', 999:'sfmA'}
        dati_2 = dati_2.replace(to_replace=linee).sort_values(by=['Linea']).round({'PUNT': 2})

        config = {'staticPlot': True}
        fig = px.bar(dati_2, x='PUNT', y='Linea', orientation='h', text='PUNT', color='Linea',
                     color_discrete_map={'sfm1':'#ef7f1a', 'sfm2':'#008dd2', 'sfm3':'#b0cb1f', 'sfm3b':'#b0cb1f', 'sfm4':'#e31e24', 'sfm6':'#8b231d', 'sfm7':'#fecc00', 'sfmA':'#0c54a0'})
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250, xaxis_title=None, yaxis_title=None, showlegend=False, yaxis={'categoryorder':'category descending'})
        #fig.update_xaxes(showticklabels=True, showgrid=True)

        st.subheader("Puntualità per linea")
        st.plotly_chart(fig, theme='streamlit', config=config)


    
def metrics_sfm_tot_sett(conn):
    date = conn.query("SELECT MAX(DATA) AS DATAMASSIMA, DATE_SUB(MAX(DATA), INTERVAL 6 DAY) AS DATA_INIZIO_SETT, DATE_SUB(MAX(DATA), INTERVAL 7 DAY) AS DATA_SCORSA_SETT, DATE_SUB(MAX(DATA), INTERVAL 13 DAY) AS DATA_INIZIO_SCORSA_SETT FROM CORSE", ttl=0, show_spinner=False)
    giorno_1 = date['DATA_INIZIO_SETT'][0]
    giorno_2 = date['DATAMASSIMA'][0]
    giorno_3 = date['DATA_INIZIO_SCORSA_SETT'][0]
    giorno_4 = date['DATA_SCORSA_SETT'][0]
   
    #st.markdown(f"{giorno_1}, {giorno_2}, {giorno_3}, {giorno_4}")

    dati = conn.query(f"with TabTot AS (SELECT COUNT(C.NumTreno) AS NUMTOT FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}'), TabOrario AS (SELECT COUNT(C.Rit) AS ORARIO FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND RIT IS NOT NULL AND RIT<5), TabR5 AS (SELECT COUNT(C.Rit) AS RIT5 FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND RIT IS NOT NULL AND RIT>=5 AND RIT<=14), TabR15 AS (SELECT COUNT(C.Rit) AS RIT15 FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND RIT IS NOT NULL AND RIT>=15), TabSopp AS (SELECT COUNT(C.Rit) AS SOPP FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<={giorno_2} AND Sopp=1), TabVar AS (SELECT COUNT(C.Rit) AS VAR FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND Var=1) SELECT IFNULL((ORARIO/NUMTOT)*100,0) AS PUNT, IFNULL(RIT5,0) AS RIT5, IFNULL(RIT15,0) AS RIT15, IFNULL(SOPP,0) AS SOPP, IFNULL(VAR,0) AS VAR, NUMTOT, ORARIO FROM TabTot AS TT, TabOrario AS TOR, TabR5 AS TR5, TabR15 AS TR15, TabSopp AS TS, TabVar AS TV;", ttl=0, show_spinner="Caricamento...")
    dati_scorsa_sett = conn.query(f"with TabTot AS (SELECT COUNT(C.NumTreno) AS NUMTOT FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_3}' AND C.Data<='{giorno_4}'), TabOrario AS (SELECT COUNT(C.Rit) AS ORARIO FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_3}' AND C.Data<='{giorno_4}' AND RIT IS NOT NULL AND RIT<5), TabR5 AS (SELECT COUNT(C.Rit) AS RIT5 FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_3}' AND C.Data<='{giorno_4}' AND RIT IS NOT NULL AND RIT>=5 AND RIT<=14), TabR15 AS (SELECT COUNT(C.Rit) AS RIT15 FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_3}' AND C.Data<='{giorno_4}' AND RIT IS NOT NULL AND RIT>=15), TabSopp AS (SELECT COUNT(C.Rit) AS SOPP FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_3}' AND C.Data<='{giorno_4}' AND Sopp=1), TabVar AS (SELECT COUNT(C.Rit) AS VAR FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_3}' AND C.Data<='{giorno_4}' AND Var=1) SELECT IFNULL((ORARIO/NUMTOT)*100,0) AS PUNT, IFNULL(RIT5,0) AS RIT5, IFNULL(RIT15,0) AS RIT15, IFNULL(SOPP,0) AS SOPP, IFNULL(VAR,0) AS VAR, NUMTOT, ORARIO FROM TabTot AS TT, TabOrario AS TOR, TabR5 AS TR5, TabR15 AS TR15, TabSopp AS TS, TabVar AS TV;", ttl=0, show_spinner="Caricamento...")
    
    punt_val = dati['PUNT'][0]
    r5_val = int(dati['RIT5'][0])
    r15_val = int(dati['RIT15'][0])
    sopp_val = int(dati['SOPP'][0])
    var_val = int(dati['VAR'][0])
    treni_tot_val = int(dati['NUMTOT'][0])

    delta_punt_val = punt_val-dati_scorsa_sett['PUNT'][0]
    delta_r5_val = int(r5_val-dati_scorsa_sett['RIT5'][0])
    delta_r15_val = int(r15_val-dati_scorsa_sett['RIT15'][0])
    delta_sopp_val = int(sopp_val-dati_scorsa_sett['SOPP'][0])
    delta_var_val = int(var_val-dati_scorsa_sett['VAR'][0])
    
    col1, col2 = st.columns([1.5,1])
    with col1:
        if dati_scorsa_sett['NUMTOT'][0] == None:
            st.subheader(f"Statistiche intera rete - ultimi 7 giorni")
            colm1,colm2,colm3, colm4, colm5=st.columns(5)
            colm1.metric(label="Puntualità", value=f'{round(punt_val,2)}%')
            colm2.metric(label="n° Rit. da 5 a 14 min", value=r5_val)
            colm3.metric(label="n° Rit. superiori a 15 min", value=r15_val)
            colm4.metric(label="n° Treni soppressi", value=sopp_val)
            colm5.metric(label="n° Treni variati", value=var_val)
            st.markdown(f"su **:blue-background[{treni_tot_val}]** treni totali -  dal **{giorno_1}** al **{giorno_2}**")
        else:
            st.subheader(f"Statistiche intera rete - ultimi 7 giorni")
            colm1,colm2,colm3=st.columns(3)
            colm1.metric(label="Puntualità", value=f'{round(punt_val,2)}%', delta=f'{round(delta_punt_val,2)}%')
            colm2.metric(label="n° Rit. da 5 a 14 min ", value=r5_val, delta=delta_r5_val, delta_color='inverse')
            colm3.metric(label="n° Rit. superiori a 15 min ", value=r15_val, delta=delta_r15_val, delta_color='inverse')
            colm4,colm5,coml6=st.columns(3)
            colm4.metric(label="n° Treni soppressi", value=sopp_val, delta=delta_sopp_val, delta_color='inverse')
            colm5.metric(label="n° Treni variati", value=var_val, delta=delta_var_val, delta_color='inverse')
            st.markdown(f"su **:blue-background[{treni_tot_val}]** treni totali -  dal **{giorno_1}** al **{giorno_2}**")

    with col2:
        dati_2 = conn.query(f"with TabTot AS (SELECT T.Linea, COUNT(C.NumTreno) AS NUMTOT FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' GROUP BY T.Linea), TabOrario AS (SELECT T.Linea, COUNT(C.Rit) AS ORARIO FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND RIT IS NOT NULL AND RIT<5 GROUP BY T.Linea) SELECT TT.Linea, IFNULL((ORARIO/NUMTOT)*100,0) AS PUNT FROM TabTot AS TT LEFT JOIN TabOrario AS TOR ON TT.Linea=TOR.Linea;", ttl=0, show_spinner="Caricamento...")
        linee={901:'sfm1', 902:'sfm2', 903:'sfm3', 904:'sfm4', 906:'sfm6', 907:'sfm7', 913:'sfm3b', 999:'sfmA'}
        dati_2 = dati_2.replace(to_replace=linee).sort_values(by=['Linea']).round({'PUNT': 2})

        config = {'staticPlot': True}
        fig = px.bar(dati_2, x='PUNT', y='Linea', orientation='h', text='PUNT', color='Linea',
                     color_discrete_map={'sfm1':'#ef7f1a', 'sfm2':'#008dd2', 'sfm3':'#b0cb1f', 'sfm3b':'#b0cb1f', 'sfm4':'#e31e24', 'sfm6':'#8b231d', 'sfm7':'#fecc00', 'sfmA':'#0c54a0'})
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250, xaxis_title=None, yaxis_title=None, showlegend=False, yaxis={'categoryorder':'category descending'})
        #fig.update_xaxes(showticklabels=True, showgrid=True)

        st.subheader("Puntualità per linea")
        st.plotly_chart(fig, theme='streamlit', config=config)


def sfm_grafico(conn):
    df = conn.query("with TabTreni AS (SELECT CONCAT(YEAR(C.Data), '-', WEEK(C.Data,1)) AS SETT, T.Linea AS LINEA, COUNT(*) AS NUMTOT FROM CORSE AS C, TRENI AS T WHERE T.NumTreno=C.NumTreno AND Linea>900 AND C.Data>='2024-11-04' GROUP BY WEEK(C.Data,1), T.Linea), TabOrario AS (SELECT CONCAT(YEAR(C.Data), '-', WEEK(C.Data,1)) AS SETT, T.Linea AS LINEA, COUNT(*) AS ORARIO FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND RIT IS NOT NULL AND RIT<5 AND Linea>900 AND C.Data>='2024-11-04' GROUP BY WEEK(C.Data,1), T.Linea) SELECT TT.SETT AS SETT, TT.LINEA AS LINEA, IFNULL((ORARIO/NUMTOT)*100,0) AS PERC_ORARIO FROM TabTreni AS TT LEFT JOIN TabOrario AS TOR ON TT.SETT=TOR.SETT AND TT.LINEA=TOR.LINEA;", ttl=0, show_spinner=False)
    linee={'901':'sfm1', '902':'sfm2', '903':'sfm3', '904':'sfm4', '906':'sfm6', '907':'sfm7', '913':'sfm3b', '999':'sfmA'}

    fig = px.line(df, x='SETT', y='PERC_ORARIO', color='LINEA', markers=True, line_shape='spline',
                  color_discrete_map={901:'#ef7f1a', 902:'#008dd2', 903:'#b0cb1f', 913:'#b0cb1f', 904:'#e31e24', 906:'#8b231d', 907:'#fecc00', 999:'#0c54a0'})
    fig.update_layout(margin=dict(t=25, b=0, l=0, r=0), height=400, xaxis_title="Settimana", yaxis_title="Puntualità")
    fig.update_xaxes(showticklabels=True, showgrid=True)
    fig.update_yaxes(range=[0, 110])
    fig.for_each_trace(lambda t: t.update(name = linee[t.name],
                                      legendgroup = linee[t.name],
                                      hovertemplate = t.hovertemplate.replace(t.name, linee[t.name])
                                     )
                  )
    st.plotly_chart(fig, theme="streamlit")


def metrics_sfm_scelta(conn):
    date=conn.query(f"SELECT MIN(DATA) AS DATAMIN, MAX(DATA) AS DATAMAX FROM CORSE, TRENI WHERE TRENI.NumTreno=CORSE.NumTreno AND LINEA>=900;", ttl=0, show_spinner="Caricamento...")
    data_min = date['DATAMIN'][0]
    data_max = date['DATAMAX'][0]

    intervallo_date = st.date_input("Scegli l'intervallo di date per i grafici",value=(),min_value=data_min,max_value=data_max)
    
    if intervallo_date != () and len(intervallo_date) != 1:
        giorno_1 = intervallo_date[0]
        giorno_2 = intervallo_date[1]

        dati = conn.query(f"with TabTot AS (SELECT COUNT(C.NumTreno) AS NUMTOT FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}'), TabOrario AS (SELECT COUNT(C.Rit) AS ORARIO FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND RIT IS NOT NULL AND RIT<5), TabR5 AS (SELECT COUNT(C.Rit) AS RIT5 FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND RIT IS NOT NULL AND RIT>=5 AND RIT<=14), TabR15 AS (SELECT COUNT(C.Rit) AS RIT15 FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND RIT IS NOT NULL AND RIT>=15), TabSopp AS (SELECT COUNT(C.Rit) AS SOPP FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<={giorno_2} AND Sopp=1), TabVar AS (SELECT COUNT(C.Rit) AS VAR FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND Var=1) SELECT IFNULL((ORARIO/NUMTOT)*100,0) AS PUNT, IFNULL(RIT5,0) AS RIT5, IFNULL(RIT15,0) AS RIT15, IFNULL(SOPP,0) AS SOPP, IFNULL(VAR,0) AS VAR, NUMTOT, ORARIO FROM TabTot AS TT, TabOrario AS TOR, TabR5 AS TR5, TabR15 AS TR15, TabSopp AS TS, TabVar AS TV;", ttl=0, show_spinner="Caricamento...")
        
        punt_val = dati['PUNT'][0]
        r5_val = int(dati['RIT5'][0])
        r15_val = int(dati['RIT15'][0])
        sopp_val = int(dati['SOPP'][0])
        var_val = int(dati['VAR'][0])
        treni_tot_val = int(dati['NUMTOT'][0])
        
        col1, col2 = st.columns([1.5,1])
        with col1:
            st.subheader(f"Statistiche intera rete")
            colm1,colm2,colm3=st.columns(3)
            colm1.metric(label="Puntualità", value=f'{round(punt_val,2)}%')
            colm2.metric(label="n° Rit. da 5 a 14 min ", value=r5_val)
            colm3.metric(label="n° Rit. superiori a 15 min ", value=r15_val)
            colm4,colm5,coml6=st.columns(3)
            colm4.metric(label="n° Treni soppressi", value=sopp_val)
            colm5.metric(label="n° Treni variati", value=var_val)
            st.markdown(f"su **:blue-background[{treni_tot_val}]** treni totali -  dal **{giorno_1}** al **{giorno_2}**")

        with col2:
            dati_2 = conn.query(f"with TabTot AS (SELECT T.Linea, COUNT(C.NumTreno) AS NUMTOT FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' GROUP BY T.Linea), TabOrario AS (SELECT T.Linea, COUNT(C.Rit) AS ORARIO FROM TRENI AS T, CORSE AS C WHERE C.NumTreno=T.NumTreno AND T.Linea>900 AND C.Data>='{giorno_1}' AND C.Data<='{giorno_2}' AND RIT IS NOT NULL AND RIT<5 GROUP BY T.Linea) SELECT TT.Linea, IFNULL((ORARIO/NUMTOT)*100,0) AS PUNT FROM TabTot AS TT LEFT JOIN TabOrario AS TOR ON TT.Linea=TOR.Linea;", ttl=0, show_spinner="Caricamento...")
            linee={901:'sfm1', 902:'sfm2', 903:'sfm3', 904:'sfm4', 906:'sfm6', 907:'sfm7', 913:'sfm3b', 999:'sfmA'}
            dati_2 = dati_2.replace(to_replace=linee).sort_values(by=['Linea']).round({'PUNT': 2})

            config = {'staticPlot': True}
            fig = px.bar(dati_2, x='PUNT', y='Linea', orientation='h', text='PUNT', color='Linea',
                         color_discrete_map={'sfm1':'#ef7f1a', 'sfm2':'#008dd2', 'sfm3':'#b0cb1f', 'sfm3b':'#b0cb1f', 'sfm4':'#e31e24', 'sfm6':'#8b231d', 'sfm7':'#fecc00', 'sfmA':'#0c54a0'})
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250, xaxis_title=None, yaxis_title=None, showlegend=False, yaxis={'categoryorder':'category descending'})
            #fig.update_xaxes(showticklabels=True, showgrid=True)

            st.subheader("Puntualità per linea")
            try:
                st.plotly_chart(fig, theme='streamlit', config=config)
            except st.errors.StreamlitDuplicateElementId:
                st.error(f"Il grafico relativo al giorno {giorno_1} è già visualizzato a inizio pagina", icon="⛔")


    else:
        st.info("Seleziona un intervallo di date per visualizzare le statistiche", icon="ℹ")
