import streamlit as st

# Configuration initiale
if 'level' not in st.session_state:
    st.session_state.level = None
if 'language' not in st.session_state:
    st.session_state.language = None

# ----------- STYLE ----------- 
def set_style():
    st.markdown("""
    <style>
    .stApp {
        position: relative;
        z-index: 1;
    }
    .background {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 0;
        background-size: cover;
        background-position: center;
    }
    .main > div {
        position: relative;
        z-index: 2;
    }
    
    /* Style des cartes de niveau */
    .level-card {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        cursor: pointer;
    }
    .level-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.1);
    }

    /* Style des cartes de langue */
    .lang-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .content-box {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem auto;
        max-width: 800px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    </style>
    <img src="https://cdn.pixabay.com/animation/2022/09/01/01/57/20220901015725_7d27c5c07d2b2a0e3fd3f25c29ab1de3.gif" class="background" />
    """, unsafe_allow_html=True)

# ----------- ÉCRAN DE SÉLECTION ----------- 
def level_selection():
    st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>🌍 Polyglot Master</h1>", unsafe_allow_html=True)
    
    cols = st.columns(2)
    with cols[0]:
        st.markdown("""
        <div class="level-card">
            <div style="font-size: 3rem; text-align: center;">🆑</div>
            <h3 style="text-align: center;">LV0 - Débutant Absolu</h3>
            <p style="text-align: center; color: #666;">Je pars de zéro total</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Choisir LV0", key="btn-lv0"):
            st.session_state.level = 0

    with cols[1]:
        st.markdown("""
        <div class="level-card">
            <div style="font-size: 3rem; text-align: center;">🔤</div>
            <h3 style="text-align: center;">LV1 - Faux Débutant</h3>
            <p style="text-align: center; color: #666;">Je connais quelques mots</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Choisir LV1", key="btn-lv1"):
            st.session_state.level = 1

    cols = st.columns(2)
    with cols[0]:
        st.markdown("""
        <div class="level-card">
            <div style="font-size: 3rem; text-align: center;">🎧</div>
            <h3 style="text-align: center;">LV2 - Intermédiaire</h3>
            <p style="text-align: center; color: #666;">Je comprends sans parler</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Choisir LV2", key="btn-lv2"):
            st.session_state.level = 2

    with cols[1]:
        st.markdown("""
        <div class="level-card">
            <div style="font-size: 3rem; text-align: center;">💬</div>
            <h3 style="text-align: center;">LV3 - Avancé</h3>
            <p style="text-align: center; color: #666;">Je forme des phrases</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Choisir LV3", key="btn-lv3"):
            st.session_state.level = 3

    st.markdown("""
    <div class="level-card">
        <div style="font-size: 3rem; text-align: center;">🎯</div>
        <h3 style="text-align: center;">LV4 - Expert</h3>
        <p style="text-align: center; color: #666;">Perfectionnement linguistique</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Choisir LV4", key="btn-lv4"):
        st.session_state.level = 4

def language_selection():
    st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>Choisissez votre langue</h2>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    languages = [
        ("Anglais", "🇬🇧"),
        ("Espagnol", "🇪🇸"),
        ("Français", "🇫🇷"),
        ("Allemand", "🇩🇪"),
        ("Italien", "🇮🇹"),
        ("Japonais", "🇯🇵")
    ]
    
    for i, (lang, flag) in enumerate(languages):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="lang-card">
                <div style="font-size: 2.5rem;">{flag}</div>
                <h4>{lang}</h4>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Choisir {lang}", key=f"btn-lang-{lang}"):
                st.session_state.language = lang

def show_exercises():
    st.markdown(f"""
    <h1 style='text-align: center; margin-bottom: 2rem;'>
        Niveau {st.session_state.level} - {st.session_state.language}
    </h1>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='content-box'>", unsafe_allow_html=True)
        
        if st.session_state.level == 0:
            st.subheader("Découverte de l'alphabet")
            st.image("https://cdn.pixabay.com/photo/2016/03/31/19/15/alphabet-1294801_1280.png", width=200)
            st.write("Écoutez et répétez : A - B - C - D")
            
        elif st.session_state.level == 1:
            st.subheader("Mots du quotidien")
            cols = st.columns(3)
            with cols[0]: 
                st.image("https://cdn.pixabay.com/photo/2016/01/05/17/51/apple-1122537_1280.jpg", width=100)
                st.write("Pomme")
            with cols[1]: 
                st.image("https://cdn.pixabay.com/photo/2016/11/29/05/07/chair-1867755_1280.jpg", width=100)
                st.write("Chaise")
            with cols[2]: 
                st.image("https://cdn.pixabay.com/photo/2016/03/05/19/02/hamburger-1238246_1280.jpg", width=100)
                st.write("Nourriture")
                
        elif st.session_state.level == 2:
            st.subheader("Phrases simples")
            st.write("Apprenez à construire des phrases de base.")
            st.markdown("""
            - Bonjour, comment vas-tu ?  
            - Je voudrais un café, s'il vous plaît.  
            - Où est la gare ?
            """)
            
        elif st.session_state.level == 3:
            st.subheader("Conversations courantes")
            st.write("Pratiquez des dialogues du quotidien.")
            st.markdown("""
            **Dialogue exemple :**  
            - A: Bonjour, je cherche un restaurant.  
            - B: Il y a un bon restaurant italien à deux rues d'ici.  
            - A: Merci, c'est loin ?  
            - B: Non, environ cinq minutes à pied.
            """)
            
        elif st.session_state.level == 4:
            st.subheader("Perfectionnement linguistique")
            st.write("Améliorez votre maîtrise avec des textes complexes.")
            st.markdown("""
            Lisez et analysez un court texte :  
            *La vie est un mystère qu'il faut vivre, et non un problème à résoudre.*  
            Traduisez cette phrase dans votre langue cible et discutez de sa signification.
            """)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    if st.button("↩️ Réinitialiser"):
        st.session_state.level = None
        st.session_state.language = None

# ----------- APPLICATION PRINCIPALE ----------- 
def main():
    set_style()
    
    if st.session_state.level is None:
        level_selection()
    elif st.session_state.language is None:
        language_selection()
    else:
        show_exercises()

if __name__ == "__main__":
    main()