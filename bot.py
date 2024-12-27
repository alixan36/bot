import asyncio
import logging
import sys
import random
import requests
from os import getenv

from datetime import datetime
from aiogram import Bot, Dispatcher, Router, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters  import CommandStart 
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import   InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData


class weatherCallback(CallbackData, prefix="weather"):
    action: str
    



# Создаем состояние для прогноза
class ForecastState(StatesGroup):
    waiting_for_city = State()


# Состояния
class WeatherState(StatesGroup):
    waiting_for_city = State()


API_KEY = "9b263cc5597617ce2f20c92da0001576"
BASE_URL = "http://api.openweathermap.org/data/2.5/weather"


# Список фактов
facts = [
    "Пчелы могут видеть ультрафиолетовый свет.",
    "Сердце голубого кита весит около 600 килограммов.",
    "Самый длинный велосипед в мире — более 35 метров.",
    "Татуировки существуют на протяжении тысячелетий. Одно из самых старых известных татуированных тел принадлежит мумии Эци, найденной в Альпах, которой более 5,000 лет.",
    "В древности татуировки использовались не только как украшение, но и для лечебных целей. У мумии Эци, например, татуировки расположены на тех участках тела, которые могли быть связаны с лечением артрита.",
    "В различных культурах татуировки играли разные роли. Например, в полинезийских культурах татуировки были символом статуса и силы, в то время как в Японии они часто ассоциировались с якудза — членами преступных группировок.",
    "В XIX веке в западных странах татуировки считались уделом преступников, моряков и маргинальных групп. В то же время, в других культурах, таких как маори или инуиты, татуировки были важной частью культурного наследия.",
    "Первые татуировочные машинки были изобретены в конце XIX века, и они значительно упростили процесс нанесения татуировок. Эти машинки были модифицированы на основе устройства для гравировки, изобретенного Томасом Эдисоном.",
    "Многие татуировки связаны с важными для человека событиями или символами, отражая религиозные, личные или культурные ценности. Например, татуировки на военных часто рассказывают истории о службе или утраченных товарищах.",
    "Удаление татуировок с помощью лазера стало доступным только в XX веке. Этот процесс сложен и часто болезненный, а на месте татуировки могут оставаться шрамы или обесцвеченные участки кожи.",
    "Сегодня татуировки распространены во всех слоях общества и воспринимаются как форма самовыражения и искусства, а также как способ рассказать историю о себе.",
]



# Список для хранения фактов, которые уже были отправлены
used_facts = []

# Количество попыток, после которых факты могут повторяться
max_attempts = 11


# Bot token can be obtained via https://t.me/BotFather
TOKEN = "7931774402:AAGNp5Xtr1YSV1bM8jfzwBmM8YmJZZGRh0U"

if not TOKEN:
    raise ValueError("Bot token not provided. Please set the BOT_TOKEN environment variable.")

# All handlers should be attached to the Router (or Dispatcher)
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()





# Подключение роутера
dp.include_router(router)


# Глобальный словарь для хранения состояния игры
games = {}


# Определяем список приветствий
greetings_keywords = {"привет", "здравствуйте", "добрый день", "доброе утро", "добрый вечер", "доброй ночи"}

# Функция для определения времени суток
def get_greeting() -> str:
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Доброе утро"
    elif 12 <= current_hour < 18:
        return "Добрый день"
    elif 18 <= current_hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"
    




@router.message(Command(commands="start"))
async def start_handler(message: Message):
   

   
    greeting = get_greeting()
    await message.answer(f"{greeting}, {html.bold(message.from_user.full_name)}!")
    
    

    # Автоматически вызываем обработчик команды /help
    #await help_handler(message)

    
    """
    Обработчик команды /start с кнопками.
    """
    # Создаем inline-клавиатуру
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Погода", callback_data="weather"),
                InlineKeyboardButton(text="Прогноз", callback_data="forecast"),
            ],
            [
                InlineKeyboardButton(text="Помощь", callback_data="help")
            ]
        ]
    )
    
    await message.answer("Выберите опцию:", reply_markup=keyboard)


