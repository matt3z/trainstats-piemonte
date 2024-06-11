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
    # data=conn.query("with TabTot AS (SELECT DATA, COUNT(*) AS NUMTOT FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea=118 GROUP BY DATA), TabOrario AS (SELECT DATA, COUNT(*) AS ORARIO FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea=118 AND RIT IS NOT NULL AND RIT<5 GROUP BY DATA), TabRit5 AS (SELECT DATA, COUNT(*) AS RIT5 FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea=118 AND RIT>=5 AND RIT<15 GROUP BY DATA), TabRit15 AS (SELECT DATA, COUNT(*) AS RIT15 FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea=118 AND RIT>=15 GROUP BY DATA), TabSopp AS (SELECT DATA, COUNT(*) AS SOPP FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea=118 AND Sopp=1 GROUP BY DATA), TabVar AS (SELECT DATA, COUNT(*) AS VAR FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea=118 AND Var=1 GROUP BY DATA) SELECT TT.DATA, (ORARIO/NUMTOT)*100 AS PERC_ORARIO, IFNULL((RIT5/NUMTOT)*100,0) AS PERC_RIT5, IFNULL((RIT15/NUMTOT)*100,0) AS PERC_RIT15, IFNULL(SOPP,0) AS N_SOPP, IFNULL(VAR,0) AS N_VAR FROM TABTOT AS TT LEFT JOIN TABORARIO AS TOR ON TT.DATA=TOR.DATA LEFT JOIN TABRIT5 AS TR5 ON TT.DATA=TR5.DATA LEFT JOIN TABRIT15 AS TR15 ON TT.DATA=TR15.DATA LEFT JOIN TABSOPP AS TS ON TT.DATA=TS.DATA LEFT JOIN TABVAR AS TV ON TT.DATA=TV.DATA;", ttl=0)
    data=conn.query(f"with TabTot AS (SELECT DATA, COUNT(*) AS NUMTOT FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} GROUP BY DATA), TabOrario AS (SELECT DATA, COUNT(*) AS ORARIO FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND RIT IS NOT NULL AND RIT<5 GROUP BY DATA), TabRit5 AS (SELECT DATA, COUNT(*) AS RIT5 FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND RIT>=5 AND RIT<15 GROUP BY DATA), TabRit15 AS (SELECT DATA, COUNT(*) AS RIT15 FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND RIT>=15 GROUP BY DATA), TabSopp AS (SELECT DATA, COUNT(*) AS SOPP FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND Sopp=1 GROUP BY DATA), TabVar AS (SELECT DATA, COUNT(*) AS VAR FROM CORSE AS C, TRENI AS T WHERE C.NumTreno=T.NumTreno AND T.Linea={int(scelta_linea_codice)} AND Var=1 GROUP BY DATA) SELECT TT.DATA, (ORARIO/NUMTOT)*100 AS PERC_ORARIO, IFNULL(RIT5,0) AS N_RIT5, IFNULL(RIT15,0) AS N_RIT15, IFNULL(SOPP,0) AS N_SOPP, IFNULL(VAR,0) AS N_VAR FROM TABTOT AS TT LEFT JOIN TABORARIO AS TOR ON TT.DATA=TOR.DATA LEFT JOIN TABRIT5 AS TR5 ON TT.DATA=TR5.DATA LEFT JOIN TABRIT15 AS TR15 ON TT.DATA=TR15.DATA LEFT JOIN TABSOPP AS TS ON TT.DATA=TS.DATA LEFT JOIN TABVAR AS TV ON TT.DATA=TV.DATA WHERE TT.DATA>='{intervallo_date[0]}' AND TT.DATA<='{intervallo_date[1]}';", ttl=0)

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
    data = conn.query(f"SELECT C.DATA, AVG(C.RIT) AS MEDIA_RIT FROM CORSE AS C, TRENI AS T WHERE C.NUMTRENO=T.NUMTRENO AND DATA>='{intervallo_date[0]}' AND DATA<='{intervallo_date[1]}' AND T.LINEA={int(scelta_linea_codice)} GROUP BY C.DATA;",
                            ttl=0)
    
    scale = alt.Scale(domain=['MEDIA_RIT'], range=['#6baed6'])
    chart = alt.Chart(data).transform_fold(['MEDIA_RIT']).mark_line(interpolate="monotone").encode(alt.X("DATA:T", axis=alt.Axis(title=None)), alt.Y("MEDIA_RIT:Q", axis=alt.Axis(title=None)), color=alt.Color('key:N', scale=scale).title('Legenda'))
    
    return chart, data
