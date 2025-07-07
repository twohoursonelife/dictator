class UsernameValidationError(Exception):
    def __init__(self, message="Invalid username."):
        super().__init__(message)


class UsernameAlreadyExistsError(Exception):
    def __init__(self, message="The username is already in use."):
        super().__init__(message)


class UserAlreadyRegisteredError(Exception):
    def __init__(self, message="The user already has an account."):
        super().__init__(message)
