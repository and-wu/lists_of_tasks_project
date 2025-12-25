class DomainError(Exception):
    pass


class UserNotFoundError(DomainError):
    def __init__(self, message: str = "❌ Такой пользователь не найден") -> None:
        self.message = message
        super().__init__(message)


class UsernameAlreadyExistsError(DomainError):
    def __init__(
        self,
        message: str = "❌ Username уже существует, придумайте новый пожалуйста, "
        "а то мы не сможем вас добавить",
    ) -> None:
        self.message = message
        super().__init__(message)


class InvalidMenuChoiceError(DomainError):
    def __init__(self, message: str = "❌ Неверный пункт меню") -> None:
        self.message = message
        super().__init__(message)


