from sqlalchemy.orm import scoped_session
from app.repositories.plan_repository import PlanRepository
from app.repositories.recalculate_repository import RecalculateRepository
from app.entities.schemas import LimitUpdateSchema, create_limit_schema, create_limits_update_schema #, create_plan_update_schema, PlanUpdateSchema

        
class LimitService:
    def __init__(self, session: scoped_session):
        self.limit_repository = PlanRepository(session)
        self.recalculate_repository = RecalculateRepository(session)
    
    def get_data(self, args):
            
        # Получаем заявки из БД
        limit_list = self.limit_repository.get_all('limit', **args)
        
        # Сериализуем в JSON
        result = create_limit_schema(limit_list)
    
        return result
    
    def update_data(self, limitsUpdate:LimitUpdateSchema):
        try:
            limits = self.limit_repository.update(limitsUpdate)
            result = create_limits_update_schema(limits)

            # recalculate
            data = self.limit_repository.get_by_id(id=limits[0]["id"])
            self.recalculate_repository.recalculate(data.year)
            
        except Exception as err:
            raise

        return result