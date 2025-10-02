import streamlit as st
import pandas as pd
import re
import html
from deep_translator import GoogleTranslator

# ========================
# Sprachmapping (Deutsch -> Kürzel)
# ========================
LANGUAGE_MAP = {
    "Englisch": "en",
    "Französisch": "fr",
    "Spanisch": "es",
    "Italienisch": "it",
    "Niederländisch": "nl",
    "Polnisch": "pl",
    "Türkisch": "tr"
}

# ========================
# Funktion: Text säubern
# ========================
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)                # HTML Entities (&ouml; -> ö)
    text = re.sub(r"<.*?>", "", text)         # HTML Tags entfernen
    text = re.sub(r"[^\w\s.,!?;:()'\"-]", "", text)  # Emojis & Sonderzeichen
    return text.strip()

# ========================
# Streamlit Konfiguration
# ========================
st.set_page_config(page_title="Produkt Übersetzer", layout="wide")

# Session State vorbereiten
if "df" not in st.session_state:
    st.session_state.df = None
if "translated_df" not in st.session_state:
    st.session_state.translated_df = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "📂 Datei Upload"

# Tabs
tab_names = ["📂 Datei Upload", "⚙️ Optionen", "📊 Ergebnis"]
tabs = st.tabs(tab_names)

# =====================
# TAB 1: Datei Upload
# =====================
with tabs[0]:
    st.header("📂 Excel Datei hochladen")
    uploaded_file = st.file_uploader("Lade eine Excel Datei hoch", type=["xlsx"])
    if uploaded_file:
        st.session_state.df = pd.read_excel(uploaded_file)
        st.success("✅ Datei erfolgreich hochgeladen")
        st.write("Vorschau:", st.session_state.df.head())
        st.session_state.active_tab = "⚙️ Optionen"   # nach Upload weiterleiten

# =====================
# TAB 2: Optionen
# =====================
with tabs[1]:
    st.header("⚙️ Optionen für die Übersetzung")

    if st.session_state.df is not None:
        column = st.selectbox("📌 Wähle die Spalte, die übersetzt werden soll:", st.session_state.df.columns)

        target_languages = st.multiselect(
            "🌍 In welche Sprachen soll übersetzt werden?",
            list(LANGUAGE_MAP.keys())
        )

        tone = st.radio("📝 Schreibstil wählen:", ["Sachlich", "Marketing-orientiert"])
        seo = st.checkbox("🔍 SEO-Optimierung hinzufügen?")

        blacklist_input = st.text_area("🚫 Wörter, die NICHT vorkommen sollen (durch Komma trennen):")
        blacklist = [w.strip() for w in blacklist_input.split(",") if w.strip()]

        html_option = st.checkbox("📄 Übersetzung zusätzlich als HTML in neuer Spalte speichern?")

        if st.button("🚀 Übersetzung starten"):
            df = st.session_state.df.copy()
            progress = st.progress(0)
            total = len(df)

            for i, text in enumerate(df[column]):
                cleaned_text = clean_text(text)

                for lang_name in target_languages:
                    lang_code = LANGUAGE_MAP[lang_name]
                    try:
                        translated = GoogleTranslator(source="de", target=lang_code).translate(cleaned_text)

                        # Blacklist anwenden
                        for bad_word in blacklist:
                            translated = translated.replace(bad_word, "")

                        # Neue Spalte
                        col_name = f"Übersetzt ({lang_name})"
                        df.loc[i, col_name] = translated

                        if html_option:
                            col_html = f"Übersetzt HTML ({lang_name})"
                            df.loc[i, col_html] = f"<p>{translated}</p>"

                    except Exception as e:
                        st.warning(f"⚠️ Fehler bei Zeile {i+1}: {e}")

                progress.progress(int(((i+1)/total)*100))

            st.session_state.translated_df = df
            st.session_state.active_tab = "📊 Ergebnis"  # nach Übersetzung weiterleiten

# =====================
# TAB 3: Ergebnis
# =====================
with tabs[2]:
    st.header("📊 Ergebnis der Übersetzung")

    if st.session_state.translated_df is not None:
        st.write("✅ Übersetzte Tabelle:")
        st.dataframe(st.session_state.translated_df)

        output_file = "translated.xlsx"
        st.session_state.translated_df.to_excel(output_file, index=False)
        with open(output_file, "rb") as f:
            st.download_button("📥 Übersetzte Datei herunterladen", f, file_name=output_file)
