import streamlit as st
import altair as alt

def sql_connect(nomeconn, tipo):
    try:
        conn = st.connection(nomeconn, type=tipo)
        conn.query('SELECT * FROM LINEE LIMIT 0;', ttl=0, show_spinner=False)
        st.sidebar.success("Connesso al DB")
        return conn
    except:
        st.sidebar.error("Connessione al DB\nnon riuscita")

def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def grafico_percent(conn, intervallo_date, scelta_linea_codice):
    data=conn.query(f"with TabTot AS (SELECT DATA, COUNT(*) AS NUMTOT FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' GROUP BY DATA), TabOrario AS (SELECT DATA, COUNT(*) AS ORARIO FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND RIT IS NOT NULL AND RIT<5 AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' GROUP BY DATA), TabRit5 AS (SELECT DATA, COUNT(*) AS RIT5 FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND RIT>=5 AND RIT<15 AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' GROUP BY DATA), TabRit15 AS (SELECT DATA, COUNT(*) AS RIT15 FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND RIT>=15 AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' GROUP BY DATA), TabSopp AS (SELECT DATA, COUNT(*) AS SOPP FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND Sopp=1 AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' GROUP BY DATA), TabVar AS (SELECT DATA, COUNT(*) AS VAR FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND Var=1 AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' GROUP BY DATA) SELECT TT.DATA, IFNULL((ORARIO/NUMTOT)*100,0) AS PERC_ORARIO, IFNULL(RIT5,0) AS N_RIT5, IFNULL(RIT15,0) AS N_RIT15, IFNULL(SOPP,0) AS N_SOPP, IFNULL(VAR,0) AS N_VAR FROM TABTOT AS TT LEFT JOIN TABORARIO AS TOR ON TT.DATA=TOR.DATA LEFT JOIN TABRIT5 AS TR5 ON TT.DATA=TR5.DATA LEFT JOIN TABRIT15 AS TR15 ON TT.DATA=TR15.DATA LEFT JOIN TABSOPP AS TS ON TT.DATA=TS.DATA LEFT JOIN TABVAR AS TV ON TT.DATA=TV.DATA;", ttl=0, show_spinner="Caricamento...")
    
    scale = alt.Scale(domain=['PERC_ORARIO','N_RIT5', 'N_RIT15', 'N_SOPP', 'N_VAR'], range=['#4daf4a','yellow', 'orange', 'red', 'purple'])

    base = alt.Chart(data).encode(alt.X('DATA:T', axis=alt.Axis(title=None)))

    bars = base.transform_fold(
        ['N_RIT5', 'N_RIT15', 'N_SOPP', 'N_VAR'],
    ).mark_bar().encode(
        y='value:Q',
        color=alt.Color('key:N', scale=scale).title('Legenda'))
    line = base.transform_fold(['PERC_ORARIO']).mark_line(interpolate="monotone").encode(alt.Y('PERC_ORARIO:Q', axis=alt.Axis(title=None)), color=alt.Color('key:N', scale=scale))

    chart = (bars + line).properties(width=600)

    return chart, data


def grafico_media(conn, intervallo_date, scelta_linea_codice):
    data = conn.query(f"SELECT C.DATA, IFNULL(AVG(C.RIT),0) AS MEDIA_RIT FROM CORSE AS C, TRENI AS T WHERE C.NUMTRENO=T.NUMTRENO AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' AND T.LINEA={int(scelta_linea_codice)} GROUP BY C.DATA;",
                            ttl=0, show_spinner="Caricamento...")
    
    scale = alt.Scale(domain=['MEDIA_RIT'], range=['#6baed6'])
    chart = alt.Chart(data).transform_fold(['MEDIA_RIT']).mark_line(interpolate="monotone").encode(alt.X("DATA:T", axis=alt.Axis(title=None)), alt.Y("MEDIA_RIT:Q", axis=alt.Axis(title=None)), color=alt.Color('key:N', scale=scale).title('Legenda'))
    
    return chart, data


