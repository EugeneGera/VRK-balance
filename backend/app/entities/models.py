from typing import Optional
from sqlalchemy.orm import relationship
import sqlalchemy as sa
import sqlalchemy.orm as so


from app.entities.db_connection import Base

# Справочники

# Справочник Базис отгрузки


class ShippingBasisDictModel(Base):
    __tablename__ = 'tab_bazis_bk'
    tablename_cyr: str = 'Базис огрузки'
    id: so.Mapped[int] = so.mapped_column(name='id', primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), name='name')
    agent_id: so.Mapped[int] = so.mapped_column(sa.Integer, name='tab_proizv_bk_ids',  # Агент/Производитель
                                                nullable=True)


# Справочник 'Продукт'
class ProductDictModel(Base):
    __tablename__ = 'tab_product_bk'
    tablename_cyr: str = 'Продукт'
    id: so.Mapped[int] = so.mapped_column(name='id', primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(255), name='name')
    product_category_id: so.Mapped[int] = so.mapped_column(sa.Integer, name='tab_category_product_bk_ids',
                                                           nullable=True)
    unit_id: so.Mapped[int] = so.mapped_column(sa.Integer,
                                               sa.ForeignKey('tab_ei_bk.id'),
                                               nullable=True, name='tab_ei_bk_ids',)
    
    unit: so.Mapped['UnitDictModel'] = relationship("UnitDictModel")

    
# Справочник Категория продукта
class ProductCategoryDictModel(Base):
    __tablename__ = 'tab_category_product_bk'
    tablename_cyr: str = 'Категория продукта'
    id: so.Mapped[int] = so.mapped_column(name='id', primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(64), name='name')


# Справочник Категория сделки
class DealCategoryDictModel(Base):
    __tablename__ = 'tab_category_sd_bk'
    tablename_cyr: str = 'Категория сделки'
    id: so.Mapped[int] = so.mapped_column(sa.Integer, primary_key=True,
                                          autoincrement=True,
                                          index=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(150))

    # Foreign keys
    deal_type_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                              name='tab_type_sd_bk_ids')
    distr_channel_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                  name='tab_kanal_sb_bk_ids')


class UnitDictModel(Base):              # Справочник Единицы измерения
    __tablename__ = 'tab_ei_bk'
    tablename_cyr: str = 'Единицы измерения'
    id: so.Mapped[int] = so.mapped_column(name='id', primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(150), name='name')


class DistrChannelDictModel(Base):  # Справочник Канал сбыта
    __tablename__ = 'tab_kanal_sb_bk'
    tablename_cyr: str = 'Канал сбыта'

    id: so.Mapped[int] = so.mapped_column(
        sa.Integer, name='id', primary_key=True, index=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(100), name='name')


# Справочник Направление реализации
class TransDirDictModel(Base):
    __tablename__ = 'tab_napr_real_bk'
    tablename_cyr: str = 'Направление реализации'

    id: so.Mapped[int] = so.mapped_column(
        sa.Integer, name='id', primary_key=True, index=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(100), name='name')


class OrgDictModel(Base):                   # Справочник Организация
    __tablename__ = 'tab_org_bk'
    tablename_cyr: str = 'Организация'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, name='id',
                                          primary_key=True,
                                          index=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(255), name='name')


class RecordOwnerDictModel(Base):           # Справочник Владелец записи
    __tablename__ = 'tab_owner_bk'
    tablename_cyr: str = ' Владелец записи'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, name='id',
                                          primary_key=True,
                                          index=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(255), name='name')

    # Foreign keys
    org_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.Integer, name='tab_org_bk_ids')


class AgentDictModel(Base):                 # Справочник Агент / Производитель
    __tablename__ = 'tab_proizv_bk'
    tablename_cyr: str = ' Агент / Производитель'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, name='id',
                                          primary_key=True,
                                          index=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(255), name='name')


# Справочник Собственник продукта
class ProductOwnerDictModel(Base):
    __tablename__ = 'tab_sobstv_bk'
    tablename_cyr: str = ' Собственник продукта'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, name='id',
                                          primary_key=True,
                                          index=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(150), name='name')


# Справочник Статус заключения сделки
class DealStatusDictModel(Base):
    __tablename__ = 'tab_status_sd_bk'
    tablename_cyr: str = ' Статус заключения сделки'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, name='id',
                                          primary_key=True,
                                          index=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100),
                                                      name='name')


