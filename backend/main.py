from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.cluster import KMeans
from google_images_search import GoogleImagesSearch

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5173",
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
    topNHigh: int = 250
    topNLow: int = 100
    tdee: float

class TDEERequest(BaseModel):
    age: int
    weight: float  # weight in kg
    height: float  # height in cm
    gender: str
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
        "lightly": 1.375,
        "moderately": 1.55,
        "very-active": 1.725,
        "extra-active": 1.9
    }
    multiplier = activity_multipliers.get(activity_level.lower(), 1.2)
    tdee = bmr * multiplier
    return tdee

def calculate_bmi(weight: float, height: float) -> float:
    height_in_meters = height / 100  # convert height to meters
    bmi = weight / (height_in_meters ** 2)
    return bmi

def get_bmi_status(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obesity"

def get_image_url(query: str) -> str:
    gis = GoogleImagesSearch('AIzaSyDHuSqbBG0RSRQiDYPFYw6_2-yGZFUuS5g', '90f5945524c6643aa')

    _search_params = {
        'q': query,
        'num': 1,
        'safe': 'high',
        'fileType': 'jpg|png|jpeg',
        'imgType': 'photo',
        'imgSize': 'medium',
    }

    gis.search(search_params=_search_params)
    if gis.results():
        return gis.results()[0].url
    return 'No image found'


@app.post("/recommendations")
async def index(
    request: FavoriteFoodRequest,
    ):
    try:
        # Extract user favorite foods
        user_favorite_foods = request.favoriteFoods
        tdee = request.tdee

        # Calculate calorie ranges based on TDEE
        breakfast_calories_min = tdee * 0.30
        breakfast_calories_max = tdee * 0.35
        lunch_calories_min = tdee * 0.35
        lunch_calories_max = tdee * 0.40
        dinner_calories_min = tdee * 0.25
        dinner_calories_max = tdee * 0.35

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
        top_high_similarity_recommendations = high_similarity_df.iloc[ranked_indices[:150]].reset_index(drop=True)

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
        top_low_similarity_recommendations = low_similarity_df.iloc[ranked_indices[:70]].reset_index(drop=True)

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
            num_recommendations_from_cluster = min(25, len(cluster_recommendations))
            diverse_recommendations.append(cluster_recommendations.head(num_recommendations_from_cluster))

        diverse_recommendations_df = pd.concat(diverse_recommendations).reset_index(drop=True)
        diverse_recommendations_df.drop_duplicates(inplace=True)

        # Randomly shuffle the DataFrame
        shuffled_recommendations = diverse_recommendations_df.sample(frac=1).reset_index(drop=True)

        # Calculate the number of items for each meal
        total_items = len(shuffled_recommendations)
        breakfast_count = total_items // 3
        lunch_count = total_items // 3
        dinner_count = total_items - breakfast_count - lunch_count

        # Split the shuffled DataFrame into three parts
        breakfast_recommendations = shuffled_recommendations.iloc[:breakfast_count]
        lunch_recommendations = shuffled_recommendations.iloc[breakfast_count:breakfast_count + lunch_count]
        dinner_recommendations = shuffled_recommendations.iloc[breakfast_count + lunch_count:breakfast_count + lunch_count + dinner_count]

        # Ensure there are no duplicates within each meal type
        breakfast_recommendations.drop_duplicates(inplace=True)
        lunch_recommendations.drop_duplicates(inplace=True)
        dinner_recommendations.drop_duplicates(inplace=True)

        # Return the serendipitous recommendations
        return {
            "totalData": {
                "breakfast": len(breakfast_recommendations),
                "lunch": len(lunch_recommendations),
                "dinner": len(dinner_recommendations),
            },
            "calories": {
                "breakfastMinimum": breakfast_calories_min,
                "breakfastMaximum": breakfast_calories_max,
                "lunchMinimum": lunch_calories_min,
                "lunchMaximum": lunch_calories_max,
                "dinnerMinimum": dinner_calories_min,
                "dinnerMaximum": dinner_calories_max,
            },
            "data": {
                "breakfast": breakfast_recommendations.to_dict(orient="records"),
                "lunch": lunch_recommendations.to_dict(orient="records"),
                "dinner": dinner_recommendations.to_dict(orient="records"),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/tdee-bmi")
async def calculate_tdee_endpoint(request: TDEERequest):
    try:
        bmr = calculate_bmr(request.gender, request.weight, request.height, request.age)
        tdee = calculate_tdee(bmr, request.activity_level)
        bmi = calculate_bmi(request.weight, request.height)
        bmi_status = get_bmi_status(bmi)
        return {"BMI": round(bmi, 2), "BMIStatus": bmi_status, "TDEE": round(tdee, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
