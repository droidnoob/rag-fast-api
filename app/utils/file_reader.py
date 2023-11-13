from typing import List, Generator, Any

from langchain.document_loaders import (
    PyPDFLoader,
    CSVLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
)
from langchain.document_loaders.base import BaseLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document
from langchain.text_splitter import CharacterTextSplitter

from app.utils.exceptions import BadRequestException


class FileReader(object):
    def __init__(self, chunk_size: int = 4000, chunk_overlap: int = 400):
        self.text_splitter = CharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, separator="\n"
        )

    @staticmethod
    def load_file(file_path: str, file_type: str) -> BaseLoader:
        if file_type == "pdf":
            return PyPDFLoader(file_path)
        if file_type == "md":
            return UnstructuredMarkdownLoader(file_path)
        if file_type == "txt":
            return TextLoader(file_path)
        raise BadRequestException(f"File type not supported: {file_type}")

    def create_chunks_gen(
        self, file_path: str, file_type: str
    ) -> Generator[Document, Any, None]:
        loader = self.load_file(file_path, file_type)
        for doc in loader.load_and_split(self.text_splitter):
            doc.page_content = doc.page_content.replace("\n", " ")
            yield doc

    def create_chunks(self, file_path: str, file_type: str) -> List[Document]:
        return list(self.create_chunks_gen(file_path, file_type))
