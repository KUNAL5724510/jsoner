import json

from aiogram import F, types
from aiogram.filters.state import StateFilter

from app.routers import user_router


@user_router.message(StateFilter("*"), F.text)
async def profile_command(message: types.Message) -> None:
    """Отвечает пользователю если никакие фильтры не сработали,
    тобиж на не известные команды"""

    # Получаем полные данные сообщения
    full_message_data = message.model_dump()

    # Формируем данные в формате Telegram API Update
    telegram_update = {
        "update_id": "N/A",  # Update ID недоступен в хэндлере
        "message": {
            "message_id": message.message_id,
            "from": {
                "id": message.from_user.id if message.from_user else None,
                "is_bot": message.from_user.is_bot if message.from_user else None,
                "first_name": message.from_user.first_name if message.from_user else None,
                "last_name": message.from_user.last_name if message.from_user else None,
                "username": message.from_user.username if message.from_user else None,
                "language_code": message.from_user.language_code if message.from_user else None,
                "is_premium": message.from_user.is_premium if message.from_user else None,
            }
            if message.from_user
            else None,
            "chat": {
                "id": message.chat.id,
                "first_name": message.chat.first_name
                if hasattr(message.chat, "first_name")
                else None,
                "last_name": message.chat.last_name if hasattr(message.chat, "last_name") else None,
                "username": message.chat.username if hasattr(message.chat, "username") else None,
                "type": message.chat.type,
                "title": message.chat.title if hasattr(message.chat, "title") else None,
            },
            "date": int(message.date.timestamp()) if message.date else None,
            "text": message.text,
        },
    }

    # Добавляем информацию о пересылке, если есть
    if hasattr(message, "forward_origin") and message.forward_origin:
        telegram_update["message"]["forward_origin"] = message.forward_origin
    if hasattr(message, "forward_from") and message.forward_from:
        telegram_update["message"]["forward_from"] = {
            "id": message.forward_from.id,
            "is_bot": message.forward_from.is_bot,
            "first_name": message.forward_from.first_name,
            "last_name": message.forward_from.last_name,
            "username": message.forward_from.username,
            "language_code": message.forward_from.language_code,
            "is_premium": message.forward_from.is_premium,
        }
    if hasattr(message, "forward_date") and message.forward_date:
        telegram_update["message"]["forward_date"] = int(message.forward_date.timestamp())

    # Убираем None значения для чистоты JSON
    def remove_none_values(obj):
        if isinstance(obj, dict):
            return {k: remove_none_values(v) for k, v in obj.items() if v is not None}
        elif isinstance(obj, list):
            return [remove_none_values(v) for v in obj if v is not None]
        return obj

    clean_data = remove_none_values(telegram_update)

    # Форматируем JSON красиво
    formatted_json = json.dumps(clean_data, indent=1, ensure_ascii=False, default=str)

    # Проверяем длину сообщения
    if len(formatted_json) > 3800:
        # Сокращённая версия
        short_data = {
            "message": {
                "message_id": message.message_id,
                "from": {"id": message.from_user.id, "first_name": message.from_user.first_name}
                if message.from_user
                else None,
                "chat": {"id": message.chat.id, "type": message.chat.type},
                "date": int(message.date.timestamp()) if message.date else None,
                "text": message.text[:150] + "..." if len(message.text) > 150 else message.text,
            }
        }
        formatted_json = json.dumps(short_data, indent=1, ensure_ascii=False)

    # Отправляем JSON пользователю
    try:
        await message.answer(f"```json\n{formatted_json}\n```", parse_mode="Markdown")
    except Exception as e:
        # Если всё ещё слишком длинно
        await message.answer(
            f"Message ID: {message.message_id}\nFrom: {message.from_user.id if message.from_user else 'N/A'}\nText: {message.text}"
        )
