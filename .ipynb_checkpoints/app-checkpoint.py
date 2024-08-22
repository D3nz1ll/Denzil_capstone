import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document, StorageContext, load_index_from_storage
from llama_index.llms import OpenAI
import openai
from PIL import Image
import requests
import base64



st.set_page_config(page_title="Streaming Platform Recommender", page_icon="👩🏻‍🏫", layout="centered", initial_sidebar_state="auto", menu_items=None)

#Context

# Set OpenAI API key
openai.api_key = st.secrets.openai_key


# URL of the image you want to display
image_url = "https://github.com/yuanman88/yuanman88.github.io/blob/main/FS%20_Banner.png?raw=true"

# Display the image in Streamlit using HTML and CSS
st.markdown(f"""
<style>
.shifted-image {{
    display: block;
    margin-left: auto;
    margin-right: auto;
    width: 600px;
    height: 160px; /* Adjust the height as needed */
    margin-top: 50px; /* Adjust this value to bring the image closer to the top */
}}
</style>
<img class="shifted-image" src="{image_url}" />
""", unsafe_allow_html=True)

# URL of the GIF you want to display
#gif_url = "https://github.com/yuanman88/yuanman88.github.io/blob/main/AI_Fengshui.gif?raw=true"

# Fetch the GIF from the URL
#response = requests.get(gif_url)

# Convert the GIF to base64
#gif_base64 = base64.b64encode(response.content).decode('utf-8')

# Display the GIF in Streamlit using base64-encoded string, center it, and adjust its height and position
#st.markdown(f"""
#<style>
#.center {{
   # display: block;
   # margin-left: auto;
   # margin-right: auto;
   # width: 600px;
   # height: 400px; /* Adjust the height as needed */
   # margin-top: 10px; /* Push the GIF down */
#}}
#.caption {{
 #   text-align: center;
  #  margin-top: 20px; /* Adjust the margin-top as needed */
#}}
#</style>
#<img class="center" src="data:image/gif;base64,{gif_base64}" />
#<div class="caption">How Can I Help You Today?</div>
#""", unsafe_allow_html=True)



# Display centered text
#st.markdown("<p style='text-align: center;'>Welcome to the Streaming Platform Recommender!</p>", unsafe_allow_html=True)


@st.cache_resource(show_spinner=False)
def load_data():
    with st.spinner(text="Loading your recommedation... Think about your favourite shows! This may take 1-2 minutes."):
        
        # Rebuild the storage context
        storage_context = StorageContext.from_defaults(persist_dir="./data/index.vecstore")

        # Load the index
        index = load_index_from_storage(storage_context)

        # Load the finetuned model 
        ft_model_name = "ft:gpt-3.5-turbo-1106:personal::9yLUndRk"
        ft_context = ServiceContext.from_defaults(llm=OpenAI(model=ft_model_name, temperature=0.3), 
        context_window=2048, 
        
        system_prompt="""
       Craft a series of insightful and relevant questions that potential customers might ask about streaming service platforms like Netflix, Disney+ and Amazon Prime Video to help them decide which streaming service platforms to use. You have multiple preferences regarding the type of shows and movies and want to ensure that the streaming service platform can match those preferences. You want to choose a streaming service platform that fits your age and price budget as well as preference for IMDB ratings, original shows, asian shows, japanese anime, animation, superheroes, documentaries and old movies. You would also want to choose a streaming service platform that fit your preference for streaming service platform's popularity, total number of shows and movies on the platform. You are particularly interested in which streaming service platform to use based on these preferences. Your goal is to recommend the most suitable streaming service platform to users based on their preferences. You are looking for a definite recommendation of streaming service platform that aligns with user preferences.
       Give the correct recommendation.
        """
        )           
        return index

index = load_data()
chat_engine = index.as_chat_engine(chat_mode="openai", verbose=True)

if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask Me Questions Relating to Streaming Platforms 😊"}
    ]

if prompt := st.chat_input("Ask Me Questions Relating to Streaming Platforms"):
    # Save the original user question to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.new_question = True

    # Create a detailed prompt for the chat engine
    chat_history = ' '.join([message["content"] for message in st.session_state.messages])
    detailed_prompt = f"{chat_history} {prompt}"

if "new_question" in st.session_state.keys() and st.session_state.new_question:
   for message in st.session_state.messages: # Display the prior chat messages
       with st.chat_message(message["role"]):
           st.write(message["content"])
   st.session_state.new_question = False # Reset new_question to False

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
   with st.chat_message("assistant"):
       with st.spinner("Calculating..."):
           response = chat_engine.chat(detailed_prompt)
           st.write(response.response)
           # Append the assistant's detailed response to the chat history
           st.session_state.messages.append({"role": "assistant", "content": response.response})
