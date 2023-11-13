from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI


class OpenAIHelper(object):
    def __init__(self, secret_key: str, *, temperature: float = 0.1):
        self.__secret_key = secret_key
        self.__temperature = temperature
        self._embedding_model = None
        self._llm = None

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            self._embedding_model = OpenAIEmbeddings(openai_api_key=self.__secret_key)
        return self._embedding_model

    @property
    def llm(self):
        if self._llm is None:
            self._llm = ChatOpenAI(
                model_name="gpt-3.5-turbo",
                openai_api_key=self.__secret_key,
                temperature=self.__temperature,
            )
        return self._llm
