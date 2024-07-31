import re

def process_links(file_path):
    with open(file_path, 'r') as file:
        raw_content = file.read()
    
    # Regular expression to find URLs
    url_pattern = re.compile(r'https?://[^\s",\\]+')
    
    # Find all URLs in the raw content
    links = url_pattern.findall(raw_content)
    
    # Clean up the links and ignore parts containing `#:~:text=`
    clean_links = [link.split('#:~:text=')[0].rstrip('\",\\') for link in links]
    
    # Print the cleaned links, each on a new line
    for link in clean_links:
        print(link)

# Specify the file path
file_path = 'chosen_links.json'

# Process the links from the file
process_links(file_path)