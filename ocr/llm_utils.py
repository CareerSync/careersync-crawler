from openai import OpenAI
import time
import json
import re


API_MAX_RETRY = 16
API_RETRY_SLEEP = 10
API_ERROR_OUTPUT = "$ERROR$"

def openai_api_messages(prompt, status='user', chat_history=list()):
    if status == 'user':
        next_chat = [{"role": "user", "content": prompt}]
    elif status == 'system':
        next_chat = [{"role": "system", "content": prompt}]
    chat_history.extend(next_chat)
    return chat_history

def openai_output(client, model, query, chat_history=list()):
    model = model
    output = API_ERROR_OUTPUT
    for _ in range(API_MAX_RETRY):
        openai_input = openai_api_messages(query, chat_history=list())
        try:
            response = client.chat.completions.create(
                model=model,
                messages=openai_input,
                n=1,
                temperature=0,
            )
            output = response.choices[0].message.content
            break
        except Exception as e:
            print("ERROR DURING OPENAI API: ", e.code, e.message)
            if 'context_length_exceeded' in e.code:
                print("Context length exceeded. Changing the model to gpt-4o for longer context length.")
                model = 'gpt-4o'
            time.sleep(API_RETRY_SLEEP)
    return output

def extract_json(text):
    match = re.search(r'\{.*?\}', text, re.S)

    if match:
        json_content = match.group(0)
        try:
            data = json.loads(json_content.replace("'", '"'))
            return data
        except json.JSONDecodeError as e:
            fixed_json = re.sub(r',\s*\}', '}', re.sub(r',\s*\]', ']', json_content))
            try:
                data = json.loads(fixed_json)
                return data
            except json.JSONDecodeError as e:
                print(f"Failed to decode JSON again: {e}")
                return None
    else:
        print("No JSON found in the response text.")
        return None

def save_to_jsonl(data_list, file_path):
    with open(file_path, 'w') as f:
        for item in data_list:
            json.dump(item, f)
            f.write('\n')