import os # get api key from .env file
import streamlit as st # used for deploying onto website
from langchain_community.embeddings import HuggingFaceEmbeddings  # converts text to vectors
from langchain_community.vectorstores import FAISS  # loads and searches the saved index
from groq import Groq  # llm api for generating recommendations
from dotenv import load_dotenv  # loads .env into environment variables
from s3_utils import ensure_faiss_index  # downloads the FAISS index from S3 at runtime

# path to the saved FAISS index folder
FAISS_PATH = "faiss_index"

# load environment variables from a local .env file (GROQ_API_KEY, S3_BUCKET, AWS creds)
load_dotenv()

# get api key from streamlit secrets when deployed
# st.secrets is used on streamlit cloud
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# fall back to local environment variable
# os.environ is used when running locally
except:
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# set up the page title, icon, and layout
st.set_page_config(page_title="Skin2Care", page_icon="🧴", layout="centered")
st.title("🧴 Skin2Care")
st.caption("Ask me anything about skincare products — I'll recommend based on real ingredient data.")

# stop the app early if the FAISS index hasn't been built yet
# (skip this check when S3 is configured, since the index gets downloaded at runtime)
if not os.path.exists(FAISS_PATH) and not os.environ.get("S3_BUCKET"):
    st.error("FAISS index not found. Run `python ml.py` first to build the index.")
    st.stop()

# load the embedding model and FAISS index once and cache it
# @st.cache_resource allows us to only run once and remember it in memory so it does not run for every user interaction
# loading ~10k embeddings every query would be too slow
@st.cache_resource
def load_vectorstore():
    # download the FAISS index from S3 if it isn't already on local disk (no-op when S3 isn't configured)
    ensure_faiss_index(FAISS_PATH)
    embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vectorstore = FAISS.load_local(FAISS_PATH, embed_model, allow_dangerous_deserialization=True)
    return vectorstore

# load the vectorstore into memory
vectorstore = load_vectorstore()

# show example prompts as clickable buttons so users know what to ask
st.markdown("**Try asking:**")
cols = st.columns(3)
examples = [
    "Best moisturizer for dry skin",
    "Recommend a gentle cleanser for sensitive skin",
    "What products have hyaluronic acid?",
]
# when a button is clicked, store it in session state so it fills the text input
for i, example in enumerate(examples):
    if cols[i].button(example):
        st.session_state["query"] = example

# text input for the user's question 
# pre-fills if an example button was clicked
query = st.text_input("Your question:", value=st.session_state.get("query", ""), placeholder="e.g. What's a good sunscreen for oily skin?")

# user have prompted a query
if query:
    with st.spinner("Finding the best products for you..."):
        # search FAISS for the 5 most relevant products to the query
        docs = vectorstore.similarity_search(query, k=5)

        # join the 5 products into one context block
        context = "\n\n-----\n\n".join(doc.page_content for doc in docs)

        # build the prompt with context + user question
        prompt = f"<CONTEXT>\n{context}\n</CONTEXT>\n\nMY QUESTION:\n{query}"

        # send to Groq and get a recommendation
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                # system prompt keeps the llm grounded to only recommend real products
                {"role": "system", "content": "You are a skincare expert. Answer clearly using only the context provided. Only recommend products if they are mentioned in the context."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response.choices[0].message.content

    # display the recommendation
    st.markdown("### Recommendation")
    st.markdown(answer)

    # let the user see which products were retrieved from FAISS to generate the answer
    with st.expander("View source products used"):
        for i, doc in enumerate(docs):
            st.markdown(f"**Product {i+1}**")
            st.code(doc.page_content, language="json")
