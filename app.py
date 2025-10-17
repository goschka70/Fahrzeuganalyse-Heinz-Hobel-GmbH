import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Fahrzeuganalyse je Kunde", layout="wide")
st.title("🚗 Fahrzeuganalyse je Kunde – Heinz Hobel GmbH")

uploaded_file = st.file_uploader("Bitte lade eine CSV-Datei hoch im Format der Auftragsliste", type="csv")

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file, sep=';', engine='python')
    except Exception as e:
        st.error(f"Fehler beim Einlesen der Datei: {e}")
    else:
        df.columns = [col.strip() for col in df.columns]
        df = df.rename(columns={
            'Auftraggeber': 'Kunde',
            'N / G': 'Fahrzeugart',
            'Fahrzeugeingang': 'Eingang',
            'Auslieferung geplant am': 'Auslieferung',
            'Platz': 'Platz'
        })

        df['Eingang'] = pd.to_datetime(df['Eingang'], errors='coerce')
        df['Auslieferung'] = pd.to_datetime(df['Auslieferung'], errors='coerce')
        heute = pd.to_datetime(datetime.today().date())
        df['Standzeit'] = (heute - df['Eingang']).dt.days
        df['Auslieferung vorhanden'] = df['Auslieferung'].notna()

        # 🔍 Platzfilter
        st.sidebar.header("🔍 Filter")
        verfügbare_plätze = sorted(df['Platz'].dropna().unique())
        ausgewählte_plätze = st.sidebar.multiselect("Platz auswählen", verfügbare_plätze, default=verfügbare_plätze)
        df_filtered = df[df['Platz'].isin(ausgewählte_plätze)]

        # 1️⃣ Anzahl neuer und gebrauchter Fahrzeuge je Kunde
        st.subheader("1️⃣ Anzahl neuer und gebrauchter Fahrzeuge je Kunde")
        fahrzeug_counts = df_filtered.groupby(['Kunde', 'Fahrzeugart']).size().reset_index(name='Anzahl')
        fig1 = px.bar(fahrzeug_counts, x='Kunde', y='Anzahl', color='Fahrzeugart')
        st.plotly_chart(fig1, use_container_width=True)

        # 2️⃣ Ø Standzeit mit/ohne Auslieferungstermin je Kunde
        st.subheader("2️⃣ Ø Standzeit mit/ohne Auslieferungstermin je Kunde")
        standzeit_avg = df_filtered.groupby(['Kunde', 'Auslieferung vorhanden'])['Standzeit'].mean().reset_index()
        fig2 = px.bar(standzeit_avg, x='Kunde', y='Standzeit', color='Auslieferung vorhanden')
        st.plotly_chart(fig2, use_container_width=True)

        # 3️⃣ Gesamtanzahl Fahrzeuge je Kunde
        st.subheader("3️⃣ Gesamtanzahl Fahrzeuge je Kunde")
        total_counts = df_filtered['Kunde'].value_counts().reset_index()
        total_counts.columns = ['Kunde', 'Gesamtanzahl']
        fig3 = px.bar(total_counts, x='Kunde', y='Gesamtanzahl')
        st.plotly_chart(fig3, use_container_width=True)

        # 4️⃣ Top 5 Fahrzeuge mit längster Standzeit je Kunde
        st.subheader("4️⃣ Top 5 Fahrzeuge mit längster Standzeit je Kunde")
        top5_per_kunde = df_filtered.sort_values(['Kunde', 'Standzeit'], ascending=[True, False]).groupby('Kunde').head(5)
        fig4 = px.bar(top5_per_kunde, x='Kunde', y='Standzeit', color='Modell',
                      hover_data=['Fahrgestellnummer', 'Eingang', 'Auslieferung', 'Platz'])
        st.plotly_chart(fig4, use_container_width=True)
