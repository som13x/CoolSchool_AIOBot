from config_data.config import load_config, Config
from aiogram import F
from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.fsm.state import default_state, State, StatesGroup
from database.database import db_connect, save_user_request, get_user_request
from keyboards.keyboards import main_keyboard, cancel_keyboard, level_keyboard, target_keyboard, time_keyboard
from keyboards.keyboards import faq_keyboard, back_keyboard
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
    await state.clear()
    await callback.message.edit_text(
        text=LEXICON_RU['/start'],
        reply_markup=main_keyboard
    )


# Этот хэндлер срабатывает на кнопку /check request
@router.callback_query(F.data.in_(['check request']))
async def check_button_press(callback: CallbackQuery, state: FSMContext):
    # Отправляем пользователю анкету, если она есть в "базе данных"
    if get_user_request(callback.from_user.id) is not None:
        user_data: tuple = get_user_request(callback.from_user.id)
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(
            text=f'Анкета была отправлена!✉️\n\nВаши данные📄:\nИмя: {user_data[1]}\nУровень английского: {user_data[2]}\nВозраст: {user_data[3]}\nЦель обучения: {user_data[4]}\nТелефон: {user_data[5]}\nУдобное время для занятий: {user_data[6]}',
            reply_markup=cancel_keyboard)
    # Если анкеты пользователя в базе нет - предлагаем заполнить
    else:
        get_user_request(callback.from_user.id)
        await callback.message.delete_reply_markup()
        await callback.message.delete()
        await callback.message.answer(text='Вы еще не заполняли анкету. Чтобы приступить - '
                                           "нажмите кнопку <✅Подать заявку>", reply_markup=main_keyboard)


# Этот хэндлер срабатывает на кнопку /apply
@router.callback_query(F.data.in_(['apply_button_pressed']))
async def apply_button_press(callback: CallbackQuery, state: FSMContext):
    if get_user_request(callback.from_user.id) is None:
        await state.clear()
        await callback.message.edit_text(text='Пожалуйста, введите ваше имя:', reply_markup=cancel_keyboard)
        await state.set_state(UserInformation.name)
    else:
        await callback.message.delete_reply_markup()
        await callback.message.delete()
        await callback.message.answer(
            text='Вы уже заполнили заявку!\n\nВы можете посмотреть свою заявку нажав кнопку\n в главном меню <👀Посмотреть мою заявку> 👇',
            reply_markup=main_keyboard)


# Этот хэндлер срабатывает на кнопку /FAQ
@router.callback_query(F.data.in_(['faq_button_pressed']))
async def apply_button_press(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='Пожалуйста, выберете интересующий вас вопрос:', reply_markup=faq_keyboard)


# Этот хэндлер будет срабатывать, если выбран одна из кнопок FAQ
@router.callback_query(F.data.in_(['faq_button1']))
async def faq_answer_sent(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='- Есть ли индивидуальные занятия?\n\n- Нет. Для наиболее эффективного '
                                          ' процесса изучения языка мы придерживаемся группового формата, тк это '
                                          ' дает ряд колоссальных преимуществ (преодоление языкового барьера; '
                                          ' мотивация; сотрудничество; разнообразие; новые знакомства; '
                                          ' положительный пример; развитие навыков аудирования; стоимость '
                                          ' обучения; здоровая конкуренция) ', reply_markup=back_keyboard)


@router.callback_query(F.data.in_(['faq_button2']))
async def faq_answer_sent(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='- Есть ли подготовка к ОГЭ/ ЕГЭ?\n\n- Да, есть. Подготовка '
                                          'осуществляется в мини группах (2-4 чел).', reply_markup=back_keyboard)


@router.callback_query(F.data.in_(['faq_button3']))
async def faq_answer_sent(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='- Когда происходит набор в группы?\n\n- В мае- августе. Но! Если '
                                          'появляется место, мы связываемся с потенциальными учениками  из листа '
                                          'ожидания в течение года.', reply_markup=back_keyboard)


@router.callback_query(F.data.in_(['faq_button4']))
async def faq_answer_sent(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='- Как записаться на занятия?\n\n- Заполнить анкету, оставив свои данные. '
                                          'С вами свяжутся и пригласят на собеседование для определения уровня.',
                                     reply_markup=back_keyboard)


