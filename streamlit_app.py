import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator
import time

# ------------------------
# Sprach-Mapping Deutsch → ISO-Codes
# ------------------------
LANGUAGES = {
    "Englisch": "en",
    "Französisch": "fr",
    "Spanisch": "es",
    "Italienisch": "it",
    "Niederländisch": "nl",
    "Polnisch": "pl",
    "Türkisch": "tr",
    "Arabisch": "ar",
    "Chinesisch": "zh-CN",
    "Japanisch": "ja",
    "Russisch": "ru",
    "Portugiesisch": "pt",
    "Deutsch": "de"
}

# ------------------------
# Streamlit Tabs
# ------------------------
st.set_page_config(page_title="Excel Übersetzer", layout="wide")
tabs = st.tabs(["📂 Datei Upload", "⚙️ Optionen", "📊 Ergebnis"])

# ------------------------
# Tab 1: Datei Upload
# ------------------------
with tabs[0]:
    st.header("📂 Lade deine Excel-Datei hoch")
    uploaded_file = st.file_uploader("Excel-Datei auswählen", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.session_state["df"] = df
        st.success("✅ Datei erfolgreich hochgeladen")
        st.dataframe(df.head())

# ------------------------
# Tab 2: Optionen
# ------------------------
with tabs[1]:
    st.header("⚙️ Optionen für die Übersetzung")

    if "df" in st.session_state:
        df = st.session_state["df"]

        # Spalte wählen
        column = st.selectbox("📌 Wähle die Spalte, die übersetzt werden soll:", df.columns)
        st.session_state["column"] = column

        # Zielsprachen
        target_languages = st.multiselect("🌍 In welche Sprachen soll übersetzt werden?",
                                          list(LANGUAGES.keys()))
        st.session_state["target_languages"] = target_languages

        # Stil
        tone = st.radio("🎨 Schreibstil wählen:", ["Sachlich", "Marketing-orientiert"])
        st.session_state["tone"] = tone

        # SEO
        seo = st.checkbox("🔍 SEO-Optimierung hinzufügen?")
        st.session_state["seo"] = seo

        # Blacklist
        blacklist = st.text_area("🚫 Wörter, die NICHT in der Übersetzung vorkommen sollen (durch Komma trennen):")
        st.session_state["blacklist"] = [w.strip() for w in blacklist.split(",")] if blacklist else []

        # HTML Option
        html_option = st.checkbox("📄 Übersetzung zusätzlich als HTML in neuer Spalte speichern?")
        st.session_state["html_option"] = html_option

        # Start Button
        if st.button("🚀 Übersetzung starten"):
            st.session_state["translate"] = True
            st.experimental_set_query_params(tab="Ergebnis")  # Automatisch zu Ergebnis springen

# ------------------------
# Tab 3: Ergebnis
# ------------------------
with tabs[2]:
    st.header("📊 Ergebnis der Übersetzung")

    if st.session_state.get("translate", False) and "df" in st.session_state:
        df = st.session_state["df"]
        column = st.session_state["column"]
        target_languages = st.session_state["target_languages"]

        progress = st.progress(0)
        result_df = df.copy()

        total = len(df) * len(target_languages)
        count = 0

        for lang_name in target_languages:
            lang_code = LANGUAGES[lang_name]
            translations = []

            for text in df[column].astype(str):
                try:
                    trans = GoogleTranslator(source="auto", target=lang_code).translate(text)

                    # Blacklist Wörter entfernen
                    for bad_word in st.session_state["blacklist"]:
                        trans = trans.replace(bad_word, "")

                    # Marketing-Ton / SEO (einfaches Beispiel)
                    if st.session_state["tone"] == "Marketing-orientiert":
                        trans = "🌟 " + trans
                    if st.session_state["seo"]:
                        trans += " ⭐"

                    translations.append(trans)
                except Exception as e:
                    translations.append(f"Fehler: {e}")

                count += 1
                progress.progress(int((count / total) * 100))

            # Neue Spalte mit Übersetzung
            result_df[f"Übersetzt ({lang_name})"] = translations

            # Optional HTML
            if st.session_state["html_option"]:
                html_translations = [f"<p>{t}</p>" for t in translations]
                result_df[f"HTML ({lang_name})"] = html_translations

        st.success("✅ Übersetzung abgeschlossen!")
        st.dataframe(result_df.head())

        # Ergebnis speichern
        output_file = "translated.xlsx"
        result_df.to_excel(output_file, index=False)

        with open(output_file, "rb") as f:
            st.download_button("📥 Übersetzte Datei herunterladen", f, file_name=output_file)

    else:
        st.info("ℹ️ Bitte zuerst eine Datei hochladen und Optionen auswählen.")
