from typing import Any, Dict, Generic, Optional, Protocol, Type, TypeVar, Union

from django.db.models import Model
from django.db.models.query import QuerySet
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request

from core.exceptions import ObjectInvalidException, ObjectNotFoundException
from core.serializers import BaseSerializer

ModelType = TypeVar("ModelType", bound=Model)
CreateSerializer = TypeVar("CreateSerializer", bound=BaseSerializer)
UpdateSerializer = TypeVar("UpdateSerializer", bound=BaseSerializer)


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

    def on_pre_delete(self, obj: ModelType) -> None:
        pass


class CreateService(Generic[ModelType, CreateSerializer]):
    def __init__(self, model: Type[ModelType]) -> None:
        self.model = model

    def create(
        self: Union[Any, ServiceInterface],
        *,
        obj_data: Dict[str, Any],
        serializer: Type[CreateSerializer],
    ) -> ModelType:
        obj_in = serializer(data_in=obj_data, data=obj_data)
        if not obj_in.is_valid(raise_exception=False):
            raise ObjectInvalidException("Event")
        if hasattr(self, "on_pre_create"):
            self.on_pre_create(obj_in)
        obj = self.model.objects.create(**obj_in.validated_data)
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
        self,
        *,
        obj_data: Dict[str, Any],
        serializer: Type[UpdateSerializer],
        obj_id: Union[str, int],
    ) -> ModelType:
        obj_in = serializer(data_in=obj_data, data=obj_data)
        if not obj_in.is_valid(raise_exception=False):
            raise ObjectInvalidException(f"{self.model.__name__}")
        try:
            obj = self.model.objects.get(pk=obj_id)
        except self.model.DoesNotExist:
            raise ObjectNotFoundException(
                model=f"{self.model.__name__}", pk=str(obj_id)
            )
        if hasattr(self, "on_pre_update"):
            self.on_pre_update(obj_in)
        self.model.objects.filter(pk=obj_id).update(**obj_in.validated_data)
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

    def remove(self, *, obj_id: Union[str, int]) -> None:
        try:
            obj = self.model.objects.get(pk=obj_id)
        except self.model.DoesNotExist:
            raise ObjectNotFoundException(
                model=f"{self.model.__name__}", pk=str(obj_id)
            )
        if hasattr(self, "on_pre_delete"):
            self.on_pre_delete(obj)
        obj.delete()

    def on_pre_delete(self, obj: ModelType) -> None:
        pass


class ReadService(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, *, pk: Any) -> Optional[ModelType]:
        try:
            obj = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return None

        return obj

    def get_filtered(
        self,
        *,
        paginator: PageNumberPagination,
        request: Request,
        filters: Optional[dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> QuerySet[ModelType]:
        if filters:
            return self.model.objects.filter(**filters)[:limit]
        return self.model.objects.all()[:limit]


class CRUDService(
    CreateService[ModelType, CreateSerializer],
    ReadService[ModelType],
    UpdateService[ModelType, UpdateSerializer],
    DeleteService[ModelType],
):
    def __init__(self, model: Type[ModelType]) -> None:
        super().__init__(model)
