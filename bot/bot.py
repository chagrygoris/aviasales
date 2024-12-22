import datetime

from aiogram import Bot, Dispatcher, html
from aiogram.filters import CommandObject
from aiogram import Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.keyboard import *
from src import session, User
import os, logging, asyncio, sys, dotenv
from src.constants import help_message
from config import Config
from fastapi import Request
from inline_handlers import inline_router
dotenv.load_dotenv()

dp = Dispatcher()
dp.include_router(inline_router)

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")


@dp.message(Command("help"))
async def helper(message: Message):
    await message.answer(help_message)


route_router = Router()
dp.include_router(route_router)

@route_router.message(Command("route"))
async def routefinder(message: Message, command: CommandObject):
    from adapters import compile_message
    commands = command.args.split()
    departure, destination, date = '', '', ''
    if len(commands) == 3:
        departure, destination, date = commands
    elif len(commands) == 2:
        departure, destination = commands
        date = datetime.datetime.today()
    else:
        await message.answer(f"пожалуйста, введите команду в формате /route откуда куда YYYY-MM-DD")
    await message.answer(f"Finding routes {departure} ---> {destination}")
    await message.answer(str(await compile_message(departure, destination, date)))



@route_router.message(Command("choose"))
async def choose_route(message: Message, command: CommandObject):
    commands = command.args.split()
    if len(commands) != 3:
        await message.answer("Пожалуйста, отправьте команду в формате: /choose откуда куда YYYY-MM-DD")
        return
    departure, destination, date = commands
    user_telegram_id = message.from_user.id
    user = session.query(User).filter_by(telegram_id=user_telegram_id).first()
    builder = InlineKeyboardBuilder()
    if not user:
        builder.row(InlineKeyboardButton(
            text=f"Завершите регистрацию и продолжите выбор!", url=f"https://a5cf-185-200-105-117.ngrok-free.app/sign_up?from_city={departure}&to_city={destination}&date={date}&telegram_id={user_telegram_id})")
        )
    else:
        search_url = f"https://a5cf-185-200-105-117.ngrok-free.app/search/results?from_city={departure}&to_city={destination}&date={date}&telegram_id={user_telegram_id}"
        builder.row(InlineKeyboardButton(
            text=f"Продолжите выбор", url=search_url)
        )
    await message.answer(
        text=f'Билеты из {departure} в {destination} уже ждут на сайте!',
        reply_markup=builder.as_markup(),
    )



async def bot_main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=Config.TELEGRAM_KEY, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(bot_main())