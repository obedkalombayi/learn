import streamlit as st
from rag_by_API import ask, generate_quiz_item

st.set_page_config(
    page_title="Learn - Préparation Exetat",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .stApp{
            background-color: #0D0F12;
            color: #FFFFFF;
        }
        .main-title {
            font-size: 2.5rem;
            font-weight: 800;
            color: #FF7A00;
            text-align: center;
            margin-bottom: 0px;
        }
        .subtitle {
            text-align: center;
            color: #A0AEC0;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }
        section[data-testid="stSidebar"] {
            background-color: #14171D;
            border-right: 1px solid #2D3748;
        }
        .quiz-card {
            background-color: #1A202C;
            border: 1px solid #FF7A00;
            border-radius: 12px;
            padding: 20px;
            margin-top: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(255, 122, 0, 0.15);
        }
        .explanation-box {
            background-color: #0F2942;
            border-left: 5px solid #FF7A00;
            border-radius: 8px;
            padding: 16px;
            margin-top: 20px;
            color: #E2E8F0;
        }
        .explanation-title {
            color: #FF7A00;
            font-weight: 700;
            font-size: 1.1rem;
            margin-bottom: 6px;
        }
        .footer {
            text-align: center;
            color: #718096;
            font-size: 0.8rem;
            margin-top: 2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.image(
        "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?auto=format&fit=crop&w=600&q=80",
        use_container_width=True,
    )
    st.markdown("## Learn")
    st.markdown(
        "Assistant pédagogique pour la **culture générale** des élèves de 6ᵉ année des humanités."
    )
    st.markdown("---")

    mode = st.radio(
        "Choisissez votre mode :",
        ["Mode Quiz (QCM)"],
        index=0,
    )

    st.markdown("---")
    st.markdown(
        "<div class='footer'>· Learn<br>© Exetat Preparation<br>obedkalombayikay@gmail.com</div>",
        unsafe_allow_html=True,
    )

st.markdown("<div class='main-title'>Learn</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Ton assistant de préparation à l'Examen d'État</div>",
    unsafe_allow_html=True,
)

# --- MODE QUIZ ---
if mode == "Mode Quiz (QCM)":
    st.subheader(" Entraînement QCM - Culture Générale")

    # Initialisation de la session
    if "current_quiz" not in st.session_state:
        st.session_state.current_quiz = None
    if "quiz_score" not in st.session_state:
        st.session_state.quiz_score = 0
    if "total_questions" not in st.session_state:
        st.session_state.total_questions = 0
    if "quiz_answered" not in st.session_state:
        st.session_state.quiz_answered = False
    if "user_choice" not in st.session_state:
        st.session_state.user_choice = None

    col_score, col_btn = st.columns([2, 1])
    with col_btn:
        if st.button("🔄 Question Suivante", use_container_width=True):
            with st.spinner("Génération de la question..."):
                st.session_state.current_quiz = generate_quiz_item()
                st.session_state.quiz_answered = False
                st.session_state.user_choice = None
                st.rerun()

    if st.session_state.current_quiz is None:
        with st.spinner("Chargement d'un exercice..."):
            st.session_state.current_quiz = generate_quiz_item()
            st.rerun()

    quiz = st.session_state.current_quiz

    if quiz:
        with col_score:
            st.caption(
                f" Score : **{st.session_state.quiz_score} / {st.session_state.total_questions}**"
            )

        # Carte de la question
        st.markdown(
            f"<div class='quiz-card'><h3 style='margin:0;'>{quiz['question']}</h3></div>",
            unsafe_allow_html=True,
        )

        # Formulaire de réponse
        with st.form("quiz_form"):
            selected = st.radio(
                "Sélectionnez votre réponse :",
                quiz["options"],
                disabled=st.session_state.quiz_answered,
            )
            submit = st.form_submit_button(
                "Valider ma réponse", disabled=st.session_state.quiz_answered
            )

            if submit:
                st.session_state.quiz_answered = True
                st.session_state.user_choice = selected
                st.session_state.total_questions += 1

                if selected == quiz["reponse_correcte"]:
                    st.session_state.quiz_score += 1

                st.rerun()

        # Affichage du résultat & explications
        if st.session_state.quiz_answered:
            is_correct = (
                st.session_state.user_choice == quiz["reponse_correcte"]
            )

            if is_correct:
                st.success("✅ **Bonne réponse ! Félicitations !**")
            else:
                st.error(
                    f"❌ **Mauvaise réponse.** La bonne réponse était : **{quiz['reponse_correcte']}**"
                )

            st.markdown(
                f"""
                <div class="explanation-box">
                    <div class="explanation-title"> Explication pédagogique</div>
                    <p style="margin: 0; line-height: 1.6;">
                        {quiz['explication']}
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