@router.callback_query()  # Добавляем обработчик нажатий
async def button_click_handler(callback: CallbackQuery):
    """
    Обрабатывает нажатия на кнопки.
    """
    if callback.data == "weather":
        await callback.message.answer("Вы выбрали 'Погода'. Введите город для прогноза.")
    elif callback.data == "forecast":
        await callback.message.answer("Вы выбрали 'Прогноз'. Укажите город для 5-дневного прогноза.")
    elif callback.data == "help":
        await callback.message.answer(
            "Команды бота:\n"
            "- /start — приветствие\n"
        "- /help — описание команд\n"
        "- /fact — рандомный факт о татуировках велосипедах китах и пчелах\n"
        "- /game_start — начать игру 'Угадай число'\n"
        "- /game_stop — завершить игру\n"
        "- /weather НАЗВАНИЕ ГОРОДА — температура в данный момент\n"
        "- /forecast НАЗВАНИЕ ГОРОДА — трехчасовой прогноз на пять дней\n"
        )
    else:
        await callback.message.answer("Неизвестная команда.")
    await callback.answer()  # Убираем "загрузку" на кнопке


    


async def fetch_and_send_weather(message: Message, city: str) -> None:
    try:
        response = requests.get(BASE_URL, params={"q": city, "appid": API_KEY, "units": "metric", "lang": "ru"})
        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            description = data["weather"][0]["description"]
            await message.answer(f"Сейчас в {city}: {temp}°C, {description}.")
        else:
            await message.answer(f"Не удалось получить данные о погоде для города '{city}'. Проверьте название.")
    except Exception as e:
        await message.answer("Произошла ошибка при запросе данных о погоде. Попробуйте позже.")


    


@dp.callback_query(weatherCallback.filter(F.action == "start"))
async def weather_callback_handler(query: CallbackQuery, message: Message, state: FSMContext) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await state.set_state(WeatherState.waiting_for_city)
        await message.answer("Пожалуйста, укажите город")
        return

    city = args[1]
    await fetch_and_send_weather(message, city)


@dp.message(StateFilter(WeatherState.waiting_for_city))
async def handle_city_input(message: Message, state: FSMContext) -> None:
    city = message.text.strip()
    if not city:
        await message.answer("Пожалуйста, введите название города.")
        return

    await fetch_and_send_weather(message, city)
    await state.clear()


@router.message(Command(commands="forecast"))
async def forecast_handler(message: Message, state: FSMContext) -> None:
    """
    Узнает 5-дневный прогноз погоды для указанного города.
    """
    city = message.text[len("/forecast "):].strip()  # Убираем команду "/forecast" и пробелы по бокам
    if not city:
        await state.set_state(ForecastState.waiting_for_city)  # Переводим пользователя в состояние ожидания города
        await message.answer("Пожалуйста, укажите город")
        return
       
# Обработка состояния
@dp.message(StateFilter(ForecastState.waiting_for_city))
async def get_city_name(message: Message, state: FSMContext):
    city = message.text.strip()
    # Здесь вы вызываете функцию для получения погоды
    forecast_message = f"Прогноз погоды для города {city}..."  # Заглушка
    await message.answer(forecast_message)
    await state.clear()
    # Используем правильный URL для прогноза
    forecast_url = "http://api.openweathermap.org/data/2.5/forecast"
    response = requests.get(forecast_url, params={"q": city, "appid": API_KEY, "units": "metric", "lang": "ru"})
    
    # Для отладки
    print(response.status_code, response.text)
    
    if response.status_code == 200:
        data = response.json()
        forecast_list = data["list"]  # Список прогнозов на 5 дней

        # Формируем сообщение с прогнозом
        forecast_message = f"Прогноз погоды для {city} на 5 дней (каждые 3 часа):\n\n"
        for entry in forecast_list[:40]:  # Берем первые 8 записей (24 часа)
            dt = datetime.fromtimestamp(entry["dt"]).strftime("%d.%m %H:%M")
            temp = entry["main"]["temp"]
            description = entry["weather"][0]["description"]
            forecast_message += f"{dt}: {temp}°C, {description}\n"

        await message.answer(forecast_message)
    else:
        error_message = response.json().get("message", "Неизвестная ошибка")
        await message.answer(f"Не удалось получить данные о погоде для '{city}'. Причина: {error_message}")






