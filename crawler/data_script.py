# -*- coding: utf-8 -*-
import json
from urllib.parse import urlparse

# Color codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"

def extract_data_from_json(file_path):
    """
    Extract all URLs, Cookies and Bodies from the JSON file.
    """
    print(f"{GREEN}[>] loading data extraction module...{RESET}")
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"{RED}[x] Error loading JSON file: {e}{RESET}")
        return []

    extracted_data = []

    for domain, users in data.items():
        domain_data = {}
        print(f"{BLUE}[>] parse target website data: {domain}{RESET}")
        for user, datas in users.items():
            print(f"{BLUE}[>] parse target user data: {user}{RESET}")
            user_data = []
            labels = set()
            for data in datas:
                request_details = data["request"]
                response_details = data["response"]
                url = request_details.get("url")
                label = f"{urlparse(url).scheme}://{urlparse(url).netloc}{urlparse(url).path}"
                params = urlparse(url).query.split("&")
                method = request_details.get("method")
                headers = request_details.get("headers")
                body = request_details.get("body")
                
                if label in labels:
                    continue
                else:
                    labels.add(label)

                user_data.append({
                    "Url": url,
                    "Method": method,
                    "Headers": headers,
                    "Body": body,
                    "Label": label,
                    "Params": params,
                    "Response": response_details
                })

            domain_data[user] = user_data
        extracted_data.append(domain_data)
        
    return extracted_data


# file_path = "output.json"
# extracted_data = extract_data_from_json(file_path)
# print(len(extracted_data))
# for data in extracted_data:
#     print(data)
#     print(len(extracted_data[data]))


# print(len(extracted_data[0]['30462']))