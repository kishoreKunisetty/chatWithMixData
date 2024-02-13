import requests
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["HUGGINGFACEHUB_API_TOKEN"]=os.getenv('HUGGINGFACEHUB_API_TOKEN')
HUGGINGFACEHUB_API_TOKEN=os.getenv('HUGGINGFACEHUB_API_TOKEN')

API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-alpha"
headers = {"Authorization": f"Bearer {HUGGINGFACEHUB_API_TOKEN}"}

def query(payload):
    print(f"[INFO] >>> reached query payload : {payload}")
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# class LLM:
    def __init__(self, data):
        self.data = data

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    
    def post_process(resp, system, counter):
        placeholder = {}
        print(f"[INFO] >>> {resp}")
        temp = resp[0]['generated_text'].split("python:")[counter].split("\n")
        
        code = temp[0].strip()
        print(f"[INFO] >>> code : {code}")
        exec(f"result = {code}", placeholder)
        exec_result = placeholder["result"]
        next_answer = f""" {temp[0].strip()}"""
        system += next_answer
        counter +=1
        return code, exec_result
    