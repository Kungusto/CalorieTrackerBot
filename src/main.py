from datetime import date, datetime
from aiogram import F, Dispatcher, Bot, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import asyncio
import logging
import sys
from io import BytesIO
from pathlib import Path

# добавление src в поле видимости
sys.path.append(str(Path(__file__).parent.parent))

from src.api.users import UserFSM
from src.utils.db_manager import get_db_manager
from src.services.api_ml_model import CalorieCounterGPT
from src.schemas.users import UserEdit
from src.database import Base, engine
from src.models import *
from src.config import settings
from src.api.users import router as user_router
from src.exceptions.exceptions import NotRegistratedException

dp = Dispatcher()
bot = Bot(token=settings.API_TOKEN_TG)

photo_router = Router()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await dp.start_polling(bot)


class IngredientEditFSM(StatesGroup):
    waiting_for_calories = State() 
    editing_name = State()         


def get_ingredients_from_state(data: dict) -> list:
    return data.get("ingredients", [])


def set_ingredients_to_state(state: FSMContext, ingredients: list):
    return state.update_data(ingredients=ingredients)


def generate_ingredients_text(ingredients: list) -> str:
    if not ingredients:
        return "Нет ингредиентов."
    result = ""
    total = 0
    for ingr in ingredients:
        result += f"{ingr['name']}: {ingr['calories']} ккал\n"
        total += ingr['calories']
    result += f"\nВсего: {total} ккал"
    return result


def get_ingredients_keyboard(ingredients: list):
    buttons = [
        [InlineKeyboardButton(text=ingr['name'], callback_data=f"edit-{ind}")]
        for ind, ingr in enumerate(ingredients)
    ]
    buttons.append([InlineKeyboardButton(text="Подтвердить ✅", callback_data="confirm-all")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def ingredients_sum(ingredients: list):
    return sum(int(ingr["calories"]) for ingr in ingredients)


@photo_router.message(UserFSM.send_photo)
async def get_file_from_message(message: Message, state: FSMContext):
    try:
        photo = message.photo[-1]
    except TypeError:
        await message.answer("Пришлите фото!")
        return
    file_id = photo.file_id
    file = await message.bot.get_file(file_id)
    file_content = await message.bot.download_file(file.file_path)
    file = BytesIO(file_content.getvalue())
    await message.answer("Обрабатываю...")
    data = CalorieCounterGPT().analyze_food(file=file)
    if isinstance(data, str): 
        await message.answer(data)
        await state.clear()
        return
    ingredients = [i.model_dump() for i in data.ingredients]
    await state.set_data({"ingredients": ingredients})  
    await message.answer(
        generate_ingredients_text(ingredients),
        reply_markup=get_ingredients_keyboard(ingredients)
    )


@photo_router.callback_query(F.data.startswith("edit-"))
async def ingredient_options(callback: CallbackQuery, state: FSMContext):
    ind = int(callback.data.split("-")[-1])
    data = await state.get_data()
    ingredients = get_ingredients_from_state(data)
    ingr = ingredients[ind]
    buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Удалить", callback_data=f"delete-{ind}")],
            [InlineKeyboardButton(text="Изменить калории", callback_data=f"change-{ind}")],
            [InlineKeyboardButton(text="Назад", callback_data="back")],
        ]
    )
    await callback.message.edit_text(f"{ingr['name']} — {ingr['calories']} ккал", reply_markup=buttons)
    await callback.answer()


@photo_router.callback_query(F.data.startswith("delete-"))
async def delete_ingredient(callback: CallbackQuery, state: FSMContext):
    ind = int(callback.data.split("-")[-1])
    data = await state.get_data()
    ingredients = get_ingredients_from_state(data)
    if 0 <= ind < len(ingredients):
        ingredients.pop(ind)
        await set_ingredients_to_state(state, ingredients)
    await callback.message.edit_text(
        generate_ingredients_text(ingredients),
        reply_markup=get_ingredients_keyboard(ingredients)
    )
    await callback.answer()


@photo_router.callback_query(F.data.startswith("change-"))
async def change_calories_start(callback: CallbackQuery, state: FSMContext):
    ind = int(callback.data.split("-")[-1])
    await state.update_data(edit_index=ind, edit_message_id=callback.message.message_id)
    await state.set_state(IngredientEditFSM.waiting_for_calories)
    await callback.message.edit_text("Введите новое количество калорий:")
    await callback.answer()


@photo_router.message(IngredientEditFSM.waiting_for_calories)
async def change_calories_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    ind = data.get("edit_index")
    ingredients = get_ingredients_from_state(data)
    try:
        new_cal = int(message.text)
        if 0 <= ind < len(ingredients):
            ingredients[ind]["calories"] = new_cal
            await set_ingredients_to_state(state, ingredients)
    except ValueError:
        await message.answer("Введите число!")
        return
    except TypeError:
        await message.answer("Введите число!")
        return
    await state.set_state(None)
    if "edit_message_id" in data:
        await message.bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=data["edit_message_id"],
            text=generate_ingredients_text(ingredients),
            reply_markup=get_ingredients_keyboard(ingredients)
        )
    else:
        await message.answer(
            generate_ingredients_text(ingredients),
            reply_markup=get_ingredients_keyboard(ingredients)
        )


@photo_router.callback_query(F.data == "back")
async def back_to_list(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ingredients = get_ingredients_from_state(data)
    await callback.message.edit_text(
        generate_ingredients_text(ingredients),
        reply_markup=get_ingredients_keyboard(ingredients)
    )
    await callback.answer()


@photo_router.callback_query(F.data == "confirm-all")
async def confirm_all(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ingredients = get_ingredients_from_state(data)
    user_id = str(callback.from_user.id)
    delta_calories = ingredients_sum(ingredients)
    async for db in get_db_manager():
        try:
            user_data = await db.users.get_user(user_id=user_id)
        except NotRegistratedException as ex:
            await callback.message.answer(ex.detail)
            return 
        data_to_add =  {"calories": (user_data.calories + delta_calories), "updated_at": datetime.now()}
        if user_data.last_date != date.today() :
            data_to_add["calories"] = 0
        await db.users.update_user_data(
            user_id=user_id,
            data=UserEdit(
               **data_to_add
            )
        )
        await db.commit()
    if (user_data.calories + delta_calories) > user_data.calories_limit:
        await callback.message.edit_text(f"Вы превысили дневной лимит. Избыток: {abs(user_data.calories - user_data.calories_limit)} ккал")
    else:
        await callback.message.edit_text(f"Ингредиенты сохранены! Ваши текущие калории: {user_data.calories + delta_calories}/{user_data.calories_limit}")
    await state.clear()
    await callback.answer()


if __name__ == "__main__":
    dp.include_router(photo_router)
    dp.include_router(user_router)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