class TransportDictModel(Base):                 # Справочник Способ отгрузки
    __tablename__ = 'tab_type_otgruz_bk'
    tablename_cyr: str = ' Способ отгрузки'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, name='id',
                                          primary_key=True,
                                          index=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(150),
                                                      name='name')


class DealTypeDictModel(Base):                  # Справочник Тип сделки
    __tablename__ = 'tab_type_sd_bk'
    tablename_cyr: str = ' Тип сделки'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, name='id',
                                          primary_key=True,
                                          index=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(150),
                                                      name='name')


# Справочник Пункт назначения
class DestinationDictModel(Base):
    __tablename__ = 'tab_point_to_bk'
    tablename_cyr: str = ' Пункт назначения'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, name='id',
                                          primary_key=True,
                                          index=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(150),
                                                      name='name')


class ClientDictModel(Base):                  # Справочник Покупатель
    __tablename__ = 'tab_pokup_bk'
    tablename_cyr: str = ' Покупатель'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, name='id',
                                          primary_key=True,
                                          index=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(150),
                                                      name='name')


# Заявки
# Таблица Заявки на реализацию товарной продукции
class TransApplicationModel(Base):
    __tablename__ = 'tab_zayav_real_bk'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, name='id',
                                          primary_key=True,
                                          index=True)

    # Дата
    year: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, name='year')
    month: so.Mapped[Optional[int]] = so.mapped_column(
        sa.Integer, name='month')

    value: so.Mapped[Optional[float]] = so.mapped_column(
        sa.Double, name='value')
    cost: so.Mapped[Optional[float]] = so.mapped_column(sa.Double, name='cost')

    comment: so.Mapped[Optional[int]] = so.mapped_column(
        sa.String(255), name='comment')

    # Foreign keys
    record_owner_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                 sa.ForeignKey(
                                                                     'tab_owner_bk.id'),
                                                                 name='tab_owner_bk_ids')
    shipping_basis_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                   sa.ForeignKey(
                                                                       'tab_bazis_bk.id'),
                                                                   name='tab_bazis_bk_ids')
    product_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                            sa.ForeignKey(
                                                                'tab_product_bk.id'),
                                                            name='tab_product_bk_ids')
    unit_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                         sa.ForeignKey(
                                                             'tab_ei_bk.id'),
                                                         name='tab_ei_bk_ids')
    trans_dir_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                              sa.ForeignKey(
                                                                  'tab_napr_real_bk.id'),
                                                              name='tab_napr_real_bk_ids')
    agent_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                          sa.ForeignKey(
                                                              'tab_proizv_bk.id'),
                                                          name='tab_proizv_bk_ids')
    product_owner_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                  sa.ForeignKey(
                                                                      'tab_sobstv_bk.id'),
                                                                  name='tab_sobstv_bk_ids')
    transport_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                              sa.ForeignKey(
                                                                  'tab_type_otgruz_bk.id'),
                                                              name='tab_type_otgruz_bk_ids')
    deal_category_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                  sa.ForeignKey(
                                                                      'tab_category_sd_bk.id'),
                                                                  name='tab_category_sd_bk_ids')
    destination_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                sa.ForeignKey(
                                                                    'tab_point_to_bk.id'),
                                                                name='tab_point_to_bk_ids')
    client_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                           sa.ForeignKey(
                                                               'tab_pokup_bk.id'),
                                                           name='tab_pokup_bk_ids')
    deal_status_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                sa.ForeignKey(
                                                                    'tab_status_sd_bk.id'),
                                                                name='tab_status_sd_bk_ids')

    #
    owner: so.Mapped['RecordOwnerDictModel'] = relationship(
        "RecordOwnerDictModel")
    shipping_basis: so.Mapped['ShippingBasisDictModel'] = relationship(
        "ShippingBasisDictModel")
    product: so.Mapped['ProductDictModel'] = relationship("ProductDictModel")
    unit: so.Mapped['UnitDictModel'] = relationship("UnitDictModel")
    trans_dir: so.Mapped['TransDirDictModel'] = relationship(
        "TransDirDictModel")
    agent: so.Mapped['AgentDictModel'] = relationship("AgentDictModel")
    product_owner: so.Mapped['ProductOwnerDictModel'] = relationship(
        "ProductOwnerDictModel")
    transport: so.Mapped['TransportDictModel'] = relationship(
        "TransportDictModel")
    deal_category: so.Mapped['DealCategoryDictModel'] = relationship(
        "DealCategoryDictModel")
    destination: so.Mapped['DestinationDictModel'] = relationship(
        "DestinationDictModel")
    client: so.Mapped['ClientDictModel'] = relationship("ClientDictModel")
    deal_status: so.Mapped['DealStatusDictModel'] = relationship(
        "DealStatusDictModel")


