from langchain.llms import HuggingFaceHub
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain import  VectorDBQA
from langchain_community.document_loaders import PyPDFLoader


class RAG:

    def __init__(self, documents):
        self.llm = self.load_llm()
        self.embeddings = self.load_embeddings()
        self.text_splitter = self.load_text_splitter()
        self.Documents = documents
        # self.Documents = PyPDFLoader(documents).load()
        print(f"[INFO] >>> reached query")
        texts = self.text_splitter.create_documents(self.Documents)
        # texts = self.text_splitter.split_documents(self.Documents)
        # texts = self.text_splitter.split_text(self.Documents)
        print(f"[INFO] >>> reached query docsearch")
        docsearch = Chroma.from_documents(texts, self.embeddings)
        print(f"[INFO] >>> Documents are stored in ChromaDB")
        self.qa = VectorDBQA.from_chain_type(llm=self.llm, chain_type="stuff", vectorstore=docsearch, return_source_documents=False)
        


    def load_llm(self):
        return HuggingFaceHub(
                repo_id="huggingfaceh4/zephyr-7b-alpha", 
                model_kwargs={"temperature": 0.9, "max_length": 512,"max_new_tokens":512}
            )

    def load_text_splitter(self):
        return CharacterTextSplitter( chunk_size=1000, chunk_overlap=200)

    def load_embeddings(self ):
        return HuggingFaceEmbeddings()

    def query(self, search_query):

        result = self.qa({"query": search_query})
        print(f"[INFO] >>> result : {result}")
        return result