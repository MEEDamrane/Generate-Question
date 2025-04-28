import streamlit as st
import google.generativeai as genai
import random
import re

# Configuration de Gemini
genai.configure(api_key="USE_YOUR_API")

# Fonction pour générer une question
def generer_question(matiere, niveau):
    model = genai.GenerativeModel('gemini-2.0-flash')
    prompt = f"""
Génère UNE seule question à choix multiples (QCM) en {matiere}.
Niveau : {niveau}.
La question doit être claire, pas de doublon, formatée ainsi :
Question : (le texte de la question)

Choisissez votre réponse :
A) (option A)
B) (option B)
C) (option C)
D) (option D)

Réponse correcte : (La ou les bonnes lettres, exemple : A ou B ou C)
IMPORTANT : Ne mets pas de code bloc (pas de ```), seulement du texte brut.
    """
    reponse = model.generate_content(prompt)
    texte = reponse.text.strip()
    
    # Nettoyage simple
    texte = re.sub(r'```.*?```', '', texte, flags=re.DOTALL)
    texte = texte.replace('"', '').replace("'", '')
    return texte

# Parse la question générée
def parser_question(texte):
    question_match = re.search(r'Question\s*:(.*?)Choisissez votre réponse\s*:', texte, re.DOTALL)
    options_match = re.findall(r'([A-D])\)\s*(.*?)\n', texte)
    reponse_match = re.search(r'Réponse correcte\s*:\s*(.+)', texte)
    
    if not (question_match and options_match and reponse_match):
        raise ValueError("Erreur de format dans la génération.")
    
    question = question_match.group(1).strip()
    options = {lettre: option.strip() for lettre, option in options_match}
    bonne_reponse = reponse_match.group(1).strip().split()  # Peut être plusieurs réponses
    
    return question, options, bonne_reponse

# Initialisation session state
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'erreurs' not in st.session_state:
    st.session_state.erreurs = 0
if 'question' not in st.session_state:
    st.session_state.question = ''
if 'options' not in st.session_state:
    st.session_state.options = {}
if 'bonne_reponse' not in st.session_state:
    st.session_state.bonne_reponse = []
if 'selection' not in st.session_state:
    st.session_state.selection = None

# Titre
st.title("🧠 Générateur de QCM Educatif avec IA")

# Choix de matière et niveau
matiere = st.text_input("Entrez la matière ou technologie :", "PHP")

niveau = st.selectbox(
    "Choisissez votre niveau :",
    ("Beginner", "Intermediate", "Advanced")
)

# Bouton pour générer une nouvelle question
if st.button("🎯 Nouvelle question"):
    try:
        texte = generer_question(matiere, niveau)
        question, options, bonne_reponse = parser_question(texte)
        
        st.session_state.question = question
        st.session_state.options = options
        st.session_state.bonne_reponse = bonne_reponse
        st.session_state.selection = None
    except Exception as e:
        st.error(f"Erreur lors de la génération : {e}")

# Affichage de la question
if st.session_state.question:
    st.subheader("Question :")
    st.write(st.session_state.question)
    
    # Radio pour choisir une réponse
    st.session_state.selection = st.radio(
        "Choisissez votre réponse :",
        list(st.session_state.options.keys()),
        format_func=lambda x: f"{x}) {st.session_state.options[x]}"
    )

    # Bouton pour soumettre
    if st.button("✅ Soumettre ma réponse"):
        if st.session_state.selection in st.session_state.bonne_reponse:
            st.success("Bonne réponse ! 🎉")
            st.session_state.score += 1
        else:
            bonnes = ', '.join(st.session_state.bonne_reponse)
            st.error(f"Mauvaise réponse ❌. La bonne réponse était : {bonnes}")
            st.session_state.erreurs += 1
        
# Affichage score et erreurs
st.sidebar.title("📈 Statistiques")
st.sidebar.write(f"Score actuel : {st.session_state.score}")
st.sidebar.write(f"Nombre d'erreurs : {st.session_state.erreurs}")
