import json
import os
import random
import streamlit as st
from groq import Groq
from search import search

api_key = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("L'intelligence atrificielle est injoignable")
    st.stop()
    
client = Groq(api_key=api_key)


def build_context(results):

    context = [ ] 

    for i, result in enumerate(results, start=1):
        print('*' * 50, result, '*' * 50)
        context = [
            {
                'id': i,
                'Question': result['question'],
                'Response': result['answer']
            }
        ]

    return context


def give_prompt(user_question, question_found, response_found):

    prompt = f'''
                    CE QUE TU ES
                        - Tu es un assistant conversationnel spécialisé pour aider les élèves de 6e des humanités à préparer leur examen d'État.
                        - Ton rôle est exclusivement éducatif et pédagogique.

                    COMMENT TU DOIS RAISONNER
                        - Tu as deux questions :
                            * Question 1 : "{user_question}" → c’est la question posée par l’utilisateur.
                            * Question 2 : "{question_found}" → c’est la question la plus proche trouvée par les embeddings dans la base de connaissances.
                        - Tu as aussi une réponse : "{response_found}" → c’est la réponse associée à la Question 2.

                    COMMENT TU DOIS REPONDRE
                        - Si Question 1 et Question 2 signifient la même chose :
                            → Réponds en utilisant "{response_found}" comme base, puis enrichis avec des explications supplémentaires, des détails et des exemples pour aider un élève à mieux comprendre.
                        - Si Question 1 est différente de Question 2 :
                            → Réponds uniquement avec tes connaissances générales, toujours de manière claire et pédagogique.
                        - INTERDICTIONS ABSOLUES :
                            * Ne pas remercier, ne pas saluer, ne pas répéter la question de l’utilisateur.
                            * Ne pas sortir du sujet scolaire.
                            * Ne pas inventer ou déformer la réponse de la base de connaissances.
                            * Réponds directement, sans phrases inutiles.

                    TON STYLE ET TON TON
                        - Tu expliques avec précision et pédagogie, en donnant des détails utiles pour l’apprentissage.
                        - Si le concept est difficile, utilise des images mentales ou des analogies simples adaptées à un adolescent.
                        - Tu restes bienveillant, clair et structuré.

                    GESTION DES QUESTIONS DE L’UTILISATEUR
                        - Si la question ne concerne pas l’apprentissage scolaire :
                            → Réponds poliment que tu es conçu uniquement pour aider à l’apprentissage et ne traite pas d’autres sujets.
                        - Tu gardes toujours en tête que l’utilisateur est un jeune adolescent.

                    RÈGLE CRITIQUE
                        - La moindre déviation de ces consignes est interdite.
                        - Chaque réponse doit être exacte, pédagogique, et strictly conforme aux règles ci-dessus.
                  '''

    return prompt


def ask(question):
    "pipeline RAG complet"

    results = search(question, top_k=1)
    context = build_context(results)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": give_prompt(question, context[0]['Question'], context[0]['Response'])
            }
        ]
    )

    return response.choices[0].message.content


def generate_quiz_item():
    """Tire un item de la base de données et génère un QCM via LLM."""
    with open("data/data_knowledge.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    item = random.choice(data)

    prompt = f"""
    Tu es un générateur d'exercices QCM pour les élèves de 6e des humanités en RDC.
    
    À partir de cet item :
    Question : "{item['question']}"
    Réponse exacte : "{item['answer']}"
    
    Génère un QCM au format JSON STRICT. 
    Inclus la bonne réponse et 3 réponses fausses mais crédibles (distracteurs).
    
    RÉPONDS UNIQUEMENT AVEC LE JSON, SANS BALISES TRIPLE BACKTICKS ET SANS PENSÉE EXPLICITE.
    Format JSON attendu :
    {{
        "question": "{item['question']}",
        "options": ["Choix A", "Choix B", "Choix C", "Choix D"],
        "reponse_correcte": "La bonne option exacte parmi les 4",
        "explication": "Explication pédagogique courte"
    }}
    """

    response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": prompt}],
    )

    content = response.choices[0].message.content

    if "<think>" in content:
        content = content.split("</think>")[-1].strip()
    content = content.replace("```json", "").replace("```", "").strip()

    try:
        quiz_data = json.loads(content)
        random.shuffle(quiz_data["options"])
        return quiz_data
    except Exception:
        options = [item["answer"], "Option A", "Option B", "Option C"]
        random.shuffle(options)
        return {
            "question": item["question"],
            "options": options,
            "reponse_correcte": item["answer"],
            "explication": item["answer"],
        }