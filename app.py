from dotenv import load_dotenv

load_dotenv() ## load all the environment variables
import requests
import numpy as np
from PIL import Image
from io import BytesIO
import streamlit as st
import os
import google.generativeai as genai
import mimetypes

genai.configure(api_key=os.getenv("GOOGLE_API_KEY_GEMINI"))
map_subscription_key =os.getenv("BING_STATIC_MAP_API_KEY")
#print(map_subscription_key)

def input_image_setup(uploaded_file):
    # Check if a file has been uploaded
    if uploaded_file is not None:
        with open(uploaded_file, 'rb') as file:
            bytes_data = file.read()
            # Read the file into bytes
            #bytes_data = uploaded_file.getvalue()
            mime_type, _ = mimetypes.guess_type(uploaded_file)
            image_parts = [
            {
                "mime_type": mime_type,  # Get the mime type of the uploaded file
                "data": bytes_data
            }
            ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Function to get the map image
def get_map_image(latitude, longitude,zoom, map_subscription_key,output_path):
    url = f'https://dev.virtualearth.net/REST/V1/Imagery/Map/Aerial/{latitude}%2C%20{longitude}/{zoom}?mapSize=700%2C512&format=jpeg&key={map_subscription_key}'
    response = requests.get(url,stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)        
        st.write(f"Image downloaded and saved to: {output_path}")
        return output_path
    else:
        st.error(f"Failed to retrieve map image. Status code: {response.status_code}")
    
def get_gemini_response(image,prompt):
    #print(f"<<====================imsgr_path=={image}-----------prompt=={prompt}")
    if image:
        model=genai.GenerativeModel('gemini-pro-vision')
        response=model.generate_content([image[0],prompt])
        return response.text
    else:
        st.error("No image available. Please obtain a map image first.")
        return None

# Streamlit app
st.set_page_config(page_title="Geo AI Land Describer")
st.title("Gemini Geo Land Descripter")
output_path = r"artifacts\map_image.jpeg"
latitude = st.number_input("Enter Latitude:", value=21.393012, format="%.6f")
longitude = st.number_input("Enter Longitude:", value=79.321489, format="%.6f")
zoom = st.number_input("zoom :", value=17)
input_prompt="""
first of all erase of all the history answers you have provided.
Then consider Youself as Geospatial Expert and Urban development expert in statelite images, GIS Mapping , Remote Sensing , land inspector, Agricultural officer where you need to see the uploaded satellite map image
and identify content in the map image whether it is the Residential land or Agricultural land or Industrial land or Barren Land or water body.
Also dont use words like "significant", "some" , "few" etc. instead give the number of %. 
Give your response in following format, Also Start new line of each respective of landtype.
land type - number of % land type
1.Residential land - n % 
2.Agricultural land - n %
3.Industrial land - n % 
4.Barren Land - n % 
5.water body -  n % 
Overall information : Your comments on the image in maximum 8 lines.
"""

image=""
if st.button("Get Map Image"):
    if map_subscription_key:
        image=get_map_image(latitude, longitude, zoom, map_subscription_key,output_path)
    else:
        st.error("invalid Maps Subscription API Key.")

submit=st.button("Get Description of Land")
# If submit button is clicked
if submit:
    st.image(output_path, caption="Map Image.", use_column_width=True)
    image_data=input_image_setup(output_path)
    response=get_gemini_response(image_data,input_prompt)
    st.subheader("Geo AI Response is")
    st.write(response)