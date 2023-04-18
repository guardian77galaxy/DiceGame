from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

reg_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

btn_registration = KeyboardButton("🗄️Регистрация")
reg_kb.add(btn_registration)


user_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

btn_game_loop = KeyboardButton("🎲🎲ИГРАТЬ🎲🎲")
btn_balance = KeyboardButton("💰БАЛАНС💰")

user_kb.add(btn_game_loop, btn_balance)

game_loop_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

btn_roll_dice =KeyboardButton("Бросить кости 🎲🎲")
btn_end_game = KeyboardButton("Закончить игру⛔")
game_loop_kb.add(btn_roll_dice, btn_end_game)
