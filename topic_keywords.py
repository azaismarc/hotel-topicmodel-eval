# app.py
import streamlit as st
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from bertopic import BERTopic
from collections import Counter, defaultdict
import streamlit.components.v1 as components

def app():

    # -------------------------
    # Caching helpers
    # -------------------------
    @st.cache_data(ttl=60*60*24)  # cache 24h; adjust as needed
    def load_embeddings(path):
        return np.load(path)

    @st.cache_data(ttl=60*60*24)
    def load_keywords(path):
        return pd.read_csv(path)

    @st.cache_resource
    def fit_topic_model(filtered_keywords, filtered_embeddings, n_topics):
        """
        Fit BERTopic with a KMeans clusterer.
        This is cached so re-fitting only happens when inputs/parameters change.
        """
        kmeans = KMeans(n_clusters=n_topics, random_state=42)
        topic_model = BERTopic(hdbscan_model=kmeans, language='french')
        topics, probs = topic_model.fit_transform(filtered_keywords, filtered_embeddings)
        return topic_model, topics

    # -------------------------
    # Paths (change if needed)
    # -------------------------
    EMBEDDINGS_PATH = "public/keywords_embeddings.npy"
    KEYWORDS_PATH = "public/keywords.csv"


    MIN_FREQ = 5
    N_TOPICS = 30

    # -------------------------
    # UI - Sidebar (paramètres)
    # -------------------------
    # with st.sidebar:
    #     st.header("⚙️ Paramètres - Mot-Clé")
    #     n_topics = st.slider("Nombre de topics (K)", min_value=2, max_value=50, value=N_TOPICS, step=1)
    #     min_freq = st.slider("Fréquence minimale (filtre)", min_value=1, max_value=100, value=MIN_FREQ, step=1)
    #     st.markdown("---")
    #     # st.caption("Chargement et modèle sont mis en cache pour éviter des recalculs inutiles.")
    #     # st.markdown("**Astuce** : changez K ou la fréquence minimale pour recomputer les topics.")

    # -------------------------
    # Chargement des données
    # -------------------------
    try:
        embeddings = load_embeddings(EMBEDDINGS_PATH)
        keywords_df = load_keywords(KEYWORDS_PATH)
    except Exception as e:
        st.error(f"Erreur lors du chargement des fichiers : {e}")
        st.stop()

    # Validate
    if not {"item", "count"}.issubset(keywords_df.columns):
        st.error("Le fichier keywords.csv doit contenir les colonnes 'item' et 'count'.")
        st.stop()

    # -------------------------
    # Filtrage par fréquence
    # -------------------------
    df_filtered = keywords_df[keywords_df['count'] >= MIN_FREQ]
    filtered_indexes = df_filtered.index.tolist()
    if len(filtered_indexes) == 0:
        st.warning("Aucun mot-clé après application du filtre de fréquence. Réduisez le seuil.")
        st.stop()

    filtered_embeddings = embeddings[filtered_indexes]
    filtered_keywords = df_filtered['item'].tolist()
    filtered_freq = df_filtered['count'].tolist()

    # -------------------------
    # Fit model (cached)
    # -------------------------
    with st.spinner("🧠 Ajustement du modèle BERTopic (cela peut prendre un moment la première fois)..."):
        topic_model, topics = fit_topic_model(filtered_keywords, filtered_embeddings, N_TOPICS)

    # Build topic -> Counter of words (fréquences)
    topic_words = defaultdict(Counter)
    for word, freq, label in zip(filtered_keywords, filtered_freq, topics):
        topic_words[label][word] = freq

    # Create readable labels (top 3 mots)
    topic_labels = {label: ' '.join(w for w, _ in c.most_common(3)) for label, c in topic_words.items()}
    if len(topic_labels) > 0:
        try:
            topic_model.set_topic_labels(topic_labels)
        except Exception:
            # some BERTopic versions may differ; ignore if it fails
            pass

    # -------------------------
    # Layout principal
    # -------------------------
    # st.title("🧠 Explorateur BERTopic — mots-clés")
    # st.markdown(
    #     "Explorez des topics créés à partir d'embeddings de mots-clés. "
    #     "Utilisez le panneau de gauche pour ajuster les paramètres."
    # )

    # Two-column main area: left = carte interactive, right = résumé

    
        fig_interactive = topic_model.visualize_document_datamap(
            docs=filtered_keywords,
            embeddings=filtered_embeddings,
            interactive=True,
            enable_search=True,
            custom_labels=True,
            int_datamap_kwds={
                "min_fontsize": 12,
                "max_fontsize": 18,
                "marker_size_array": filtered_freq,
                "point_radius_min_pixels": 4,
                "point_radius_max_pixels": 40,
                "initial_zoom_fraction": 0.4,
            }
        )
        components.html(str(fig_interactive), height=700)


       

        # st.subheader("☁️ Nuages de mots par topic")
        # # Display wordclouds in rows of 5
        # def display_wordclouds(topic_words_map, cols_per_row=5):
        #     topics = sorted(topic_words_map.items(), key=lambda x: x[0])
        #     if len(topics) == 0:
        #         st.warning("Aucun topic à afficher.")
        #         return
        #     # chunk into rows
        #     for i in range(0, len(topics), cols_per_row):
        #         row = topics[i:i+cols_per_row]
        #         cols = st.columns(cols_per_row)
        #         for j, (label, counter) in enumerate(row):
        #             col = cols[j]
        #             with col:
        #                 wc = WordCloud(width=300, height=200, background_color='white', min_font_size=12)
        #                 wc.generate_from_frequencies(counter)
        #                 fig, ax = plt.subplots(figsize=(3,2))
        #                 ax.imshow(wc, interpolation='bilinear')
        #                 ax.axis('off')
        #                 title = topic_labels.get(label, f"Topic {label}")
        #                 ax.set_title(title, fontsize=10)
        #                 st.pyplot(fig)
        #                 plt.close(fig)

        # display_wordclouds(topic_words, cols_per_row=5)

    # with right_col:
    #     st.subheader("🔎 Résumé rapide")
    #     st.markdown(f"- **Embeddings chargés** : {embeddings.shape[0]} éléments")
    #     st.markdown(f"- **Mots-clés après filtre** : {len(filtered_keywords)}")
    #     st.markdown(f"- **Nombre de topics (K)** : {N_TOPICS}")
    #     st.markdown("---")

    #st.markdown("---")

    # -------------------------
    # Section similaire (autocomplete)
    # -------------------------
    # st.subheader("🔍 Trouver les tokens les plus similaires")
    # st.markdown("Recherchez un token via la liste (autocomplétion). Le calcul de similarité n'entraîne pas la recomputation du modèle.")

    # # Use a searchable selectbox for autocomplete-like behavior
    # token_choice = st.selectbox(
    #     "Sélectionnez un token (commencez à taper pour rechercher) :",
    #     options=sorted(keywords_df['item'].unique()),
    #     index=0 if len(keywords_df)>0 else None,
    #     help="Selectionnez un mot-clé existant"
    # )

    # if token_choice:
    #     # compute similarity against the full embeddings (not only filtered) so results are global
    #     idx_full = keywords_df[keywords_df['item'] == token_choice].index
    #     if len(idx_full) == 0:
    #         st.error("Token introuvable dans la liste des mots-clés.")
    #     else:
    #         idx_full = idx_full[0]
    #         token_emb = embeddings[idx_full].reshape(1, -1)
    #         sims = cosine_similarity(token_emb, embeddings)[0]
    #         sim_df = pd.DataFrame({
    #             'item': keywords_df['item'],
    #             'similarity': sims
    #         })
    #         sim_df = sim_df[sim_df['item'] != token_choice]
    #         top10 = sim_df.sort_values(by="similarity", ascending=False).head(10).reset_index(drop=True)

    #         # Chart + table
    #         st.markdown(f"**Top 10 tokens similaires à** : `{token_choice}`")
    #         bar = alt.Chart(top10).mark_bar().encode(
    #             x=alt.X('similarity:Q', title='Similarité (cosinus)', scale=alt.Scale(domain=[0,1])),
    #             y=alt.Y('item:N', sort='-x', title='Token similaire'),
    #             tooltip=['item', alt.Tooltip('similarity:Q', format='.4f')]
    #         ).properties(height=360, width=700)
    #         st.altair_chart(bar, use_container_width=True)
    

        # export_data = {}
        # for _, counter in topic_words.items():
        #     # topic = concaténation des 3 premiers mots
        #     topic = '.'.join(x for x, _ in counter.most_common(3))
        #     # liste de tous les mots du topic
        #     words = [w for w, f in counter.most_common()]
        #     export_data[topic] = words

        # # Construction du CSV manuellement
        # lines = []
        # for topic, words in export_data.items():
        #     line = ",".join([topic] + words)
        #     lines.append(line)

        # csv_str = "\n".join(lines)

        # # Bouton de téléchargement CSV
        # st.download_button(
        #     label="📥 Télécharger topics en CSV",
        #     data=csv_str,
        #     file_name="topics_keywords.csv",
        #     mime="text/csv"
        # )

    
    #st.caption("Application développée pour l'exploration interactive de topics — modifiez K ou le filtre de fréquence pour recalculer les topics (opération coûteuse).")