def grafico_per_num_treno(conn, intervallo_date, scelta_linea_codice):
    data = conn.query(f"with TabTreni AS (SELECT C.NumTreno FROM CORSE AS C, TRENI AS T WHERE T.NumTreno=C.NumTreno AND T.LINEA={int(scelta_linea_codice)} AND C.Data>='{intervallo_date[0]}' AND C.Data<='{intervallo_date[1]}' GROUP BY NUMTRENO), TabRit5 AS (SELECT C.NumTreno, COUNT(*) AS RIT5 FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND RIT>=5 AND RIT<15 AND C.Data>='{intervallo_date[0]}' AND C.Data<='{intervallo_date[1]}' GROUP BY NumTreno), TabRit15 AS (SELECT C.NumTreno, COUNT(*) AS RIT15 FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND RIT>=15 AND C.Data>='{intervallo_date[0]}' AND C.Data<='{intervallo_date[1]}' GROUP BY NumTreno), TabSopp AS (SELECT C.NumTreno, COUNT(*) AS SOPP FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND Sopp=1 AND C.Data>='{intervallo_date[0]}' AND C.Data<='{intervallo_date[1]}' GROUP BY NumTreno), TabVar AS (SELECT C.NumTreno, COUNT(*) AS VAR FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND Var=1 AND C.Data>='{intervallo_date[0]}' AND C.Data<='{intervallo_date[1]}' GROUP BY NumTreno) SELECT TT.NumTreno AS NUMTRENO, IFNULL(RIT5,0) AS N_RIT5, IFNULL(RIT15,0) AS N_RIT15, IFNULL(SOPP,0) AS N_SOPP, IFNULL(VAR,0) AS N_VAR FROM TABTreni AS TT LEFT JOIN TABRIT5 AS TR5 ON TT.NumTreno=TR5.NumTreno LEFT JOIN TABRIT15 AS TR15 ON TT.NumTreno=TR15.NumTreno LEFT JOIN TABSOPP AS TS ON TT.NumTreno=TS.NumTreno LEFT JOIN TABVAR AS TV ON TT.NumTreno=TV.NumTreno;",
                            ttl=0, show_spinner="Caricamento...")

    data['NUMTRENO'] = data.NUMTRENO.astype('str')
    
    scale = alt.Scale(domain=['N_RIT5', 'N_RIT15', 'N_SOPP', 'N_VAR'], range=['yellow', 'orange', 'red', 'purple'])
    chart = alt.Chart(data).transform_fold(['N_RIT5', 'N_RIT15', 'N_SOPP', 'N_VAR']).mark_bar(size=15).encode(alt.X("NUMTRENO", axis=alt.Axis(title=None)), alt.Y("value:Q", axis=alt.Axis(title=None)), color=alt.Color('key:N', scale=scale).title('Legenda'))
   
    return chart, data


def grafico_media_per_num_treno(conn, intervallo_date, scelta_linea_codice):
    data = conn.query(f"SELECT C.NumTreno AS NUMTRENO, AVG(rit) AS MEDIA_RIT FROM CORSE C, TRENI T WHERE C.NumTreno=T.NumTreno AND Linea={int(scelta_linea_codice)} AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY C.NumTreno;", ttl=0, show_spinner="Caricamento...")
    
    data['NUMTRENO'] = data.NUMTRENO.astype('str')

    scale = alt.Scale(domain=['MEDIA_RIT'], range=['#6baed6'])
    chart = alt.Chart(data).transform_fold(['MEDIA_RIT']).mark_bar(size=15).encode(alt.X("NUMTRENO", axis=alt.Axis(title=None)), alt.Y("MEDIA_RIT:Q", axis=alt.Axis(title=None)), color=alt.Color('key:N', scale=scale).title('Legenda'))

    return chart, data


