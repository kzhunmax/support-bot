from aiogram import (
    Bot,
    Dispatcher,
    F,
    Router,
    html
)
from core.keyboard.inline import (
    select_language,
    ukrainian_select_message_type,
    english_select_message_type,
    rating_buttons
)
from aiogram.types import Message, CallbackQuery
from core.settings import settings
from aiogram.filters import Command
from core.utils.commands import set_commands
from typing import Any, Dict
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

bot = Bot(token=settings.bots.bot_token, parse_mode='HTML')
dp = Dispatcher()
form_router = Router()

boss_id = settings.bots.admin_id
user_data = {}


class Form(StatesGroup):
    language = State()
    name = State()
    surname = State()
    complaint_eng = State()
    proposal_eng = State()
    gratitude_eng = State()
    complaint_ukr = State()
    proposal_ukr = State()
    gratitude_ukr = State()


@dp.message(Command('start'))
async def command_start(message: Message, state: FSMContext) -> None:
    await set_commands(bot)
    await state.set_state(Form.language)
    language_message = await message.answer("Choose your language:", reply_markup=select_language)
    await state.update_data(language_message_id=language_message.message_id)


@dp.message(Command("restart"))
async def restart_bot(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("The bot has restarted")
    await command_start(message, state)


@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    selected_language = data.get("language")
    if selected_language == "English":
        if len(message.text) > 15:
            await message.answer(
                "Name should be less than 15 symbols, don't enter surname here, you will enter it soon")
        elif message.text.isalpha():
            await state.update_data(name=message.text)
            await state.set_state(Form.surname)
            await message.answer(f"Nice to meet you, {html.quote(message.text)}! Enter your surname")
        elif message.text == "/restart":
            return await restart_bot(message, state)
        elif message.text == "/continue":
            await message.answer("You must enter name")
        else:
            await message.answer("You must use only letters, no special characters or spaces")
    else:
        if len(message.text) > 15:
            await message.answer(
                "Ім'я повинно бути менше 15 символів, не вводьте тут прізвище, ви його введете незабаром")
        elif message.text.isalpha():
            await state.update_data(name=message.text)
            await state.set_state(Form.surname)
            await message.answer(f"Радий бачити, {html.quote(message.text)}! Введіть ваше прізвище")
        elif message.text == "/restart":
            return await restart_bot(message, state)
        elif message.text == "/continue":
            await message.answer("Ви повинні ввести ім'я")
        else:
            await message.answer("Ви повинні використовувати лише літери, без спеціальних символів та пробілів")


@dp.message(Form.surname)
async def process_surname(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    selected_language = data.get("language")
    if selected_language == "English":
        if len(message.text) > 15:
            await message.answer("Surname should be less than 15 symbols")
        elif message.text.isalpha():
            await state.update_data(surname=message.text)
            await show_summary(message=message, data=await state.get_data())
            user_data[message.chat.id] = await state.get_data()
            await state.clear()
        elif message.text == "/restart":
            return await restart_bot(message, state)
        elif message.text == "/continue":
            await message.answer("You must enter surname")
        else:
            await message.answer("You must use only letters, no special characters or spaces")
    else:
        if len(message.text) > 15:
            await message.answer("Прізвище повинно бути менше 15 символів")
        elif message.text.isalpha():
            await state.update_data(surname=message.text)
            await show_summary(message=message, data=await state.get_data())
            user_data[message.chat.id] = await state.get_data()
            await state.clear()
        elif message.text == "/restart":
            return await restart_bot(message, state)
        elif message.text == "/continue":
            await message.answer("Ви повинні ввести прізвище")
        else:
            await message.answer("Ви повинні використовувати лише літери, без спеціальних символів та пробілів")


@dp.callback_query(F.data == "ukrainian_language")
async def select_language_handler(callback: CallbackQuery, state: FSMContext):
    language = "Українську"
    await state.update_data(language=language)
    await state.set_state(Form.name)
    data = await state.get_data()
    language_message_id = data.get("language_message_id")
    await callback.message.answer(f"Вашою мовою вибрано <b>{language}</b>. Як вас звати?")
    if language_message_id:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=language_message_id)


@dp.callback_query(F.data == "english_language")
async def select_language_handler(callback: CallbackQuery, state: FSMContext):
    language = "English"
    await state.update_data(language=language)
    await state.set_state(Form.name)
    data = await state.get_data()
    language_message_id = data.get("language_message_id")
    await callback.message.answer(f"Your language is set to <b>{language}</b>. What's your name?")
    if language_message_id:
        await bot.delete_message(chat_id=callback.message.chat.id, message_id=language_message_id)


async def show_summary(message: Message, data: Dict[str, Any]) -> None:
    name = data["name"]
    surname = data["surname"]
    selected_language = data["language"]
    if selected_language == "English":
        await message.answer(f"Hello, <i>{html.quote(name)} {html.quote(surname)}</i>",
                             reply_markup=english_select_message_type)
    else:
        await message.answer(f"Привіт, <i>{html.quote(name)} {html.quote(surname)}</i>",
                             reply_markup=ukrainian_select_message_type)


@dp.callback_query(F.data == "cancel")
async def send_inline_buttons(callback: CallbackQuery, state: FSMContext):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    await callback.message.delete()
    await restart_bot(callback.message, state)


@dp.message(Command("info"))
async def info(message: Message):
    await message.answer(f"This bot is used to collect and send messages about your complaints, "
                         f"suggestions and acknowledgments. Send /restart, to restart the bot")


@dp.message(Command("continue"))
async def bot_continue(message: Message):
    user_id = message.chat.id
    data = user_data.get(user_id, {})
    name = data.get("name")
    surname = data.get("surname")
    selected_language = data.get("language")
    if selected_language is None:
        await message.answer(f"You must choose language\n"
                             f"Ви повинні вибрати мову")
    elif selected_language == "English":
        if name is None or surname is None:
            await message.answer("You must enter name and surname")
        else:
            await message.answer(f"Let's continue!", reply_markup=english_select_message_type)
    elif selected_language == "Українську":
        if name is None or surname is None:
            await message.answer("Ви повинні ввести ім'я та прізвище")
        else:
            await message.answer(f"Продовжуємо!", reply_markup=ukrainian_select_message_type)


@dp.callback_query(F.data == "complaint")
async def send_complaint(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Describe the problem, we will fix it")
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    await state.set_state(Form.complaint_eng)


@dp.message(Form.complaint_eng)
async def process_complaint(message: Message, state: FSMContext):
    user_id = message.chat.id
    data = user_data.get(user_id, {})
    name = data.get("name", "")
    surname = data.get("surname", "")
    complaint_text = message.text
    await bot.send_message(boss_id, f"Name: {name}, surname: {surname}, complaint describing: \n{complaint_text}")
    await state.clear()
    await message.answer("Thank you for your complaint. We will address it as soon as possible. If you want to "
                         "continue use this bot send /continue")


@dp.callback_query(F.data == "proposal")
async def send_proposal(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "What can we improve?")
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    await state.set_state(Form.proposal_eng)


@dp.message(Form.proposal_eng)
async def process_proposal(message: Message, state: FSMContext):
    user_id = message.chat.id
    data = user_data.get(user_id, {})
    name = data.get("name", "")
    surname = data.get("surname", "")
    proposal_text = message.text
    await bot.send_message(boss_id, f"Name: {name}, surname: {surname}, proposal describing: \n{proposal_text}")
    await state.clear()
    await message.answer("Thank you for your proposal. We will address it as soon as possible. If you want to "
                         "continue use this bot send /continue")


@dp.callback_query(F.data == "gratitude")
async def send_gratitude(callback: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    await bot.send_message(callback.from_user.id, "Rate our work", reply_markup=rating_buttons)


@dp.callback_query(F.data == "скарга")
async def send_complaint(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Опишіть вашу проблему, щоб ми могли її вирішити")
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    await state.set_state(Form.complaint_ukr)


@dp.message(Form.complaint_ukr)
async def process_complaint(message: Message, state: FSMContext):
    user_id = message.chat.id
    data = user_data.get(user_id, {})
    name = data.get("name", "")
    surname = data.get("surname", "")
    complaint_text = message.text
    await bot.send_message(boss_id, f"Ім'я: {name}, прізвище: {surname}, опис скарги: \n{complaint_text}")
    await state.clear()
    await message.answer("Дякуємо за вашу скаргу. Ми розглянемо її якнайшвидше. Якщо ви хочете "
                         "продовжувати роботу з ботом відправте /continue")


@dp.callback_query(F.data == "пропозиція")
async def send_proposal(callback: CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Що ми можемо покращити?")
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    await state.set_state(Form.proposal_ukr)


@dp.message(Form.proposal_ukr)
async def process_proposal(message: Message, state: FSMContext):
    user_id = message.chat.id
    data = user_data.get(user_id, {})
    name = data.get("name", "")
    surname = data.get("surname", "")
    proposal_text = message.text
    await bot.send_message(boss_id, f"Ім'я: {name}, прізвище: {surname}, опис пропозиції: \n{proposal_text}")
    await state.clear()
    await message.answer("Дякуємо за вашу пропозицію. Ми розглянемо її якнайшвидше. Якщо ви хочете "
                         "продовжувати роботу з ботом відправте /continue")


@dp.callback_query(F.data == "подяка")
async def send_gratitude(callback: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    await bot.send_message(callback.from_user.id, "Оцініть нашу роботу", reply_markup=rating_buttons)


@dp.callback_query(F.data == "one_star")
async def send_rating(callback: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})
    name = data.get("name")
    surname = data.get("surname")
    selected_language = data.get("language")
    await bot.send_message(boss_id, f"Ім'я: {name}, прізвище: {surname}, оцінив роботу готеля на одну зірку")
    if selected_language == "English":
        await bot.send_message(callback.from_user.id, "Thanks for rating us, we will try to improve our hotel. "
                                                      "If you want to continue use this bot send /continue")
    else:
        await bot.send_message(callback.from_user.id, "Дякуємо за ваш відгук, ми постараємось покращити наш готель. "
                                                      "Якщо ви хочете продовжувати роботу з ботом відправте "
                                                      "/continue")


@dp.callback_query(F.data == "two_stars")
async def send_rating(callback: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})
    name = data.get("name")
    surname = data.get("surname")
    selected_language = data.get("language")
    await bot.send_message(boss_id, f"Ім'я: {name}, прізвище: {surname}, оцінив роботу готеля на дві зірки")
    if selected_language == "English":
        await bot.send_message(callback.from_user.id, "Thanks for rating us, we will try to improve our hotel. "
                                                      "If you want to continue use this bot send /continue")
    else:
        await bot.send_message(callback.from_user.id, "Дякуємо за ваш відгук, ми постараємось покращити наш готель. "
                                                      "Якщо ви хочете продовжувати роботу з ботом відправте "
                                                      "/continue")


@dp.callback_query(F.data == "three_stars")
async def send_rating(callback: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})
    name = data.get("name")
    surname = data.get("surname")
    selected_language = data.get("language")
    await bot.send_message(boss_id, f"Ім'я: {name}, прізвище: {surname}, оцінив роботу готеля на три зірки")
    if selected_language == "English":
        await bot.send_message(callback.from_user.id, "Thanks for rating us, we will try to improve our hotel. "
                                                      "If you want to continue use this bot send /continue")
    else:
        await bot.send_message(callback.from_user.id, "Дякуємо за ваш відгук, ми постараємось покращити наш готель. "
                                                      "Якщо ви хочете продовжувати роботу з ботом відправте "
                                                      "/continue")


@dp.callback_query(F.data == "four_stars")
async def send_rating(callback: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})
    name = data.get("name")
    surname = data.get("surname")
    selected_language = data.get("language")
    await bot.send_message(boss_id, f"Ім'я: {name}, прізвище: {surname}, оцінив роботу готеля на чотири зірки")
    if selected_language == "English":
        await bot.send_message(callback.from_user.id, "Thanks for rating us, we will try to improve our hotel. "
                                                      "If you want to continue use this bot send /continue")
    else:
        await bot.send_message(callback.from_user.id, "Дякуємо за ваш відгук, ми постараємось покращити наш готель. "
                                                      "Якщо ви хочете продовжувати роботу з ботом відправте "
                                                      "/continue")


@dp.callback_query(F.data == "five_stars")
async def send_rating(callback: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})
    name = data.get("name")
    surname = data.get("surname")
    selected_language = data.get("language")
    await bot.send_message(boss_id, f"Ім'я: {name}, прізвище: {surname}, оцінив роботу готеля на п'ять зірки")
    if selected_language == "English":
        await bot.send_message(callback.from_user.id, "Thanks for rating us, we will try to improve our hotel. "
                                                      "If you want to continue use this bot send /continue")
    else:
        await bot.send_message(callback.from_user.id, "Дякуємо за ваш відгук, ми постараємось покращити наш готель. "
                                                      "Якщо ви хочете продовжувати роботу з ботом відправте "
                                                      "/continue")


@dp.callback_query(F.data == "six_stars")
async def send_rating(callback: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})
    name = data.get("name")
    surname = data.get("surname")
    selected_language = data.get("language")
    await bot.send_message(boss_id, f"Ім'я: {name}, прізвище: {surname}, подякував та оцінив роботу готеля на шість зірок")
    if selected_language == "English":
        await bot.send_message(callback.from_user.id, "Thanks for rating us, we will try to improve our hotel. "
                                                      "If you want to continue use this bot send /continue")
    else:
        await bot.send_message(callback.from_user.id, "Дякуємо за ваш відгук, ми постараємось покращити наш готель. "
                                                      "Якщо ви хочете продовжувати роботу з ботом відправте "
                                                      "/continue")


