from typing import Any, Generic, List, Optional, Protocol, Type, TypeVar, Union

from django.db.models import Model
from rest_framework.serializers import Serializer

ModelType = TypeVar("ModelType", bound=Model)
CreateSerializer = TypeVar("CreateSerializer", bound=Serializer)
UpdateSerializer = TypeVar("UpdateSerializer", bound=Serializer)


class ServiceInterface(Protocol[ModelType]):
    model: ModelType

    def create(self, obj_in: CreateSerializer) -> ModelType:
        pass

    def get(self, id: Any) -> Optional[ModelType]:
        pass

    def on_pre_create(self, obj_in: CreateSerializer) -> None:
        pass

    def on_post_create(self, obj: ModelType) -> None:
        pass

    def on_pre_update(self, obj_in: UpdateSerializer) -> None:
        pass

    def on_post_update(self, obj: ModelType) -> None:
        pass


class CreateService(Generic[ModelType, CreateSerializer]):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    def create(
        self: Union[Any, ServiceInterface], *, obj_in: CreateSerializer
    ) -> ModelType:
        if hasattr(self, "on_pre_create"):
            self.on_pre_create(obj_in)
        obj = self.model(**obj_in.validated_data)
        if hasattr(self, "on_post_create"):
            self.on_post_create(obj)
        return obj

    def on_pre_create(self, obj_in: CreateSerializer) -> None:
        pass

    def on_post_create(self, obj: ModelType) -> None:
        pass


class UpdateService(Generic[ModelType, UpdateSerializer]):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    def update(
        self: Union[Any, ServiceInterface], *, obj: ModelType, obj_in: UpdateSerializer
    ) -> ModelType:
        if hasattr(self, "on_pre_update"):
            self.on_pre_update(obj_in)
        obj = self.model.objects.filter(pk=obj.pk).update(**obj_in.validated_data)
        if hasattr(self, "on_post_update"):
            self.on_post_update(obj)
        return obj

    def on_pre_update(self, obj_in: UpdateSerializer) -> None:
        pass

    def on_post_update(self, obj: ModelType) -> None:
        pass


class DeleteService(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def remove(self: Union[Any, ModelType], *, obj: ModelType):
        obj.delete()


class ReadService(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self: Union[Any, ModelType], *, pk: Any) -> Optional[ModelType]:
        try:
            obj = self.objects.get(pk=pk)
        except self.DoesNotExist:
            return None

        return obj

    def get_filtered(
        self: Union[Any, ModelType],
        *,
        filters: Optional[dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[ModelType]:
        if filters:
            return list(self.objects.filter(**filters)[:limit])
        return list(self.model.objects.all()[:limit])


class CRUDService(
    CreateService[ModelType, CreateSerializer],
    ReadService[ModelType],
    UpdateService[ModelType, UpdateSerializer],
    DeleteService[ModelType],
):
    def __init__(self, model: Type[ModelType]) -> None:
        super().__init__(model)