@router.callback_query(F.data.in_(['faq_button5']))
async def faq_answer_sent(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='- Кто преподаватель?\n\n- Юлия Смирнова (руководитель школы), преподаватель, '
                                          'лингвист, методист, сертифицирована Кембриджем, 15 лет в преподавании.',
                                     reply_markup=back_keyboard)


@router.callback_query(F.data.in_(['faq_button6']))
async def faq_answer_sent(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='- Сколько стоит обучение?\n\n- Обучение оплачивается авансом за месяц (от 8 '
                                          'до 10 занятий в месяц; занятия два раза в неделю). Оплачивать следует 1 '
                                          'числа каждого месяца. Стоимость одного занятия (60мин.):\n* школьники - '
                                          '1000р.\n* подготовка к ЕГЭ/ОГЭ - 1800р.\n* разговорный клуб - 1500р.',
                                     reply_markup=back_keyboard)


@router.callback_query(F.data.in_(['faq_button7']))
async def faq_answer_sent(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='- Сколько человек в группе?\n\n- От 4 до 8 человек (школьники); от 2-4 '
                                          'человек - ОГЭ/ЕГЭ; 2-6 человек - разговорный клуб.',
                                     reply_markup=back_keyboard)


@router.callback_query(F.data.in_(['faq_button8']))
async def faq_answer_sent(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='- Сколько длится обучение?\n\n- Обучение длится 9,5 месяцев (1 сентября - 15 '
                                          'июня). Предполагаются зимние каникулы(10 дней).',
                                     reply_markup=back_keyboard)


@router.callback_query(F.data.in_(['faq_button9']))
async def faq_answer_sent(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='- Можно ли получить чек об оплате образовательных услуг?\n\n- Да, для этого '
                                          'составляется и подписывается договор с двух сторон. Чек Вы получаете '
                                          'ежемесячно в электронном виде.', reply_markup=back_keyboard)


@router.callback_query(F.data.in_(['faq_button10']))
async def faq_answer_sent(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='- Есть ли домашние задания?\n\n- Да, домашнее задание является неотъемлемой '
                                          'частью обучения и служит цели закрепления изученного материала.',
                                     reply_markup=back_keyboard)


@router.callback_query(F.data.in_(['faq_button11']))
async def faq_answer_sent(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='- Где и как проходят занятия?\n\n- Занимаемся на платформе zoom, на доске '
                                          'MIRO. Занятие длится 60 минут. После занятия высылается домашнее задание; '
                                          'весь изученный материал на уроке остается у студентов.',
                                     reply_markup=back_keyboard)


@router.callback_query(F.data.in_(['faq_button12']))
async def faq_answer_sent(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='- Нужно ли покупать учебники?\n\n- Учебные материалы покупать не нужно. ',
                                     reply_markup=back_keyboard)


@router.callback_query(F.data.in_(['faq_button13']))
async def faq_answer_sent(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='- Как платить, если пропустил занятие?\n\n- В случае пропуска урока ученику '
                                          'высылается запись занятия для самостоятельного изучения. Оплата при этом '
                                          'не возвращается.', reply_markup=back_keyboard)


@router.callback_query(F.data.in_(['back_button_pressed']))
async def back_button_press(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete_reply_markup()
    await callback.message.edit_text(text='Пожалуйста, выберете интересующий вас вопрос:', reply_markup=faq_keyboard)


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
        text='Спасибо! Ваши данные сохранены!\n\n''С вами свяжутся в ближайшее время для уточнения деталей!',
        reply_markup=main_keyboard
    )

    await bot.send_message(text=f"Имя:{user_dict[callback.from_user.id]['name']}\n"
                                f"Уровень английского: {user_dict[callback.from_user.id]['level']}\n"
                                f"Возраст: {user_dict[callback.from_user.id]['age']}\n"
                                f"Цель обучения: {user_dict[callback.from_user.id]['target']}\n"
                                f"Телефон: {user_dict[callback.from_user.id]['telephone']}\n"
                                f"Удобное время для занятий: {user_dict[callback.from_user.id]['time']}",
                           chat_id=1726588078
                           )


# Этот хэндлер будет срабатывать на любые сообщения в состоянии "по умолчанию",
# кроме тех, для которых есть отдельные хэндлеры!
@router.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.delete()

