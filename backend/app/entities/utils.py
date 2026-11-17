from marshmallow import fields, ValidationError
import math

from app.utils import round_to_significant

    
# Month
MONTHS = [ "Январь", "Февраль", "Март", "Апрель",
           "Май", "Июнь", "Июль", "Август", 
           "Сентябрь", "Октябрь", "Ноябрь", "Декабрь" ]

class MonthField(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
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
            raise ValidationError(f"Invalid month name. Must be one of: {MONTHS}")

# Rounded        
class RoundedFloat(fields.Float):
    def __init__(self, *args, digits=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.digits = digits

    def _format_num(self, value):
        # Округляем число до первого значащего десятичного символа
        #return round(value, len(str(int(value))) + 1)
        return round_to_significant(value, self.digits)

    def _serialize(self, value, attr, obj, **kwargs):
        rounded_value = self._format_num(value)
        return super()._serialize(rounded_value, attr, obj, **kwargs)