# Таблица План производства товарной продукции
class ProductionPlanModel(Base):
    __tablename__ = 'tab_zayav_proizv_bk'

    id: so.Mapped[int] = so.mapped_column(sa.Integer, name='id',
                                          primary_key=True,
                                          index=True)

    # Дата
    year: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer, name='year')
    month: so.Mapped[Optional[int]] = so.mapped_column(
        sa.Integer, name='month')

    left: so.Mapped[Optional[float]] = so.mapped_column(sa.Double, name='ost')
    plan: so.Mapped[Optional[float]] = so.mapped_column(sa.Double, name='plan')
    min_left: so.Mapped[Optional[float]] = so.mapped_column(
        sa.Double, name='min_ost')
    max_shipment: so.Mapped[Optional[float]] = so.mapped_column(
        sa.Double, name='max_otgr')
    resource: so.Mapped[Optional[float]] = so.mapped_column(
        sa.Double, name='summ_res')
    percent_exchange: so.Mapped[Optional[float]] = so.mapped_column(
        sa.Double, name='percent_birga')
    value_exchange: so.Mapped[Optional[float]] = so.mapped_column(
        sa.Double, name='value_birga')

    comment_plan: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    comment_ost: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255))
    comment_min_ost: so.Mapped[Optional[str]
                               ] = so.mapped_column(sa.String(255))
    comment_max_otgr: so.Mapped[Optional[str]
                                ] = so.mapped_column(sa.String(255))

    # FK
    shipping_basis_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                   sa.ForeignKey(
                                                                       'tab_bazis_bk.id'),
                                                                   name='tab_bazis_bk_ids')
    product_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                            sa.ForeignKey(
                                                                'tab_product_bk.id'),
                                                            name='tab_product_bk_ids')
    unit_id: so.Mapped[int] = so.mapped_column(sa.Integer,
                                               sa.ForeignKey('tab_ei_bk.id'),
                                               name='tab_ei_bk_ids',
                                               nullable=True)
    agent_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                          sa.ForeignKey(
                                                              'tab_proizv_bk.id'),
                                                          name='tab_proizv_bk_ids')
    product_owner_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                  sa.ForeignKey(
                                                                      'tab_sobstv_bk.id'),
                                                                  name='tab_sobstv_bk_ids')

    shipping_basis: so.Mapped['ShippingBasisDictModel'] = relationship(
        "ShippingBasisDictModel")
    product: so.Mapped['ProductDictModel'] = relationship("ProductDictModel")
    unit: so.Mapped['UnitDictModel'] = relationship("UnitDictModel")
    agent: so.Mapped['AgentDictModel'] = relationship("AgentDictModel")
    product_owner: so.Mapped['ProductOwnerDictModel'] = relationship(
        "ProductOwnerDictModel")

# Данные
# TODO! добавить первичный ключ(


