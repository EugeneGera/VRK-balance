import math
from marshmallow import post_dump, pre_dump, fields, Schema, pre_load, missing, validate, ValidationError, validates
from typing import Dict, List, Type, Union

from app.entities.utils import MonthField, RoundedFloat
from app.utils import round_to_significant, MONTHS

# Кастомное поле Float с автоматическим округлением до первого значащего разряда


class RoundedFloat(fields.Float):
    def __init__(self, *args, **kwargs):
        self._round_grade = kwargs.pop('round_grade', None)
        self._zero_to_none = kwargs.pop('zero_to_none', False)
        self._none_to_zero = kwargs.pop('none_to_zero', False)
        self._inverse = kwargs.pop('inverse', False)
        self._abs = kwargs.pop('is_abs', False)

        self.is_optional = kwargs.pop('is_optional', False)


        super(RoundedFloat, self).__init__(*args, **kwargs) 

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None and self.is_optional:
            return missing
        
        if value is not None:
            value = round_to_significant(value)
        if self._zero_to_none:
            value = None if value == 0 else value
        if self._none_to_zero:
            value = 0 if value is None else value

        if self._inverse and value is not None:
            value *= -1
        if self._abs and value is not None:
            value = abs(value)

        return super()._serialize(value, attr, obj, **kwargs)

def create_list_schema(field_name: str, item_type: Type[fields.Field] = fields.String) -> type:
    DynamicListSchema = Schema.from_dict(
        {
            field_name: fields.List(item_type),
        })

    return DynamicListSchema

# class GradedRoundificationSchema(Schema):
#     def __init__(self, *args, **kwargs):
#         self.round_grade = kwargs.pop('round_grade') if 'round_grade' in kwargs else None
#         super(Schema, self).__init__(*args, **kwargs)

products_list_schema = create_list_schema(field_name='products')()
category_products_list_schema = create_list_schema(field_name='category_product')()
basises_list_schema = create_list_schema(field_name='shipping_basises')()

class SankeySingularFlowSchema(Schema):
    source = fields.String(allow_none=False, missing=None)
    target = fields.String(allow_none=False, missing=None)
    target_kind = fields.String(allow_none=True, missing=None)
    value = RoundedFloat(allow_none=True)
    # , validate=validate.OneOf(['заводы', 'розница'],
    kind = fields.String(allow_none=False, missing=None)
    # error="Kind must be either 'заводы' or 'розница'")
    # )
    price = RoundedFloat(allow_none=True)
    volume_left = RoundedFloat(allow_none=True)
    unit = fields.String(allow_none=True)
    shipping_basis = fields.String(allow_none=True)

    @pre_load
    def process_volume_left(self, data, **kwargs):
        if 'volume_left' in data and data['volume_left'] is not None:
            data['volume_left'] = max(0, data['volume_left'])
        return data


class SankeyDataSchema(Schema):
    data = fields.List(fields.Nested(
        SankeySingularFlowSchema), allow_none=True)
    products = fields.String(allow_none=True, missing=None)
    trans_dirs = fields.List(fields.String)

    @pre_load
    def clear_empty_flows(self, sch, **kwargs):
        if all(flow['value'] is None for flow in sch['data']):
            sch['data'] = []
        return sch


class MonthField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        try:
            value = int(value)
        except Exception:
            raise ValidationError("Month must be number")
        try:
            return MONTHS[value - 1]
        except IndexError:
            raise ValidationError("Month must be between 1 and 12")

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, int):
            return value
        try:
            return MONTHS.index(value) + 1
        except ValueError:
            raise ValidationError(
                f"Invalid month name. Must be one of: {MONTHS}")


