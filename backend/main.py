from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.cluster import KMeans

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset
df = pd.read_csv('./data/recipes.csv')

# Load TF-IDF Models
with open('./models/tfidf_vectorizer.pkl', 'rb') as f:
    tfidf_vectorizer = pickle.load(f)
with open('./models/tfidf_matrix.pkl', 'rb') as f:
    tfidf_matrix = pickle.load(f)

class FavoriteFoodRequest(BaseModel):
    favoriteFoods: list[str]
    topNHigh: int = 50
    topNLow: int = 5

class TDEERequest(BaseModel):
    gender: str
    age: int
    weight: float
    height: float
    activity_level: str

def calculate_bmr(gender: str, weight: float, height: float, age: int) -> float:
    if gender.lower() == "male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    return bmr

def calculate_tdee(bmr: float, activity_level: str) -> float:
    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very active": 1.9
    }
    return bmr * activity_multipliers.get(activity_level.lower(), 1.2)

@app.post("/recommendations")
async def index(
    request: FavoriteFoodRequest,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1),
    max_calories: int = Query(None, ge=0)
    ):
    try:
        # Extract user favorite foods
        user_favorite_foods = request.favoriteFoods

        # Generate combinations for similarity calculations
        user_favorites = user_favorite_foods + [' '.join(user_favorite_foods)]
        user_favorites_length = len(user_favorites)

        # Initialize a dictionary to store similarities
        df_combined = df["Combined"]
        similarity_dict = {}

        # Calculate similarities for each string
        for favorite in user_favorites:
            # Transform the string to a TF-IDF vector
            favorite_vector = tfidf_vectorizer.transform([favorite])

            # Calculate cosine similarities
            similarities = cosine_similarity(favorite_vector, tfidf_matrix).flatten()

            # Store the similarities in the dictionary
            similarity_dict[favorite] = similarities

        similarity_df = pd.DataFrame(similarity_dict, index=df_combined)

        # Filter High Similarity
        high_similarity_candidates = []
        top_n_high = request.topNHigh

        for favorite, similarities in similarity_df.items():
            # Get top n indices
            top_n_indices = similarities.argsort()[-top_n_high:][::-1]

            # Select the top n candidate recipes
            candidate_recipes = df.iloc[top_n_indices].copy()
            candidate_recipes['CosineSimilarity'] = similarities.iloc[top_n_indices].tolist()
            candidate_recipes['Favorite'] = favorite

            # Append the candidate DataFrame to the list
            high_similarity_candidates.append(candidate_recipes)

        high_similarity_df = pd.concat(high_similarity_candidates).drop_duplicates().reset_index(drop=True)

        # Filter Low Similarity
        top_n_low = request.topNLow
        low_similarity_candidates = []

        for favorite, similarities in similarity_df.items():
            # Get indices of foods with non-zero and low similarity
            non_zero_indices = np.where(similarities > 0)[0]
            low_similarity_indices = non_zero_indices[similarities.iloc[non_zero_indices].argsort()[:top_n_low]]

            # Select random foods from these low similarity candidates
            random_low_sim_candidates = df.iloc[low_similarity_indices].sample(top_n_low, random_state=42)
            random_low_sim_candidates['CosineSimilarity'] = similarities.iloc[low_similarity_indices].tolist()
            random_low_sim_candidates['Favorite'] = favorite

            # Append the low similarity DataFrame to the list
            low_similarity_candidates.append(random_low_sim_candidates)

        low_similarity_df = pd.concat(low_similarity_candidates).drop_duplicates().reset_index(drop=True)

        high_similarity_df.replace([np.inf, -np.inf], np.nan, inplace=True)
        high_similarity_df.dropna(inplace=True)

        low_similarity_df.replace([np.inf, -np.inf], np.nan, inplace=True)
        low_similarity_df.dropna(inplace=True)

        # Calculate diversity scores on high similarity
        candidate_high_similarity_vectors = high_similarity_df['CosineSimilarity'].values.reshape(-1, 1)
        similarity_matrix = cosine_similarity(candidate_high_similarity_vectors)
        diversity_high_similarity_scores = np.sum(similarity_matrix, axis=1) / similarity_matrix.shape[1]

        # Assuming CosineSimilarity as relevance score
        relevance_high_similarity_scores = high_similarity_df['CosineSimilarity'].values

        # Calculate serendipity scores
        serendipity_scores = (0.5 * relevance_high_similarity_scores) + (0.5 * diversity_high_similarity_scores)

        # Rank items by serendipity
        ranked_indices = np.argsort(serendipity_scores)[::-1]
        top_high_similarity_recommendations = high_similarity_df.iloc[ranked_indices[:50]].reset_index(drop=True)

        # Calculate diversity scores on low similarity
        candidate_low_similarity_vectors = low_similarity_df['CosineSimilarity'].values.reshape(-1, 1)
        similarity_matrix = cosine_similarity(candidate_low_similarity_vectors)
        diversity_low_similarity_scores = np.sum(similarity_matrix, axis=1) / similarity_matrix.shape[1]

        # Assuming CosineSimilarity as relevance score
        relevance_low_similarity_scores = low_similarity_df['CosineSimilarity'].values

        # Calculate serendipity scores
        serendipity_scores = (0.5 * relevance_low_similarity_scores) + (0.5 * diversity_low_similarity_scores)

        # Rank items by serendipity
        ranked_indices = np.argsort(serendipity_scores)[::-1]
        top_low_similarity_recommendations = low_similarity_df.iloc[ranked_indices[:50]].reset_index(drop=True)

        # Combine high and low similarity recommendations
        top_recommendations = pd.concat([top_high_similarity_recommendations, top_low_similarity_recommendations]).reset_index(drop=True)

        # Ensure diversity by clustering
        favorites_hashed = top_recommendations['Favorite'].apply(lambda x: hash(str(x)) % 10**8).values.reshape(-1, 1)
        kmeans = KMeans(n_clusters=user_favorites_length, random_state=42)
        clusters = kmeans.fit_predict(favorites_hashed)

        diverse_recommendations = []
        for cluster in np.unique(clusters):
            cluster_indices = np.where(clusters == cluster)[0]
            cluster_recommendations = top_recommendations.iloc[cluster_indices]
            num_recommendations_from_cluster = min(10, len(cluster_recommendations))
            diverse_recommendations.append(cluster_recommendations.head(num_recommendations_from_cluster))

        diverse_recommendations_df = pd.concat(diverse_recommendations).reset_index(drop=True)

        # Stage 1 drop columns
        diverse_recommendations_df.drop(['Combined', 'CosineSimilarity'], axis=1, inplace=True)
        diverse_recommendations_df.drop_duplicates(inplace=True)

         # Filter based on name and max calories
        if max_calories is not None:
            diverse_recommendations_df = diverse_recommendations_df[diverse_recommendations_df['Calories'] <= float(max_calories)]

        # Pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_recommendations = diverse_recommendations_df.iloc[start_idx:end_idx]

        # Return the serendipitous recommendations
        return {
            "data": paginated_recommendations.to_dict(orient="records"),
            "page": page,
            "page_size": page_size,
            "total_length": len(diverse_recommendations_df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/tdee")
async def calculate_tdee_endpoint(request: TDEERequest):
    try:
        bmr = calculate_bmr(request.gender, request.weight, request.height, request.age)
        tdee = calculate_tdee(bmr, request.activity_level)
        return {"BMR": bmr, "TDEE": tdee}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
