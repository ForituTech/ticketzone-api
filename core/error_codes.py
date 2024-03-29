import enum


class ErrorCodes(enum.Enum):
    ACCESS_DENIED = "You don't have permissions to access this resource"
    ACCESS_ONLY_FOR_SELF = "This action can only be performed on your own data"
    BAD_PHONENUMBER = "The phone number provided is invalid/ doesn't belong to any user"
    ENTITY_NOT_FOUND = "entity {} with identitfier {} not found"
    EVENT_DELETED = "The event has been deleted"
    EXPIRED_REFRESH_TOKEN = "The refresh token has expired, please login again"
    GENERIC_TICKET_TYPE_LISTING = (
        "Global ticket type listing is forbidden. event_id filter is required."
    )
    INTERGRATION_ERROR = "Intergration Error: {}"
    INVALID_ACCESS_TOKEN = "The provided access token is invalid"
    INVALID_CREDENTIALS = "The provided credentials don't match any user"
    INVALID_EVENT_FOR_TICKET = "Invalid event id on tickect creation"
    INVALID_EVENT_ID = "An event with the given ID does not exist"
    INVALID_OTP = "The provided OTP could not be verified"
    INVALID_PARTNER_ID = "A partner with the given ID does not exist"
    INVALID_PERSON_ID = "The person with the given ID does not exist"
    INVALID_REFRESH_TOKEN = "The provided refresh token is invalid"
    INVALID_SIGNATURE = "The auth request signature was invalid"
    INVALID_TICKET_ID = "A ticket with the given ID was not found"
    MULTIPLE_TICKETS_ONE_HASH = "Can't resolve target ticket from hash value"
    MULTIPLE_USERS_SAME_PHONENUMBER = (
        "Internal Error: The server returned multiple people with a single phonenumer"
    )
    NO_MEMBERSHIP = "The given person isn't associated to a partner"
    NO_PARTNERSHIP = "The given person has no partner"
    NO_SMS_PACKAGE = "The given partner has no sms package"
    NOT_SUPPORTED = "The action you attempted is not supported: {}"
    PARTNER_NOT_FOUND = "The partnership was not found"
    PARTNER_NOT_VERIFIED = "The partnership was not verified"
    PAYMENT_INTENT_NOT_FOUND = "Related payment intent could not be found"
    PAYMENT_PROCESSING_FAILED = "Payment processing failed"
    PROMO_NOT_FOUND = "The promotion code was not found"
    PROVIDER_NOT_SUPPORTED = "The chosen provider is not currently supported"
    REDEEMED_TICKET = "The current ticket has already been redeemed"
    SERVICE_EXCEPTION = "Operation Failed: {}"
    TARGET_MODEL_HAS_NO_SEARCH_VECTOR = "The target model does not have a search vector"
    TICKET_TYPE_OBJECT_DELETED = "Ticket type object sucessfully deleted"
    TICKET_TYPE_SOLD_OUT = "The ticket {} has just sold out :("
    TICKET_TYPE_INSUFFICIENT = "There's is an insufficient amount of tickets: {}"
    UNPAID_FOR_TICKET = "A ticket with an unverified payment cannot be redeemed"
    UNPROCESSABLE_FILTER = "Some of the filters passed could not be processed: {}"
    UNPROCESSABLE_TOKEN = (
        "The token in the request could not be decoded or had missing data"
    )
    UNRESOLVABLE_HASH = "THe provided hash doesn't corespond to any ticket"