# Application schema
class TransApplicationSchema(Schema):
    id = fields.Int(dump_only=True)
    owner = fields.Function(
        lambda obj: obj.owner.name if obj.owner else "", allow_none=True, required=False)
    year = fields.Int()
    month = MonthField(attribute="month")

    shipmentBasis = fields.String(attribute="shipping_basis.name",
                                  allow_none=True, required=False, dump_default="-", missing="-")
    product = fields.String(attribute="product.name", allow_none=True,
                            required=False, dump_default="-", missing="-")
    unit = fields.String(attribute="unit.name", allow_none=True,
                         required=False, dump_default="-", missing="-")
    direction = fields.String(attribute="trans_dir.name", allow_none=True,
                              required=False, dump_default="-", missing="-")
    agentManufacturer = fields.String(
        attribute="agent.name", allow_none=True, required=False, dump_default="-", missing="-")
    productOwner = fields.String(attribute="product_owner.name",
                                 allow_none=True, required=False, dump_default="-", missing="-")
    shipmentMethod = fields.String(
        attribute="transport.name", allow_none=True, required=False, dump_default="-", missing="-")
    dealCategory = fields.String(attribute="deal_category.name",
                                 allow_none=True, required=False, dump_default="-", missing="-")
    destinationStation = fields.String(
        attribute="destination.name", allow_none=True, required=False, dump_default="-", missing="-")
    buyer = fields.String(attribute="client.name", allow_none=True,
                          required=False, dump_default="-", missing="-")
    dealStatus = fields.String(attribute="deal_status.name",
                               allow_none=True, required=False, dump_default="-", missing="-")

    applicationSize = RoundedFloat(attribute="value", digits=1)
    price = RoundedFloat(attribute="cost", digits=1)

    remark = fields.String(attribute="comment")

    class Meta:
        ordered = True
        render_none = True  # Всегда включать None-поля в вывод


def create_application_schema(application_list) -> type:
    return {'applications': TransApplicationSchema(many=True).dump(application_list)}


class ApplicationUpdateSchema(Schema):

    id = fields.Int(required=True, validate=lambda x: x > 0,
                    error_messages={"required": "ID is required",
                                    "validator_failed": "ID must be greater than zero"})

    applicationSize = fields.Float(attribute="value")
    price = fields.Float(attribute="cost")
    # min_left = fields.Float(attribute="min_left")
    # max_shipment = fields.Float(attribute="max_shipment")

    # resource = fields.Float(attribute="resource")
    # percent_exchange = fields.Float(attribute="percent_exchange")
    # value_exchange = fields.Float(attribute="value_exchange")

    remark = fields.String(attribute="comment")


def create_application_update_schema(plan) -> type:
    return {'application': ApplicationUpdateSchema().dump(plan)}


def create_applications_update_schema(plan) -> type:
    return {'applications': ApplicationUpdateSchema(many=True).dump(plan)}

# class ApplicationUpdateSchema(Schema):

#     id = fields.Int(required=True, validate=lambda x: x > 0,
#                         error_messages={"required": "ID is required",
#                                         "validator_failed": "ID must be greater than zero"})

#     applicationSize = fields.Float(attribute="value")
#     price = fields.Float(attribute="cost")

# def create_application_update_schema(application) -> type:
#     return {'application': ApplicationUpdateSchema().dump(application)}

# Plan schema


class PlanSchema(Schema):
    id = fields.Int(dump_only=True)

    year = fields.Int()
    month = MonthField(attribute="month")

    shipmentBasis = fields.String(attribute="shipping_basis.name",
                                  allow_none=True, required=False, dump_default="-", missing="-")
    product = fields.String(attribute="product.name", allow_none=True,
                            required=False, dump_default="-", missing="-")
    unit = fields.String(attribute="unit.name", allow_none=True,
                         required=False, dump_default="-", missing="-")
    agentManufacturer = fields.String(
        attribute="agent.name", allow_none=True, required=False, dump_default="-", missing="-")
    productOwner = fields.String(attribute="product_owner.name",
                                 allow_none=True, required=False, dump_default="-", missing="-")

    plan = RoundedFloat(attribute="plan", digits=1)

    remark = fields.String(attribute="comment")

    class Meta:
        ordered = True
        render_none = True  # Всегда включать None-поля в вывод


