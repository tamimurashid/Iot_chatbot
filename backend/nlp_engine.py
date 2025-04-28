from sklearn.metrics.pairwise import cosine_similarity  
from response import *

# NLP response
def get_best_reply(user_message):
    user_embedding = model.encode(user_message)
    similarities = cosine_similarity([user_embedding], phrase_embeddings)[0]
    best_idx = np.argmax(similarities)

    reply = reply_keys[best_idx] if similarities[best_idx] > 0.6 else \
            "❌ Sorry, I didn’t understand that. Type 'help' to see valid commands."

    return reply

