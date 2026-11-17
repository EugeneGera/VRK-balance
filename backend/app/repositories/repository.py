import abc


class BaseRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, model, *args, **kwargs):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def get_all(self, *args, **kwargs):
        raise NotImplementedError()
    
    @abc.abstractmethod
    def get_by_id(self, id: int, *args, **kwargs):
        raise NotImplementedError()