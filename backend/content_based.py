from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import pickle

# Load TF-IDF Models
with open('./models/tfidf_vectorizer.pkl', 'rb') as f:
    tfidf_vectorizer = pickle.load(f)
with open('./models/tfidf_matrix.pkl', 'rb') as f:
    tfidf_matrix = pickle.load(f)

def calculate_similarity(df, user_favorites):
    similarity_dict = {}
    for favorite in user_favorites:
        # Transform the string to a TF-IDF vector
        favorite_vector = tfidf_vectorizer.transform([favorite])

        # Calculate cosine similarities
        similarities = cosine_similarity(favorite_vector, tfidf_matrix).flatten()

        # Store the similarities in the dictionary
        similarity_dict[favorite] = similarities

    return pd.DataFrame(similarity_dict, index=df['NameClean'])

def filter_similarity(similarity_df, df, top_n_high, top_n_low):
    high_similarity_candidates = []
    low_similarity_candidates = []

    for favorite, similarities in similarity_df.items():
        # Get top n high similarity indices
        top_n_high_indices = similarities.argsort()[-top_n_high:][::-1]
        high_sim_recipes = df.iloc[top_n_high_indices].copy()
        high_sim_recipes['CosineSimilarity'] = similarities.iloc[top_n_high_indices].tolist()
        high_sim_recipes['Favorite'] = favorite
        high_similarity_candidates.append(high_sim_recipes)

        # Get top n low similarity indices
        non_zero_indices = np.where(similarities > 0)[0]
        low_similarity_indices = non_zero_indices[similarities.iloc[non_zero_indices].argsort()[:top_n_low]]
        low_sim_recipes = df.iloc[low_similarity_indices].copy()
        low_sim_recipes['CosineSimilarity'] = similarities.iloc[low_similarity_indices].tolist()
        low_sim_recipes['Favorite'] = favorite
        low_similarity_candidates.append(low_sim_recipes)

    high_similarity_df = pd.concat(high_similarity_candidates).drop_duplicates().reset_index(drop=True)
    low_similarity_df = pd.concat(low_similarity_candidates).drop_duplicates().reset_index(drop=True)

    high_similarity_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    high_similarity_df.dropna(inplace=True)

    low_similarity_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    low_similarity_df.dropna(inplace=True)

    # return high_similarity_df, low_similarity_df
    return pd.concat([high_similarity_df, low_similarity_df]).drop_duplicates().reset_index(drop=True)

def cluster_recommendations(recommendations_df, user_favorites_length):
    favorites_hashed = recommendations_df['Favorite'].apply(lambda x: hash(str(x)) % 10**8).values.reshape(-1, 1)
    kmeans = KMeans(n_clusters=user_favorites_length, random_state=42)
    clusters = kmeans.fit_predict(favorites_hashed)

    diverse_recommendations = []
    for cluster in np.unique(clusters):
        cluster_indices = np.where(clusters == cluster)[0]
        cluster_recommendations = recommendations_df.iloc[cluster_indices]
        num_recommendations_from_cluster = min(25, len(cluster_recommendations))
        diverse_recommendations.append(cluster_recommendations.head(num_recommendations_from_cluster))

    diverse_recommendations_df = pd.concat(diverse_recommendations).reset_index(drop=True)
    diverse_recommendations_df.drop_duplicates(inplace=True)
    return diverse_recommendations_df
