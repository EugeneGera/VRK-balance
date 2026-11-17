from typing import List, Union
from app.entities.models import AgentDictModel, ClientDictModel, DealCategoryDictModel, DealStatusDictModel, DealTypeDictModel, DestinationDictModel, DistrChannelDictModel, OrgDictModel, ProductCategoryDictModel, ProductDictModel, ProductOwnerDictModel, RecordOwnerDictModel, ShippingBasisDictModel, TransDirDictModel, TransportDictModel, UnitDictModel
from app.repositories.base_dict_repository import DictRepository
from app.repositories.utils import ensure_list
from sqlalchemy.orm import scoped_session

# Репо для отдельных справочников


class ProductDictRepository(DictRepository[ProductDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, ProductDictModel)


class ProductCategoryDictRepository(DictRepository[ProductCategoryDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, ProductCategoryDictModel)

    def get_first_unit_by_id(self, ids: Union[int, List[int]]):
        return self.session.query(UnitDictModel
                                  ).join(
                                      ProductDictModel, UnitDictModel.id == ProductDictModel.unit_id
                                  ).join(
                                      ProductCategoryDictModel, ProductDictModel.product_category_id == ProductCategoryDictModel.id
                                  ).where(
                                      ProductCategoryDictModel.id.in_(ensure_list(ids))
                                  ).first()


class ShippingBasisDictRepository(DictRepository[ShippingBasisDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, ShippingBasisDictModel)


class DealCategoryDictRepository(DictRepository[DealCategoryDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, DealCategoryDictModel)


class TransDirDictRepository(DictRepository[TransDirDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, TransDirDictModel)


class UnitDictRepository(DictRepository[UnitDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, UnitDictModel)


class AgentDictRepository(DictRepository[AgentDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, AgentDictModel)


class RecordOwnerDictRepository(DictRepository[RecordOwnerDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, RecordOwnerDictModel)


class DistrChannelDictRepository(DictRepository[DistrChannelDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, DistrChannelDictModel)


class OrgDictRepository(DictRepository[OrgDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, OrgDictModel)


class ClientDictRepository(DictRepository[ClientDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, ClientDictModel)


class ProductOwnerDictRepository(DictRepository[ProductOwnerDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, ProductOwnerDictModel)


class TransportDictRepository(DictRepository[TransportDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, TransportDictModel)


class DestinationDictRepository(DictRepository[DestinationDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, DestinationDictModel)


class DealStatusDictRepository(DictRepository[DealStatusDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, DealStatusDictModel)


class DealTypeDictRepository(DictRepository[DealTypeDictModel]):
    def __init__(self, db_session: scoped_session):
        super().__init__(db_session, DealTypeDictModel)
