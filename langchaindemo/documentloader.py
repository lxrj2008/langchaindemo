
from langchain_community.document_loaders import (
    UnstructuredWordDocumentLoader,
    CSVLoader,
    PyPDFLoader,
    TextLoader,
    DirectoryLoader,
)
import os
from langchain_community.document_loaders.unstructured import UnstructuredFileLoader
from langchain_community.document_loaders.pdf import PyPDFDirectoryLoader
 
 

 
def load_pdf_from_dir(directory_path):
    loader = PyPDFDirectoryLoader(directory_path)
    print(loader)
    data = loader.load()
    return data
 
 
def load_pdf_from_one(filepath):
    data = ''
    if filepath.endswith(".pdf"):
        print(filepath)
        # print the file name
        loader = PyPDFLoader(f'{filepath}')
        print(loader)
        data = loader.load()
    return data
 
 
def load_word_from_dir(directory_path):
    data = []
    for filename in os.listdir(directory_path):
        
        if filename.endswith(".doc") or filename.endswith(".docx"):
            
            loader = UnstructuredWordDocumentLoader(f'{directory_path}/{filename}')
            print(loader)
            data.append(loader.load())
    return data
 
 
def load_word_from_one(filename):
    data = ''
    if filename.endswith(".doc") or filename.endswith(".docx"):
        print(filename)
        loader = UnstructuredWordDocumentLoader(f'{filename}')
        print(loader)
        data = loader.load()
    return data
 
 
def load_txt_from_dir(directory_path):
    data = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            print(filename)
            loader = TextLoader(f'{directory_path}/{filename}',encoding='utf-8')
            print(loader)
            data.append(loader.load())
 
    return data
 
 
def load_text_from_one(filename):
    data = ''
    if filename.endswith(".txt"):
        print(filename)
        loader = TextLoader(f'{filename}',encoding='utf-8')
        print(loader)
        data = loader.load()
    return data
 
 
def load_csv_from_dir(directory_path):
    data = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            print(filename)
            loader = CSVLoader(f'{directory_path}/{filename}',encoding='utf-8')
            print(loader)
            data.append(loader.load())
 
    return data
 
 
def load_csv_from_one(filename):
    data = ''
    if filename.endswith(".csv"):
        print(filename)
        loader = CSVLoader(f'{filename}',encoding='utf-8')
        print(loader)
        data = loader.load()
    return data
 
 

def load_all_from_dir(directory_path, glob, show_progress=False, use_multithreading=False, loader_cls=UnstructuredFileLoader):
    loader = DirectoryLoader(directory_path, glob=glob, show_progress=show_progress, use_multithreading=use_multithreading, loader_cls=loader_cls)
    data = loader.load()
    return data
 
if __name__ == '__main__':
    res = load_all_from_dir("knowledge_base/","*")
    print(res)
 