@dp.callback_query(F.data == "seven_stars")
async def send_rating(callback: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})
    name = data.get("name")
    surname = data.get("surname")
    selected_language = data.get("language")
    await bot.send_message(boss_id, f"Ім'я: {name}, прізвище: {surname}, подякував та оцінив роботу готеля на сім зірок")
    if selected_language == "English":
        await bot.send_message(callback.from_user.id, "Thanks for rating us, we will try to improve our hotel. "
                                                      "If you want to continue use this bot send /continue")
    else:
        await bot.send_message(callback.from_user.id, "Дякуємо за ваш відгук, ми постараємось покращити наш готель. "
                                                      "Якщо ви хочете продовжувати роботу з ботом відправте "
                                                      "/continue")


@dp.callback_query(F.data == "eight_stars")
async def send_rating(callback: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})
    name = data.get("name")
    surname = data.get("surname")
    selected_language = data.get("language")
    await bot.send_message(boss_id, f"Ім'я: {name}, прізвище: {surname}, подякував та оцінив роботу готеля на вісім зірок")
    if selected_language == "English":
        await bot.send_message(callback.from_user.id, "Thanks for rating us, we will try to improve our hotel. "
                                                      "If you want to continue use this bot send /continue")
    else:
        await bot.send_message(callback.from_user.id, "Дякуємо за ваш відгук, ми постараємось покращити наш готель. "
                                                      "Якщо ви хочете продовжувати роботу з ботом відправте "
                                                      "/continue")


