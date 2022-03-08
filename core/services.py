from http import HTTPStatus
from typing import (
    Any,
    Dict,
    Generic,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    no_type_check,
)

from django.contrib.postgres.search import SearchQuery, SearchVector
from django.db.models import Model
from django.db.models.query import QuerySet
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request

from core.error_codes import ErrorCodes
from core.exceptions import (
    HttpErrorException,
    ObjectInvalidException,
    ObjectNotFoundException,
)
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

    def on_pre_create(self, obj_in: Dict[str, Any]) -> None:
        pass

    def on_post_create(self, obj: ModelType) -> None:
        pass

    def on_pre_update(self, obj_in: UpdateSerializer, obj: ModelType) -> None:
        pass

    def on_post_update(self, obj: ModelType) -> None:
        pass

    def on_pre_delete(self, obj: ModelType) -> None:
        pass

    def on_relationship(self, obj_in: UpdateSerializer, obj: ModelType) -> None:
        pass

    def on_relationship_update(self, obj_data: Dict[str, Any], obj: ModelType) -> None:
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
        if hasattr(self, "on_pre_create"):
            self.on_pre_create(obj_data)
        obj_in = serializer(data_in=obj_data, data=obj_data)
        if not obj_in.is_valid(raise_exception=False):
            raise ObjectInvalidException(self.model.__name__)
        obj = self.model.objects.create(**dict(obj_in.validated_data))
        if hasattr(self, "on_relationship"):
            self.on_relationship(obj_in=obj_in, obj=obj)
        if hasattr(self, "on_post_create"):
            self.on_post_create(obj)
        return obj

    def on_pre_create(self, obj_in: Dict[str, Any]) -> None:
        pass

    def on_post_create(self, obj: ModelType) -> None:
        pass

    def on_relationship(self, obj_in: UpdateSerializer, obj: ModelType) -> None:
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
        for key in list(obj_data.keys()):
            if key not in self.model.__dict__.keys():
                delattr(obj_data, key)

        try:
            obj = self.model.objects.get(pk=obj_id)
        except self.model.DoesNotExist:
            raise ObjectNotFoundException(
                model=f"{self.model.__name__}", pk=str(obj_id)
            )

        if hasattr(self, "on_relationship_update"):
            self.on_relationship_update(obj_data=obj_data, obj=obj)

        obj_in = serializer(data_in=obj_data, data=obj_data)
        if not obj_in.is_valid(raise_exception=False):
            raise ObjectInvalidException(f"{self.model.__name__}")

        if hasattr(self, "on_pre_update"):
            self.on_pre_update(obj_in, obj)

        self.model.objects.filter(pk=obj_id).update(**dict(obj_in.validated_data))
        obj = self.model.objects.get(pk=obj_id)
        if hasattr(self, "on_post_update"):
            self.on_post_update(obj)
        return obj

    def on_pre_update(self, obj_in: UpdateSerializer, obj: ModelType) -> None:
        pass

    def on_post_update(self, obj: ModelType) -> None:
        pass

    def on_relationship_update(self, obj_data: Dict[str, Any], obj: ModelType) -> None:
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
            return self.model.objects.filter(**filters).order_by("id")[:limit]
        return self.model.objects.all().order_by("id")[:limit]

    @no_type_check  # FIX
    def search(self, *, search_term: str) -> QuerySet[ModelType]:
        if hasattr(self.model, "search_vector") and len(self.model.search_vector) > 0:
            unpacked_vector = None
            for vector in self.model.search_vector:
                if self.model.search_vector.index(vector) == 0:
                    unpacked_vector = SearchVector(vector)
                    continue
                unpacked_vector += SearchVector(vector)
            query = SearchQuery(search_term)
            return (
                self.model.objects.annotate(search=unpacked_vector)
                .filter(search=query)
                .order_by("id")
            )
        else:
            raise HttpErrorException(
                status_code=HTTPStatus.BAD_REQUEST,
                code=ErrorCodes.TARGET_MODEL_HAS_NO_SEARCH_VECTOR,
            )


class CRUDService(
    CreateService[ModelType, CreateSerializer],
    ReadService[ModelType],
    UpdateService[ModelType, UpdateSerializer],
    DeleteService[ModelType],
):
    def __init__(self, model: Type[ModelType]) -> None:
        super().__init__(model)
