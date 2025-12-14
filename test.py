class DomainError(Exception):
    pass

class UserNotFoundError(DomainError):
    def __init__(self, message = 'УУУУУУУУУ'):
        self.message = message
        super().__init__(message)


try:
    raise UserNotFoundError()
except Exception as e:
    print(e)
