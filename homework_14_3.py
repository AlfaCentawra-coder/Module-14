from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
import asyncio

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

# Main menu keyboard
keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = types.KeyboardButton('Рассчитать')
button_info = types.KeyboardButton('Информация')
button_buy = types.KeyboardButton('Купить')
keyboard.add(button_calculate, button_info, button_buy)

inline_keyboard = InlineKeyboardMarkup(row_width=2)
inline_keyboard.add(
    InlineKeyboardButton("Product1", callback_data="product_buying"),
    InlineKeyboardButton("Product2", callback_data="product_buying"),
    InlineKeyboardButton("Product3", callback_data="product_buying"),
    InlineKeyboardButton("Product4", callback_data="product_buying")
)

@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    await message.answer("Выберите действие:", reply_markup=keyboard)

@dp.message_handler(text='Купить')
async def get_buying_list(message: types.Message):
    for i in range(1, 5):
        with open(f'product{i}.jpg', 'rb') as photo:
            await message.answer_photo(photo, f"Название: Product{i} | Описание: описание {i} | Цена: {i * 100}")
    await message.answer("Выберите продукт для покупки:", reply_markup=inline_keyboard)

@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer() 

class UserStates(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    activity = State()

@dp.message_handler(text='Рассчитать')
async def set_age(message: types.Message):
    await message.answer('Введите свой возраст')
    await UserStates.age.set()

@dp.message_handler(state=UserStates.age)
async def set_growth(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Пожалуйста, введите числовое значение для возраста.')
        return
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост')
    await UserStates.growth.set()

@dp.message_handler(state=UserStates.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Пожалуйста, введите числовое значение для роста.')
        return
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес')
    await UserStates.weight.set()

@dp.message_handler(state=UserStates.weight)
async def set_activity(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Пожалуйста, введите числовое значение для веса.')
        return
    await state.update_data(weight=message.text)
    await message.answer('Выберите свою активность \n'
                         'Минимальная активность 1.2 \n'
                         'Слабая активность 1.375 \n'
                         'Средняя активность 1.55 \n'
                         'Высокая активность 1.725 \n'
                         'Экстрa-активность 1.9')
    await UserStates.activity.set()

@dp.message_handler(state=UserStates.activity)
async def send_calories(message: types.Message, state: FSMContext):
    try:
        activity = float(message.text)
        if activity not in [1.2, 1.375, 1.55, 1.725, 1.9]:
            raise ValueError
    except ValueError:
        await message.answer('Пожалуйста, выберите корректное значение активности.')
        return

    await state.update_data(activity=activity)
    data = await state.get_data()
    calories = (10 * float(data["weight"]) + 6.25 * float(data["growth"]) - 5 * float(data["age"]) - 161) * activity
    await message.answer(f'Необходимое количество каллорий в день для вас {calories}')
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)