class AllResourceModel(Base):                   # Таблица Весь ресурс
    __tablename__ = 'tab_resource_bk'

    shipping_basis_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                   sa.ForeignKey(
                                                                       'tab_bazis_bk.id'),
                                                                   name='tab_bazis_bk_ids',
                                                                   primary_key=True)
    product_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                            sa.ForeignKey(
                                                                'tab_product_bk.id'),
                                                            name='tab_product_bk_ids',
                                                            primary_key=True)

    # Дата
    year: so.Mapped[Optional[int]] = so.mapped_column(
        sa.Integer, name='year', primary_key=True)
    month: so.Mapped[Optional[int]] = so.mapped_column(
        sa.Integer, name='month', primary_key=True)

    resource: so.Mapped[Optional[float]] = so.mapped_column(
        sa.Double, name='summ_res')
    restrictions: so.Mapped[Optional[float]
                            ] = so.mapped_column(sa.Double, name='ogr') # !
    leftovers: so.Mapped[Optional[float]
                         ] = so.mapped_column(sa.Double, name='ost') # !
    plan: so.Mapped[Optional[float]
                         ] = so.mapped_column(sa.Double, name='plan') # !

    shipping_basis: so.Mapped['ShippingBasisDictModel'] = relationship(
        "ShippingBasisDictModel")
    product: so.Mapped['ProductDictModel'] = relationship("ProductDictModel")


    # shipment: so.Mapped['ShipmentsModel'] = relationship("ShipmentsModel", 
    #                                                      secondaryjoin=lambda: 
    #                                                         AllResourceModel.shipping_basis_id==ShipmentsModel.shipping_basis_id and
    #                                                         AllResourceModel.product_id==ShipmentsModel.product_id and
    #                                                         AllResourceModel.month==ShipmentsModel.month and
    #                                                         AllResourceModel.year==ShipmentsModel.year
    #                                                      )

# TODO! добавить первичный ключ(


