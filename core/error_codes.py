import enum


class ErrorCodes(enum.Enum):
    ACCESS_DENIED = "You don't have permissions to access this resource"
    INVALID_EVENT_FOR_TICKET = "Invalid event id on tickect creation"
    INVALID_EVENT_ID = "An event with the given ID does not exist"
    TICKET_TYPE_OBJECT_DELETED = "Ticket type object sucessfully deleted"
    EVENT_DELETED = "The event has been deleted"
    GENERIC_TICKET_TYPE_LISTING = (
        "Global ticket type listing is forbidden. event_id filter is required."
    )
    UNPROCESSABLE_TOKEN = (
        "The token in the request could not be decoded or had missing data"
    )
    BAD_PHONENUMBER = "The phone number provided is invalid/ doesn't belong to any user"
    INVALID_CREDENTIALS = "The provided credentials don't match any user"
