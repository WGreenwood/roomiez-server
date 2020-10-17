from enum import Enum


class ErrorCode(Enum):
    Success = 0
    UnknownError = 666
    NoContentType = 10
    InvalidContentType = 11
    NotFound = 12

    # Basic form Errors
    MissingParameter = 20
    EmptyParameter = 21
    Self = 22

    # Auth Errors
    UnauthorizedAccess = 40

    # Login/Register Errors
    InvalidEmail = 41
    EmailAlreadyRegistered = 42
    WeakPassword = 43
    IncorrectLogin = 44

    # Bill Field Validation Errors
    InvalidBillType = 60
    InvalidName = 61
    InvalidCost = 62
    InvalidDate = 63
    NoTimezoneInfo = 64
    DateInFuture = 65
    DateNotCurrentCycle = 66
    InvalidBillIdList = 67

    # Household Api Errors
    AlreadyInHousehold = 80
