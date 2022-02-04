import enum


class ErrorCodes(enum.Enum):
    INVALID_EVENT_FOR_TICKET = "Invalid event id on tickect creation"
    INVALID_EVENT_ID = "An event with the given ID does not exist"
    TICKET_TYPE_OBJECT_DELETED = "Ticket type object sucessfully deleted"