@dp.callback_query(F.data == "nine_stars")
async def send_rating(callback: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})
    name = data.get("name")
    surname = data.get("surname")
    selected_language = data.get("language")
    await bot.send_message(boss_id, f"Ім'я: {name}, прізвище: {surname}, подякував та оцінив роботу готеля на дев'ять зірок")
    if selected_language == "English":
        await bot.send_message(callback.from_user.id, "Thanks for rating us, we will try to improve our hotel. "
                                                      "If you want to continue use this bot send /continue")
    else:
        await bot.send_message(callback.from_user.id, "Дякуємо за ваш відгук, ми постараємось покращити наш готель. "
                                                      "Якщо ви хочете продовжувати роботу з ботом відправте "
                                                      "/continue")


@dp.callback_query(F.data == "ten_stars")
async def send_rating(callback: CallbackQuery):
    await bot.edit_message_reply_markup(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                                        reply_markup=None)
    user_id = callback.from_user.id
    data = user_data.get(user_id, {})
    name = data.get("name")
    surname = data.get("surname")
    selected_language = data.get("language")
    await bot.send_message(boss_id, f"Ім'я: {name}, прізвище: {surname}, подякував та оцінив роботу готеля на десять зірок")
    if selected_language == "English":
        await bot.send_message(callback.from_user.id, "Thanks for rating us, we will try to improve our hotel. "
                                                      "If you want to continue use this bot send /continue")
    else:
        await bot.send_message(callback.from_user.id, "Дякуємо за ваш відгук, ми постараємось покращити наш готель. "
                                                      "Якщо ви хочете продовжувати роботу з ботом відправте "
                                                      "/continue")


@dp.message()
async def echo(message: Message):
    await message.answer("This command is not registered")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(form_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
