from aiogram import Bot, types, Dispatcher
from aiogram.utils import executor
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from telegrambot.save_login_password.bot_dp1 import *
import os


bot = Bot('5412674596:AAEn0fN0AvcyHgNhpHuH69-RnSL3IzZRIE8')
dp = Dispatcher(bot, storage=MemoryStorage())
admin_id = 976896597


users = {}


class FSMAdmin(StatesGroup):
    show_info = State()
    get_login = State()
    get_password = State()
    accept = State()
    get_info = State()
    delete_accounts = State()
    delete_login = State()


@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, 'Вход отменен', reply_markup=user_srart_kb)
    await FSMAdmin.show_info.set()


@dp.message_handler(Text(equals=['Добавить аккаунт', 'Показать информацию', 'Удалить все аккаунты',
                                 'Удалить один аккаунт'], ignore_case=True))
async def start_choice(message: types.Message, state: FSMContext):
    if message.text == 'Добавить аккаунт':
        await bot.send_message(message.from_user.id, 'Введите логин', reply_markup=cancel_button)
        await FSMAdmin.get_login.set()
    elif message.text == 'Удалить все аккаунты':
        await sql_read_info(message=message)
        await state.finish()
    elif message.text == 'Удалить один аккаунт':
        await bot.send_message(message.from_user.id, 'Введите логин аккаунта который хотите удалить',
                               reply_markup=cancel_button)
        await FSMAdmin.delete_login.set()
    else:
        await sql_read_info(message)
        await state.finish()


@dp.message_handler(state=FSMAdmin.delete_login)
async def delete_account(message:types.Message,state:FSMContext):
    await delete_account_db(message=message, login=message.text)
    await state.finish()


@dp.message_handler(commands='start')
async def start_mess(message: types.Message, state: FSMContext):
    if message.from_user.id == admin_id:
        await bot.send_message(message.from_user.id, 'Выберите действие', reply_markup=user_srart_kb)
        await FSMAdmin.show_info.set()
    else:
        await bot.send_message(message.from_user.id, 'Вы не имеете прав для работы с этим ботом')


@dp.message_handler(state=FSMAdmin.show_info)
async def send_info(message: types.Message, state: FSMContext):
    if message.text == 'Показать информацию':
        await sql_read_info(message=message)
        await state.finish()

    elif message.text == 'Удалить все аккаунты':
        await delete_all_accounts(message=message)
        await state.finish()

    elif message.text == 'Удалить один аккаунт':
        await bot.send_message(message.from_user.id, 'Введите логин аккаунта который хотите удалить',
                               reply_markup=cancel_button)
        await FSMAdmin.delete_login.set()

    else:
        await bot.send_message(message.from_user.id, 'Введите логин', reply_markup=cancel_button)
        await FSMAdmin.get_login.set()


@dp.message_handler(state=FSMAdmin.get_login)
async def get_login(message: types.Message, state: FSMContext):
    async with state.proxy()as data:
        data['login'] = message.text

    await FSMAdmin.get_password.set()
    await bot.send_message(message.from_user.id, 'Введите пароль', reply_markup=cancel_button)


@dp.message_handler(state=FSMAdmin.get_password)
async def get_password(message: types.Message, state: FSMContext):
    global login, password, users
    async with state.proxy() as data:
        data['password'] = message.text

    login = data.get('login')
    password = data.get('password')
    await bot.send_message(message.from_user.id, f'Убедитесь в правильности введных данных\n\nЛогин: {login}, '
                                                 f'Пароль: {password}', reply_markup=yes_no_kb)
    await FSMAdmin.accept.set()


@dp.message_handler(state=FSMAdmin.accept)
async def accept(message: types.Message, state: FSMContext):
    global login, password, users
    if message.text == 'Да':
        try:
            await sql_add_account(login=login, password=password)
            await bot.send_message(message.from_user.id, 'Ваши данные успешно сохранены',
                                   reply_markup=user_srart_kb)
            await state.finish()
        except Exception as ex:
            print(repr(ex))
            await bot.send_message(message.from_user.id, 'Произошла ошибка возможно такой логин уже существует',
                                   reply_markup=user_srart_kb)
            await FSMAdmin.show_info.set()
    # if message.text == 'Да':
    #     users[login] = password
    #     print(users)
    #     await state.finish().
    # else:
    #     await bot.send_message(message.from_user.id,'Вход отменен,выберите действие', reply_markup=user_srart_kb)
    #     await FSMAdmin.show_info.set()


# ******************************************* buttons ************************************
user_srart_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Добавить аккаунт'))\
    .add(KeyboardButton('Показать информацию')).add(KeyboardButton('Удалить все аккаунты'))\
    .add(KeyboardButton('Удалить один аккаунт'))


cancel_button = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton('Отмена'))

choise_button = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(KeyboardButton('Добавить'))

yes_no_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('Да')).add(KeyboardButton('Нет'))

if __name__ == '__main__':
    print('bot polling started')
    sql_start()
    executor.start_polling(dp, skip_updates=True)

