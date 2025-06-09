from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from src.utils.db_manager import get_db_manager
from src.schemas.users import UserAdd, UserEdit


class UserFSM(StatesGroup):
    input_calories = State()
    send_photo = State()


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    async for db in get_db_manager():
        tg_id = str(message.from_user.id)
        is_new = await db.users.is_new(user_id=tg_id)
        if is_new:
            await db.users.new_user(UserAdd(user_id=tg_id))
            await state.set_state(UserFSM.input_calories)
            await message.answer("Введите дневную норму калорий")
            await db.commit()
        else:
            ...


@router.message(UserFSM.input_calories)
async def testing(message: Message, state: FSMContext):
    calories = int(message.text)
    async for db in get_db_manager():
        await db.users.update_user_data(
            user_id=str(message.from_user.id), data=UserEdit(calories_limit=calories)
        )
        await db.commit()
        await message.answer("Дневной лимит успешно обновлен")
        await state.clear()


@router.message(Command("limit"))
async def set_limit(message: Message, state: FSMContext):
    await state.set_state(UserFSM.input_calories)
    await message.answer("Введите дневную норму калорий")


@router.message(Command("photo"))
async def input_photo(message: Message, state: FSMContext):
    await message.answer("Сфотографируйте блюдо, и я расчитаю сколько в нем калорий")
    await state.set_state(UserFSM.send_photo)
