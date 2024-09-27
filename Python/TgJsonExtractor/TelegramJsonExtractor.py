import json
from datetime import datetime
import re

# Configuration
INPUT_FILE = 'result.json'
OUTPUT_FILE = 'out'
KEYWORDS = ['Your', 'keywords', 'can', 'be', 'here']
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
CASE_SENSITIVE = False  # Set to True if you want case-sensitive keyword matching

# New configuration options
OUTPUT_FORMAT = 'text'  # 'text' or 'json'
FIELDS_TO_INCLUDE = ['date', 'text']  # json fields as needed, e.g., ['date', 'text', 'id', 'from']


def clean_text(text):
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def extract_text(message):
    if isinstance(message.get('text'), str):
        return message['text'].replace('\n', ' ')
    elif isinstance(message.get('text_entities'), list):
        return ' '.join([entity.get('text', '').replace('\n', ' ') for entity in message['text_entities']])
    else:
        return ''


def contains_keyword(text):
    if CASE_SENSITIVE:
        return any(keyword in text for keyword in KEYWORDS)
    else:
        return any(keyword.lower() in text.lower() for keyword in KEYWORDS)


def process_json(json_data):
    filtered_messages = []
    for message in json_data['messages']:
        text = extract_text(message)
        if text and contains_keyword(text):
            filtered_message = {}
            for field in FIELDS_TO_INCLUDE:
                if field == 'date':
                    filtered_message[field] = datetime.fromisoformat(message['date']).strftime(DATE_FORMAT)
                elif field == 'text':
                    filtered_message[field] = clean_text(text)
                else:
                    filtered_message[field] = message.get(field, '')
            filtered_messages.append(filtered_message)
    return filtered_messages


def write_output(filtered_messages):
    if OUTPUT_FORMAT == 'json':
        with open(f"{OUTPUT_FILE}.json", 'w', encoding='utf-8') as file:
            json.dump(filtered_messages, file, ensure_ascii=False, indent=2)
        print(f"Processed and filtered {len(filtered_messages)} messages and saved them to '{OUTPUT_FILE}.json'")
    else:  # plain text
        with open(f"{OUTPUT_FILE}.txt", 'w', encoding='utf-8') as file:
            for message in filtered_messages:
                for field in FIELDS_TO_INCLUDE:
                    file.write(f"{field}: {message[field]}\n")
                file.write("\n")
        print(f"Processed and filtered {len(filtered_messages)} messages and saved them to '{OUTPUT_FILE}.txt'")


def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)

    filtered_messages = process_json(data)
    write_output(filtered_messages)


if __name__ == "__main__":
    main()
