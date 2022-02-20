from typing import Any, Dict, List

from rest_framework import viewsets


class AbstractPermissionedView(viewsets.ViewSet):
    """
    An abstraction that allows limiting permissions to specific
    viewset methods.
    Example:
        permissions_by_action = {
            "create": PartnerPermission,
        }
    """

    permissions_by_action: Dict[str, List[Any]] = {}

    def get_permissions(self) -> List[Any]:
        try:
            return [
                permission() for permission in self.permissions_by_action[self.action]
            ]
        except KeyError:
            return [permission() for permission in self.permission_classes]
