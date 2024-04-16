
import ast  # for converting embeddings saved as strings back to arrays
from openai import AzureOpenAI # for calling the OpenAI API
import pandas as pd  # for storing text and embeddings data
import tiktoken  # for counting tokens
import os # for getting API token from env variable OPENAI_API_KEY
from scipy import spatial  # for calculating vector similarities for search
from docx import Document

os.environ["AZURE_OPENAI_KEY"] = 'd58136d46efe4cedb8e9c33d682d518f'#填写自己的Azure Api_key

# 从.docx文件中读取文本内容
def read_docx(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text.strip()

client = AzureOpenAI(
  azure_endpoint = "https://zdopenai.openai.azure.com/", 
  api_key=os.getenv("AZURE_OPENAI_KEY"),  
  api_version="2024-02-15-preview"
)

# 读取.docx文件
docx_file_path = "F:\\SystemRestory\\SystemUserData\\admin\Desktop\\新建文件夹\\常见问题汇总(2).docx"
text_content = read_docx(docx_file_path)

res = client.embeddings.create(input=text_content, model="text-embedding-ada-002")
print(res.data[0].embedding)