from config_data.config import load_config, Config
from aiogram import F
from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message

from database.database import db_connect, save_user_request, get_user_request
from keyboards.keyboards import main_keyboard, cancel_keyboard, level_keyboard, target_keyboard, time_keyboard
from lexicon.lexicon import LEXICON_RU
from states.states import UserInformation

# Создаем "базу данных" пользователей
user_dict: dict[int, dict[str, str | int | bool]] = {}
config: Config = load_config()
bot = Bot(token=config.tg_bot.token)
router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=main_keyboard
    )
    await db_connect()


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


# Этот хэндлер срабатывает на кноппку cancel
@router.callback_query(F.data.in_(['cancel_pressed']))
async def apply_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='Подача заявки отменена!')
    await state.clear()
    await callback.message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=main_keyboard
    )


# Этот хэндлер срабатывает на кнопку /check request
@router.callback_query(F.data.in_(['check request']))
async def check_button_press(callback: CallbackQuery, state: FSMContext):
    # Отправляем пользователю анкету, если она есть в "базе данных"
    if get_user_request(callback.from_user.id) is not None:
        user_data: tuple = get_user_request(callback.from_user.id)
        await callback.message.answer(text=f'Анкета была отправлена!✉️\n\nВаши данные📄:\nИмя: {user_data[1]}\nУровень английского: {user_data[2]}\nВозраст: {user_data[3]}\nЦель обучения: {user_data[4]}\nТелефон: {user_data[5]}\nУдобное время для занятий: {user_data[6]}', reply_markup=main_keyboard)
    # Если анкеты пользователя в базе нет - предлагаем заполнить
    else:
        get_user_request(callback.from_user.id)
        await callback.message.answer(text='Вы еще не заполняли анкету. Чтобы приступить - '
                                           "нажмите кнопку <✅Подать заявку>")


# Этот хэндлер срабатывает на кнопку /apply
@router.callback_query(F.data.in_(['apply_button_pressed']))
async def apply_button_press(callback: CallbackQuery, state: FSMContext):
    if get_user_request(callback.from_user.id) is None:
        await callback.message.edit_text(text='Пожалуйста, введите ваше имя:', reply_markup=cancel_keyboard)
        await state.set_state(UserInformation.name)
    else:
        await callback.message.answer(text='Вы уже заполнили заявку!\n\nВы можете посмотреть свою заявку нажав кнопку\n в главном меню <👀Посмотреть мою заявку> 👇', reply_markup=main_keyboard)


