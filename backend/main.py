from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from sklearn.cluster import KMeans
from google_images_search import GoogleImagesSearch
from bmi_bmr_tdee import calculate_bmi, get_bmi_status, calculate_bmr, calculate_tdee
from image import get_image_url
from content_based import calculate_similarity, filter_similarity, cluster_recommendations

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

class FavoriteFoodRequest(BaseModel):
    favoriteFoods: list[str]
    topNHigh: int = 80
    topNLow: int = 20
    tdee: float

class TDEERequest(BaseModel):
    age: int
    weight: float
    height: float
    gender: str
    activity_level: str


@app.post("/recommendations")
async def index(
    request: FavoriteFoodRequest,
    ):
    try:
        user_favorites = request.favoriteFoods
        user_favorites_length = len(user_favorites)
        tdee = request.tdee
        top_n_high = request.topNHigh
        top_n_low = request.topNLow

        breakfast_calories_min = tdee * 0.30
        breakfast_calories_max = tdee * 0.35
        lunch_calories_min = tdee * 0.35
        lunch_calories_max = tdee * 0.40
        dinner_calories_min = tdee * 0.25
        dinner_calories_max = tdee * 0.35

        foods_similarity_df = calculate_similarity(df, user_favorites)
        high_low_similarity_df = filter_similarity(foods_similarity_df, df, top_n_high, top_n_low)
        diverse_recommendations_df = cluster_recommendations(high_low_similarity_df, user_favorites_length)

        shuffled_recommendations = diverse_recommendations_df.sample(frac=1).reset_index(drop=True)

        total_items = len(shuffled_recommendations)
        breakfast_count = total_items // 3
        lunch_count = total_items // 3
        dinner_count = total_items - breakfast_count - lunch_count

        breakfast_recommendations = shuffled_recommendations.iloc[:breakfast_count]
        lunch_recommendations = shuffled_recommendations.iloc[breakfast_count:breakfast_count + lunch_count]
        dinner_recommendations = shuffled_recommendations.iloc[breakfast_count + lunch_count:breakfast_count + lunch_count + dinner_count]

        breakfast_recommendations.drop(columns=['Favorite', 'CosineSimilarity', 'Combined'], inplace=True)
        breakfast_recommendations.drop_duplicates(inplace=True)
        lunch_recommendations.drop(columns=['Favorite', 'CosineSimilarity', 'Combined'], inplace=True)
        lunch_recommendations.drop_duplicates(inplace=True)
        dinner_recommendations.drop(columns=['Favorite', 'CosineSimilarity', 'Combined'], inplace=True)
        dinner_recommendations.drop_duplicates(inplace=True)

        final_recommendations = {
            "breakfast": breakfast_recommendations,
            "lunch": lunch_recommendations,
            "dinner": dinner_recommendations
        }

        for i, row in final_recommendations["breakfast"].iterrows():
            recipe_image = row['ImagesClean']
            if recipe_image == "['character(0']":
                try:
                    image_link = get_image_url(row['NameClean'])
                    final_recommendations["breakfast"].at[i, 'ImagesClean'] = f"[{image_link}]"
                except Exception as e:
                    final_recommendations["breakfast"].at[i, 'ImagesClean'] = f"Error finding image: {str(e)}"

        for i, row in final_recommendations["lunch"].iterrows():
            recipe_image = row['ImagesClean']
            if recipe_image == "['character(0']":
                try:
                    image_link = get_image_url(row['NameClean'])
                    final_recommendations["lunch"].at[i, 'ImagesClean'] = f"[{image_link}]"
                except Exception as e:
                    final_recommendations["lunch"].at[i, 'ImagesClean'] = f"Error finding image: {str(e)}"

        for i, row in final_recommendations["dinner"].iterrows():
            recipe_image = row['ImagesClean']
            if recipe_image == "['character(0']":
                try:
                    image_link = get_image_url(row['NameClean'])
                    final_recommendations["dinner"].at[i, 'ImagesClean'] = f"[{image_link}]"
                except Exception as e:
                    final_recommendations["dinner"].at[i, 'ImagesClean'] = f"Error finding image: {str(e)}"
        foods_similarity_df = calculate_similarity(df, user_favorites)
        high_low_similarity_df = filter_similarity(foods_similarity_df, df, top_n_high, top_n_low)
        diverse_recommendations_df = cluster_recommendations(high_low_similarity_df, user_favorites_length)

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
