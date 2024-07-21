from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import pickle
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sklearn.cluster import KMeans
from bmi_bmr_tdee import calculate_bmi, get_bmi_status, calculate_bmr, calculate_tdee
from knn_model import recommend_by_calories
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from content_based import calculate_similarity, filter_similarity, combine_recommendations, cluster_recommendations
from image import get_image_url

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
df = pd.read_csv('./data/preprocessed_recipes.csv')

# Load TF-IDF Models
with open('./models/tfidf_vectorizer.pkl', 'rb') as f:
    tfidf_vectorizer = pickle.load(f)
with open('./models/tfidf_matrix.pkl', 'rb') as f:
    tfidf_matrix = pickle.load(f)

class FavoriteFoodRequest(BaseModel):
    favoriteFoods: list[str]
    topNHigh: int = 40
    topNLow: int = 10
    tdee: float

class TDEERequest(BaseModel):
    age: int
    weight: float  # weight in kg
    height: float  # height in cm
    gender: str
    activity_level: str

@app.post("/recommendations")
async def index(
    request: FavoriteFoodRequest,
    ):
    try:
        # Extract user favorite foods
        user_favorite_foods = request.favoriteFoods
        tdee = request.tdee
        top_n_high = request.topNHigh
        top_n_low = request.topNLow

        # Calculate calorie ranges based on TDEE
        breakfast_calories_min = tdee * 0.30
        breakfast_calories_max = tdee * 0.35
        lunch_calories_min = tdee * 0.35
        lunch_calories_max = tdee * 0.40
        dinner_calories_min = tdee * 0.25
        dinner_calories_max = tdee * 0.35

        max_Calories=1000
        max_daily_fat=100
        max_daily_Saturatedfat=13
        max_daily_Cholesterol=300
        max_daily_Sodium=2300
        max_daily_Carbohydrate=325
        max_daily_Fiber=40
        max_daily_Sugar=40
        max_daily_Protein=200
        max_list=[max_Calories,max_daily_fat,max_daily_Saturatedfat,max_daily_Cholesterol,max_daily_Sodium,max_daily_Carbohydrate,max_daily_Fiber,max_daily_Sugar,max_daily_Protein]

        # Generate combinations for similarity calculations
        user_favorites = user_favorite_foods + [' '.join(user_favorite_foods)]
        user_favorites_length = len(user_favorites)

        # KNN Filter for Calories (100 foods)
        breakfast_filtered_calories = recommend_by_calories(df, breakfast_calories_max, max_list)
        lunch_filtered_calories = recommend_by_calories(df, lunch_calories_max, max_list)
        dinner_filtered_calories = recommend_by_calories(df, dinner_calories_max, max_list)

        breakfast_similarity_df = calculate_similarity(breakfast_filtered_calories, user_favorites)
        lunch_similarity_df = calculate_similarity(lunch_filtered_calories, user_favorites)
        dinner_similarity_df = calculate_similarity(dinner_filtered_calories, user_favorites)

        # Content Based Filter (TopHighN = 40, TopLowN = 10) (50 foods)
        breakfast_high_sim, breakfast_low_sim = filter_similarity(breakfast_similarity_df, df, top_n_high, top_n_low)
        lunch_high_sim, lunch_low_sim = filter_similarity(lunch_similarity_df, df, top_n_high, top_n_low)
        dinner_high_sim, dinner_low_sim = filter_similarity(dinner_similarity_df, df, top_n_high, top_n_low)

        # Combine Recommendations (TopHighN = 20, TopLowN = 5) (25 foods)
        top_breakfast_recommendations = combine_recommendations(breakfast_high_sim, breakfast_low_sim)
        top_lunch_recommendations = combine_recommendations(lunch_high_sim, lunch_low_sim)
        top_dinner_recommendations = combine_recommendations(dinner_high_sim, dinner_low_sim)

        # Cluster Recommendations (TopN = 5) (5 foods)
        diverse_breakfast_recommendations = cluster_recommendations(top_breakfast_recommendations, user_favorites_length)
        diverse_lunch_recommendations = cluster_recommendations(top_lunch_recommendations, user_favorites_length)
        diverse_dinner_recommendations = cluster_recommendations(top_dinner_recommendations, user_favorites_length)

        # Drop Combined, CosineSimilarity, Favorite column
        diverse_breakfast_recommendations.drop(["Combined", "CosineSimilarity", "Favorite"], axis=1, inplace=True)
        diverse_lunch_recommendations.drop(["Combined", "CosineSimilarity", "Favorite"], axis=1, inplace=True)
        diverse_dinner_recommendations.drop(["Combined", "CosineSimilarity", "Favorite"], axis=1, inplace=True)

        final_recommendations = {
            "breakfast": diverse_breakfast_recommendations,
            "lunch": diverse_lunch_recommendations,
            "dinner": diverse_dinner_recommendations
        }

        for i, row in final_recommendations["breakfast"].iterrows():
            # check if the column ImagesClean contains "['character(0']"
            recipe_image = row['ImagesClean']
            if recipe_image == "['character(0']":
                try:
                    image_link = get_image_url(row['NameClean'])
                    final_recommendations["breakfast"].at[i, 'ImagesClean'] = [image_link]
                except Exception as e:
                    final_recommendations["breakfast"].at[i, 'ImagesClean'] = f"Error finding image: {str(e)}"

        for i, row in final_recommendations["lunch"].iterrows():
            # check if the column ImagesClean contains "['character(0']"
            recipe_image = row['ImagesClean']
            if recipe_image == "['character(0']":
                try:
                    image_link = get_image_url(row['NameClean'])
                    final_recommendations["lunch"].at[i, 'ImagesClean'] = [image_link]
                except Exception as e:
                    final_recommendations["lunch"].at[i, 'ImagesClean'] = f"Error finding image: {str(e)}"

        for i, row in final_recommendations["dinner"].iterrows():
            # check if the column ImagesClean contains "['character(0']"
            recipe_image = row['ImagesClean']
            if recipe_image == "['character(0']":
                try:
                    image_link = get_image_url(row['NameClean'])
                    final_recommendations["dinner"].at[i, 'ImagesClean'] = [image_link]
                except Exception as e:
                    final_recommendations["dinner"].at[i, 'ImagesClean'] = f"Error finding image: {str(e)}"

        # Return the serendipitous recommendations
        response = {
            "totalData": {
                "breakfast": len(final_recommendations["breakfast"]),
                "lunch": len(final_recommendations["lunch"]),
                "dinner": len(final_recommendations["dinner"]),
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
                "breakfast": final_recommendations["breakfast"].to_dict(orient="records"),
                "lunch": final_recommendations["lunch"].to_dict(orient="records"),
                "dinner": final_recommendations["dinner"].to_dict(orient="records"),
            }
        }

        return response
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
