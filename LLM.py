import requests
import openai
import configparser
from datetime import datetime, timedelta
import json

# Load configuration
config = configparser.ConfigParser()
config.read('config.ini')
openai.api_key = config['openai']['apikey']
MODEL = 'gpt-4o-mini'  # Specify the model

# Function to read links.json and query.txt, then pass contents to GPT-4O
def process_links_with_gpt4o(search_query):
    # Load links from JSON file
    with open('links.json', 'r') as infile:
        links = json.load(infile)
    
    # Format the data for GPT-4O
    formatted_data = "\n".join([f"Title: {link['Title']}\nLink: {link['Link']}" for link in links])
    
    # Prepare the messages for GPT-4O
    messages = [
        {"role": "system", "content": "You are a helpful research assistant."},
        {"role": "user", "content": f"""Here are the search results for the query '{search_query}':\n\n{formatted_data}\n\nRespond with the 5 most relevant "Link" values to the query (avoid links that end with .pdf), in a CHOSEN_LINKS json object."""}
    ]
    
    # Make the API call to OpenAI
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        max_tokens=5000  # Adjust the max tokens as needed
    )
    
    # Get the response text
    response_text = response['choices'][0]['message']['content']
    print(response_text)
    with open("chosen_links.json", "w") as outfile:
        json.dump(response_text, outfile)
