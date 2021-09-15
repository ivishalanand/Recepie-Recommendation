import azure.functions as func
from .http_asgi import AsgiMiddleware
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional, Set
import pandas as pd
import numpy as np
from scipy.spatial import distance
import random

app = FastAPI()

class RecipeRequest(BaseModel):
    meals: List[str]
    recommended_items: Optional[List[str]]


@app.post("/recipe-recommendation/")
async def create_item(request: RecipeRequest):

    similarity_matrix = pd.read_csv("similarity_matrix.csv", index_col=0)
    similarity_matrix.index.name = "MEALS"


    def get_recommendations(meal_list):

        if len(meal_list) == 1:
            recommendations = list(similarity_matrix[meal_list[0]].sort_values(ascending=False)[1:11].keys())
        
        if len(meal_list) == 2:
            recommendations = similarity_matrix[meal_list[0]].sort_values(ascending=False)[1:6]
            recommendations = list(recommendations.append(similarity_matrix[meal_list[1]].sort_values(ascending=False)[1:6]).keys())

        if len(meal_list) == 3:
            recommendations = similarity_matrix[meal_list[0]].sort_values(ascending=False)[1:5]
            recommendations=recommendations.append(similarity_matrix[meal_list[1]].sort_values(ascending=False)[1:4])
            recommendations = list(recommendations.append(similarity_matrix[meal_list[2]].sort_values(ascending=False)[1:4]).keys())
        
        if len(meal_list) == 4:
            recommendations = similarity_matrix[meal_list[0]].sort_values(ascending=False)[1:4]
            recommendations=recommendations.append(similarity_matrix[meal_list[1]].sort_values(ascending=False)[1:4])
            recommendations=recommendations.append(similarity_matrix[meal_list[2]].sort_values(ascending=False)[1:3])
            recommendations = list(recommendations.append(similarity_matrix[meal_list[3]].sort_values(ascending=False)[1:3]).keys())

        if len(meal_list) == 5:
            recommendations = similarity_matrix[meal_list[0]].sort_values(ascending=False)[1:3]
            recommendations=recommendations.append(similarity_matrix[meal_list[1]].sort_values(ascending=False)[1:3])
            recommendations=recommendations.append(similarity_matrix[meal_list[2]].sort_values(ascending=False)[1:3])
            recommendations=recommendations.append(similarity_matrix[meal_list[3]].sort_values(ascending=False)[1:3])
            recommendations = list(recommendations.append(similarity_matrix[meal_list[4]].sort_values(ascending=False)[1:3]).keys())

        # random.shuffle(recommendations)

        return recommendations
        

    request.recommended_items = get_recommendations(request.meals)
        
    return request


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return AsgiMiddleware(app).handle(req, context)