import os
import json
import faiss
import numpy as np
from groq import Groq
from sentence_transformers import SentenceTransformer



def product_to_text(product):
  return (
    f"{product['product_name']} by {product['brand']}"
    f"{product['product_details']}"
    f"{product['ingredients']}"
  )



def build(products, save_path):
  model = SentenceTransformer('all-mpnet-base-v2')
  text = [product_to_text(p) for p in products]
  vectors = model.encode(text, normalize_embeddings=True)
  np_vectors = np.array(vectors).astype('float32')

  dimension = np_vectors.shape[1] # need to know for memory allocation
  index = faiss.IndexFlatIP(dimension) # hence we tell create index big enough for our data

  index.add(np_vectors)
  os.makedirs(save_path, exist_ok=True)
  faiss.write_index(index, os.path.join(save_path, "index.faiss"))
  with open(os.path.join(save_path, "docs.json"), "w", encoding="utf-8") as file:
    json.dump(products, file)

