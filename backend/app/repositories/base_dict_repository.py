from typing import Generic, List, Type, TypeVar, Union
from sqlalchemy import update
from sqlalchemy.orm import scoped_session

from app.entities.models import (ShippingBasisDictModel, ProductDictModel, ProductCategoryDictModel,
                                 DealCategoryDictModel, UnitDictModel, DistrChannelDictModel, TransDirDictModel,
                                 OrgDictModel, RecordOwnerDictModel, AgentDictModel, ProductOwnerDictModel,
                                 DealStatusDictModel, TransportDictModel, DealTypeDictModel, DestinationDictModel,
                                 ClientDictModel)
from app.repositories.repository import BaseRepository
from app.repositories.utils import ensure_list

DictModel = TypeVar('DictModel',                       # Справочники
                    ShippingBasisDictModel,
                    ProductDictModel,
                    ProductCategoryDictModel,
                    DealCategoryDictModel,
                    UnitDictModel,
                    DistrChannelDictModel,
                    TransDirDictModel,
                    OrgDictModel,
                    RecordOwnerDictModel,
                    AgentDictModel,
                    ProductOwnerDictModel,
                    DealStatusDictModel,
                    TransportDictModel,
                    DealTypeDictModel,
                    DestinationDictModel,
                    ClientDictModel)


class DictRepository(BaseRepository, Generic[DictModel]):
    def __init__(self, session: scoped_session, model: Type[DictModel]):
        self.session : scoped_session = session
        self.model = model

    def get_names(self,                          # Получить все наименования справочника
                  *args, **kwargs
                  ) -> List[str]:
        return [item[0] for item in self.session.query(self.model.name).filter(*args).filter_by(**kwargs).all()]

    def get_all(self,                            # Получить все модели справочника
                *args, **kwargs
                ) -> List[str]:
        return self.session.query(self.model).filter(*args).filter_by(**kwargs).all()

    def get_by_id(self, ids: Union[int, List[int]],                # Получить модель по id
                  *args, **kwargs
                  ) -> Type[DictModel]:
        return self.session.query(self.model).filter(self.model.id.in_(ensure_list(ids))).filter(*args).filter_by(**kwargs).first()

    def add(self, model):
        raise NotImplementedError()

    def get_by_names(self, names: Union[str, List[str]],
                     *args, **kwargs) -> DictModel:
        return self.session.query(self.model).filter(self.model.name.in_(ensure_list(names))).filter(*args).filter_by(**kwargs).all()

    def get_table_name(self) -> str:
        return self.model.__tablename__

    def get_none_empty_records_count(self): 
        return self.session.query(self.model).filter(self.model.name != None).count()

    def get_all_id_name(self):
        return self.session.query(self.model.id, self.model.name).filter(self.model.name != None).all()

    def update_by_id(self, id, fields):
        statement = update(self.model).where(
            self.model.id == id).values(**fields)
        self.session.execute(statement)
