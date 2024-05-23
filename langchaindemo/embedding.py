
from openai import AzureOpenAI 
import os 
import documentloader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
import cfg
from datetime import datetime
import time
from mylogging import setup_logging
import re

chunksize=cfg.TextSplitterCfg["chunksize"]
chunkoverlap=cfg.TextSplitterCfg["overlap"]


os.environ["AZURE_OPENAI_API_KEY"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_key"]
os.environ["OPENAI_API_VERSION"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_version"]
os.environ["AZURE_OPENAI_ENDPOINT"] = cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["api_base_url"]


embeddings = AzureOpenAIEmbeddings(model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["embedding"])
text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunksize, chunk_overlap=chunkoverlap, separators=[
            "\n\n",
            "\n",
            "。|！|？",
            "\.\s|\!\s|\?\s",
            "；|;\s",
            "，|,\s"
        ])

logger_info, logger_error,logger_debug = setup_logging()

top_k=cfg.SimilaritySearchCfg["top_k"]
button_name_pattern = r"\*按钮名称\*:\s*(.*)"

def Split_Documents(documents):
    all_chunks = []
    for singledoc in documents:
        chunks = text_splitter.split_documents(singledoc)
        for chunk in chunks:
            all_chunks.append(chunk) 
    return all_chunks


def save_documents(documents,index = "faiss_index"):
    db = FAISS.from_documents(documents, embeddings)
    db.save_local(index)
    print('Init FAISS IS COMPLETE')
    return db

def create_and_save_faiss_index(path='knowledge_base/'):
    
    loaderdoc = documentloader.load_csv_from_dir(path)
    all_chunks=Split_Documents(loaderdoc)
    save_documents(all_chunks)

def InitMappingIndex(path='exchangdoc/'):
    
    loaderdoc = documentloader.load_csv_from_dir(path)
    all_chunks=Split_Documents(loaderdoc)
    save_documents(all_chunks,"mapping_faiss")

def get_documents(index="faiss_index", query="",relevance_score=0):
    start_time = time.time()
    db = FAISS.load_local(index, embeddings,allow_dangerous_deserialization=True)
    docs = db.similarity_search_with_relevance_scores(query,top_k)
    filtered_docs = [(doc, score) for doc, score in docs if score >= relevance_score]
    button_names = []
    for d in filtered_docs:
        match = re.search(button_name_pattern, d[0].page_content)
        if match:
            button_names.append(match.group(1).strip())
            d[0].page_content=re.sub(button_name_pattern, '', d[0].page_content)
    docs_page_content = " ".join([d[0].page_content for d in filtered_docs])
    button_name = button_names[0] if button_names else ''
    data={"content":f"{docs_page_content}","button":f"{button_name}"}
    end_time = time.time()  
    elapsed_time = end_time - start_time  
    logger_debug.info(f'搜索嵌知识库耗时：{elapsed_time}秒')
    return data

def get_mapping_documents(index="faiss_index", query="",relevance_score=0):
    db = FAISS.load_local(index, embeddings,allow_dangerous_deserialization=True)
    docs = db.similarity_search_with_relevance_scores(query,1)
    filtered_docs = [(doc, score) for doc, score in docs if score >= relevance_score]
    docs_page_content = " ".join([d[0].page_content for d in filtered_docs]).strip()
    if docs_page_content:
        codevalue=query
        lines = docs_page_content.split('\n')
        for line in lines:
            if line.startswith("code:"):
                codevalue= line.split(':')[1].strip()
                codevalue=re.sub(r'_(C|P|S|W)', '', codevalue)
                break
        return codevalue
    else:
        return query

def add_txt_from_dir_bymerge(index="faiss_index"):
    db1 = FAISS.load_local(index, embeddings,allow_dangerous_deserialization=True)
    
    loaderdoc=documentloader.load_txt_from_dir("Add_docments/")
    if len(loaderdoc)==0:
        return
    all_chunks=Split_Documents(loaderdoc)
    db2=FAISS.from_documents(all_chunks, embeddings)
    db1.merge_from(db2);
    db1.save_local(index)
    print("ADD FAISS IS COMPLETE")

def delfromdb(index="faiss_index",metadata=None):
    db = FAISS.load_local(index, embeddings,allow_dangerous_deserialization=True)
    docids=db.index_to_docstore_id
    vetor=db.docstore._dict
    deleteIds=[];
    for key, value in vetor.items():
         print(key, value.metadata)
         if(value.metadata['source']==metadata):
             for key1,value1 in docids.items():
                 if value1==key:
                     strkey=str(key1)
                     deleteIds.append(value1)
    if(len(deleteIds)>0):
        db.delete(deleteIds)
        db.save_local(index)

def add_doc_from_dir(index="faiss_index"):
    
    db = FAISS.load_local(index, embeddings,allow_dangerous_deserialization=True)
    loaderdoc=documentloader.load_word_from_dir("Add_docments/")
    if len(loaderdoc)==0:
        return
    all_chunks=Split_Documents(loaderdoc)
    db.add_documents(all_chunks)
    db.save_local(index)
    print("ADD FAISS IS COMPLETE")

def add_txt_from_dir(index="faiss_index"):
    db = FAISS.load_local(index, embeddings,allow_dangerous_deserialization=True)
    
    loaderdoc=documentloader.load_txt_from_dir("Add_docments/")
    if len(loaderdoc)==0:
        return
    all_chunks=Split_Documents(loaderdoc)
    db.add_documents(all_chunks)
    db.save_local(index)
    print("ADD FAISS IS COMPLETE")

def add_csv_from_dir(index="faiss_index"):
    db = FAISS.load_local(index, embeddings,allow_dangerous_deserialization=True)
    
    loaderdoc=documentloader.load_csv_from_dir("Add_docments/")
    if len(loaderdoc)==0:
        return
    all_chunks=Split_Documents(loaderdoc)
    db.add_documents(all_chunks)
    db.save_local(index)
    print("ADD FAISS IS COMPLETE")

def add_pdf_from_dir(index="faiss_index"):
    db = FAISS.load_local(index, embeddings,allow_dangerous_deserialization=True)
    
    loaderdoc=documentloader.load_pdf_from_dir("Add_docments/")
    if len(loaderdoc)==0:
        return
    all_chunks=Split_Documents(loaderdoc)
    db.add_documents(all_chunks)
    db.save_local(index)
    print("ADD FAISS IS COMPLETE")
    

if __name__ == '__main__':
    #InitMappingIndex()
    #create_and_save_faiss_index()
    #add_csv_from_dir()
    #add_txt_from_dir()
    #add_doc_from_dir()
    #add_pdf_from_dir()
    #delfromdb('faiss_index','Add_docments//ask_question.csv')
    
    while True:
        index = "faiss_index"
        query = input("You: ")  
        if query.lower() in ["exit", "quit", "bye"]:
            print("再见！")
            break  
        current_time = datetime.now().strftime("%H:%M:%S")  
        print(f"[{current_time}] you: {query}")  
        txts = get_documents(index, query,cfg.SimilaritySearchCfg["min_score"])["content"]
        client = AzureOpenAI()
        completion = client.chat.completions.create(
            model=cfg.ONLINE_LLM_MODEL["AzureOpenAI"]["model_name"],
            messages=[
                {"role": "system", "content": f"你是上海直达软件有限公司开发的智能机器人小达达，你很有礼貌且很聪明，可以根据知识库回答问题。通过搜索知识库：{txts}，回答以下问题：{query}。如果你觉得知识库内容信息不足以回答这个问题，可以根据你的经验来回答"},
                {"role": "user", "content": query}
            ]
        )
        current_time = datetime.now().strftime("%H:%M:%S") 
        print(f"[{current_time}] Bot: {completion.choices[0].message.content}")  