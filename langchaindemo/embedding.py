
from http import client
from openai import AzureOpenAI # for calling the OpenAI API
import os # for getting API token from env variable OPENAI_API_KEY
import documentloader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS





# Set up environment variables
os.environ["OPENAI_API_TYPE"] = "azure"
os.environ["AZURE_OPENAI_ENDPOINT"] = "https://zdopenai.openai.azure.com/"
os.environ["OPENAI_API_VERSION"] = "2024-02-15-preview"
os.environ["AZURE_OPENAI_API_KEY"] = 'd58136d46efe4cedb8e9c33d682d518f'#填写自己的Azure Api_key


embeddings = AzureOpenAIEmbeddings(model="text-embedding-3-large")
text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=250, chunk_overlap=50, separators=[
            "\n\n",
            "\n",
            "。|！|？",
            "\.\s|\!\s|\?\s",
            "；|;\s",
            "，|,\s"
        ])


def save_documents(documents,index = "faiss_index"):
    all_chunks = []
    for singledoc in documents:
        chunks = text_splitter.split_documents(singledoc)
        for chunk in chunks:
            all_chunks.append(chunk)  # 将每个文档的 chunks 合并到一个列表中
    db = FAISS.from_documents(all_chunks, embeddings)
    db.save_local(index)
    print('DO FAISS IS COMPLETE')
    return db

def create_and_save_faiss_index(path='knowledge_base/'):
    
    loaderdoc = documentloader.load_word_from_dir(path)
    save_documents(loaderdoc)

def get_documents(index="faiss_index", query="", limit=3):
    db = FAISS.load_local(index, embeddings,allow_dangerous_deserialization=True)
    docs = db.similarity_search_with_score(query)
    docs_page_content = " ".join([d[0].page_content for d in docs])
    print(f"docs_page_content：{docs}")
    return docs_page_content

if __name__ == '__main__':
    #create_and_save_faiss_index()
    index="faiss_index"
    query = "你可以python写一个下载页面的示例吗？"
    txts = get_documents(index,query,3)
    client = AzureOpenAI()
    completion = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": f"你是个礼貌且聪明的助理，可以根据给定文档回答问题。通过搜索文档：{txts}，回答以下问题：{query}。如果你觉得自己没有足够的信息来回答这个问题，可以根据你的经验来回答，回答结束时，请一定要说谢谢你的提问！"},
        {"role": "user", "content": f"{query}"}
    ])
    
print(completion.choices[0].message)