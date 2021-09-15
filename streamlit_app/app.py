from urllib.error import URLError

import pandas as pd
import streamlit as st


def get_response_locally(meals):
    similarity_matrix = pd.read_csv("/Users/visanand2/Desktop/Pycharm/Recepie-Recommendation/fastapi_azure/similarity_matrix.csv", index_col=0)
    similarity_matrix.index.name = "MEALS"

    if len(meals) == 1:
        recco = list(similarity_matrix[meals[0]].sort_values(ascending=False)[1:11].keys())

    if len(meals) == 2:
        recco = similarity_matrix[meals[0]].sort_values(ascending=False)[1:6]
        recco = list(
            recco.append(similarity_matrix[meals[1]].sort_values(ascending=False)[1:6]).keys())

    if len(meals) == 3:
        recco = similarity_matrix[meals[0]].sort_values(ascending=False)[1:5]
        recco = recco.append(similarity_matrix[meals[1]].sort_values(ascending=False)[1:4])
        recco = list(
            recco.append(similarity_matrix[meals[2]].sort_values(ascending=False)[1:4]).keys())

    if len(meals) == 4:
        recco = similarity_matrix[meals[0]].sort_values(ascending=False)[1:4]
        recco = recco.append(similarity_matrix[meals[1]].sort_values(ascending=False)[1:4])
        recco = recco.append(similarity_matrix[meals[2]].sort_values(ascending=False)[1:3])
        recco = list(
            recco.append(similarity_matrix[meals[3]].sort_values(ascending=False)[1:3]).keys())

    if len(meals) == 5:
        recco = similarity_matrix[meals[0]].sort_values(ascending=False)[1:3]
        recco = recco.append(similarity_matrix[meals[1]].sort_values(ascending=False)[1:3])
        recco = recco.append(similarity_matrix[meals[2]].sort_values(ascending=False)[1:3])
        recco = recco.append(similarity_matrix[meals[3]].sort_values(ascending=False)[1:3])
        recco = list(
            recco.append(similarity_matrix[meals[4]].sort_values(ascending=False)[1:3]).keys())

    return recco


def get_recommendations(meals):
    response = get_response_locally(meals)
    # response = requests.post('https://recommendation-recipe.azurewebsites.net/recipe-recommendation/', headers=headers, data=data)

    return response


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
    if (st.button("Generate Recommendations")):
        placeholder = st.markdown("![Alt Text](https://media.giphy.com/media/9rgi4j5MclWdMNIsHz/giphy.gif)")
        recommendations = get_recommendations(meals)
        placeholder.empty()
        placeholder.empty()

        st.markdown("")
        st.markdown("")
        st.markdown("")
        meal_url_mapper = pd.read_csv(
            "/Users/visanand2/Desktop/Pycharm/Recepie-Recommendation/streamlit_app/meal_url_mapper.csv")
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
