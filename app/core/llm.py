import json
from json import JSONDecodeError
from typing import List, Type, TypeVar, Generic

from langchain.chat_models.base import BaseChatModel
from langchain.schema import Document, SystemMessage, BaseMessage, HumanMessage
from pydantic import BaseModel
from pydantic_core import ValidationError

SchemaOutType = TypeVar("SchemaOutType", bound=BaseModel)


class LLMManager(Generic[SchemaOutType]):
    def __init__(self, chat_model: BaseChatModel):
        self.chat_model = chat_model

    def ask_llm(
        self,
        query: str,
        documents: List[Document],
        response_schema: Type[SchemaOutType],
    ) -> SchemaOutType | None:
        prompt = self.create_prompt(query, documents, response_schema)
        return self.get_response(prompt, response_schema)

    def get_response(
        self, prompt: List[BaseMessage], response_schema: Type[SchemaOutType]
    ):
        try:
            return response_schema(**json.loads(self.chat_model(prompt).content))
        except (JSONDecodeError, ValidationError):
            return None

    def create_prompt(
        self,
        query: str,
        documents: List[Document],
        response_schema: Type[SchemaOutType],
    ) -> List[BaseMessage]:
        messages = [
            SystemMessage(
                content="You are a helpful assistant that retrieves relevant information for "
                "the user query based on the context given."
            )
        ]
        self.add_context(messages, documents)
        self.add_response_schema(messages, response_schema)
        self.add_query(messages, query)
        return messages

    @classmethod
    def add_context(cls, messages: List[BaseMessage], documents: List[Document]):
        messages.append(
            SystemMessage(
                content="Below contains the context for the question. Answer the query only based on the context."
                "The contexts are given inside <CONTEXT> tag. If you are not confident response should be "
                "`Cannot form an answer with the present knowledge base`. "
                "You should not make up an answer"
            )
        )
        for doc in documents:
            messages.append(
                SystemMessage(content=f"<CONTEXT>{doc.page_content}</CONTEXT>")
            )

    @staticmethod
    def file_location(location: str):
        if location is None:
            return None
        return f'/uploads/{location.split("./app/uploads/")[-1]}'

    @staticmethod
    def add_response_schema(
        messages: List[BaseMessage], response_schema: Type[SchemaOutType]
    ):
        messages.append(
            SystemMessage(
                content="The response should only be in the following json format"
            )
        )
        messages.append(
            SystemMessage(content=json.dumps(response_schema.model_json_schema()))
        )

    @staticmethod
    def add_query(messages: List[BaseMessage], query: str):
        messages.append(HumanMessage(content=query))
