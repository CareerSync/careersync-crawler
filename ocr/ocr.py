import json
import os
import time
import ast
from openai import OpenAI
from main import PororoOcr
from prompts import PreprocessPrompt
from llm_utils import openai_output, extract_json
from dotenv import load_dotenv


def read_json(file_path):
    """
    Read a JSON file and return its content.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The content of the JSON file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json(data, file_path):
    """
    Write data to a JSON file.

    Args:
        data (dict): The data to write to the JSON file.
        file_path (str): The path to the JSON file.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

def write_multiple_json(data_list, file_path):
    """
    Write a list of dict data to a JSON file sequentially.

    Args:
        data_list (list): The list of dict data to write to the JSON file.
        file_path (str): The path to the JSON file.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write('[\n')
        for index, data in enumerate(data_list):
            json.dump(data, file, ensure_ascii=False)
            file.write(',\n' if index < len(data_list) - 1 else '\n')
        file.write(']')

def measure_time(func, *args):
    start_time = time.time()
    result = func(*args)
    end_time = time.time()
    print(f"Time taken for this query: {end_time - start_time} seconds")
    return result

def process_image_urls(ocr, img_urls, co_name, client, model, num_retry=4):
    """
    Process a list of image URLs using OCR and OpenAI API.

    Args:
        ocr (PororoOcr): The OCR instance.
        img_urls (list): The list of image URLs.
        co_name (str): The company name.
        client (OpenAI): The OpenAI client instance.
        model (str): The model name for OpenAI API.

    Returns:
        list: A list of OCR results for each image URL.
    """
    OCR_results = []
    for img_url in img_urls:
        ocr_result = ocr.run_ocr(img_url, debug=False)
        print("=" * 50)
        print(ocr_result)
        
        for i in range(num_retry):  # Retry up to 4 times
            try:
                OpenAI_input = PreprocessPrompt.format(Co_name=co_name, ocr_result=ocr_result)
                preprocessed_ocr_result = openai_output(client, model, OpenAI_input)
                preprocessed_ocr_result = json.loads(preprocessed_ocr_result)
                OCR_results.append(preprocessed_ocr_result['OCR_result'])
                break
            except json.JSONDecodeError:
                try:
                    ocr_result = preprocessed_ocr_result.split("\"OCR_result\":")[1].strip("{}\"")
                    OCR_results.append(ocr_result)
                    break
                except:
                    if i < num_retry - 1:
                        time.sleep(1)
                    else:
                        print(f"Failed to decode JSON for {img_url}")
                        OCR_results.append("Failed to decode JSON")
    
    OCR_results = '\n\n'.join(OCR_results)
    return OCR_results

def main():
    """
    Main function to read data, process images using OCR and OpenAI API,
    and save the updated data back to the JSON file.
    """
    # Initialize OCR and OpenAI client
    ocr = PororoOcr()
    load_dotenv()
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    data_path = "./data/saramin_job_data.json"
    result_path = "./data/OCR_saramin_job_data.json"
    model = 'gpt-3.5-turbo'

    # Load data
    data = read_json(data_path)
    
    updated_data = []
    
    # Process each item in data
    print_interval = 100  # Set this to the desired interval
    for i, item in enumerate(data):
        img_list = item['img_list']
        co_name = item['Co_name']
        if img_list == []:
            print(f"No images found for {co_name}")
            continue
        item['OCR_results'] = measure_time(process_image_urls, ocr, img_list, co_name, client, model)
        updated_data.append(item)

        if (i + 1) % print_interval == 0:
            remaining = len(data) - (i + 1)
            print(f"Remaining items to process: {remaining} / {len(data)}")

    # Save updated data
    write_multiple_json(updated_data, result_path)

if __name__ == "__main__":
    main()
