"""Vectorstore for the app."""

from {{ cookiecutter.__project_name_snake_case }}.data_models.models import Item


class Vectorstore:
    """Vectorstore containing items."""

    def read_item(self, item_id: int) -> Item:
        """Retrieve item by id."""
        raise NotImplementedError

    def upsert_item(self, item: Item) -> None:
        """Upsert item."""
        raise NotImplementedError

    def hybrid_search(self, query: str) -> Item:
        """Search for items."""
        raise NotImplementedError
