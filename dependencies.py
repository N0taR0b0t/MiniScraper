import json
import requests
from bs4 import BeautifulSoup
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Enhanced cleaning function to handle all known problematic characters and sequences
def clean_json_content(content):
    content = re.sub(r'```json|```', '', content).strip()
    content = re.sub(r'\\n|\\t', '', content)
    content = re.sub(r'[\n\r]', '', content)
    content = re.sub(r'\\', '', content)  # Remove backslashes
    content = re.sub(r'\s{2,}', ' ', content)  # Replace multiple spaces with a single space
    logging.debug(f"Cleaned content: {content}")
    return content

# Function to clean and extract links without using json library
def extract_links(file_path):
    try:
        with open(file_path, 'r') as file:
            raw_content = file.read()
        logging.debug(f"Raw content read from file: {raw_content}")

        clean_content = clean_json_content(raw_content)
        
        # Regular expression to find URLs
        url_pattern = re.compile(r'https?://[^\s",]+')
        links = url_pattern.findall(clean_content)
        
        # Clean up the links and ignore parts containing `#:~:text=`
        clean_links = [link.split('#:~:text=')[0].rstrip('\",') for link in links]
        
        logging.debug(f"Extracted links: {clean_links}")
        return clean_links
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return []

# Function to clean text content by removing excessive whitespace and irrelevant sections
def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[\u00a0\u202f\u2000-\u200A\u3000]+', ' ', text)
    return text

# Function to check if content is likely a PDF
def is_likely_pdf(content):
    return content.startswith('%PDF-')

# Function to fetch and extract text content from a URL using requests and BeautifulSoup
def fetch_text_from_url(url, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(url)
            response.raise_for_status()
            response.encoding = 'utf-8'  # Force encoding to UTF-8

            # Check for PDF content and skip if found
            if is_likely_pdf(response.text):
                logging.info(f"Skipping PDF content from {url}")
                return ""

            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup(["script", "style", "nav", "footer", "header", "button", "a"]):
                script.decompose()
            text = soup.get_text(separator=' ')
            cleaned_text = clean_text(text)
            return cleaned_text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching {url} with requests: {e}")
            attempt += 1
        except Exception as e:
            logging.error(f"Error parsing content from {url} on attempt {attempt}: {e}")
            attempt += 1

    logging.error(f"Skipping {url} after {retries} attempts.")
    return ""

# Function to fetch text using Selenium
def fetch_text_with_selenium(url, wait_time=2, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            options = Options()
            options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1")
            
            # Disable headless mode
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(wait_time)  # Allow the page to load completely
            
            main_content = driver.find_element(By.TAG_NAME, 'body')
            unwanted_elements = main_content.find_elements(By.XPATH, '//*[self::script or self::style or self::nav or self::footer or self::header or self::button or self::a]')
            for element in unwanted_elements:
                try:
                    driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);", element)
                except Exception as e:
                    logging.error(f"Error removing element with Selenium: {e}")

            text = main_content.text
            cleaned_text = clean_text(text)
            driver.quit()
            return cleaned_text
        except Exception as e:
            logging.error(f"Error fetching {url} with Selenium on attempt {attempt + 1}: {e}")
            attempt += 1
            time.sleep(wait_time)  # Wait longer before next attempt
    
    logging.error(f"Skipping {url} after {retries} attempts with Selenium.")
    return ""

# Function to fetch text using an aggressive Selenium strategy
def fetch_text_aggressively_with_selenium(url, retries=3, wait_time=5):
    for attempt in range(retries):
        try:
            options = Options()
            options.add_argument("user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_1 like Mac OS X) AppleWebKit/603.1.30 (KHTML, like Gecko) Version/10.0 Mobile/14E304 Safari/602.1")
            
            # Disable headless mode
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(wait_time)  # Allow the page to load completely

            main_content = driver.find_element(By.TAG_NAME, 'body')
            unwanted_elements = main_content.find_elements(By.XPATH, '//*[self::script or self::style or self::nav or self::footer or self::header or self::button or self::a]')
            for element in unwanted_elements:
                try:
                    driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);", element)
                except Exception as e:
                    logging.error(f"Error removing element with aggressive Selenium: {e}")
            
            text = main_content.text
            cleaned_text = clean_text(text)
            driver.quit()
            return cleaned_text
        except Exception as e:
            logging.error(f"Error fetching {url} with aggressive Selenium on attempt {attempt + 1}: {e}")
            time.sleep(wait_time)  # Wait longer before next attempt
    
    logging.error(f"Skipping {url} after {retries} attempts with aggressive Selenium.")
    return ""

def grab_website_text():
    # Read URLs from the chosen_links.json file
    urls = extract_links('chosen_links.json')

    if len(urls) == 0:
        logging.error("No URLs found in 'CHOSEN_LINKS'. Exiting.")
        exit(1)

    logging.debug(f"URLs to process: {urls}")

    # Fetch and save text content from each URL
    texts = []
    for url in urls:
        text = fetch_text_from_url(url)
        if not text:  # Use Selenium as a fallback
            text = fetch_text_with_selenium(url)
        if not text:  # Use aggressive Selenium strategy if previous attempts fail
            text = fetch_text_aggressively_with_selenium(url)
        texts.append({"URL": url, "Text": text})

    # Save the extracted text content to an output file
    with open('output_texts.json', 'w') as outfile:
        json.dump(texts, outfile, indent=4)

    logging.info("Text contents saved to output_texts.json")