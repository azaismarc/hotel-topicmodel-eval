import streamlit as st
import topic_keywords
import topic_sentence
import json

def load_json(uploaded_file):
    return json.load(uploaded_file)

# -------------------------
# Config page
# -------------------------
st.set_page_config(
    page_title="Explorateur BERTopic",
    page_icon="🧠",
    layout="wide",
)

# Tout le contenu dans la sidebar
import streamlit as st

with st.sidebar:

    st.markdown("""
    Nous voulons comprendre comment différentes interprétations peuvent mener à des définitions variées d’un même thème entre plusieurs personnes, et quelles en sont les conséquences sur l’analyse qualitative réalisée par une IA.  
    
    *Par exemple : la **salle de bain** fait-elle partie de la **chambre**, ou s’agit-il d’un thème à part ?*

    
    Pour cela, nous prendrons un exemple simple : **la comparaison de deux hôtels à La Rochelle**.
    """)

    st.markdown("# 🏨 Hôtels étudiés")

    st.image(
        "public/hotel-le-rupella-la-rochelle-charente-maritime-photo-5.webp",
        caption="Hôtel Le Rupella"
    )
    st.markdown("[🔗 Lien vers Le Rupella](https://hotel-lerupella-larochelle.com/)")

    st.image(
        "public/1019344_640_360_FSImage_1_Edit_Front4.webp",
        caption="Hôtel Le Saint Nicolas"
    )
    st.markdown("[🔗 Lien vers Le Saint Nicolas](https://www.hotel-saint-nicolas.com/en/)")

    st.header("🎯 Votre tâche")
    st.markdown("""
        Nous souhaitons répondre à la **question de recherche suivante**:  
        *Entre deux hôtels situés à La Rochelle, lequel se distingue le plus favorablement ?*
        
                 
    Vous avez accès aux **sites web** des hôtels pour vous renseigner et êtes libres d’effectuer toutes les recherches que vous jugez utiles.  

    Vous disposez également, **à droite de l’écran**, d’une **visualisation globale** des mots et commentaires regroupés par thématique  
    (un mode d’emploi est disponible dans le menu déroulant à droite).  

    **À la fin de l’étude, vous devrez indiquer ce qui a motivé vos choix**  
    (recherche web, visualisation par mots/thématiques, barre de recherche, etc.)  
    dans le **formulaire Google** à remplir.
    """)
    

    st.subheader("📌 Thèmes à définir")
    st.markdown("""
    ⚠️ 5 thèmes sont déjà définis – vous devez **compléter leurs définitions**.  
    ⚠️ Chaque définition doit être **aussi précise que possible**.
    """)
    topics = {
        "Chambre": "Qualité, taille, propreté, confort et équipements de la chambre.",
        "Emplacement": "Localisation de l’hôtel dans la ville, proximité des attractions et accessibilité.",
        "Ambiance": "Atmosphère générale, décoration, style, charme ou modernité ressentie.",
        "Rapport qualité-prix": "Adéquation entre le prix payé et l’expérience vécue.",
        "Personnel": "Accueil, amabilité, professionnalisme et disponibilité du personnel."
    }

    for topic, definition in topics.items():
        st.markdown(f"- **{topic}**")

    st.markdown("""
    **Vous pouvez ajouter d’autres thèmes** que vous jugez pertinents  
    (par ex. : *propreté, petit-déjeuner, installations, services additionnels…*).  
    Chaque définition doit être **claire et opérationnelle** pour guider l’annotation.
    """)

    st.subheader("⚙️ Précisions")

    st.markdown("""
    - Une **classification automatique** des avis par thématique sera réalisée à l’aide d’une IA ;  
    - Le **sentiment** sera déterminé en fonction de la section du commentaire : « points forts » ou « points faibles » ;  
    - Il n’est donc **pas nécessaire d’indiquer explicitement le sentiment**, sauf si vous souhaitez adopter une **granularité différente**.
    """)

    st.header("✍️ Participez à l’étude")
    st.markdown("""
    Pour contribuer à l’étude, merci de renseigner vos réponses dans le formulaire suivant :  
    👉 [Remplir le Google Form](https://docs.google.com/forms/d/e/1FAIpQLScC-BQ7IFnl71rBlxpLRrOE7qD6coHpMl6kc3kjCeOgiMZB-Q/viewform?usp=header)
    """)
# Mise en page en deux colonnes
col1, col2 = st.columns([3, 1])  # gauche large, droite étroite

with col1:
    st.subheader("Regroupement des mots par thématique")
    topic_keywords.app()  # votre fonction de visualisation

    st.subheader("Regroupement des avis par thématique")
    topic_sentence.app()  # votre fonction de visualisation

with col2:
    with st.expander("ℹ️ Mode d'emploi", expanded=True):
        st.markdown("""
### 📊 Visualisation des mots par thématique
Liste de tous les mots, présentés sous une forme **canonique**, sans accent 
(ex. *chambres → chambre*, *situés → situer*, *jolie → beau*, *côté → cote*).  

- **Taille des points** → fréquence du mot dans les commentaires  

---

### 💬 Visualisation des avis par thématique
Liste des commentaires

- **Taille des points** → longueur du commentaire  
- 🙂 commentaire **positif** → tendance à droite  
- ☹️ commentaire **négatif** → tendance à gauche  

---

### 🖱️ Interaction
- Vous pouvez **zoomer** et **déplacer** la visualisation  
- Placez la souris sur un point pour voir le **mot** ou l’**avis représenté**  
- **Filtrez** selon un mot ou une expression spécifique  
- La **couleur** n’a pas de signification → elle sert uniquement à distinguer les groupes  

---

### 💡 Conseil
- Identifiez les **mots les plus fréquents** dans la visualisation *par mots*  
- Observez le **contexte** d'un mot en utilisant le filtre de la visualisation *par avis*  
""")