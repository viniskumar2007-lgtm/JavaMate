import streamlit as st
from google import genai
import re


# =========================================================
# CONFIG
# =========================================================

MODEL = "gemini-3.8-flash"
KB_FILE = "java.txt"


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="JavaMate — Java Programming Assistant",
    page_icon="☕",
    layout="centered"
)


# =========================================================
# STYLING
# =========================================================

st.markdown("""
<style>

#MainMenu, footer, header {
    visibility: hidden;
}

.stApp {
    background: linear-gradient(
        180deg,
        #0f1117 0%,
        #161a23 100%
    );
}

.hero {
    padding: 1.6rem 1.8rem;
    border-radius: 18px;
    background: linear-gradient(
        135deg,
        #f89820 0%,
        #b1560f 100%
    );
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


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">

    <h1>☕ JavaMate</h1>

    <p>
        Your personal Java programming assistant —
        concepts, syntax, OOP & more.
    </p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# KNOWLEDGE BASE
# =========================================================

@st.cache_data
def load_kb():

    with open(KB_FILE, "r", encoding="utf-8") as f:
        kb = f.read()

    sections = re.split(
        r'(?m)(?=^[A-Z][A-Z0-9\s-]+:$)',
        kb
    )

    sections = [
        section.strip()
        for section in sections
        if section.strip()
    ]

    return sections


sections = load_kb()


# =========================================================
# KNOWLEDGE RETRIEVAL
# =========================================================

def retrieve_knowledge(question):

    question_lower = question.lower()


    # -----------------------------------------------------
    # STATIC KEYWORD / STATIC METHOD
    # -----------------------------------------------------

    if "static" in question_lower:

        for section in sections:

            heading = (
                section
                .split("\n")[0]
                .strip()
                .lower()
            )

            if (
                "static method" in heading
                or "static or class method" in heading
            ):

                return section[:6000]


    # -----------------------------------------------------
    # STOP WORDS
    # -----------------------------------------------------

    stop_words = {
        "what",
        "is",
        "are",
        "the",
        "a",
        "an",
        "in",
        "of",
        "to",
        "for",
        "and",
        "or",
        "how",
        "why",
        "can",
        "do",
        "does",
        "explain",
        "tell",
        "me",
        "about",
        "give",
        "show",
        "please",
        "with",
        "example",
        "java",
        "keyword"
    }


    # -----------------------------------------------------
    # CONVERT QUESTION INTO USEFUL WORDS
    # -----------------------------------------------------

    question_words = set(
        re.findall(
            r'\b[a-zA-Z][a-zA-Z0-9]*\b',
            question_lower
        )
    )


    question_words = {
        word
        for word in question_words
        if word not in stop_words
    }


    # -----------------------------------------------------
    # SCORE SECTIONS
    # -----------------------------------------------------

    scored_sections = []


    for section in sections:

        section_lower = section.lower()


        # First line is the section heading

        heading = (
            section
            .split("\n")[0]
            .strip()
            .lower()
        )


        # Words in heading

        heading_words = set(
            re.findall(
                r'\b[a-zA-Z][a-zA-Z0-9]*\b',
                heading
            )
        )


        # Words in entire section

        section_words = set(
            re.findall(
                r'\b[a-zA-Z][a-zA-Z0-9]*\b',
                section_lower
            )
        )


        # Words matching anywhere in section

        body_matches = (
            question_words.intersection(
                section_words
            )
        )


        score = len(body_matches)


        # Heading matches are much more important

        heading_matches = (
            question_words.intersection(
                heading_words
            )
        )


        score += len(heading_matches) * 100


        # Exact topic match in heading

        if heading_matches:

            score += 100


        if score > 0:

            scored_sections.append(
                (score, section)
            )


    # -----------------------------------------------------
    # SORT BY HIGHEST SCORE
    # -----------------------------------------------------

    scored_sections.sort(
        key=lambda x: x[0],
        reverse=True
    )


    # -----------------------------------------------------
    # NO MATCH
    # -----------------------------------------------------

    if not scored_sections:

        return ""


    # -----------------------------------------------------
    # SELECT BEST KNOWLEDGE
    # -----------------------------------------------------

    if scored_sections[0][0] >= 200:

        knowledge = scored_sections[0][1]

    else:

        top_sections = scored_sections[:2]

        knowledge = "\n\n".join(
            section
            for score, section in top_sections
        )


    return knowledge[:6000]


# =========================================================
# FALLBACK ANSWER
# =========================================================

def fallback_answer(knowledge, question):

    if not knowledge:

        return (
            "Sorry, I don't have that information "
            "in my Java knowledge base."
        )


    question_lower = question.lower()


    # -----------------------------------------------------
    # METHOD OVERLOADING VS METHOD OVERRIDING
    # -----------------------------------------------------

    if (
        "difference" in question_lower
        or "compare" in question_lower
        or "between" in question_lower
        or " vs " in question_lower
    ):

        if (
            "overloading" in question_lower
            and "overriding" in question_lower
        ):

            return """
### Method Overloading vs Method Overriding

| Method Overloading | Method Overriding |
|---|---|
| Same method name with different parameters. | Child class provides its own implementation of a parent class method. |
| Happens in the same class. | Happens between parent and child classes. |
| Compile-time polymorphism. | Runtime polymorphism. |

### Example of Method Overloading

```java
class Calculator {

    int add(int a, int b) {
        return a + b;
    }

    double add(double a, double b) {
        return a + b;
    }
}


# ---------------- GEMINI CLIENT ----------------

client = genai.Client(
    api_key=st.secrets["key"]
)

# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown("### ☕ JavaMate")

    st.caption(
        "Java Programming Assistant"
    )

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

    if st.button(
        "🗑️ Clear chat",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ---------------- CHAT HISTORY ----------------

if "messages" not in st.session_state:

    st.session_state.messages = []


for message in st.session_state.messages:

    avatar = (
        "🧑‍💻"
        if message["role"] == "user"
        else "☕"
    )

    with st.chat_message(
        message["role"],
        avatar=avatar
    ):

        st.markdown(
            message["content"]
        )


# ---------------- USER INPUT ----------------

user_question = st.chat_input(
    "Ask a Java question..."
)


if user_question:

    # Save user question

    st.session_state.messages.append({
        "role": "user",
        "content": user_question
    })

    with st.chat_message(
        "user",
        avatar="🧑‍💻"
    ):

        st.markdown(user_question)

    # ---------------- RETRIEVE ----------------

    relevant_knowledge = retrieve_knowledge(
        user_question
    )

    # ---------------- GEMINI ----------------

    with st.chat_message(
        "assistant",
        avatar="☕"
    ):

        with st.spinner("Thinking..."):

            try:

                if not relevant_knowledge:

                    bot_reply = (
                        "Sorry, I don't have that information "
                        "in my Java knowledge base."
                    )

                else:

                    prompt = f"""
You are JavaMate, a Java Programming Assistant.

Answer the student's question using ONLY the
provided Java knowledge base.

KNOWLEDGE:
{relevant_knowledge}

STUDENT QUESTION:
{user_question}

RULES:

1. Explain the concept in simple English suitable for a college student.

2. Start with a clear heading containing the topic name.

3. Give a short definition first.

4. If the knowledge base contains syntax, show the syntax.

5. If the student asks for an example, provide a complete and
easy-to-understand Java example using only information supported
by the knowledge base.

6. If you provide code, format it inside a Java code block.

7. If the code has output that is supported by the example,
show the output separately.

8. If the student asks for an explanation, explain the concept
step by step.

9. Use bullet points or tables when they make the answer easier
to understand.

10. Do not make the answer unnecessarily long.

11. Do not invent information that is not present in the
knowledge base.

12. Use ONLY the provided knowledge.

13. If the answer is not available in the knowledge base, say:

"Sorry, I don't have that information in my Java knowledge base."

14. Never mention internal retrieval, API errors, tokens,
fallback systems, or the knowledge-base implementation.

Give a clear, student-friendly answer.
"""
            
                    response = client.models.generate_content(
                        model=MODEL,
                        contents=prompt
                    )

                    bot_reply = response.text

            except Exception as e:

                error = str(e)

                if "429" in error:

                    bot_reply = fallback_answer(
                        relevant_knowledge,
                        user_question
                    )

                elif "503" in error:

                    bot_reply = fallback_answer(
                        relevant_knowledge,
                        user_question
                    )

                else:

                    bot_reply = fallback_answer(
                    relevant_knowledge,
                    user_question
                    )

        st.markdown(bot_reply)

    # Save bot response

    st.session_state.messages.append({
        "role": "assistant",
        "content": bot_reply
    })
