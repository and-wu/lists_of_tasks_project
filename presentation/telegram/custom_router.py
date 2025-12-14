from aiogram import Router


class ControllerRouter(Router):
    """
    Router с дополнительным атрибутом под контроллер.
    Это позволяет IDE видеть commands_router.controller.
    """
    controller = None