# Обработчик команды /game_start
@dp.message(Command(commands="game_start"))
async def start_game_game(message: Message) -> None:
    """
    Инициализация игры "Угадай число".
    """
    global games
    user_id = message.from_user.id

    if user_id in games:
        await message.answer("Вы уже играете! Попробуйте угадать мое число.")
        return

    # Генерируем случайное число для пользователя
    secret_number = random.randint(1, 10)
    games[user_id] = secret_number
    await message.answer("Я загадал число от 1 до 10. Попробуйте угадать!")


# Обработчик команды /game_stop
@dp.message(Command(commands="game_stop"))
async def stop_game_game(message: Message) -> None:
    """
    Завершение игры "Угадай число".
    """
    global games
    user_id = message.from_user.id

    if user_id not in games:
        await message.answer("Игра завершена. Если захотите сыграть снова, введите /game_start.")
        return

    # Удаляем состояние игры для пользователя
    del games[user_id]
    await message.answer("Игра завершена. Если захотите сыграть снова, введите /game_start.")


# Обработчик для угадывания числа
@dp.message(lambda message: message.text.isdigit())
async def game_number_handler(message: Message) -> None:
    """
    Игра: угадай число.
    """
    global games
    user_id = message.from_user.id

    # Проверяем, запущена ли игра для пользователя
    if user_id not in games:
        await message.answer("Чтобы начать игру, введите команду /game_start.")
        return

    # Получаем число пользователя и сравниваем
    user_number = int(message.text)
    secret_number = games[user_id]

    if user_number == secret_number:
        await message.answer("Поздравляю! Вы угадали! Игра завершена.")
        # Удаляем игру после угадывания
        del games[user_id]
    elif user_number < secret_number:
        await message.answer("Мое число больше!")
    else:
        await message.answer("Мое число меньше!")


@dp.message(lambda message: message.text.isdigit())
async def game_number_handler(message: Message) -> None:
    """
    Игра: угадай число
    """
    user_number = int(message.text)
    if user_number == secret_number:
        await message.answer("Поздравляю! Вы угадали!")
    elif user_number < secret_number:
        await message.answer("Мое число больше!")
    else:
        await message.answer("Мое число меньше!")


 # Обработчик для приветственных сообщений
@dp.message(lambda message: not message.text.startswith('/'))
async def greeting_response_handler(message: Message) -> None:
    """
    Ответ на приветственные сообщения пользователя.
    """
    # Преобразуем сообщение в нижний регистр и проверяем, содержит ли оно ключевые слова
    user_message = message.text.lower()
    if any(keyword in user_message for keyword in greetings_keywords):
        greeting = get_greeting()
        await message.answer(f"{greeting}, {html.bold(message.from_user.full_name)}!")


@dp.message(Command(commands="fact"))
async def fact_handler(message: Message) -> None:
    """
    Этот обработчик отвечает на команду /fact
    """
    global used_facts

    # Проверяем, если список used_facts содержит все возможные факты
    if len(used_facts) == len(facts):
        used_facts = []  # Очищаем список, если все факты использованы

    # Выбираем случайный факт, который еще не был использован
    random_fact = random.choice([fact for fact in facts if fact not in used_facts])
    used_facts.append(random_fact)  # Добавляем факт в список использованных

    # Если количество использованных фактов превышает максимальное количество попыток
    if len(used_facts) > max_attempts:
        used_facts.pop(0)  # Убираем самый старый факт, чтобы не использовать его в будущем
     
    await message.answer(random_fact)


@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    """
    Этот обработчик отвечает на команду /help
    """
    await message.answer(
        "Я бот и вот что я умею:\n"
        "- /start — приветствие\n"
        "- /help — описание команд\n"
        "- /fact — рандомный факт о татуировках велосипедах китах и пчелах\n"
        "- /game_start — начать игру 'Угадай число'\n"
        "- /game_stop — завершить игру\n"
        "- /weather НАЗВАНИЕ ГОРОДА — температура в данный момент\n"
        "- /forecast НАЗВАНИЕ ГОРОДА — трехчасовой прогноз на пять дней\n"
        "- Эхо-сообщения — повторяю ваш текст\n"
    )


@dp.message(lambda message: not message.text.startswith('/'))
async def echo_handler(message: Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    try:
        # Send a copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")





async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())