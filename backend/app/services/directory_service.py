from sqlalchemy.orm import scoped_session

from app.entities.models import AgentDictModel, ClientDictModel, DealCategoryDictModel, DealStatusDictModel, DealTypeDictModel, DestinationDictModel, DistrChannelDictModel, OrgDictModel, ProductCategoryDictModel, ProductDictModel, ProductOwnerDictModel, RecordOwnerDictModel, ShippingBasisDictModel, TransDirDictModel, TransportDictModel
from app.repositories.base_dict_repository import DictRepository


class DirectoryService:
    def __init__(self, session: scoped_session):
        self.session = session

        self.redactable_dicts_models = [
            ShippingBasisDictModel,
            ProductDictModel,
            ProductCategoryDictModel,
            DealCategoryDictModel,
            DistrChannelDictModel,
            TransDirDictModel,
            AgentDictModel,
            RecordOwnerDictModel,
            OrgDictModel,
            ClientDictModel,
            ProductOwnerDictModel,
            TransportDictModel,
            DestinationDictModel,
            DealStatusDictModel,
            DealTypeDictModel,
        ]

    def get_directories_list(self):
        directories = [
            {
                "table_id": model.__tablename__,
                "table_name": model.tablename_cyr,
                "fields_count": DictRepository(model=model, session=self.session).get_none_empty_records_count()
            }
            for model in self.redactable_dicts_models
        ]
        return {"directories": directories}

    def get_directory_by_tablename(self, id):
        directory = self.find_current_table_by_name(id)
        return directory

    def make_formated_fields(self, results):
        return [
            {"id": result.id, "name": getattr(
                result, "name", "Unknown")}
            for result in results
            if getattr(result, "name", None) and getattr(result, "name", "") != ""
        ]

    def find_current_table_by_name(self, tablename):
        try:
            for model in self.redactable_dicts_models:
                if model.__tablename__ == tablename:
                    data = DictRepository(
                        model=model, session=self.session).get_all_id_name()
                    return {
                        "table_name": model.__tablename__,
                        "fields": [
                            {"id": record.id, "name": getattr(
                                record, "name", "Unknown")}
                            for record in data
                        ],
                    }
            return {"error": f"Table '{tablename}' not found"}, 404
        except Exception as e:
            return {"error": f"Error retrieving table data: {str(e)}"}, 400

    def find_model_by_tablename(self, tablename):
        for model in self.redactable_dicts_models:
            if model.__tablename__ == tablename:
                result = model
                return result

    def update_directory(self, tablename, objs):
        try:
            model = self.find_model_by_tablename(tablename)
            repo = DictRepository(model=model, session=self.session)
            for obj in objs:
                if not obj.get("name") or obj["name"].strip() == "":
                    raise ValueError(
                        f"Поле name не может быть пустым для объекта с id {obj['id']}")
                repo.update_by_id(obj["id"], obj)

            self.session.commit()

            return "Успешно"
        except Exception as e:
            raise
