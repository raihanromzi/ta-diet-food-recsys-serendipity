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
