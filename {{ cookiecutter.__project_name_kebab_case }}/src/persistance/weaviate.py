"""Weaviate implementation of the vectorstore interface."""

from weaviate import Client

from {{ cookiecutter.__project_name_snake_case }}.data_models.models import Item
from {{ cookiecutter.__project_name_snake_case }}.helpers.vectorstore import Vectorstore


class WeaviateVectorstore(Vectorstore):
    """Weaviate implementation of the vectorstore interface."""

    def __init__(self, client: Client, vectorstore_name: str) -> None:
        """Initialize the vectorstore."""
        self.client = client
        self.vectorstore_name = vectorstore_name

    def read_item(self, item_id: int) -> Item:
        """Retrieve item by id."""
        return Item(field="value")

    def upsert_item(self, item: Item) -> None:
        """Upsert item."""

    def hybrid_search(self, query: str) -> Item:
        """Search for items."""
        return Item(field="value")
