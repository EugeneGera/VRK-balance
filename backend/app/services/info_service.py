from typing import List, Optional, Union
from sqlalchemy.orm import scoped_session

from app.entities.schemas import products_list_schema, basises_list_schema, category_products_list_schema
from app.repositories.dict_repositories import DealCategoryDictRepository, ProductDictRepository, ShippingBasisDictRepository, TransDirDictRepository, UnitDictRepository, ProductCategoryDictRepository
from app.repositories.shipments_repository import ShipmentsRepository

class InfoService:
    def __init__(self, session: scoped_session):
        self.session = session
        self.product_dict_repository = ProductDictRepository(session)
        self.category_product_dict_repository = ProductCategoryDictRepository(session)
        self.basises_dict_repository = ShippingBasisDictRepository(session)
        self.shipments_repository = ShipmentsRepository(session)

    def get_latest_period(self):
        period = self.shipments_repository.get_latest_period()
        if period is None:
            return None
        return {
            'year': period.year,
            'month_start': period.month,
            'category_product': period.category_product,
        }

    def get_products_names(self):
        names_list = self.product_dict_repository.get_names()
        return products_list_schema.dump({'products': names_list})
    
    def get_category_product_names(self):
        names_list = self.category_product_dict_repository.get_names()
        return category_products_list_schema.dump({'category_product': names_list})
    
    def get_basises_names(self):
        names_list = self.basises_dict_repository.get_names()
        return basises_list_schema.dump({'shipping_basises': names_list})
    
    def get_basises_names_filtered(self,
                                   year: int,
                                   months: List[int],
                                   products: Optional[Union[List[str], str]] = None,
                                   product_categories: Optional[Union[List[str], str]] = None):
        names_list = [basis.name for basis in self.shipments_repository.get_working_basises(year=year, months=months, product_names=products, category_names=product_categories)]
        return basises_list_schema.dump({'shipping_basises': names_list})
    
    def get_products_names_filtered(self, category_product: Optional[Union[List[str], str]] = None):
        products = self.shipments_repository.get_working_products(category_names=category_product)
        return products_list_schema.dump({'products': [p.name for p in products]})
