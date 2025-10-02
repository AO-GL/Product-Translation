import streamlit as st
import pandas as pd
from deep_translator import GoogleTranslator

# -------------------------------
# Hilfsfunktion für die Übersetzung
# -------------------------------
def translate_text(text, target_lang, tone, seo_enabled, seo_keywords, blacklist_words):
    if not isinstance(text, str) or text.strip() == "":
        return ""

    translated = GoogleTranslator(source="auto", target=target_lang).translate(text)

    if tone == "marketing":
        translated = f"{translated} 🚀✨"
    elif tone == "sachlich":
        translated = translated.replace("!", ".")

    if seo_enabled and seo_keywords:
        translated += " " + " ".join(seo_keywords)

    for word in blacklist_words:
        translated = translated.replace(word, "")

    return translated


# -------------------------------
# Streamlit App Einstellungen
# -------------------------------
st.set_page_config(page_title="🌍 Produkt-Übersetzer", layout="wide")

# -------------------------------
# Custom CSS Styles
# -------------------------------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(to right, #f9f9f9, #eef3f7);
        font-family: 'Segoe UI', sans-serif;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
        font-weight: 800;
    }
    button[kind="secondary"], .stButton>button {
        background-color: #3498db;
        color: white;
        border-radius: 10px;
        padding: 0.6em 1.2em;
        font-weight: 600;
        transition: 0.3s;
    }
    button[kind="secondary"]:hover, .stButton>button:hover {
        background-color: #1abc9c;
        transform: scale(1.05);
    }
    .stDataFrame {
        border: 2px solid #3498db;
        border-radius: 10px;
        padding: 5px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Tabs
# -------------------------------
tab1, tab2, tab3 = st.tabs(["📂 Datei Upload", "⚙️ Optionen", "📊 Ergebnis"])

# -------------------------------
# Tab 1 – Datei Upload
# -------------------------------
with tab1:
    st.title("📂 Lade deine Excel-Datei hoch")
    uploaded_file = st.file_uploader("Bitte wähle eine Datei aus", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.success(f"✅ Datei geladen: **{uploaded_file.name}**")
        with st.expander("👀 Vorschau der Daten"):
            st.dataframe(df.head())

        st.session_state["df"] = df
        st.session_state["uploaded_file"] = uploaded_file

# -------------------------------
# Tab 2 – Optionen
# -------------------------------
with tab2:
    st.title("⚙️ Optionen für die Übersetzung")

    if "df" in st.session_state:
        df = st.session_state["df"]

        selected_column = st.selectbox("📌 Wähle die Spalte, die übersetzt werden soll:", df.columns)

        languages = st.multiselect(
            "🌐 In welche Sprachen soll übersetzt werden?",
            ["en", "fr", "es", "it", "nl", "pl", "tr"],
            default=["en"]
        )

        tone = st.radio("🎭 Welchen Tonfall sollen die Übersetzungen haben?", ("sachlich", "marketing"))

        seo_enabled = st.checkbox("📈 Soll der Text SEO-optimiert werden?")
        seo_keywords = []
        if seo_enabled:
            keywords_input = st.text_input("🔑 Gib SEO-Keywords ein (Komma-getrennt)")
            if keywords_input:
                seo_keywords = [k.strip() for k in keywords_input.split(",")]

        blacklist_input = st.text_input("🚫 Wörter, die NICHT vorkommen dürfen (Komma-getrennt)")
        blacklist_words = []
        if blacklist_input:
            blacklist_words = [w.strip() for w in blacklist_input.split(",")]

        st.session_state["options"] = {
            "selected_column": selected_column,
            "languages": languages,
            "tone": tone,
            "seo_enabled": seo_enabled,
            "seo_keywords": seo_keywords,
            "blacklist_words": blacklist_words,
        }

# -------------------------------
# Tab 3 – Ergebnis
# -------------------------------
with tab3:
    st.title("📊 Ergebnis")

    if "df" in st.session_state and "options" in st.session_state:
        df = st.session_state["df"]
        opts = st.session_state["options"]

        if st.button("🚀 Starte Übersetzung"):
            with st.spinner("Übersetze... bitte warten ⏳"):
                for lang in opts["languages"]:
                    df[f"Übersetzung_{lang}"] = df[opts["selected_column"]].apply(
                        lambda text: translate_text(
                            text,
                            lang,
                            opts["tone"],
                            opts["seo_enabled"],
                            opts["seo_keywords"],
                            opts["blacklist_words"],
                        )
                    )

            st.success("✅ Übersetzung abgeschlossen!")
            st.dataframe(df)

            output_file = "translated.xlsx"
            df.to_excel(output_file, index=False)

            with open(output_file, "rb") as f:
                st.download_button("📥 Übersetzte Datei herunterladen", f, file_name=output_file)
    else:
        st.info("⬅️ Bitte zuerst eine Datei hochladen und Optionen auswählen.")
