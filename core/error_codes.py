import enum


class ErrorCodes(enum.Enum):
    ACCESS_DENIED = "You don't have permissions to access this resource"
    INVALID_EVENT_FOR_TICKET = "Invalid event id on tickect creation"
    INVALID_EVENT_ID = "An event with the given ID does not exist"
    INVALID_PERSON_ID = "The person with the given ID does not exist"
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
    NO_PARTNERSHIP = "The given person has no partner"
    MULTIPLE_USERS_SAME_PHONENUMBER = (
        "Internal Error: The server returned multiple people with a single phonenumer"
    )
    ACCESS_ONLY_FOR_SELF = "This action can only be performed on your own data"
    INVALID_PARTNER_ID = "A partner with the given ID does not exist"
    TARGET_MODEL_HAS_NO_SEARCH_VECTOR = "The target model does not have a search vector"
    MULTIPLE_TICKETS_ONE_HASH = "Can't resolve target ticket from hash value"
    INVALID_TICKET_ID = "A ticket with the given ID was not found"
    UNPAID_FOR_TICKET = "A ticket with an unverified payment cannot be redeemed"
    UNRESOLVABLE_HASH = "THe provided has doesn't corespond to any ticket"
    PROMO_NOT_FOUND = "The promotion code was not found"
