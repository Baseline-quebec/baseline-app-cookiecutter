"""{{ cookiecutter.project_name }} service layer."""

from {{ cookiecutter.__project_name_snake_case }}.models import Item, ItemCreate


class ItemService:
    """In-memory item service demonstrating the service layer pattern."""

    def __init__(self) -> None:
        self._items: dict[int, Item] = {}
        self._next_id: int = 1

    def create(self, data: ItemCreate) -> Item:
        """Create a new item and return it with an assigned id."""
        item = Item(id=self._next_id, **data.model_dump())
        self._items[self._next_id] = item
        self._next_id += 1
        return item

    def get(self, item_id: int) -> Item | None:
        """Return an item by id, or None if not found."""
        return self._items.get(item_id)

    def list_all(self) -> list[Item]:
        """Return all items."""
        return list(self._items.values())
