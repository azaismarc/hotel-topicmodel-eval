# app.py
import streamlit as st
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from bertopic import BERTopic
from collections import Counter, defaultdict
import streamlit.components.v1 as components
from sklearn.feature_extraction.text import CountVectorizer
from utils import STOPWORDS


STOPWORDS = list(STOPWORDS)


def app():

    # -------------------------
    # Caching helpers
    # -------------------------
    @st.cache_data(ttl=60*60*24)
    def load_embeddings(path):
        return np.load(path)

    @st.cache_data(ttl=60*60*24)
    def load_keywords(path):
        return pd.read_csv(path, sep='\t')

    @st.cache_resource
    def fit_topic_model(keywords, embeddings, n_topics):
        kmeans = KMeans(n_clusters=n_topics, random_state=42)
        topic_model = BERTopic(
            hdbscan_model=kmeans,
            language='french',
            vectorizer_model=CountVectorizer(stop_words=STOPWORDS, strip_accents='ascii')
        )
        topics, _ = topic_model.fit_transform(keywords, embeddings)
        return topic_model, topics

    # -------------------------
    # Paths
    # -------------------------
    EMBEDDINGS_PATH = "public/sentences_embeddings.npy"
    SENTENCES_PATH = "public/sentences.tsv"

    # -------------------------
    # Sidebar
    # -------------------------
    # with st.sidebar:
    #     st.header("⚙️ Paramètres - Reviews")
    #     k_all = st.slider("Nombre de topics (K)", min_value=2, max_value=50, value=25, step=1)
    K_ALL = 30
    # -------------------------
    # Load data
    # -------------------------
    try:
        embeddings = load_embeddings(EMBEDDINGS_PATH)
        sentences_df = load_keywords(SENTENCES_PATH)
    except Exception as e:
        st.error(f"Erreur lors du chargement des fichiers : {e}")
        st.stop()

    # Validate
    if not {"sentiment", "text"}.issubset(sentences_df.columns):
        st.error("Le fichier sentences.tsv doit contenir les colonnes 'sentiment' et 'text'.")
        st.stop()

    # -------------------------
    # Merge POS & NEG
    # -------------------------
    df_all = sentences_df.reset_index(drop=True)
    

    # -------------------------
    # Fit model
    # -------------------------
    with st.spinner("🧠 Ajustement du modèle BERTopic sur tous les avis..."):
        topic_model, topics = fit_topic_model(df_all["text"].tolist(), embeddings, K_ALL)

    # -------------------------
    # Build topic words
    # -------------------------
    topic_words = defaultdict(Counter)
    for label, word_scores in topic_model.get_topics().items():
        for word, score in word_scores:
            if word not in STOPWORDS:
                topic_words[label][word] = score

    topic_labels = {label: ' '.join(w for w, _ in c.most_common(3)) for label, c in topic_words.items()}
    try:
        topic_model.set_topic_labels(topic_labels)
    except Exception:
        pass

    # -------------------------
    # Interactive Map
    # -------------------------

    hover_text = [
        f"{"🙂" if sent == "positif" else "☹️"} {txt}"
        for sent, txt in zip(df_all["sentiment"], df_all["text"])
    ]

    try:
        fig_interactive = topic_model.visualize_document_datamap(
            docs=hover_text,
            embeddings=embeddings,
            custom_labels=True,
            enable_search=True,
            interactive=True,
            int_datamap_kwds={
                "min_fontsize": 12,
                "max_fontsize": 18,
                "point_radius_min_pixels": 4,
                "point_radius_max_pixels": 40,
                "initial_zoom_fraction": 0.4,
                "marker_size_array": [len(s.split()) for s in df_all["text"].tolist()],
            }
        )
        components.html(str(fig_interactive), height=600)
    except Exception as e:
        st.error(f"Impossible d'afficher la carte interactive : {e}")

    # -------------------------
    # Wordclouds
    # -------------------------
    # st.markdown("☁️ **Nuages de mots par topic**")
    # topics_sorted = sorted(topic_words.items(), key=lambda x: x[0])
    # for i in range(0, len(topics_sorted), 5):
    #     row = topics_sorted[i:i+5]
    #     cols = st.columns(len(row))
    #     for j, (label, counter) in enumerate(row):
    #         with cols[j]:
    #             wc = WordCloud(width=300, height=200, background_color='white', min_font_size=12)
    #             wc.generate_from_frequencies(counter)
    #             fig, ax = plt.subplots(figsize=(3, 2))
    #             ax.imshow(wc, interpolation='bilinear')
    #             ax.axis('off')
    #             title = topic_labels.get(label, f"Topic {label}")
    #             ax.set_title(title, fontsize=10)
    #             st.pyplot(fig)
    #             plt.close(fig)
