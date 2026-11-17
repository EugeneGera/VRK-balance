from sqlalchemy.orm import scoped_session

from app.entities.schemas import products_list_schema, basises_list_schema
from app.repositories.dict_repositories import ProductDictRepository, ShippingBasisDictRepository

class JournalService:
    def __init__(self, session: scoped_session):
        self.session = session
        self.product_dict_repository = ProductDictRepository(session)
        self.basises_dict_repository = ShippingBasisDictRepository(session)

    def get_products_names(self):
        names_list = self.product_dict_repository.get_names()
        return products_list_schema.dump({'products': names_list})
    
    def get_basises_names(self):
        names_list = self.basises_dict_repository.get_names()
        return basises_list_schema.dump({'shipping_basises': names_list})