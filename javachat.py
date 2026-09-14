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
    # STATIC METHOD SPECIAL HANDLING
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
                or heading == "static:"
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
    # QUESTION WORDS
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


        # First line = heading

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


        # Body matches

        body_matches = (
            question_words.intersection(
                section_words
            )
        )


        score = len(body_matches)


        # Heading matches are more important

        heading_matches = (
            question_words.intersection(
                heading_words
            )
        )


        score += len(heading_matches) * 100


        # Extra score for heading match

        if heading_matches:
            score += 100


        if score > 0:

            scored_sections.append(
                (score, section)
            )


    # -----------------------------------------------------
    # SORT
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
    # SELECT KNOWLEDGE
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
    # METHOD OVERLOADING VS OVERRIDING
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
Example of Method Overriding
class Animal {

    void sound() {
        System.out.println("Animal sound");
    }
}

class Dog extends Animal {

    @Override
    void sound() {
        System.out.println("Dog barks");
    }
}

"""

# -----------------------------------------------------
# PROGRAM / CODE / SYNTAX
# -----------------------------------------------------

    if (
        "program" in question_lower
        or "code" in question_lower
        or "syntax" in question_lower
    ):

        return (
            "### Java Program / Syntax\n\n"
            + knowledge
        )


# -----------------------------------------------------
# EXAMPLE
# -----------------------------------------------------

    if "example" in question_lower:

        return (
            "### Java Example\n\n"
            + knowledge
        )


# -----------------------------------------------------
# EXPLANATION
# -----------------------------------------------------

if (
    "explain" in question_lower
    or "how" in question_lower
    or "why" in question_lower
):

    return (
        "### Simple Explanation\n\n"
        + knowledge
    )


# -----------------------------------------------------
# NORMAL ANSWER
# -----------------------------------------------------

return (
    "### JavaMate Answer\n\n"
    + knowledge
)
#=========================================================

#=========================================================

client = genai.Client(
api_key=st.secrets["key"]
)

#=========================================================

#=========================================================

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
#=========================================================
#CHAT HISTORY
#=========================================================

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
#=========================================================
#USER INPUT
#=========================================================

user_question = st.chat_input(
"Ask a Java question..."
)

if user_question:

# -----------------------------------------------------
# SAVE USER QUESTION
# -----------------------------------------------------

    st.session_state.messages.append({
        "role": "user",
        "content": user_question
    })


with st.chat_message(
    "user",
    avatar="🧑‍💻"
):

    st.markdown(user_question)


# -----------------------------------------------------
# RETRIEVE KNOWLEDGE
# -----------------------------------------------------

relevant_knowledge = retrieve_knowledge(
    user_question
)


# -----------------------------------------------------
# ASSISTANT RESPONSE
# -----------------------------------------------------

with st.chat_message(
    "assistant",
    avatar="☕"
):

    with st.spinner("Thinking..."):

        try:


            # -------------------------------------------------
            # NO KNOWLEDGE
            # -------------------------------------------------

            if not relevant_knowledge:

                bot_reply = (
                    "Sorry, I don't have that information "
                    "in my Java knowledge base."
                )


            # -------------------------------------------------
            # GEMINI
            # -------------------------------------------------

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

Explain the concept in simple English suitable
for a college student.
Start with a clear heading containing the topic name.
Give a short definition first.
If the knowledge base contains syntax,
show the syntax.
If the student asks for an example, provide a
complete and easy-to-understand Java example
using only information supported by the knowledge base.
If you provide code, format it inside a Java code block.
If the code has output that is supported by the example,
show the output separately.
If the student asks for an explanation,
explain the concept step by step.
Use bullet points or tables when they make
the answer easier to understand.
Do not make the answer unnecessarily long.
Do not invent information that is not present
in the knowledge base.
Use ONLY the provided knowledge.
If the answer is not available in the knowledge base,
say exactly:

"Sorry, I don't have that information in my Java knowledge base."

Never mention internal retrieval, API errors,
tokens, fallback systems, or knowledge-base implementation.

Give a clear, student-friendly answer.
"""

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt
            )


            bot_reply = response.text


    # -------------------------------------------------
    # ERROR HANDLING
    # -------------------------------------------------

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
    
    # -----------------------------------------------------
    # DISPLAY BOT RESPONSE
    # -----------------------------------------------------

st.markdown(bot_reply)
