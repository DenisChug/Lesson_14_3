# aiogram 3.15 python 3.12
import asyncio
import os

from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile

all_media_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))

api = '7740609310:AAFF5C1m19VVZmeYT5itM8gDP8biaVlKrQU'
bot = Bot(token=api)
dp = Dispatcher()

kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Рассчитать'), KeyboardButton(text='Информация')],
                                   [KeyboardButton(text='Купить')]],
                         resize_keyboard=True)

inline_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories'),
                                    InlineKeyboardButton(text='Формулы расчёта', callback_data='formula')]])

catalog_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Product1', callback_data="product_buying")],
                                                   [InlineKeyboardButton(text='Product2', callback_data="product_buying")],
                                                   [InlineKeyboardButton(text='Product3', callback_data="product_buying")],
                                                   [InlineKeyboardButton(text='Product4', callback_data="product_buying")]])

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Привет! Я бот, помогающий твоему здоровью.", reply_markup=kb)

@dp.message(F.text.lower()=="Рассчитать".lower())
async def inline_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=inline_kb)

@dp.callback_query(F.data=='formula')
async def get_formulas(callback: CallbackQuery):
    print('Ok formula')
    formula = (
        "Формула Миффлина-Сан Жеора:\n"
        "10 * вес(кг) + 6.25 * рост(см) - 5 * возраст - 161"
    )
    await callback.message.answer(f'{formula}')
    await callback.answer()

@dp.callback_query(F.data=='calories')
async def set_age(callback: CallbackQuery, state: FSMContext):
    print('Ok colories')
    await callback.message.answer("Введите свой возраст:")
    await callback.answer()
    await state.set_state(UserState.age)


@dp.message(UserState.age)
async def set_growth(message: Message, state: FSMContext):
    try:
        UserState.age = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для возраста.")
        return
    await state.update_data(age=UserState.age)
    await message.answer("Введите свой рост (в сантиметрах):")
    await state.set_state(UserState.growth)

@dp.message(UserState.growth)
async def set_weight(message: Message, state: FSMContext):
    try:
        UserState.growth = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для роста.")
        return
    await state.update_data(growth=UserState.growth)
    await message.answer("Введите свой вес (в килограммах):")
    await state.set_state(UserState.weight)

@dp.message(UserState.weight)
async def send_calories(message: Message, state: FSMContext):
    try:
        UserState.weight = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректное число для веса.")
        return
    await state.update_data(weight=UserState.weight)

    data = await state.get_data()
    age = data.get('age')
    growth = data.get('growth')
    weight = data.get('weight')
    bmr = 10 * weight + 6.25 * growth - 5 * age +5
    await message.answer(f"Ваша норма калорий: {bmr:.2f} ккал в день.")
    await state.clear()

@dp.message(F.text == 'Купить')
async def get_buying_list(message: Message):
    products = [
        {"name": "Яблоки", "description": "Яблоко как яблоко", "price": 100, "image": "Apple.png"},
        {"name": "Груши", "description": "Груша как груша", "price": 200, "image": "Pear.png"},
        {"name": "Апельсины", "description": "Апельсин как апельсин", "price": 300, "image": "Orange.png"},
        {"name": "Бананы", "description": "Бана как банан", "price": 400, "image": "Banana.png"}]

    for product in products:
        await message.answer(f"Название: {product['name']} | Описание: {product['description']} | Цена: {product['price']}")
        prod = (f'"{product['image']}"')
        img = FSInputFile(path=os.path.join(all_media_dir, product['image']))
        await message.answer_photo(img)

    await message.answer("Выберите продукт для покупки:", reply_markup=catalog_kb)

@dp.callback_query(F.data == 'product_buying')
async def send_confirm_message(callback: CallbackQuery):
    await callback.message.answer("Вы успешно приобрели продукт!")
    await callback.answer()
async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())