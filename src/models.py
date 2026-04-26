import asyncio
from typing import Any
from datetime import datetime
import uuid
from src.special_errors import InvalidPriorityError,InvalidStatusError

class TaskStatus:
    """Константы статусов задачи """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ALL = {PENDING, IN_PROGRESS, COMPLETED, FAILED}

class PriorityDescriptor:
    """ Дескриптор для приоритета задачи"""
    def __set_name__(self, owner, name):
        self.storage_name=f'_{name}'

    def __get__(self,obj,objtype=None):
        if obj is None:
            return self
        return getattr(obj,self.storage_name,3)
    def __set__(self, obj, value):
        if not isinstance(value,int):
            raise TypeError("Значение должно быть типа int")
        if not 1<=value<=5:
            raise InvalidPriorityError(obj.id,"Значение должно быть в диапазоне от 1 до 5")
        setattr(obj,self.storage_name,value)

class StatusDescriptor:
    """ Дескриптор для статуса задачи"""
    def __set_name__(self, owner, name):
        self.storage_name=f'_{name}'
    def __get__(self,obj,objtype=None):
        if obj is None:
            return self
        return getattr(obj,self.storage_name,TaskStatus.PENDING)
    def __set__(self, obj, value):
        if not isinstance(value,str):
            raise TypeError("Статус должен быть строкой")
        if value not in TaskStatus.ALL:
            raise InvalidStatusError(obj.id,f"Допустимые:{TaskStatus.ALL}")
        setattr(obj,self.storage_name,value)

class Task:
    """Модель задачи"""
    __slots__ = (
        '_id',
        '_payload',
        '_priority',
        '_status',
        '_time_created',)
    priority= PriorityDescriptor()
    status= StatusDescriptor()

    def __init__(self, payload: dict[str, Any]=None,priority:int = 3):
        self._id = str(uuid.uuid4())
        self.payload = payload or {}
        self.priority = priority
        self.status = TaskStatus.PENDING
        self._time_created = datetime.now()

    @property
    def is_ready(self) -> bool:
        return self._status == TaskStatus.PENDING

    @property
    def age(self)->float:
        return (datetime.now() - self._time_created).total_seconds()

    @property
    def time_created(self) -> datetime:
        return self._time_created

    @property
    def id(self)->str:
        return self._id

    @property
    def payload(self)->dict:
        return self._payload

    @payload.setter
    def payload(self, payload: dict[str, Any]):
        if not isinstance(payload, dict):
            raise TypeError("payload должен быть словарем")
        self._payload = payload

    def start(self)->None:
        """ Начать выполнение задачи """
        if self.status!=TaskStatus.PENDING:
            raise InvalidStatusError(self.id,"Метод применим только к задаче со статусом PENDING")
        self.status = TaskStatus.IN_PROGRESS

    def complete(self)->None:
        """ Выполнение задачи завершилось успехом"""
        if self.status!=TaskStatus.IN_PROGRESS:
            raise InvalidStatusError(self.id,"Метод применим только к задаче со статусом IN_PROGRESS")
        self.status = TaskStatus.COMPLETED

    def fail(self)->None:
        """ Выполнение задачи завершилось ошибкой"""
        if self.status!=TaskStatus.IN_PROGRESS:
            raise InvalidStatusError(self.id,"Метод применим только к задаче со статусом IN_PROGRESS")
        self.status = TaskStatus.FAILED

    def retry(self)->None:
        """Возобновить задачу"""
        if self.status!=TaskStatus.FAILED:
            raise InvalidStatusError(self.id,"Метод применим только к задаче со статусом FAILED")
        self.status = TaskStatus.PENDING

    def __repr__(self) -> str:
        return (
            f"Task(id={self._id!r}, payload={self._payload}, priority={self._priority}, "
            f"status={self._status}, is_ready={self.is_ready}, time_created={self._time_created})"
        )
