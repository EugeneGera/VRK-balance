from sqlalchemy.orm import scoped_session
from app.repositories.application_repository import ApplicationRepository
from app.repositories.recalculate_repository import RecalculateRepository
from app.entities.schemas import create_application_schema, create_applications_update_schema, ApplicationUpdateSchema

        
class ApplicationService:
    def __init__(self, session: scoped_session):
        self.application_repository = ApplicationRepository(session)
        self.recalculate_repository = RecalculateRepository(session)
    
    def get_data(self, args):
        # filters = args.copy()#{}
        # filters['months'] = list(range(args['month_start'], args['month_end'] + 1))
            
        # Получаем заявки из БД
        application_list = self.application_repository.get_all(**args)
        
        # Сериализуем в JSON
        result = create_application_schema(application_list)
    
        return result
    
    def update_data(self, applicationsUpdate:ApplicationUpdateSchema):
        try:
            applications = self.application_repository.update(applicationsUpdate)
            result = create_applications_update_schema(applications)

            # recalculate
            data = self.application_repository.get_by_id(id=applications[0]["id"])
            self.recalculate_repository.recalculate(data.year)

        except Exception as err:
            raise

        return result
    
    # def update_data(self, applicationUpdate:ApplicationUpdateSchema):

    #     try:
    #         application = self.application_repository.update(**applicationUpdate)
    #         result = create_application_update_schema(application)
    #     except Exception as err:
    #         raise

    #     return result