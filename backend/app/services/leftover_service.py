from sqlalchemy.orm import scoped_session
from app.repositories.plan_repository import PlanRepository
from app.repositories.recalculate_repository import RecalculateRepository
from app.entities.schemas import LeftoverUpdateSchema, create_leftover_schema, create_leftovers_update_schema #, create_plan_update_schema, PlanUpdateSchema

        
class LeftoverService:
    def __init__(self, session: scoped_session):
        self.leftover_repository = PlanRepository(session)
        self.recalculate_repository = RecalculateRepository(session)
    
    def get_data(self, args):
        # Получаем заявки из БД
        leftover_list = self.leftover_repository.get_all('leftover', **args)
        
        # Сериализуем в JSON
        result = create_leftover_schema(leftover_list)
    
        return result
    
    def update_data(self, leftoversUpdate:LeftoverUpdateSchema):

        try:
            leftovers = self.leftover_repository.update(leftoversUpdate)
            result = create_leftovers_update_schema(leftovers)

            # recalculate
            data = self.leftover_repository.get_by_id(id=leftovers[0]["id"])
            self.recalculate_repository.recalculate(data.year)
            
        except Exception as err:
            raise

        return result