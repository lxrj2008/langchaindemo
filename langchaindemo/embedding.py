
from http import client
from openai import AzureOpenAI # for calling the OpenAI API
import os # for getting API token from env variable OPENAI_API_KEY
import documentloader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import cfg



# Set up environment variables
os.environ["AZURE_OPENAI_API_KEY"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_key"]
os.environ["OPENAI_API_VERSION"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_version"]
os.environ["AZURE_OPENAI_ENDPOINT"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_base_url"]

#块大小：800 个令牌
#块重叠：400 个令牌
#嵌入模型：text-embedding-3-large256 维
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

def get_documents(index="faiss_index", query=""):
    db = FAISS.load_local(index, embeddings,allow_dangerous_deserialization=True)
    docs = db.similarity_search_with_score(query)
    docs_page_content = " ".join([d[0].page_content for d in docs])
    #print(f"docs_page_content：{docs}")
    return docs_page_content

if __name__ == '__main__':
    #create_and_save_faiss_index()
    index="faiss_index"
    query = "请介绍下开户流程"
    txts = get_documents(index,query)
    client = AzureOpenAI()
    completion = client.chat.completions.create(
    model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
    messages=[
        {"role": "system", "content": f"你是上海直达软件有限公司开发的智能机器人小达达，你很有礼貌且很聪明，可以根据知识库回答问题。通过搜索知识库：{txts}，回答以下问题：{query}。如果你觉得知识库内容信息不足以回答这个问题，可以根据你的经验来回答"},
        {"role": "user", "content": f"{query}"}
    ])
    
    print(completion.choices[0].message)