# Этот хэндлер будет срабатывать, если введено корректное имя
# и переводить в состояние ожидания ввода уровня английского языка
@router.message(StateFilter(UserInformation.name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(text='Спасибо!\n\nУкажите свой уровень английского из списка или отправьте свой вариант: '
                              'вариант:', reply_markup=level_keyboard)
    await state.set_state(UserInformation.language_level)


# Этот хэндлер будет срабатывать, если во время ввода имени
# будет введено что-то некорректное
@router.message(StateFilter(UserInformation.name))
async def warning_not_name(message: Message):
    await message.answer(
        text='То, что вы отправили не похоже на имя\n\n'
             'Пожалуйста, введите ваше имя!\n\n'
             'Если вы хотите прервать заполнение анкеты - '
             'нажмите кеопку "Отмена подачи заявки', reply_markup=cancel_keyboard)


# Этот хэндлер будет срабатывать, если введен уровень английского языка
# и переводить в состояние ввода возраста
@router.callback_query(StateFilter(UserInformation.language_level), F.data.in_(
    ['beginner', 'intermediate', 'advanced', 'dont know']))
async def process_level_sent1(callback: CallbackQuery, state: FSMContext):
    # Cохраняем уровень английского в хранилище по ключу "level"
    await state.update_data(level=callback.data)
    await callback.message.delete()
    await callback.message.answer(
        text='Спасибо! Укажите свой возраст:'
    )
    # Устанавливаем состояние ожидания ввода возраста
    await state.set_state(UserInformation.age)


@router.callback_query(F.data.in_('own answer'))
async def process_level_sent2(callback: CallbackQuery, state: FSMContext):
    # Cохраняем уровень английского в хранилище по ключу "level"
    await callback.message.edit_text(text='Введите свой вариант ответа о уровне английского языка:',
                                     reply_markup=cancel_keyboard)
    await state.set_state(UserInformation.language_level)


@router.message(StateFilter(UserInformation.language_level), F.text.isalnum())
async def process_level_sent1(message: Message, state: FSMContext):
    # Cохраняем уровень английского в хранилище по ключу "level"
    await state.update_data(level=message.text)
    await message.answer(
        text='Спасибо! Укажите свой возраст:')


# Этот хэндлер будет срабатывать, если введен корректный возраст
# и переводить в состояние выбора цели изучения английского языка
@router.message(StateFilter(UserInformation.age), lambda x: x.text.isdigit() and 7 <= int(x.text) <= 60)
async def process_age_sent(message: Message, state: FSMContext):
    # Cохраняем возраст в хранилище по ключу "age"
    await state.update_data(age=message.text)
    await message.answer(text='Спасибо!\n\nУкажите цель изучения английского языка:', reply_markup=target_keyboard)
    # Устанавливаем состояние ожидания выбора цели изучения английского языка
    await state.set_state(UserInformation.learn_target)


# Этот хэндлер будет срабатывать, если во время ввода возраста
# будет введено что-то некорректное
@router.message(StateFilter(UserInformation.age))
async def warning_not_age(message: Message):
    await message.answer(text='Возраст должен быть целым числом от 7 до 60\n\n''Попробуйте еще раз\n\n''Если вы '
                              'хотите прервать заполнение анкеты - нажмите кеопку "Отмена подачи заявки',
                         reply_markup=cancel_keyboard)


# Этот хэндлер будет срабатывать, если введена цель изучения английского языка
# и переводить в состояние ввода номера телефона
@router.callback_query(StateFilter(UserInformation.learn_target), F.data.in_(
    ['for work', 'for exam prep', 'for school', 'for self development']))
async def process_target_sent(callback: CallbackQuery, state: FSMContext):
    # Cохраняем уровень английского в хранилище по ключу "target"
    await state.update_data(target=callback.data)
    await callback.message.delete()
    await callback.message.answer(
        text='Спасибо! Укажите свой номер телефона для связи в формате 8xxxxxxxxxx:'
    )
    # Устанавливаем состояние ожидания ввода номера телефона
    await state.set_state(UserInformation.telephone)


# Этот хэндлер будет срабатывать, если введен корректный номер телефона
# и переводить в состояние выбора цели изучения английского языка
@router.message(StateFilter(UserInformation.telephone), lambda x: x.text.isdigit())
async def process_telephone_sent(message: Message, state: FSMContext):
    # Cохраняем телефон в хранилище по ключу "telephone"
    await state.update_data(telephone=message.text)
    await message.answer(text='Спасибо!\n\nВыберите промежуток времени удобного вам для обучения:',
                         reply_markup=time_keyboard)
    # Устанавливаем состояние ожидания выбора промежутка времени изучения английского языка
    await state.set_state(UserInformation.time_priority)


# Этот хэндлер будет срабатывать, если во время ввода телефона
# будет введено что-то некорректное
@router.message(StateFilter(UserInformation.telephone))
async def warning_not_telephone(message: Message):
    await message.answer(
        text='Номер телефона должен из чисел в формате 8xxxxxxxxxx\n\n''Попробуйте еще раз\n\n''Если вы '
             'хотите прервать заполнение анкеты - нажмите кеопку "Отмена подачи заявки',
        reply_markup=cancel_keyboard)


# Этот хэндлер будет срабатывать, если выбран промежуток времени для проведения занятия
# и переходить к сохранению заполненной анкеты
@router.callback_query(StateFilter(UserInformation.time_priority),
                       F.data.in_(['in the morning', 'in the afternoon', 'in the evening']))
async def process_target_sent(callback: CallbackQuery, state: FSMContext):
    # Cохраняем уровень английского в хранилище по ключу "time"
    await state.update_data(time=callback.data)
    await callback.message.delete()
    # Добавляем в "базу данных" анкету пользователя
    # по ключу id пользователя
    user_dict[callback.from_user.id] = await state.get_data()
    await save_user_request(user_dict)
    # Завершаем машину состояний
    await state.clear()
    await callback.message.answer(
        text='Спасибо! Ваши данные сохранены!\n\n''С вами свяжутся в ближайшее время для уточнения деталей!', reply_markup=main_keyboard
    )

    await bot.send_message(text=f'Имя:{user_dict[callback.from_user.id]['name']}\n'
                                f'Уровень английского: {user_dict[callback.from_user.id]['level']}\n'
                                f'Возраст: {user_dict[callback.from_user.id]['age']}\n'
                                f'Цель обучения: {user_dict[callback.from_user.id]['target']}\n'
                                f'Телефон: {user_dict[callback.from_user.id]['telephone']}\n'
                                f'Удобное время для занятий: {user_dict[callback.from_user.id]['time']}',
                           chat_id=1726588078
                           )