def metrics_intervallo(conn, intervallo_date, scelta_linea_codice):
    data = conn.query(f"WITH TabGroupDay AS (SELECT CORSE.Data as DATE, COUNT(*) AS NUMTOT FROM CORSE, TRENI WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)} AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY CORSE.Data), TabOr AS (SELECT CORSE.Data as DATE, COUNT(*) AS ORARIO FROM CORSE, TRENI WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)} AND RIT IS NOT NULL AND RIT<5 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY CORSE.Data), TabR5 AS (SELECT CORSE.Data as DATE, COUNT(*) AS RIT5 FROM CORSE, TRENI WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)} AND RIT IS NOT NULL AND RIT>=5 AND RIT<15 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY CORSE.Data), TabR15 AS (SELECT CORSE.Data as DATE, COUNT(*) AS RIT15 FROM CORSE, TRENI WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)} AND RIT IS NOT NULL AND RIT>=15 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY CORSE.Data), TabSopp AS (SELECT CORSE.Data as DATE, COUNT(*) AS SOPP FROM CORSE, TRENI WHERE CORSE.NumTreno=TRENI.NumTreno AND TRENI.Linea={int(scelta_linea_codice)} AND CORSE.Sopp=1 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY CORSE.Data), TabVar AS (SELECT CORSE.Data as DATE, COUNT(*) AS VAR FROM CORSE, TRENI WHERE CORSE.NumTreno=TRENI.NumTreno AND TRENI.Linea={int(scelta_linea_codice)} AND CORSE.Var=1 AND Data>='{intervallo_date[0]}' AND Data<='{intervallo_date[1]}' GROUP BY CORSE.Data), TabDati1 AS (SELECT TGD.DATE AS DATE, NUMTOT, IFNULL(ORARIO,0) AS ORARIO, IFNULL(RIT5,0) AS RIT5, IFNULL(RIT15,0) AS RIT15, IFNULL(SOPP,0) AS SOPP, IFNULL(VAR,0) AS VAR FROM TabGroupDay AS TGD LEFT JOIN TabOr AS TOR ON TGD.DATE=TOR.DATE LEFT JOIN TabR5 AS TR5 ON TGD.DATE=TR5.DATE LEFT JOIN TabR15 AS TR15 ON TGD.DATE=TR15.DATE LEFT JOIN TabSopp AS TSP ON TGD.DATE=TSP.DATE LEFT JOIN TabVar as TVR ON TGD.DATE=TVR.DATE) SELECT MIN(DATE) AS DATA_DA, MAX(DATE) AS DATA_A, (SUM(ORARIO)/SUM(NUMTOT))*100 AS PUNTUALITA, SUM(RIT5) AS RIT5, SUM(RIT15) AS RIT15, SUM(SOPP) AS SOPP, SUM(VAR) AS VAR, SUM(NUMTOT) AS TRENI_TOT FROM TabDati1;", ttl=0, show_spinner="Caricamento...")
    punt_val = data['PUNTUALITA'][0]
    r5_val = int(data['RIT5'][0])
    r15_val = int(data['RIT15'][0])
    sopp_val = int(data['SOPP'][0])
    var_val = int(data['VAR'][0])
    treni_tot_val = int(data['TRENI_TOT'][0])

    return punt_val, r5_val, r15_val, sopp_val, var_val, treni_tot_val


