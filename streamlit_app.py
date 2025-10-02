import streamlit as st
import pandas as pd
import re
import html
from deep_translator import GoogleTranslator

# Sprachmapping
LANGUAGE_MAP = {
    "Englisch": "en",
    "Französisch": "fr",
    "Spanisch": "es",
    "Italienisch": "it",
    "Niederländisch": "nl",
    "Polnisch": "pl",
    "Türkisch": "tr"
}

# Textbereinigung
def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)  # &ouml; -> ö
    text = re.sub(r'[^\w\s.,!?;:()\'\"-]', '', text)
    return text.strip()

# -----------------------
# State
# -----------------------
if "step" not in st.session_state:
    st.session_state.step = "upload"
if "df" not in st.session_state:
    st.session_state.df = None

st.set_page_config(page_title="Produkt Übersetzer", layout="wide")

# -----------------------
# Step 1: Upload
# -----------------------
if st.session_state.step == "upload":
    st.header("📂 Excel Datei hochladen")
    uploaded_file = st.file_uploader("Lade eine Excel Datei hoch", type=["xlsx"])
    if uploaded_file:
        st.session_state.df = pd.read_excel(uploaded_file)
        st.success("✅ Datei erfolgreich hochgeladen")
        st.write("Vorschau:", st.session_state.df.head())
        if st.button("➡️ Weiter zu Optionen"):
            st.session_state.step = "options"
            st.rerun()

# -----------------------
# Step 2: Optionen
# -----------------------
elif st.session_state.step == "options":
    st.header("⚙️ Optionen für die Übersetzung")
    df = st.session_state.df

    column = st.selectbox("📌 Wähle die Spalte, die übersetzt werden soll:", df.columns)
    target_languages = st.multiselect("🌍 In welche Sprachen soll übersetzt werden?", list(LANGUAGE_MAP.keys()))
    tone = st.radio("📝 Schreibstil wählen:", ["Sachlich", "Marketing-orientiert"])
    seo = st.checkbox("🔍 SEO-Optimierung hinzufügen?")
    blacklist_input = st.text_area("🚫 Wörter, die NICHT vorkommen sollen (Komma-getrennt):")
    blacklist = [w.strip() for w in blacklist_input.split(",") if w.strip()]
    html_option = st.checkbox("📄 Übersetzung zusätzlich als HTML speichern?")

    if st.button("🚀 Übersetzung starten"):
        df_copy = df.copy()
        progress = st.progress(0)
        total = len(df_copy)

        for i, text in enumerate(df_copy[column]):
            cleaned_text = clean_text(text)
            for lang_name in target_languages:
                lang_code = LANGUAGE_MAP[lang_name]
                try:
                    translated = GoogleTranslator(source="de", target=lang_code).translate(cleaned_text)
                    for bad_word in blacklist:
                        translated = translated.replace(bad_word, "")
                    col_name = f"Übersetzt ({lang_name})"
                    df_copy.loc[i, col_name] = translated
                    if html_option:
                        col_html = f"Übersetzt HTML ({lang_name})"
                        df_copy.loc[i, col_html] = f"<p>{translated}</p>"
                except Exception as e:
                    st.warning(f"⚠️ Fehler bei Zeile {i+1}: {e}")
            progress.progress(int(((i+1)/total)*100))

        st.session_state.translated_df = df_copy
        st.session_state.step = "result"
        st.rerun()

# -----------------------
# Step 3: Ergebnis
# -----------------------
elif st.session_state.step == "result":
    st.header("📊 Ergebnis der Übersetzung")
    df_copy = st.session_state.translated_df
    st.write("✅ Übersetzte Tabelle:")
    st.dataframe(df_copy)

    output_file = "translated.xlsx"
    df_copy.to_excel(output_file, index=False)
    with open(output_file, "rb") as f:
        st.download_button("📥 Übersetzte Datei herunterladen", f, file_name=output_file)

    if st.button("⬅️ Neue Datei hochladen"):
        st.session_state.step = "upload"
        st.rerun()