class ShipmentsModel(Base):  # Таблица Отгрузки ('tab_dataset_bk')
    __tablename__ = 'tab_dataset_bk'
    id: so.Mapped[Optional[str]] = so.mapped_column(sa.String, name='id', primary_key=True)
    # Дата
    year: so.Mapped[Optional[int]] = so.mapped_column(
        sa.Integer, name='year')#, primary_key=True)
    month: so.Mapped[Optional[int]] = so.mapped_column(
        sa.Integer, name='month')#, primary_key=True)

    value: so.Mapped[Optional[float]] = so.mapped_column(
        sa.Double, name='value')
    cost: so.Mapped[Optional[float]] = so.mapped_column(sa.Double, name='cost')
    cost_x_value: so.Mapped[Optional[float]] = so.mapped_column(
        sa.Double, name='cost_x_value')
    all_resource: so.Mapped[Optional[float]] = so.mapped_column(sa.Double,              # требуется распределить (весь ресурс)
                                                                name='all_resourse')  # TODO! CHECK ON DEV
    before_deal_resource: so.Mapped[Optional[float]] = so.mapped_column(sa.Double,      # требуется распределить (остаток ресурса до заявки)
                                                                        name='resourсe_before_zayav')
    accepted_deal: so.Mapped[Optional[float]] = so.mapped_column(sa.Double,      # принято по заявке
                                                                 name='accept_zayav')
    after_deal_resource: so.Mapped[Optional[float]] = so.mapped_column(sa.Double,      # остаток от ресурса после заявки
                                                                       name='ost_resource_after_zayav')
    left_resource: so.Mapped[Optional[float]] = so.mapped_column(sa.Double,      # остаток от заявки
                                                                 name='ost_zayav')
    total_cost: so.Mapped[Optional[float]] = so.mapped_column(sa.Double,      # Цена * объем принятый
                                                              name='cos_x_value')
    value_exchange: so.Mapped[Optional[float]] = so.mapped_column(sa.Double,      # Биржа
                                                                  name='value_birga')

    comment: so.Mapped[Optional[str]] = so.mapped_column(
        sa.String(255), name='comment')
    restrictions: so.Mapped[Optional[float]
                            ] = so.mapped_column(sa.Double, name='ogr') # !
    leftovers: so.Mapped[Optional[float]
                         ] = so.mapped_column(sa.Double, name='ost') # !
    plan: so.Mapped[Optional[float]
                         ] = so.mapped_column(sa.Double, name='plan') # !
    # Foreign keys
    record_owner_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                 sa.ForeignKey(
                                                                     'tab_owner_bk.id'),
                                                                 name='tab_owner_bk_ids',
                                                                 primary_key=True)
    shipping_basis_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                   sa.ForeignKey(
                                                                       'tab_bazis_bk.id'),
                                                                   name='tab_bazis_bk_ids',
                                                                   primary_key=True)
    product_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                            sa.ForeignKey(
                                                                'tab_product_bk.id'),
                                                            name='tab_product_bk_ids',
                                                            primary_key=True)
    unit_id: so.Mapped[int] = so.mapped_column(sa.Integer,
                                               sa.ForeignKey('tab_ei_bk.id'),
                                               name='tab_ei_bk_ids',
                                               nullable=True)
    trans_dir_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                              sa.ForeignKey(
                                                                  'tab_napr_real_bk.id'),
                                                              name='tab_napr_real_bk_ids')
    agent_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                          sa.ForeignKey(
                                                              'tab_proizv_bk.id'),
                                                          name='tab_proizv_bk_ids')
    product_owner_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                  sa.ForeignKey(
                                                                      'tab_sobstv_bk.id'),
                                                                  name='tab_sobstv_bk_ids')
    transport_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                              sa.ForeignKey(
                                                                  'tab_type_otgruz_bk.id'),
                                                              name='tab_type_otgruz_bk_ids')
    deal_category_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                  sa.ForeignKey(
                                                                      'tab_category_sd_bk.id'),
                                                                  name='tab_category_sd_bk_ids')
    destination_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                sa.ForeignKey(
                                                                    'tab_point_to_bk.id'),
                                                                name='tab_point_to_bk_ids')
    client_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                           sa.ForeignKey(
                                                               'tab_pokup_bk.id'),
                                                           name='tab_pokup_bk_ids')
    deal_status_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                sa.ForeignKey(
                                                                    'tab_status_sd_bk.id'),
                                                                name='tab_status_sd_bk_ids')
    product_category_id: so.Mapped[int] = so.mapped_column(sa.Integer,
                                                           sa.ForeignKey(
                                                               'tab_category_product_bk.id'),
                                                           name='tab_category_product_bk_ids',
                                                           nullable=True)
    deal_type_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                              sa.ForeignKey(
                                                                  'tab_type_sd_bk.id'),
                                                              name='tab_type_sd_bk_ids')
    distr_channel_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                  sa.ForeignKey(
                                                                      'tab_kanal_sb_bk.id'),
                                                                  name='tab_kanal_sb_bk_ids')
    trans_application_id: so.Mapped[Optional[int]] = so.mapped_column(sa.Integer,
                                                                      sa.ForeignKey(
                                                                          'tab_zayav_real_bk.id'),
                                                                      name='id_zayav_real')

    record_owner: so.Mapped['RecordOwnerDictModel'] = relationship(
        "RecordOwnerDictModel")
    shipping_basis: so.Mapped['ShippingBasisDictModel'] = relationship(
        "ShippingBasisDictModel")
    product: so.Mapped['ProductDictModel'] = relationship("ProductDictModel")
    unit: so.Mapped['UnitDictModel'] = relationship("UnitDictModel")
    trans_dir: so.Mapped['TransDirDictModel'] = relationship(
        "TransDirDictModel")
    agent: so.Mapped['AgentDictModel'] = relationship("AgentDictModel")
    product_owner: so.Mapped['ProductOwnerDictModel'] = relationship(
        "ProductOwnerDictModel")
    transport: so.Mapped['TransportDictModel'] = relationship(
        "TransportDictModel")
    deal_category: so.Mapped['DealCategoryDictModel'] = relationship(
        "DealCategoryDictModel")
    destination: so.Mapped['DestinationDictModel'] = relationship(
        "DestinationDictModel")
    client: so.Mapped['ClientDictModel'] = relationship("ClientDictModel")
    deal_status: so.Mapped['DealStatusDictModel'] = relationship(
        "DealStatusDictModel")
    product_category: so.Mapped['ProductCategoryDictModel'] = relationship(
        "ProductCategoryDictModel")
    deal_type: so.Mapped['DealTypeDictModel'] = relationship(
        "DealTypeDictModel")
    distr_channel: so.Mapped['DistrChannelDictModel'] = relationship(
        "DistrChannelDictModel")
    trans_application: so.Mapped['TransApplicationModel'] = relationship(
        "TransApplicationModel")


    # resource: so.Mapped['AllResourceModel'] = relationship("AllResourceModel", 
    #                                                      primaryjoin=lambda: 
    #                                                         AllResourceModel.shipping_basis_id==ShipmentsModel.shipping_basis_id and
    #                                                         AllResourceModel.product_id==ShipmentsModel.product_id and
    #                                                         AllResourceModel.month==ShipmentsModel.month and
    #                                                         AllResourceModel.year==ShipmentsModel.year
    #                                                      )