def calcola_df_puntualita_iniziali(conn, scelta_linea_codice):
    puntualita = conn.query(f"WITH TabMaxDate AS (SELECT MAX(DATA) AS DATAMASSIMA FROM CORSE, TRENI WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)}), TabGroupDay AS (SELECT CORSE.Data as DATE, COUNT(*) AS NUMTOT FROM CORSE, TRENI WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)} AND Data >= DATE_SUB((SELECT DATAMASSIMA FROM TabMaxDate), INTERVAL 6 DAY) GROUP BY CORSE.Data), TabOr AS (SELECT CORSE.Data as DATE, COUNT(*) AS ORARIO FROM CORSE, TRENI WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)} AND RIT IS NOT NULL AND RIT<5 AND Data >= DATE_SUB((SELECT DATAMASSIMA FROM TabMaxDate), INTERVAL 6 DAY) GROUP BY CORSE.Data), TabR5 AS (SELECT CORSE.Data as DATE, COUNT(*) AS RIT5 FROM CORSE, TRENI WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)} AND RIT IS NOT NULL AND RIT>=5 AND RIT<15 AND Data >= DATE_SUB((SELECT DATAMASSIMA FROM TabMaxDate), INTERVAL 6 DAY) GROUP BY CORSE.Data), TabR15 AS (SELECT CORSE.Data as DATE, COUNT(*) AS RIT15 FROM CORSE, TRENI WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)} AND RIT IS NOT NULL AND RIT>=15 AND Data >= DATE_SUB((SELECT DATAMASSIMA FROM TabMaxDate), INTERVAL 6 DAY) GROUP BY CORSE.Data), TabSopp AS (SELECT CORSE.Data as DATE, COUNT(*) AS SOPP FROM CORSE, TRENI WHERE CORSE.NumTreno=TRENI.NumTreno AND TRENI.Linea={int(scelta_linea_codice)} AND CORSE.Sopp=1 AND Data >= DATE_SUB((SELECT DATAMASSIMA FROM TabMaxDate), INTERVAL 6 DAY) GROUP BY CORSE.Data), TabVar AS (SELECT CORSE.Data as DATE, COUNT(*) AS VAR FROM CORSE, TRENI WHERE CORSE.NumTreno=TRENI.NumTreno AND TRENI.Linea={int(scelta_linea_codice)} AND CORSE.Var=1 AND Data >= DATE_SUB((SELECT DATAMASSIMA FROM TabMaxDate), INTERVAL 6 DAY) GROUP BY CORSE.Data), TabDati1 AS (SELECT TGD.DATE AS DATE, NUMTOT, IFNULL(ORARIO,0) AS ORARIO, IFNULL(RIT5,0) AS RIT5, IFNULL(RIT15,0) AS RIT15, IFNULL(SOPP,0) AS SOPP, IFNULL(VAR,0) AS VAR FROM TabGroupDay AS TGD LEFT JOIN TabOr AS TOR ON TGD.DATE=TOR.DATE LEFT JOIN TabR5 AS TR5 ON TGD.DATE=TR5.DATE LEFT JOIN TabR15 AS TR15 ON TGD.DATE=TR15.DATE LEFT JOIN TabSopp as TSP ON TGD.DATE=TSP.DATE LEFT JOIN TabVar as TVR ON TGD.DATE=TVR.DATE) SELECT MIN(DATE) AS DATA_DA, MAX(DATE) AS DATA_A, (SUM(ORARIO)/SUM(NUMTOT))*100 AS PUNTUALITA, SUM(RIT5) AS RIT5, SUM(RIT15) AS RIT15, SUM(SOPP) AS SOPP, SUM(VAR) AS VAR, SUM(NUMTOT) AS TRENI_TOT FROM TabDati1;", ttl=0, show_spinner="Caricamento...")
    puntualita_scorsa_sett = conn.query(f"WITH TabMaxDate AS (SELECT MAX(DATA) AS DATAMASSIMA FROM CORSE, TRENI WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)}), TabGroupDay AS (SELECT CORSE.Data as DATE, COUNT(*) AS NUMTOT FROM CORSE, TRENI, TabMaxDate WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)} AND Data>=DATE_SUB(DATAMASSIMA, INTERVAL 13 DAY) AND Data<=DATE_SUB(DATAMASSIMA, INTERVAL 7 DAY) GROUP BY CORSE.Data), TabOr AS (SELECT CORSE.Data as DATE, COUNT(*) AS ORARIO FROM CORSE, TRENI, TabMaxDate WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)} AND RIT IS NOT NULL AND RIT<5 AND Data>=DATE_SUB(DATAMASSIMA, INTERVAL 13 DAY) AND Data<=DATE_SUB(DATAMASSIMA, INTERVAL 7 DAY) GROUP BY CORSE.Data), TabR5 AS (SELECT CORSE.Data as DATE, COUNT(*) AS RIT5 FROM CORSE, TRENI, TabMaxDate WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)} AND RIT IS NOT NULL AND RIT>=5 AND RIT<15 AND Data>=DATE_SUB(DATAMASSIMA, INTERVAL 13 DAY) AND Data<=DATE_SUB(DATAMASSIMA, INTERVAL 7 DAY) GROUP BY CORSE.Data), TabR15 AS (SELECT CORSE.Data as DATE, COUNT(*) AS RIT15 FROM CORSE, TRENI, TabMaxDate WHERE CORSE.NumTreno = TRENI.NumTreno AND TRENI.LINEA={int(scelta_linea_codice)} AND RIT IS NOT NULL AND RIT>=15 AND Data>=DATE_SUB(DATAMASSIMA, INTERVAL 13 DAY) AND Data<=DATE_SUB(DATAMASSIMA, INTERVAL 7 DAY) GROUP BY CORSE.Data), TabSopp AS (SELECT CORSE.Data as DATE, COUNT(*) AS SOPP FROM CORSE, TRENI, TabMaxDate WHERE CORSE.NumTreno=TRENI.NumTreno AND TRENI.Linea={int(scelta_linea_codice)} AND CORSE.Sopp=1 AND Data>=DATE_SUB(DATAMASSIMA, INTERVAL 13 DAY) AND Data<=DATE_SUB(DATAMASSIMA, INTERVAL 7 DAY) GROUP BY CORSE.Data), TabVar AS (SELECT CORSE.Data as DATE, COUNT(*) AS VAR FROM CORSE, TRENI, TabMaxDate WHERE CORSE.NumTreno=TRENI.NumTreno AND TRENI.Linea={int(scelta_linea_codice)} AND CORSE.Var=1 AND Data>=DATE_SUB(DATAMASSIMA, INTERVAL 13 DAY) AND Data<=DATE_SUB(DATAMASSIMA, INTERVAL 7 DAY) GROUP BY CORSE.Data), TabDati1 AS (SELECT TGD.DATE AS DATE, NUMTOT, IFNULL(ORARIO,0) AS ORARIO, IFNULL(RIT5,0) AS RIT5, IFNULL(RIT15,0) AS RIT15, IFNULL(SOPP,0) AS SOPP, IFNULL(VAR,0) AS VAR FROM TabGroupDay AS TGD LEFT JOIN TabOr AS TOR ON TGD.DATE=TOR.DATE LEFT JOIN TabR5 AS TR5 ON TGD.DATE=TR5.DATE LEFT JOIN TabR15 AS TR15 ON TGD.DATE=TR15.DATE LEFT JOIN TabSopp as TSP ON TGD.DATE=TSP.DATE LEFT JOIN TabVar as TVR ON TGD.DATE=TVR.DATE) SELECT MIN(DATE) AS DATA_DA, MAX(DATE) AS DATA_A, (SUM(ORARIO)/SUM(NUMTOT))*100 AS PUNTUALITA, SUM(RIT5) AS RIT5, SUM(RIT15) AS RIT15, SUM(SOPP) AS SOPP, SUM(VAR) AS VAR FROM TabDati1;", ttl=0, show_spinner="Caricamento...")
    return puntualita, puntualita_scorsa_sett

