import os
from typing import List

from elasticsearch import Elasticsearch
from langchain.schema import Document
from langchain.schema.embeddings import Embeddings
from langchain.vectorstores.elasticsearch import ElasticsearchStore


class ElasticSearch(object):
    def __init__(
        self,
        client: Elasticsearch,
        index_name: str,
        embedding: Embeddings,
    ):
        self._client = client
        self._elastic_db = ElasticsearchStore(
            index_name=index_name, es_connection=self._client, embedding=embedding
        )

    def add_documents(self, documents: List[Document]):
        return self._elastic_db.add_documents(documents, refresh_indices=True)

    def similarity_search(
        self, query: str, *, k: int = 3, threshold: float = 0.9
    ) -> List[Document]:
        docs = self._elastic_db.similarity_search_with_score(query=query, k=k)
        return [doc for doc, score in docs if score >= threshold]
