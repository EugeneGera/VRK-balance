from sqlalchemy.orm import scoped_session
from app.repositories.plan_repository import PlanRepository
from app.repositories.recalculate_repository import RecalculateRepository
from app.entities.schemas import create_plan_schema, create_plans_update_schema, PlanUpdateSchema

        
class PlanService:
    def __init__(self, session: scoped_session):
        self.plan_repository = PlanRepository(session)
        self.recalculate_repository = RecalculateRepository(session)
    
    def get_data(self, args):
            
        # Получаем заявки из БД
        plan_list = self.plan_repository.get_all('plan', **args)
        
        # Сериализуем в JSON
        result = create_plan_schema(plan_list)
    
        return result
    
    def update_data(self, plansUpdate:PlanUpdateSchema):

        try:
            plans = self.plan_repository.update(plansUpdate)
            result = create_plans_update_schema(plans)

            # recalculate
            data = self.plan_repository.get_by_id(id=plans[0]["id"])
            self.recalculate_repository.recalculate(data.year)

        except Exception as err:
            raise

        return result
    
    #  def update_data(self, plansUpdate:PlanUpdateSchema):

    #     try:
    #         plan = self.plan_repository.update(**planUpdate)
    #         result = create_plan_update_schema(plan)
    #     except Exception as err:
    #         raise

    #     return result