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
