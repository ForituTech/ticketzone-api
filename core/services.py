import json
from http import HTTPStatus
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Protocol,
    Type,
    TypeVar,
    Union,
    no_type_check,
)

from django.contrib.postgres.search import SearchQuery, SearchVector
from django.core.exceptions import FieldError, ValidationError
from django.db.models import Model
from django.db.models.query import QuerySet
from rest_framework.exceptions import ValidationError as ValidationErrDRF
from rest_framework.pagination import PageNumberPagination

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

    def on_post_create(self, obj: ModelType, obj_in: Dict[str, Any]) -> None:
        pass

    def on_pre_update(self, obj_in: Dict[Any, Any], obj: ModelType) -> None:
        pass

    def on_post_update(self, obj: ModelType) -> None:
        pass

    def on_pre_delete(self, obj: ModelType) -> None:
        pass

    def on_relationship(
        self, obj_in: Dict[str, Any], obj: ModelType, create: bool = True
    ) -> None:
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
        obj_data_cleaned = obj_data.copy()
        for key in list(obj_data_cleaned.keys()):
            if key not in self.model.__dict__.keys() or isinstance(
                obj_data_cleaned[key], list
            ):
                del obj_data_cleaned[key]

        if hasattr(self, "on_pre_create"):
            self.on_pre_create(obj_data_cleaned)

        obj_in = serializer(data_in=obj_data.copy(), data=obj_data.copy())
        try:
            obj_in.is_valid(raise_exception=True)
        except ValidationErrDRF as exc:
            raise ObjectInvalidException(self.model.__name__, extra=str(exc))
        obj = self.model.objects.create(**obj_data_cleaned)

        obj.save()

        if hasattr(self, "on_relationship"):
            self.on_relationship(obj_in=obj_data, obj=obj, create=True)

        if hasattr(self, "on_post_create"):
            self.on_post_create(obj, obj_data)
        return obj

    def on_pre_create(self, obj_in: Dict[str, Any]) -> None:
        pass

    def on_post_create(self, obj: ModelType, obj_in: Dict[str, Any]) -> None:
        pass

    def on_relationship(
        self, obj_in: Dict[str, Any], obj: ModelType, create: bool = True
    ) -> None:
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
        obj_data_cleaned = obj_data.copy()
        for key in list(obj_data_cleaned.keys()):
            if key not in self.model.__dict__.keys() or isinstance(
                obj_data_cleaned[key], list
            ):
                del obj_data_cleaned[key]

        try:
            obj = self.model.objects.get(pk=obj_id)
        except self.model.DoesNotExist:
            raise ObjectNotFoundException(
                model=f"{self.model.__name__}", pk=str(obj_id)
            )

        if hasattr(self, "on_relationship"):
            self.on_relationship(obj_in=obj_data, obj=obj, create=False)

        obj_in = serializer(data_in=obj_data.copy(), data=obj_data.copy())
        try:
            obj_in.is_valid(raise_exception=True)
        except ValidationErrDRF as exc:
            raise ObjectInvalidException(f"{self.model.__name__}", extra=str(exc))

        if hasattr(self, "on_pre_update"):
            self.on_pre_update(obj_data_cleaned, obj)

        obj.save()
        self.model.objects.filter(pk=obj_id).update(**obj_data_cleaned)
        obj = self.model.objects.get(pk=obj_id)
        if hasattr(self, "on_post_update"):
            self.on_post_update(obj)
        return obj

    def on_pre_update(self, obj_in: Dict[Any, Any], obj: ModelType) -> None:
        pass

    def on_post_update(self, obj: ModelType) -> None:
        pass

    def on_relationship(
        self, obj_in: Dict[str, Any], obj: ModelType, create: bool = False
    ) -> None:
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

    def _clean_filters(self, filters: Optional[dict] = None) -> None:
        if filters:
            for key, value in list(filters.items()):
                if value is None or value == "":
                    del filters[key]
                if (
                    isinstance(key, str)
                    and key.endswith("__in")
                    and isinstance(value, str)
                ):
                    filters[key] = filters[key].split(",")
                if value == "true" or value == "false":
                    filters[key] = json.loads(value)
                if value == "True" or value == "False":
                    filters[key] = eval(value)

    def _clean_sort_fields(self, order_by_fields: List) -> None:
        invalid_indexes = []
        for index, value in enumerate(order_by_fields):
            if value.strip("-") not in self.model.__dict__.keys():
                invalid_indexes.append(index)
        for index in invalid_indexes:
            del order_by_fields[index]

    def get(self, *args: Any, **kwargs: Any) -> Optional[ModelType]:
        try:
            obj = self.model.objects.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None

        return obj

    def get_all(
        self,
        *,
        filters: Optional[dict[str, Any]] = None,
    ) -> QuerySet[ModelType]:
        self._clean_filters(filters)
        order_by_fields = ["created_at"]
        if not filters:
            filters = {}
        return self.model.objects.filter(**filters).order_by(*order_by_fields)

    def get_filtered(
        self,
        *,
        filters: Optional[dict[str, Any]] = None,
        limit: Optional[int] = 100,
        paginator: Optional[PageNumberPagination] = None,
    ) -> QuerySet[ModelType]:
        self._clean_filters(filters)
        order_by_fields = ["created_at"]
        query: QuerySet = self.model.objects.distinct()
        if filters:
            if "ordering" in filters:
                order_by_fields = filters["ordering"].split(",")
                filters.pop("ordering")
            if "page" in filters:
                filters.pop("page")
            if "per_page" in filters:
                try:
                    limit = int(filters.pop("per_page"))
                except ValueError as e:
                    raise HttpErrorException(
                        422, code=ErrorCodes.UNPROCESSABLE_FILTER, extra=str(e)
                    )
            if "search" in filters:
                query = self.search(search_term=filters["search"], query=query)

        if hasattr(self, "modify_query"):
            query = self.modify_query(query, order_by_fields, filters)

        self._clean_sort_fields(order_by_fields)

        if paginator:
            paginator.page_size = limit

        try:
            query: QuerySet = query.filter(**filters or {})  # type: ignore
        except ValidationError as e:
            raise HttpErrorException(
                422, code=ErrorCodes.UNPROCESSABLE_FILTER, extra=str(e)
            )

        try:
            query = query.order_by(*order_by_fields)
        except FieldError as exc:
            raise HttpErrorException(
                422, code=ErrorCodes.UNPROCESSABLE_FILTER, extra=str(exc)
            )

        return query

    @no_type_check  # TODO: FIX
    def search(self, *, search_term: str, query: QuerySet) -> QuerySet[ModelType]:
        if hasattr(self.model, "search_vector") and len(self.model.search_vector) > 0:
            unpacked_vector = None
            for vector in self.model.search_vector:
                if self.model.search_vector.index(vector) == 0:
                    unpacked_vector = SearchVector(vector)
                    continue
                unpacked_vector += SearchVector(vector)
            search_query = SearchQuery(search_term)

            return query.annotate(search=unpacked_vector).filter(search=search_query)
        else:
            raise HttpErrorException(
                status_code=HTTPStatus.BAD_REQUEST,
                code=ErrorCodes.TARGET_MODEL_HAS_NO_SEARCH_VECTOR,
            )

    def modify_query(
        self,
        query: QuerySet,
        order_fields: Optional[List] = None,
        filters: Optional[dict] = None,
    ) -> QuerySet:
        return query


class CRUDService(
    CreateService[ModelType, CreateSerializer],
    ReadService[ModelType],
    UpdateService[ModelType, UpdateSerializer],
    DeleteService[ModelType],
):
    def __init__(self, model: Type[ModelType]) -> None:
        super().__init__(model)
