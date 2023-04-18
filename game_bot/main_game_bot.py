from email_validate import validate, validate_or_fail
import logging
from asyncio import sleep
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text, Command
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.storage import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode, Message
from config import TG_TOKEN
from keyboards.main_murkup import reg_kb, user_kb, game_loop_kb
from database.raccoon_db import RDataBase

logging.basicConfig(level=logging.INFO)

bot = Bot(TG_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class ClientStateGroup(StatesGroup):
    registration = State()
    game = State()

data_base = RDataBase("raccoon_db.sqlite")
async def on_startup(_):
    print("Бот запущен!")


@dp.message_handler(Command("start"))
async def start_cmd(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    if data_base.user_exist(user_id):
        await message.answer(f"С возвращением в игру {user_name}🐾🎲🎲🎲", reply_markup=user_kb)
    else:
        await message.answer(f"Привет {user_name}🖐 Зарегистрируйся и сможем играть 🎲🎲", reply_markup=reg_kb)


@dp.message_handler(Text(equals="Закончить игру⛔"), state="*")
async def game_stop(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer(text="Выбор функции", reply_markup=user_kb)


@dp.message_handler(Text(equals="💰БАЛАНС💰"))
async def get_wallet(message: Message):
    user_id = message.from_user.id
    game_balance = data_base.validate_balance(user_id)[0]
    await bot.send_message(message.from_user.id, text=f"<b>Ваш игровой баланс составляет</b>: <b>{game_balance} PAW🐾</b>", reply_markup=user_kb, parse_mode=ParseMode.HTML)

@dp.message_handler(Text(equals="🗄️Регистрация"))
async def reg_user(message: Message):
    await message.answer("Введите свой email адрес:")
    await ClientStateGroup.registration.set()

@dp.message_handler(lambda message: message.text, state=ClientStateGroup.registration)
async def add_user_db(message: Message, state: FSMContext):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    email_text = message.text
    param = validate(
            email_address=email_text,
            check_format=True,
            check_blacklist=True,
            check_dns=True,
            dns_timeout=10,
            check_smtp=False,
            smtp_debug=False
    )
    if param:
        async with state.proxy() as data:
            data["email"] = email_text
        data_base.add_user(user_id, user_name, email=email_text)
        await message.answer("Вы успешно зарегистрированы!\nВам начислено < 100 PAW >\nВрывайся в игру🚀🚀🚀", reply_markup=user_kb)
        await state.finish()
    else:
        await message.answer("email addres недействителен или введен с ошибкой! Повторите ввод!", reply_markup=reg_kb)


@dp.message_handler(Text(equals="🎲🎲ИГРАТЬ🎲🎲"))
async def game_run(message: Message):
    await message.answer("Для начала игры нажми кнопку ⬇️", reply_markup=game_loop_kb)
    await ClientStateGroup.game.set()


@dp.message_handler(lambda message: message.text, state=ClientStateGroup.game)
async def add_user_db(message: Message, state: FSMContext):
    user_id = message.from_user.id
    game_balance = data_base.validate_balance(user_id)[0]
    if game_balance >= 5:
        await sleep(2)
        user_res = await bot.send_dice(message.from_user.id)
        user_res = user_res["dice"]["value"]
        await sleep(5)
        bot_res = await bot.send_dice(message.from_user.id)
        bot_res = bot_res["dice"]["value"]

        if user_res > bot_res:
            game_balance = game_balance + 5
            await message.answer(f"Вы победили 🎉🎊🎇\n"f"Игровой баланс: < {game_balance} >", reply_markup=game_loop_kb)
        elif user_res < bot_res:
            game_balance = game_balance - 5
            await message.answer("Проиграли, удача улыбнется в следуюющий раз\n"f"Игровой баланс: < {game_balance} >", reply_markup=game_loop_kb)
        else:
            await message.answer("Победила дружба ⚖️")
    data_base.update_game_balance(user_id, balance=game_balance)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)