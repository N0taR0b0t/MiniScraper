import requests
import openai
import configparser
from datetime import datetime, timedelta
import json

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')
openai.api_key = config['openai']['apikey']
MODEL = 'gpt-4o'  # Specify the model

# Function to read Texts.json and query.txt, then pass contents to GPT-4O
def synthesis_with_gpt4o(search_query):
    # Load Texts from JSON file
    with open('web_text.json', 'r') as infile:
        Texts = json.load(infile)
    
    # Format the data for GPT-4O
    formatted_data = "\n".join([f"URL: {Text['URL']}\nText: {Text['Text']}" for Text in Texts])
    
    # Prepare the messages for GPT-4O
    messages = [
        {"role": "system", "content": "You are a helpful research assistant."},
        {"role": "user", "content": f"""Below are the google search results for the query '{search_query}'.\n Some results may be incomplete.\n{formatted_data}\n\nIgnore irrelevent information, and provide a detailed explanation of the available data to the user."""}
    ]
    
    # Make the API call to OpenAI
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages
    )
    
    # Get the response text
    response_text = response['choices'][0]['message']['content']
    print(response_text)
    with open("Synthesis.txt", "w") as outfile:
        json.dump(response_text, outfile)

if __name__ == '__main__':
    synthesis_with_gpt4o("")