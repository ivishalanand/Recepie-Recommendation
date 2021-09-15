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
    original_title = '<p style="color:#f63468; font-size:25px";">Choose Meals</p>'
    st.markdown(original_title, unsafe_allow_html=True)
    meals = st.multiselect(
        "", list(df.Meals),
         default=["Creamy King Prawn Linguine", "Paneer Butter Masala With Coriander Naan"]
    )
    if not meals:
        st.error("Please select at least one meal.")
    if len(meals) > 5:
        st.error("Please enter a maximum of 5 meals")
    
    # col1, col2, col3, col4, col5 = st.columns(5)
    # with col2:
        # Create a simple button 
    if(st.button("Generate Recommendations")):
        placeholder = st.markdown("![Alt Text](https://media.giphy.com/media/9rgi4j5MclWdMNIsHz/giphy.gif)")
        recommendations = get_recommendations(meals)
        placeholder.empty()
        placeholder.empty()

        st.markdown("")
        st.markdown("")
        st.markdown("")
        meal_url_mapper = pd.read_csv("/Users/visanand2/Desktop/Pycharm/Recepie-Recommendation/streamlit_app/meal_url_mapper.csv")
        meal_url_mapper.set_index("meal", inplace=True)
        subtitle = '<p style=color:#f63468; font-size: 15px;">Recommendations</p>'
        st.markdown(subtitle, unsafe_allow_html=True)
        for recommendation in recommendations:
            url = meal_url_mapper.loc[recommendation]["url"]
            prep_time = meal_url_mapper.loc[recommendation]["prep_time"]
            region = meal_url_mapper.loc[recommendation]["region"]
            st.write("🍕" + recommendation + " ⏳ " + prep_time + " 🌎 " + region + " [link](" + url + ")")
            # st.write("check out this [link](url)")
            

        # st.altair_chart(chart, use_container_width=True)
except URLError as e: 
    st.error(
        """
        **This demo requires internet access.**

        Connection error: %s
    """
        % e.reason
    )