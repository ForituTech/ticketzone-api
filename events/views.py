from rest_framework.decorators import api_view
from rest_framework.response import Response

from events.serializers import EventReadSerializer
from events.services import event_service


@api_view(["GET"])
def list_events(request):
    events = event_service.get_filtered()
    return Response(EventReadSerializer(events, many=True).data)
