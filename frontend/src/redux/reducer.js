import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  age: '',
  weight: '',
  height: '',
  gender: '',
  activityLevel: '',
  numberOfMealsPerDay: '',
  bmi: '',
  tdee: '',
  bmiStatus: '',
  favoriteFoods: [],
  breakfast: [],
  lunch: [],
  dinner: [],
  recommendations: [],
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUserDetails: (state, action) => {
      state.age = action.payload.age;
      state.weight = action.payload.weight;
      state.height = action.payload.height;
      state.gender = action.payload.gender;
      state.activityLevel = action.payload.activityLevel;
      state.numberOfMealsPerDay = action.payload.numberOfMealsPerDay;
    },
    setBMIandTDEE: (state, action) => {
      state.bmi = action.payload.bmi;
      state.tdee = action.payload.tdee;
      state.bmiStatus = action.payload.bmiStatus;
    },
    setFavoriteFoods: (state, action) => {
      state.favoriteFoods = action.payload;
    },
    setRecommendations: (state, action) => {
      state.recommendations = action.payload;
    },
    setBreakfast: (state, action) => {
      state.breakfast = action.payload;
    },
    setLunch: (state, action) => {
      state.lunch = action.payload;
    },
    setDinner: (state, action) => {
      state.dinner = action.payload;
    },
  },
});

export const {
  setUserDetails,
  setBMIandTDEE,
  setFavoriteFoods,
  setRecommendations,
  setBreakfast,
  setLunch,
  setDinner,
} = userSlice.actions;
export default userSlice.reducer;
