@router.callback_query(F.data == "task:cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext, service: UserService):
    """
    Отмена текущего действия (FSM)
    """
    # достаём сохранённые данные
    data = await state.get_data()
    list_id = data.get("list_id")

    # очищаем состояние
    await state.clear()

    user_id = callback.from_user.id

    task_list = service.get_list_by_id(user_id=user_id, list_id=list_id)
    tasks = service.get_tasks(user_id=user_id, list_of_tasks_id=list_id)

    text = task_view.get_list_title(task_list.title)

    await callback.message.edit_text(text=text,
                         parse_mode="Markdown",
                         reply_markup=get_tasks_keyboard(tasks=tasks, list_id=list_id))


@router.callback_query(F.data == "task_text:cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext, service: UserService):
    """
    Отмена текущего действия (FSM)
    """
    # достаём сохранённые данные
    data = await state.get_data()
    task_id = data["task_id"]

    # очищаем состояние
    await state.clear()


    task, list_id = service.get_task_with_list(callback.from_user.id, task_id)

    text = task_view.task_text(task)

    await callback.message.edit_text(
        text=text,
        reply_markup=get_task_detail_keyboard(task, list_id)
    )
    await callback.answer()
