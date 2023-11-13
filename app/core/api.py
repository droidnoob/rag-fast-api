import uuid

import aiofiles
from fastapi import APIRouter, UploadFile
from pydantic import BaseModel

from app.clients.elastic import ElasticSearch
from app.clients.openai import OpenAIHelper
from app.core.llm import LLMManager
from app.core.manager import RAGManager
from app.core.schema import ResponseSchema
from app.resources import get_elastic_client, OpenAISettings
from app.utils.exceptions import BadRequestException

open_ai = OpenAIHelper(secret_key=OpenAISettings().secret_key)


class Query(BaseModel):
    query: str


class RAGApiRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rag_manager = RAGManager(
            elastic_helper=ElasticSearch(
                client=get_elastic_client(),
                index_name="test_index",
                embedding=open_ai.embedding_model,
            ),
            llm_manager=LLMManager[ResponseSchema](open_ai.llm),
        )

    @staticmethod
    def validate_content_type(file: UploadFile):
        if file.content_type not in {"application/pdf", "text/markdown", "text/plain"}:
            raise BadRequestException("File is not in the supported type")

    @classmethod
    async def save_file(cls, file: UploadFile):
        cls.validate_content_type(file)
        extension = file.filename.split(".")[-1]
        file_name = f"{uuid.uuid4()}.{extension}"
        out_file_path = f"./app/uploads/{file_name}"
        async with aiofiles.open(out_file_path, "wb") as out_file:
            while content := await file.read(1024):  # async read chunk
                await out_file.write(content)
        return out_file_path, extension, file_name

    def add_custom_routes(self):
        @self.post("/ingest-file")
        async def ingest_file(file: UploadFile):
            out_file_path, extension, file_name = await self.save_file(file)
            self._rag_manager.embed_files(out_file_path, extension)
            return {"file_location": f"uploads/{file_name}"}

        @self.post("/query")
        async def query(query_request: Query) -> ResponseSchema:
            response = self._rag_manager.query_llm(query=query_request.query)
            return response

        return self


route = RAGApiRouter().add_custom_routes()
