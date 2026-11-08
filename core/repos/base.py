from django.core.files.storage import Storage
from django.db import transaction


class BaseDBRepo:
    @staticmethod
    def delete_file_on_commit(storage: Storage, name: str) -> None:
        if name:
            transaction.on_commit(lambda: storage.delete(name), robust=True)