def valori_puntualita_iniziali(puntualita):
    data_da = puntualita['DATA_DA'][0]
    data_a = puntualita['DATA_A'][0]
    punt_val = puntualita['PUNTUALITA'][0]
    r5_val = int(puntualita['RIT5'][0])
    r15_val = int(puntualita['RIT15'][0])
    sopp_val = int(puntualita['SOPP'][0])
    var_val = int(puntualita['VAR'][0])
    treni_tot_val = int(puntualita['TRENI_TOT'][0])
    return data_da, data_a, punt_val, r5_val, r15_val, sopp_val, var_val, treni_tot_val

def valori_delta_puntualita(puntualita_scorsa_sett, punt_val, r5_val, r15_val, sopp_val, var_val):
    delta_or_val = punt_val-puntualita_scorsa_sett['PUNTUALITA'][0]
    delta_r5_val = int(r5_val-puntualita_scorsa_sett['RIT5'][0])
    delta_r15_val = int(r15_val-puntualita_scorsa_sett['RIT15'][0])
    delta_sopp_val = int(sopp_val-puntualita_scorsa_sett['SOPP'][0])
    delta_var_val = int(var_val-puntualita_scorsa_sett['VAR'][0])
    return delta_or_val, delta_r5_val, delta_r15_val, delta_sopp_val, delta_var_val
