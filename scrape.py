import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from LLM import process_links_with_gpt4o
from synthesis import synthesis_with_gpt4o
from dependencies import grab_website_text
from token_budget import budget_entries
import time

def get_title(result):
    try:
        return result.find_element(By.TAG_NAME, "h3").text
    except:
        pass
    try:
        return result.find_element(By.CSS_SELECTOR, 'a').text
    except:
        pass
    return ""

def search(search_query):
    # Initialize the Chrome driver
    driver = webdriver.Chrome()

    #search_query = input("Enter Query: ")
    #search_query = "How is MU doing today?"

    # Open Google
    driver.get("https://www.google.com")

    # Find the search box
    search_box = driver.find_element(By.NAME, "q")

    # Type the search query
    search_box.send_keys(search_query)

    # Save the search query to a file
    with open("query.txt", "w") as query_file:
        query_file.write(search_query)

    # Submit the search form
    search_box.send_keys(Keys.RETURN)

    # Allow search results to load
    time.sleep(2)

    # Find the first 8 results
    results = driver.find_elements(By.CSS_SELECTOR, 'div.g')[:8]

    # Prepare data for JSON
    data = []
    url_id = 1

    for result in results:
        link = ""
        title = get_title(result)
        try:
            link = result.find_element(By.TAG_NAME, "a").get_attribute("href")
        except:
            link = ""
            
        data.append({"URL_ID": url_id, "Title": title, "Link": link})
        url_id += 1

    # Save to links.json
    with open("links.json", "w") as outfile:
        json.dump(data, outfile, indent=4)

    # Close the browser
    driver.quit()

    print("Links saved to links.json")
    process_links_with_gpt4o(search_query)
    grab_website_text()
    budget_entries()
    synthesis_with_gpt4o(search_query)
    
if __name__ == '__main__':
    search("Pittsburgh news")