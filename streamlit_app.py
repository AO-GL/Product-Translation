import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator

# Sprach-Mapping: Deutsch → Sprachcode
LANGUAGES = {
    "Englisch": "en",
    "Französisch": "fr",
    "Spanisch": "es",
    "Italienisch": "it",
    "Niederländisch": "nl",
    "Polnisch": "pl",
    "Türkisch": "tr",
    "Russisch": "ru",
    "Arabisch": "ar",
    "Chinesisch": "zh-CN",
    "Japanisch": "ja",
    "Portugiesisch": "pt",
    "Griechisch": "el",
    "Schwedisch": "sv",
    "Dänisch": "da",
    "Finnisch": "fi",
    "Ungarisch": "hu",
}

# 🎨 Streamlit Design
st.set_page_config(page_title="🌍 Produkt Übersetzer", layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f9fafc;
    }
    .main-title {
        text-align: center;
        color: #1f4e79;
        font-size: 36px;
        font-weight: bold;
    }
    .subtitle {
        text-align: center;
        color: #4b5563;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Titel
st.markdown('<p class="main-title">🌍 Produkt-Übersetzer Tool</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Übersetze deine Excel Produktdaten mit Stil, SEO & HTML-Optionen</p>', unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📂 Datei Upload", "⚙️ Optionen", "📊 Ergebnis"])

with tab1:
    st.header("📂 Lade deine Excel-Datei hoch")
    uploaded_file = st.file_uploader("Excel-Datei hochladen", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.success("✅ Datei erfolgreich geladen!")
        st.dataframe(df.head())

with tab2:
    st.header("⚙️ Optionen für die Übersetzung")

    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        # Spaltenauswahl
        column_to_translate = st.selectbox("📌 Wähle die Spalte, die übersetzt werden soll:", df.columns)

        # Zielsprachen
        target_languages = st.multiselect(
            "🌐 In welche Sprachen soll übersetzt werden?",
            list(LANGUAGES.keys())
        )

        # Schreibstil
        tone = st.radio(
            "🎯 Schreibstil auswählen",
            ["Sachlich", "Marketing-orientiert"]
        )

        # SEO-Option
        seo_opt = st.checkbox("🔍 SEO-Optimierung aktivieren (wichtige Begriffe betonen)")

        # HTML-Ausgabe
        html_opt = st.checkbox("📝 HTML-Version in einer zusätzlichen Spalte speichern")

        start_translation = st.button("🚀 Übersetzen starten")

with tab3:
    st.header("📊 Ergebnisse & Download")

    if uploaded_file and "start_translation" in locals() and start_translation:
        df = pd.read_excel(uploaded_file)

        for lang in target_languages:
            lang_code = LANGUAGES[lang]

            def process_text(x):
                if pd.isna(x):
                    return ""

                # Übersetzen
                translated = GoogleTranslator(source="auto", target=lang_code).translate(str(x))

                # Marketing Ton
                if tone == "Marketing-orientiert":
                    translated = f"✨ {translated}. Jetzt entdecken!"

                # SEO
                if seo_opt:
                    translated += " | Top Qualität, jetzt online bestellen!"

                return translated

            # Neue Spalte
            df[f"{column_to_translate}_{lang}"] = df[column_to_translate].apply(process_text)

            # Optional HTML
            if html_opt:
                df[f"{column_to_translate}_{lang}_HTML"] = df[f"{column_to_translate}_{lang}"].apply(
                    lambda txt: f"<p>{txt}</p>"
                )

        # Speichern
        output_file = "translated.xlsx"
        df.to_excel(output_file, index=False)

        # Ergebnis anzeigen
        st.dataframe(df.head())

        with open(output_file, "rb") as f:
            st.download_button("📥 Übersetzte Datei herunterladen", f, file_name=output_file)

        st.success("✅ Übersetzung abgeschlossen!")
