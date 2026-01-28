# backend/data/storage_adapter.py
from abc import ABC, abstractmethod
from backend.data.schema import FinancialRecord

class StorageAdapter(ABC):

    @abstractmethod
    def save(self, record: FinancialRecord) -> None:
        pass

class InMemoryStorage(StorageAdapter):
    def __init__(self):
        self.records = []

    def save(self, record: FinancialRecord) -> None:
        self.records.append(record)
