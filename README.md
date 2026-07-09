# Skin2Care

An AI-powered skincare product recommendation system built with Retrieval-Augmented Generation (RAG).

**Live App:** [skin2care.streamlit.app](https://skin2care.streamlit.app)

## What It Does

Skin2Care lets users ask natural language questions about skincare and receive personalized product recommendations grounded in real ingredient data from nearly 10,000 products scraped from Incidecoder.

**Example queries:**

- "Best moisturizer for dry skin"
- "Recommend a gentle cleanser for sensitive skin"
- "What products have hyaluronic acid?"

## How It Works

1. **Data Collection** — Scraped nearly 10,000 skincare products from Incidecoder using `requests` + BeautifulSoup, capturing product names, brands, ingredients, and descriptions. The scraper paginates the full product listing, is resumable (checkpoints to disk every 100 products), and rate-limits requests to avoid getting blocked.
2. **Embedding** — Each product is converted into a 768-dimensional vector embedding using `sentence-transformers/all-mpnet-base-v2`
3. **Vector Search** — Embeddings are indexed with FAISS for fast semantic similarity search
4. **RAG Pipeline** — User queries retrieve the top 5 most relevant products, which are passed as context to an LLM (GPT-OSS 120B via Groq) to generate a grounded recommendation. A system prompt keeps the model from recommending anything outside the retrieved context.
5. **Frontend** — Streamlit app for interactive querying, with the FAISS index cached in memory so the app stays fast between interactions

## Tech Stack

- **FAISS** — Vector similarity search
- **Sentence Transformers** — Text embeddings (`all-mpnet-base-v2`)
- **LangChain** — Embedding, document, and vectorstore components (`langchain-community`, `langchain-core`)
- **Groq** — LLM inference (GPT-OSS 120B)
- **Streamlit** — Web app frontend
- **Requests + BeautifulSoup** — Web scraping

## Run Locally

```bash
git clone https://github.com/erinflee/Skin2Care.git
cd Skin2Care
pip install -r requirements.txt
```

Add a `.env` file with your Groq API key:

```
GROQ_API_KEY=your-key-here
```

Run the app (the FAISS index is already included in the repo, no need to rebuild it):

```bash
streamlit run app.py
```

> If you update the product data and need to rebuild the FAISS index, delete the `faiss_index/` folder first, then run `python ml.py` (it skips rebuilding if the index already exists).
