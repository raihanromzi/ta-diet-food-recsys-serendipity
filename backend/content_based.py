from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import pandas as pd
import numpy as np

def calculate_similarity(filtered_df, user_favorites):
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(filtered_df['Combined'])

    similarity_dict = {}
    for favorite in user_favorites:
        favorite_vector = tfidf_vectorizer.transform([favorite])
        similarities = cosine_similarity(favorite_vector, tfidf_matrix).flatten()
        similarity_dict[favorite] = similarities
    return pd.DataFrame(similarity_dict, index=filtered_df['Combined'])

def cluster_recommendations(recommendations_df, user_favorites_length):
    favorites_hashed = recommendations_df['Favorite'].apply(lambda x: hash(str(x)) % 10**8).values.reshape(-1, 1)
    kmeans = KMeans(n_clusters=user_favorites_length, random_state=42)
    clusters = kmeans.fit_predict(favorites_hashed)

    diverse_recommendations = []
    for cluster in np.unique(clusters):
        cluster_indices = np.where(clusters == cluster)[0]
        cluster_recommendations = recommendations_df.iloc[cluster_indices]
        num_recommendations_from_cluster = min(10, len(cluster_recommendations))
        diverse_recommendations.append(cluster_recommendations.head(num_recommendations_from_cluster))

    diverse_recommendations_df = pd.concat(diverse_recommendations).reset_index(drop=True)
    diverse_recommendations_df.drop_duplicates(inplace=True)
    return diverse_recommendations_df

def filter_similarity(similarity_df, df, top_n_high, top_n_low):
    high_similarity_candidates = []
    low_similarity_candidates = []

    # To make sure on each run, the top_n_high and top_n_low are different

    top_n_high = top_n_high + np.random.randint(0, 15)
    top_n_low = top_n_low + np.random.randint(0, 3)

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

    return high_similarity_df, low_similarity_df


def combine_recommendations(high_sim_df, low_sim_df, top_n_high=80, top_n_low=20):
    # Calculate diversity scores on high similarity
    candidate_high_similarity_vectors = high_sim_df['CosineSimilarity'].values.reshape(-1, 1)
    high_similarity_matrix = cosine_similarity(candidate_high_similarity_vectors)
    diversity_high_similarity_scores = np.sum(high_similarity_matrix, axis=1) / high_similarity_matrix.shape[1]

    # Assuming CosineSimilarity as relevance score
    relevance_high_similarity_scores = high_sim_df['CosineSimilarity'].values

    # Calculate serendipity scores
    high_serendipity_scores = (0.5 * relevance_high_similarity_scores) + (0.5 * diversity_high_similarity_scores)

    # Rank items by serendipity
    high_ranked_indices = np.argsort(high_serendipity_scores)[::-1]
    top_high_similarity_recommendations = high_sim_df.iloc[high_ranked_indices[:top_n_high]].reset_index(drop=True)

    # Calculate diversity scores on low similarity
    candidate_low_similarity_vectors = low_sim_df['CosineSimilarity'].values.reshape(-1, 1)
    low_similarity_matrix = cosine_similarity(candidate_low_similarity_vectors)
    diversity_low_similarity_scores = np.sum(low_similarity_matrix, axis=1) / low_similarity_matrix.shape[1]

    # Assuming CosineSimilarity as relevance score
    relevance_low_similarity_scores = low_sim_df['CosineSimilarity'].values

    # Calculate serendipity scores
    low_serendipity_scores = (0.5 * relevance_low_similarity_scores) + (0.5 * diversity_low_similarity_scores)

    # Rank items by serendipity
    low_ranked_indices = np.argsort(low_serendipity_scores)[::-1]
    top_low_similarity_recommendations = low_sim_df.iloc[low_ranked_indices[:top_n_low]].reset_index(drop=True)

    # Combine high and low similarity recommendations
    top_recommendations = pd.concat([top_high_similarity_recommendations, top_low_similarity_recommendations]).drop_duplicates().reset_index(drop=True)

    return top_recommendations
