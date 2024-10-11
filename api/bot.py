import os
import telebot
from telebot import types
from flask import Flask, request

app = Flask(__name__)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

user_languages = {}
user_phone_numbers = {}
user_statuses = {}

# Установите вебхук
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    logging.info(f"Received update: {update}")  # Логируем полученное обновление
    if update:  # Проверяем, что обновление не пустое
        bot.process_new_updates([telebot.types.Update.de_json(update)])
    return '', 200  # Возвращаем 200 OK

# Установите вебхук
@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    bot.remove_webhook()  # Удаляем предыдущий вебхук, если он установлен
    webhook_url = f'https://glovo-food-delivery-39we4s6it-tsaigetsus-projects.vercel.app/webhook'  # Замените на URL вашего проекта на Vercel
    bot.set_webhook(url=webhook_url)  # Устанавливаем новый вебхук
    return 'Webhook set', 200

# Начальный хэндлер для выбора языка
@bot.message_handler(commands=['start', 'hello'])
def sendWelcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn_ru = types.KeyboardButton('Русский')
    btn_en = types.KeyboardButton('English')
    markup.add(btn_ru, btn_en)
    bot.send_message(message.chat.id, "Please select your language / Пожалуйста, выберите язык:", reply_markup=markup)

# Обработчик выбора языка
@bot.message_handler(func=lambda msg: msg.text in ['Русский', 'English'])
def handleLanguageSelection(message):
    if message.text == 'Русский':
        user_languages[message.chat.id] = 'ru'
        bot.send_message(message.chat.id, "Вы выбрали русский язык.")
    elif message.text == 'English':
        user_languages[message.chat.id] = 'en'
        bot.send_message(message.chat.id, "You have selected English.")
    showRegisterLogin(message)

# Показываем кнопки Register и Login после выбора языка
def showRegisterLogin(message):
    language = user_languages.get(message.chat.id)
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    if language == 'ru':
        btn_register = types.KeyboardButton('Регистрация')
        btn_login = types.KeyboardButton('Войти')
        markup.add(btn_register, btn_login)
        bot.send_message(message.chat.id, "Приветствую! Я бот по доставке еды. Пройдите регистрацию или залогиньтесь в свой аккаунт Glovo:", reply_markup=markup)
    else:
        btn_register = types.KeyboardButton('Register')
        btn_login = types.KeyboardButton('Login')
        markup.add(btn_register, btn_login)
        bot.send_message(message.chat.id, "Welcome! I am Food Delivery Bot. Please register or sign in your Glovo account:", reply_markup=markup)

# Обработчик нажатия на кнопку "Регистрация" или "Register"
@bot.message_handler(func=lambda msg: msg.text in ['Регистрация', 'Register'])
def handleRegister(message):
    language = user_languages.get(message.chat.id)
    user_statuses[message.chat.id] = 'register'  # Устанавливаем статус пользователя на регистрацию
    if language == 'ru':
        bot.send_message(message.chat.id, "Введите номер телефона в международном формате (Пример: +1 111111111):")
    else:
        bot.send_message(message.chat.id, "Please enter your phone number in international format (Example: +1 111111111):")
    bot.register_next_step_handler(message, handlePhoneNumber)

# Обработчик нажатия на кнопку "Войти" или "Login"
@bot.message_handler(func=lambda msg: msg.text in ['Войти', 'Login'])
def handleLogin(message):
    language = user_languages.get(message.chat.id)
    user_statuses[message.chat.id] = 'login'  # Устанавливаем статус пользователя на логин
    if language == 'ru':
        bot.send_message(message.chat.id, "Введите номер телефона в международном формате (Пример: +1 111111111):")
    else:
        bot.send_message(message.chat.id, "Please enter your phone number in international format (Example: +1 111111111):")
    bot.register_next_step_handler(message, handlePhoneNumber)

# Обработчик ввода номера телефона
def handlePhoneNumber(message):
    phoneNumber = message.text
    user_phone_numbers[message.chat.id] = phoneNumber
    language = user_languages.get(message.chat.id)

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn_yes = types.KeyboardButton('Да' if language == 'ru' else 'Yes')
    btn_change = types.KeyboardButton('Изменить' if language == 'ru' else 'Change')
    markup.add(btn_yes, btn_change)

    if language == 'ru':
        bot.send_message(message.chat.id, f"Ваш номер {phoneNumber}, правильно?", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"Your number is {phoneNumber}, correct?", reply_markup=markup)

# Обработчик подтверждения или изменения номера телефона
@bot.message_handler(func=lambda msg: msg.text in ['Да', 'Изменить', 'Yes', 'Change'])
def handleConfirmation(message):
    language = user_languages.get(message.chat.id)

    if message.text in ['Да', 'Yes']:
        if user_statuses[message.chat.id] == 'register':
            # Сообщение о том, что код отправлен на номер
            bot.send_message(message.chat.id, f"На ваш номер телефона: {user_phone_numbers[message.chat.id]} отправлено сообщение с кодом. Введите его ниже.")
            # Здесь можно добавить логику для обработки кода
            bot.register_next_step_handler(message, handleCodeInput)  # Регистрация обработчика для ввода кода
            return
        elif user_statuses[message.chat.id] == 'login':
            # Сообщение о том, что код отправлен на номер при логине
            bot.send_message(message.chat.id, f"На ваш номер телефона: {user_phone_numbers[message.chat.id]} отправлено сообщение с кодом. Введите его ниже.")
            # Здесь можно добавить логику для обработки кода
            bot.register_next_step_handler(message, handleCodeInput)  # Регистрация обработчика для ввода кода
            return

        if language == 'ru':
            bot.send_message(message.chat.id, "Спасибо! Номер сохранен.")
        else:
            bot.send_message(message.chat.id, "Thank you! Your number is saved.")

    elif message.text in ['Изменить', 'Change']:
        if language == 'ru':
            bot.send_message(message.chat.id, "Введите новый номер телефона:")
        else:
            bot.send_message(message.chat.id, "Please enter a new phone number:")
        bot.register_next_step_handler(message, handlePhoneNumber)

# Обработчик ввода кода
def handleCodeInput(message):
    code = message.text
    # Здесь можно добавить логику для проверки кода
    bot.send_message(message.chat.id, f"Вы ввели код: {code}.")  # Например, подтверждение кода

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