def create_plan_schema(plan_list) -> type:
    return {'plans': PlanSchema(many=True).dump(plan_list)}


class PlanUpdateSchema(Schema):

    id = fields.Int(required=True, validate=lambda x: x > 0,
                    error_messages={"required": "ID is required",
                                    "validator_failed": "ID must be greater than zero"})

    # left = fields.Float(attribute="left")
    plan = fields.Float(attribute="plan")
    # min_left = fields.Float(attribute="min_left")
    # max_shipment = fields.Float(attribute="max_shipment")

    resource = fields.Float(attribute="resource")
    # percent_exchange = fields.Float(attribute="percent_exchange")
    # value_exchange = fields.Float(attribute="value_exchange")

    remark = fields.String(attribute="comment")


def create_plan_update_schema(plan) -> type:
    return {'plan': PlanUpdateSchema().dump(plan)}


def create_plans_update_schema(plan) -> type:
    return {'plans': PlanUpdateSchema(many=True).dump(plan)}

# Leftover schema


class LeftoverSchema(Schema):
    id = fields.Int(dump_only=True)

    year = fields.Int()
    month = MonthField(attribute="month")

    shipmentBasis = fields.String(attribute="shipping_basis.name",
                                  allow_none=True, required=False, dump_default="-", missing="-")
    product = fields.String(attribute="product.name", allow_none=True,
                            required=False, dump_default="-", missing="-")
    unit = fields.String(attribute="unit.name", allow_none=True,
                         required=False, dump_default="-", missing="-")
    agentManufacturer = fields.String(
        attribute="agent.name", allow_none=True, required=False, dump_default="-", missing="-")
    productOwner = fields.String(attribute="product_owner.name",
                                 allow_none=True, required=False, dump_default="-", missing="-")

    left = RoundedFloat(attribute="left", digits=1)
    # plan = RoundedFloat(attribute="plan", digits=1)
    # min_left = RoundedFloat(attribute="min_left", digits=1)
    # max_shipment = RoundedFloat(attribute="max_shipment", digits=1)
    # resource = RoundedFloat(attribute="resource", digits=1)
    # percent_exchange = RoundedFloat(attribute="percent_exchange", digits=1)
    # value_exchange = RoundedFloat(attribute="value_exchange", digits=1)

    remark = fields.String(attribute="comment_ost")

    class Meta:
        ordered = True
        render_none = True  # Всегда включать None-поля в вывод


def create_leftover_schema(leftover_list) -> type:
    return {'leftovers': LeftoverSchema(many=True).dump(leftover_list)}


class LeftoverUpdateSchema(Schema):

    id = fields.Int(required=True, validate=lambda x: x > 0,
                    error_messages={"required": "ID is required",
                                    "validator_failed": "ID must be greater than zero"})

    left = fields.Float(attribute="left")
    # plan = fields.Float(attribute="plan")
    # min_left = fields.Float(attribute="min_left")
    # max_shipment = fields.Float(attribute="max_shipment")

    # resource = fields.Float(attribute="resource")
    # percent_exchange = fields.Float(attribute="percent_exchange")
    # value_exchange = fields.Float(attribute="value_exchange")

    remark = fields.String(attribute="comment_ost")


def create_leftover_update_schema(plan) -> type:
    return {'leftover': LeftoverUpdateSchema().dump(plan)}


def create_leftovers_update_schema(plan) -> type:
    return {'leftovers': LeftoverUpdateSchema(many=True).dump(plan)}

# Limit schema


class LimitSchema(Schema):
    id = fields.Int(dump_only=True)

    year = fields.Int()
    month = MonthField(attribute="month")

    shipmentBasis = fields.String(attribute="shipping_basis.name",
                                  allow_none=True, required=False, dump_default="-", missing="-")
    product = fields.String(attribute="product.name", allow_none=True,
                            required=False, dump_default="-", missing="-")
    unit = fields.String(attribute="unit.name", allow_none=True,
                         required=False, dump_default="-", missing="-")
    agentManufacturer = fields.String(
        attribute="agent.name", allow_none=True, required=False, dump_default="-", missing="-")
    productOwner = fields.String(attribute="product_owner.name",
                                 allow_none=True, required=False, dump_default="-", missing="-")

    min_left = RoundedFloat(attribute="min_left", digits=1)
    min_remark = fields.String(attribute="comment_min_ost",
                               allow_none=True, required=False, dump_default="", missing="")
    max_shipment = RoundedFloat(attribute="max_shipment", digits=1)
    max_remark = fields.String(attribute="comment_max_otgr",
                               allow_none=True, required=False, dump_default="", missing="")

    # remark = fields.String(attribute="comment")

    class Meta:
        ordered = True
        render_none = True  # Всегда включать None-поля в вывод


def create_limit_schema(limit_list) -> type:
    return {'limits': LimitSchema(many=True).dump(limit_list)}


class LimitUpdateSchema(Schema):

    id = fields.Int(required=True, validate=lambda x: x > 0,
                    error_messages={"required": "ID is required",
                                    "validator_failed": "ID must be greater than zero"})

    min_left = fields.Float(attribute="min_left")
    min_remark = fields.String(attribute="comment_min_ost")
    max_shipment = fields.Float(attribute="max_shipment")
    max_remark = fields.String(attribute="comment_max_otgr")

    # resource = fields.Float(attribute="resource")
    # percent_exchange = fields.Float(attribute="percent_exchange")
    # value_exchange = fields.Float(attribute="value_exchange")

    remark = fields.String(attribute="comment")


def create_limit_update_schema(plan) -> type:
    return {'limit': LimitUpdateSchema().dump(plan)}


def create_limits_update_schema(plan) -> type:
    return {'limits': LimitUpdateSchema(many=True).dump(plan)}

# Схемы для детализации по бирже, транспорту и базисам

class TypeValueDetailsSchema(Schema):
    type = fields.String(allow_none=True, missing=None)
    value = RoundedFloat(allow_none=True)
    category = fields.String(allow_none=True, missing=None)
    delta = RoundedFloat(allow_none=True, missing=None)
    percent = RoundedFloat(allow_none=True)
    restrictions = RoundedFloat(allow_none=True)

    # waterfall
    name = fields.String(allow_none=True)
    claim = RoundedFloat(allow_none=False, is_optional=True)
    plan = RoundedFloat(allow_none=True)
    leftovers = RoundedFloat(allow_none=True)
    available = RoundedFloat(allow_none=True)
    need = RoundedFloat(allow_none=True)




class FactoryDetailsSchema(Schema):
    factory_name = fields.String(allow_none=False)
    transports = fields.List(fields.Nested(TypeValueDetailsSchema))


class TransportDetailsSchema(Schema):
    total = fields.List(fields.Nested(TypeValueDetailsSchema))
    factories = fields.List(fields.Nested(
        FactoryDetailsSchema), allow_none=True)


class DetalisationUnionField(fields.Field):
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return TypeValueDetailsSchema(many=True).load(value)
        except ValidationError:
            pass

        try:
            return TransportDetailsSchema(many=True).load(value)
        except ValidationError:
            raise ValidationError(
                "Data must match StockMarketChannelsDetailsSchema or TransportDetailsSchema schema")


class MonthDetailsSchema(Schema):
    month = MonthField(allow_none=False)
    value = RoundedFloat(allow_none=True)
    detalization = DetalisationUnionField()


# детализации по бирже и транспорту
month_details_list_schema = create_list_schema(
    field_name='months', item_type=fields.Nested(MonthDetailsSchema))()


# Детализация по заводам
class FactoryLeftoverDataSchema(Schema):
    factory_name = fields.Str(allow_none=False, missing=None)
    leftovers = fields.List(fields.Nested(TypeValueDetailsSchema))


class FactoryDetailsSchema(Schema):
    #pie_data = fields.List(fields.Nested(TypeValueDetailsSchema))
    pie_left_plan_data = fields.List(fields.Nested(TypeValueDetailsSchema))
    pie_resource_restriction = fields.List(fields.Nested(TypeValueDetailsSchema))
    pie_progress_application = fields.Nested(TypeValueDetailsSchema)
    pie_progress_delta = fields.Nested(TypeValueDetailsSchema)
    total_percent = fields.Nested(TypeValueDetailsSchema)
    pie_progress_data = fields.Nested(TypeValueDetailsSchema)
    factory_leftover_data = fields.List(
        fields.Nested(FactoryLeftoverDataSchema))
    unit = fields.String(allow_none=True)



######### STOCK DETAILS SCHEMAS
class DataPieceSchema(Schema):
    type = fields.String()
    value = RoundedFloat(round_grade = 2, zero_to_none=True)
    category = fields.String()

class StockDetailsMonthDetailsSchema(Schema):
    month = MonthField()
    data = fields.List(fields.Nested(DataPieceSchema))

class StockDetailsSchema(Schema):
    percent = fields.List(fields.Nested(StockDetailsMonthDetailsSchema))
    absolute = fields.List(fields.Nested(StockDetailsMonthDetailsSchema))


######### WATERFALL
class WaterfallTypeValueDetailsSchema(Schema):
    value = RoundedFloat(none_to_zero=True, missing=None, inverse=True, round_grade=2)
    restrictions = RoundedFloat(allow_none=True, missing=None)

    # waterfall
    name = fields.String(allow_none=True)
    claim = RoundedFloat(allow_none=False, is_optional=True, round_grade=2, is_abs=True)
    plan = RoundedFloat(allow_none=True, missing=None, round_grade=2)
    leftovers = RoundedFloat(allow_none=True, missing=None, round_grade=2)
    available = RoundedFloat(allow_none=True, missing=None, round_grade=2)
    need = RoundedFloat(none_to_zero=True, missing=None, round_grade=2)

# class DistributionField(fields.List):
#     def _serialize(self, value, attr, obj, **kwargs):
#         if not value:
#             return missing
        
#         filtered_value = []
#         for item in value:
#             item_value = item.get('value', None) if isinstance(item, dict) else getattr(item, 'value', None)
#             item_claim = item.get('claim', None) if isinstance(item, dict) else getattr(item, 'claim', None)
            
#             # print(f'serializing: {item_value} {item_claim}')
#             all_none = True
#             if (item_value is not None and item_value is not missing):
#                 item['value'] *= -1
#                 all_none = False
#             if (item_claim is not None and item_claim is not missing):
#                 # item['claim'] *= -1
#                 all_none = False
#             if not all_none:#(item_value is not None and item_value is not missing) or (item_claim is not None and item_claim is not missing):
#             #    item['value'] *= -1
#             #    item['claim'] *= -1
#                filtered_value.append(item)
        
#         # if not filtered_value:
#         #     return missing
        
#         return super()._serialize(filtered_value, attr, obj, **kwargs)

class WaterfallDataSchema(Schema):
    # TODO! add 'total' for serialization
    # name = fields.String(default='Total')
    total = fields.Nested(WaterfallTypeValueDetailsSchema, default={'plan': None, 'leftovers': None})
    available_resource = fields.Nested(WaterfallTypeValueDetailsSchema,default={'available': None, 'restriction': None})
    distribution = fields.List(fields.Nested(WaterfallTypeValueDetailsSchema), default=[{'Внутренний рынок': {'value': 0}}, {'Экспорт': {'value': 0}}, {'Нужды ДО': {'value': 0}}])
    resource_leftover = fields.Nested(WaterfallTypeValueDetailsSchema, default={'leftovers': None})
    need = fields.Nested(WaterfallTypeValueDetailsSchema, default={'need': None})

    @post_dump
    def remove_none_fields(self, data, **kwargs):
        return {k: v for k, v in data.items() if v is not missing}


class WaterfallSchema(Schema):
    name = fields.String(default='Total')
    data = fields.Nested(WaterfallDataSchema)

# class WaterfallListSchema(Schema):