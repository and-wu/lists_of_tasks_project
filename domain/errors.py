
class DomainError(Exception):
    pass

class UserNotFoundError(DomainError):
    def __init__(self, message="❌ Такой пользователь не найден"):
        self.message = message
        super().__init__(message)

class UsernameAlreadyExistsError(DomainError):
    def __init__(self, message="❌ Username уже существует, придумайте новый пожалуйста, а то мы не сможем вас добавить"):
        self.message = message
        super().__init__(message)

class InvalidMenuChoiceError(DomainError):
    def __init__(self, message="❌ Неверный пункт меню"):
        self.message = message
        super().__init__(message)

class ListAlreadyExistsError(Exception):
    pass
