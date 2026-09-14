import streamlit as st
from google import genai

# ---------------- CONFIG ----------------

API_KEY = ""
MODEL = "gemini-3.8-flash"
KB_FILE = "java.txt"

# -----------------------------------------

st.set_page_config(
    page_title="JavaMate — Java Programming Assistant",
    page_icon="☕",
    layout="centered"
)

# ---------------- STYLING ----------------

st.markdown("""
<style>
#MainMenu, footer, header {
    visibility: hidden;
}

.stApp {
    background: linear-gradient(180deg, #0f1117 0%, #161a23 100%);
}

.hero {
    padding: 1.6rem 1.8rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #f89820 0%, #b1560f 100%);
    margin-bottom: 1.4rem;
}

.hero h1 {
    color: white;
    font-size: 1.6rem;
    margin: 0;
}

.hero p {
    color: white;
    margin: 0.3rem 0 0 0;
}

.topic-chip {
    display: inline-block;
    background: rgba(248,152,32,0.12);
    color: #f89820;
    border: 1px solid rgba(248,152,32,0.35);
    border-radius: 20px;
    padding: 0.25rem 0.7rem;
    margin: 0.2rem;
    font-size: 0.78rem;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.markdown("""
<div class="hero">
    <h1>☕ JavaMate</h1>
    <p>Your personal Java programming assistant — concepts, syntax, OOP & more.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- KNOWLEDGE BASE ----------------

@st.cache_data
def load_kb():
    with open(KB_FILE, "r", encoding="utf-8") as f:
        return f.read()

kb = load_kb()

# ---------------- GEMINI CLIENT ----------------

client = genai.Client(api_key=st.secrets["key"])

# ---------------- PROMPT ----------------

prompt = f"""
You are JavaMate, a Java Programming Assistant chatbot.

Your purpose is to help students learn Java programming.

You can help with:

- Java concepts
- Java syntax
- Java programs
- OOP
- Classes and Objects
- Constructors
- Inheritance
- Polymorphism
- Encapsulation
- Abstraction
- Interfaces
- Exception Handling
- Threads

Use the following knowledge base:

---------------- KNOWLEDGE BASE ----------------

{kb}

--------------------------------------------------

Rules:

1. Give simple and easy explanations.
2. Give syntax when the user asks for syntax.
3. Give Java code examples when requested.
4. Explain code step by step when requested.
5. Keep answers suitable for students.
6. Use the knowledge base as the main source.
7. Do not invent information.
8. If the answer is not available in the knowledge base, say:

"Sorry, I don't have that information in my Java knowledge base."
"""

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown("### ☕ JavaMate")
    st.caption("Java Programming Assistant")

    st.divider()

    st.markdown("**Topics covered**")

    topics = [
        "Syntax",
        "OOP",
        "Classes",
        "Objects",
        "Constructors",
        "Inheritance",
        "Polymorphism",
        "Encapsulation",
        "Abstraction",
        "Interfaces",
        "Exceptions",
        "Threads"
    ]

    st.markdown(
        "".join(
            f'<span class="topic-chip">{topic}</span>'
            for topic in topics
        ),
        unsafe_allow_html=True
    )

    st.divider()

    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------- CHAT HISTORY ----------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display old messages

for message in st.session_state.messages:

    avatar = "🧑‍💻" if message["role"] == "user" else "☕"

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):
        st.markdown(message["content"])

# ---------------- USER INPUT ----------------

user_question = st.chat_input(
    "Ask a Java question..."
)

if user_question:

    # Show user message

    st.session_state.messages.append({
        "role": "user",
        "content": user_question
    })

    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(user_question)

    # Create conversation history

    history = ""

    for message in st.session_state.messages:

        history += (
            f"{message['role'].upper()}: "
            f"{message['content']}\n"
        )

    # Ask Gemini

    with st.chat_message("assistant", avatar="☕"):

        with st.spinner("Thinking..."):

            try:

                response = client.models.generate_content(
                    model=MODEL,
                    contents=prompt + """

CONVERSATION:
""" + history + """

Answer the user's latest question.
"""
                )

                bot_reply = response.text

            except Exception as e:

                bot_reply = (
                    "Sorry, something went wrong.\n\n"
                    + str(e)
                )

        st.markdown(bot_reply)

    # Save bot response

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })