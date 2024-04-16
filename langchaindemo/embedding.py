# coding=gbk
import ast  # for converting embeddings saved as strings back to arrays
from openai import AzureOpenAI # for calling the OpenAI API
import pandas as pd  # for storing text and embeddings data
import tiktoken  # for counting tokens
import os # for getting API token from env variable OPENAI_API_KEY
from scipy import spatial  # for calculating vector similarities for search

os.environ["AZURE_OPENAI_KEY"] = 'd58136d46efe4cedb8e9c33d682d518f'#填写自己的Azure Api_key

client = AzureOpenAI(
  azure_endpoint = "https://zdopenai.openai.azure.com/", 
  api_key=os.getenv("AZURE_OPENAI_KEY"),  
  api_version="2024-02-15-preview"
)
query = 'Which athletes won the gold medal in curling at the 2022 Winter Olympics?请用中文回答'

response = client.chat.completions.create(
    messages=[
        {'role': 'system', 'content': 'You answer questions about the 2022 Winter Olympics.'},
        {'role': 'user', 'content': query},
    ],
    model="gpt-4",
    temperature=0,
)

print(response.choices[0].message.content)