import json

def read_output_texts(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def save_web_text(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def select_shortest_texts(data, char_budget):
    # Sort the data by the length of the "Text" field
    sorted_data = sorted(data, key=lambda x: len(x['Text']))
    
    selected_entries = []
    current_total_length = 0
    
    for entry in sorted_data:
        entry_length = len(entry['Text'])
        
        if current_total_length + entry_length < char_budget:
            selected_entries.append(entry)
            current_total_length += entry_length
        else:
            # Add a partial text entry if there's any remaining budget
            remaining_budget = char_budget - current_total_length
            if remaining_budget > 0:
                partial_entry = entry.copy()
                partial_entry['Text'] = entry['Text'][:remaining_budget]
                selected_entries.append(partial_entry)
                current_total_length += remaining_budget
            break
            
    return selected_entries

def budget_entries():
    input_file = 'output_texts.json'
    output_file = 'web_text.json'
    char_budget = 12500
    
    data = read_output_texts(input_file)
    selected_entries = select_shortest_texts(data, char_budget)
    save_web_text(output_file, selected_entries)
    
    print(f"Selected {len(selected_entries)} entries with a total of {sum(len(entry['Text']) for entry in selected_entries)} characters.")
    
if __name__ == "__main__":
    budget_entries()