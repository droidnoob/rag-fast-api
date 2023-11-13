from app.clients.elastic import ElasticSearch
from app.utils.exceptions import NotFoundException, BadRequestException
from app.utils.file_reader import FileReader
from app.core.llm import LLMManager
from app.core.schema import ResponseSchema


class RAGManager(object):
    def __init__(
        self, elastic_helper: ElasticSearch, llm_manager: LLMManager[ResponseSchema]
    ):
        self.file_reader = FileReader()
        self.elastic_helper = elastic_helper
        self.llm_manager = llm_manager

    def embed_files(self, file_path: str, file_type: str):
        documents = self.file_reader.create_chunks(file_path, file_type)
        if len(documents) == 0:
            raise BadRequestException("Empty file received")
        self.elastic_helper.add_documents(documents)

    def query_knowledge_base(self, query: str):
        documents = self.elastic_helper.similarity_search(query)
        if len(documents) == 0:
            raise NotFoundException("Do not have enough info to give a response")
        return documents

    def query_llm(self, query: str):
        documents = self.query_knowledge_base(query)
        print(documents)
        response = self.llm_manager.ask_llm(query, documents, ResponseSchema)
        if response is None:
            raise NotFoundException("Do not have enough info to give a response")
        response.context = [doc.page_content for doc in documents]
        response.file_loc = set(
            [
                self.llm_manager.file_location(doc.metadata.get("source"))
                for doc in documents
                if doc.metadata.get("source")
            ]
        )
        return response
