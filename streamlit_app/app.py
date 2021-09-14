from requests.sessions import default_headers
import streamlit as st
import pandas as pd
import requests
import time
from urllib.error import URLError


def get_recommendations(meals):
    headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json',
    }
    data = str({ "meals": meals }).replace("'", '^').replace('"', "'").replace('^','"')

    response = requests.post('https://recommendation-recipe.azurewebsites.net/recipe-recommendation/', headers=headers, data=data)

    return response.json()["recommended_items"]


@st.cache
def get_data():
    df = pd.read_csv("/Users/visanand2/Desktop/Pycharm/Recepie-Recommendation/Meals.csv")
    return df


try:
    df = get_data()
    original_title = '<p style="font-family:Calibri; color:#f63468; font-size: 25px;">Choose Meals</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    meals = st.multiselect(
        "", list(df.Meals),
         default=["Creamy King Prawn Linguine", "Paneer Butter Masala With Coriander Naan"]
    )
    if not meals:
        st.error("Please select at least one meal.")
    
    # col1, col2, col3, col4, col5 = st.columns(5)
    # with col2:
        # Create a simple button 
    if(st.button("Generate Recommendations")):
        placeholder= st.markdown("![Alt Text](https://media.giphy.com/media/CNocEFcF9IBegtgW3q/giphy.gif)")
        recommendations = get_recommendations(meals)
        placeholder.empty()
        st.markdown("")
        st.markdown("")
        st.markdown("")
        for recommendation in recommendations:
            st.markdown(recommendation)
            

        # st.altair_chart(chart, use_container_width=True)
except URLError as e: 
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )