import os
import logging
import re
import paramiko
import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, ConversationHandler, MessageHandler, Filters

# Загружаем переменные среды из файла .env
load_dotenv()

# # Подключаем логирование
logging.basicConfig(
    filename='logfile.txt', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

# Токен Telegram-бота
TOKEN = os.getenv("TOKEN")

# Учетные данные SSH
SSH_HOST = os.getenv("RM_HOST")
SSH_PORT = os.getenv("RM_PORT")
SSH_USER = os.getenv("RM_USER")
SSH_PASSWORD = os.getenv("RM_PASSWORD")

# Учетные данные DB
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_DATABASE = os.getenv("DB_DATABASE")

# Инициализируем SSH-клиент
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh_client.close()

# Функция для установления SSH-соединения
def ssh_connect():
    ssh_client.connect(hostname=SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, port=SSH_PORT)

# Функция для выполнения команд через SSH
def execute_command(command):
    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode('utf-8')
    return output

def create_reply_keyboard(commands):
    keyboard = [[KeyboardButton(command) for command in commands]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def start(update: Update, context: CallbackContext) -> None:
    reply_keyboard = [['/find_email', '/find_phone_number'],
                      ['/get_emails', '/get_phone_numbers'],
                      ['/verify_password', '/get_repl_logs'],
                      ['/get_release', '/get_uname'],
                      ['/get_uptime', '/get_df', '/get_free', '/get_mpstat'],
                      ['/get_w', '/get_auths', '/get_critical', '/get_ps'],
                      ['/get_ss', '/get_apt_list', '/get_services']]

    update.message.reply_text('Пожалуйста, выберите команду:',
    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))


def find_emailCommand(update: Update, context: CallbackContext):
    reply_keyboard = create_reply_keyboard(['/start'])
    update.message.reply_text('Введите текст для поиска email: ', reply_markup=reply_keyboard)

    return 'find_email'

def find_email(update: Update, context) -> None:
    global emails
    text = update.message.text
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
    if emails:
        update.message.reply_text(f"Email-адреса найдены: {', '.join(emails)}")
        update.message.reply_text("Записать в базу данных? (ответьте 'да' или 'нет')")
        return 'write_email'
    else:
        update.message.reply_text("Email-адреса не найдены")
        return ConversationHandler.END


def write_email(update: Update, context: CallbackContext):
    global emails
    text = update.message.text
    if (text == "да"):
        try:
            connection = psycopg2.connect(user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT, 
                database=DB_DATABASE)
            cursor = connection.cursor()
            cursor.execute("SELECT email FROM emails;")
            email_rows = len(cursor.fetchall())
            for i in range(len(emails)):
                email_rows += 1
                cursor.execute(f'INSERT INTO emails VALUES{email_rows, emails[i]};')
            connection.commit() 
            logging.info("Команда успешно выполнена")
            update.message.reply_text("Команда успешно выполнена")
        except (Exception, Error) as error:
            logging.error(f'Ошибка при работе с PostgreSQL: {error}')
            update.message.reply_text(f'Ошибка при работе с PostgreSQL: {error}')
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")

        return ConversationHandler.END

    elif (text == "нет"):
        return ConversationHandler.END


def findPhoneNumbersCommand(update: Update, context: CallbackContext):
    reply_keyboard = create_reply_keyboard(['/start'])
    update.message.reply_text('Введите текст для поиска телефонных номеров: ', reply_markup=reply_keyboard)

    return 'find_phone_number'

def find_phone_number(update: Update, context: CallbackContext):
    global phoneNumberList
    user_input = update.message.text # Получаем текст, содержащий(или нет) номера телефонов
    phoneNumRegex = re.compile(r'(?:\+7|8)(?: \(\d{3}\) \d{3}-\d{2}-\d{2}|\d{10}|\(\d{3}\)\d{7}| \d{3} \d{3} \d{2} \d{2}| \(\d{3}\) \d{3} \d{2} \d{2}|-\d{3}-\d{3}-\d{2}-\d{2})')
    phoneNumberList = phoneNumRegex.findall(user_input) # Ищем номера телефонов

    if not phoneNumberList: # Обрабатываем случай, когда номеров телефонов нет
        update.message.reply_text('Телефонные номера не найдены')
        return # Завершаем выполнение функции

    phoneNumbers = '' # Создаем строку, в которую будем записывать номера телефонов
    for i in range(len(phoneNumberList)):
        phoneNumbers += f'{i+1}. {phoneNumberList[i]}\n' # Записываем очередной номер

    update.message.reply_text(phoneNumbers) # Отправляем сообщение пользователю
    update.message.reply_text("Записать в базу данных? (ответьте 'да' или 'нет')")
    return 'write_phone_number'

def write_phone_number(update: Update, context: CallbackContext):
    global phoneNumberList
    text = update.message.text
    if (text == "да"):
        try:
            connection = psycopg2.connect(user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT, 
                database=DB_DATABASE)
            cursor = connection.cursor()
            cursor.execute("SELECT phone_number FROM phone_numbers;")
            phone_number_rows = len(cursor.fetchall())
            for i in range(len(phoneNumberList)):
                phone_number_rows += 1
                cursor.execute(f'INSERT INTO phone_numbers VALUES{phone_number_rows, phoneNumberList[i]};')
            connection.commit() 
            logging.info("Команда успешно выполнена")
            update.message.reply_text("Команда успешно выполнена")
        except (Exception, Error) as error:
            logging.error(f'Ошибка при работе с PostgreSQL: {error}')
            update.message.reply_text(f'Ошибка при работе с PostgreSQL: {error}')
        finally:
            if connection is not None:
                cursor.close()
                connection.close()
                logging.info("Соединение с PostgreSQL закрыто")

        return ConversationHandler.END

    elif (text == "нет"):
        return ConversationHandler.END


def verify_passwordCommand(update: Update, context: CallbackContext):
    reply_keyboard = create_reply_keyboard(['/start'])
    update.message.reply_text('Введите пароль: ', reply_markup=reply_keyboard)

    return 'verify_password'

def verify_password(update: Update, context: CallbackContext) -> None:
    password = update.message.text
    lenFlag = A_ZFlag = a_zFlag = num_Flag = spe_symFlag = 0

    spe_sym = "!@#$%^&*()"

    if len(password) > 7:
        lenFlag = 1

    for i in password:
        if i.isalpha():
            if i.isupper():
                A_ZFlag = 1
            else:
                a_zFlag = 1
        elif i.isdigit():
            num_Flag = 1
        elif i in spe_sym:
            spe_symFlag = 1

    if lenFlag * A_ZFlag * a_zFlag * num_Flag * spe_symFlag == 0:
        update.message.reply_text('Пароль простой')
    else:
        update.message.reply_text('Пароль сложный')

    return ConversationHandler.END



def get_emails(update: Update, context: CallbackContext):
    try:
        connection = psycopg2.connect(user=DB_USER,
                                password=DB_PASSWORD,
                                host=DB_HOST,
                                port=DB_PORT, 
                                database=DB_DATABASE)
        cursor = connection.cursor()
        cursor.execute("SELECT email FROM emails;")
        data = cursor.fetchall()
        result = ''
        for i in range(len(data)):
            result += f'{i+1}. {data[i][0]}\n' 
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error(f'Ошибка при работе с PostgreSQL: {error}')
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
    update.message.reply_text(result)


def get_phone_numbers(update: Update, context: CallbackContext):
    try:
        connection = psycopg2.connect(user=DB_USER,
                                password=DB_PASSWORD,
                                host=DB_HOST,
                                port=DB_PORT, 
                                database=DB_DATABASE)
        cursor = connection.cursor()
        cursor.execute("SELECT phone_number FROM phone_numbers;")
        data = cursor.fetchall()
        result = ''
        for i in range(len(data)):
            result += f'{i+1}. {data[i][0]}\n' 
        logging.info("Команда успешно выполнена")
    except (Exception, Error) as error:
        logging.error(f'Ошибка при работе с PostgreSQL: {error}')
    finally:
        if connection is not None:
            cursor.close()
            connection.close()
    update.message.reply_text(result)


# Функции мониторинга Linux-системы
def get_repl_logs(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Чтобы получить информацию о логах репликации, нужно подключиться к пользователю с правами root, иначе информация будет недоступна')
    ssh_connect()
    logs = execute_command(f'cat /var/log/postgresql/* | grep repl | tail -n 20')
    update.message.reply_text(logs)

def get_release(update: Update, context: CallbackContext) -> None:
    ssh_connect()
    release_info = execute_command("lsb_release -a")
    update.message.reply_text(release_info)

def get_uname(update: Update, context: CallbackContext) -> None:
    ssh_connect()
    uname_info = execute_command("uname -a")
    update.message.reply_text(uname_info)

def get_uptime(update: Update, context: CallbackContext) -> None:
    ssh_connect()
    uptime_info = execute_command("uptime")
    update.message.reply_text(uptime_info)

def get_df(update: Update, context: CallbackContext) -> None:
    ssh_connect()
    df_info = execute_command("df -h")
    update.message.reply_text(df_info)

def get_free(update: Update, context: CallbackContext) -> None:
    ssh_connect()
    free_info = execute_command("free -m")
    update.message.reply_text(free_info)

def get_mpstat(update: Update, context: CallbackContext) -> None:
    ssh_connect()
    mpstat_info = execute_command("mpstat")
    update.message.reply_text(mpstat_info)

def get_w(update: Update, context: CallbackContext) -> None:
    ssh_connect()
    w_info = execute_command("w")
    update.message.reply_text(w_info)

def get_auths(update: Update, context: CallbackContext) -> None:
    ssh_connect()
    auths_info = execute_command("last -n 10")
    update.message.reply_text(auths_info)

def get_critical(update: Update, context: CallbackContext) -> None:
    ssh_connect()
    critical_info = execute_command("journalctl -p crit -n 5")
    update.message.reply_text(critical_info)

def get_ps(update: Update, context: CallbackContext) -> None:
    ssh_connect()
    ps_info = execute_command("ps aux | head -n 10")
    update.message.reply_text(ps_info)

def get_ss(update: Update, context: CallbackContext) -> None:
    ssh_connect()
    ss_info = execute_command("ss -tuln")
    update.message.reply_text(ss_info)

def get_apt_listCommand(update: Update, context: CallbackContext):
    update.message.reply_text('Введите --all, если хотите получить данные обо всех установленных пакетах, или --find [имя пакета], если хотите узнать данные о конкретном пакете')

    return 'get_apt_list'

def get_apt_list(update: Update, context: CallbackContext) -> None:
    ssh_connect()
    user_input = update.message.text
    if (user_input[:5] == "--all"):
        data = execute_command("apt list --installed | head -n 10")
        update.message.reply_text(data)
    elif (user_input[:6] == "--find"):
        command = "apt show " + user_input[7:]
        data = execute_command(command)
        update.message.reply_text(data)
    return ConversationHandler.END


def get_services(update: Update, context: CallbackContext) -> None:
    ssh_connect()
    services_info = execute_command("systemctl --type=service --state=running")
    update.message.reply_text(services_info)


def main() -> None:
    # Инициализируем бота
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    #Обработчик диалога find_email
    convHandlerfind_email = ConversationHandler(
        entry_points=[CommandHandler('find_email', find_emailCommand)],
        states={
            'find_email': [MessageHandler(Filters.text & ~Filters.command, find_email)],
            'write_email': [MessageHandler(Filters.text & ~Filters.command, write_email)],
        },
        fallbacks=[]
    )

    #Обработчик диалога find_phone_number
    convHandlerfind_phone_number = ConversationHandler(
        entry_points=[CommandHandler('find_phone_number', findPhoneNumbersCommand)],
        states={
            'find_phone_number': [MessageHandler(Filters.text & ~Filters.command, find_phone_number)],
            'write_phone_number': [MessageHandler(Filters.text & ~Filters.command, write_phone_number)],
        },
        fallbacks=[]
    )

    #Обработчик диалога verify_password
    convHandlerverify_password = ConversationHandler(
        entry_points=[CommandHandler('verify_password', verify_passwordCommand)],
        states={
            'verify_password': [MessageHandler(Filters.text & ~Filters.command, verify_password)],
        },
        fallbacks=[]
    )

    #Обработчик диалога get_apt_list
    convHandlerget_apt_list = ConversationHandler(
        entry_points=[CommandHandler('get_apt_list', get_apt_listCommand)],
        states={
            'get_apt_list': [MessageHandler(Filters.text & ~Filters.command, get_apt_list)],
        },
        fallbacks=[]
    )

    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(convHandlerfind_email)
    dispatcher.add_handler(convHandlerfind_phone_number)
    dispatcher.add_handler(convHandlerverify_password)
    dispatcher.add_handler(CommandHandler("get_repl_logs", get_repl_logs))
    dispatcher.add_handler(CommandHandler("get_release", get_release))
    dispatcher.add_handler(CommandHandler("get_uname", get_uname))
    dispatcher.add_handler(CommandHandler("get_uptime", get_uptime))
    dispatcher.add_handler(CommandHandler("get_df", get_df))
    dispatcher.add_handler(CommandHandler("get_free", get_free))
    dispatcher.add_handler(CommandHandler("get_mpstat", get_mpstat))
    dispatcher.add_handler(CommandHandler("get_w", get_w))
    dispatcher.add_handler(CommandHandler("get_auths", get_auths))
    dispatcher.add_handler(CommandHandler("get_critical", get_critical))
    dispatcher.add_handler(CommandHandler("get_ps", get_ps))
    dispatcher.add_handler(CommandHandler("get_ss", get_ss))
    dispatcher.add_handler(convHandlerget_apt_list)
    dispatcher.add_handler(CommandHandler("get_services", get_services))
    dispatcher.add_handler(CommandHandler("get_emails", get_emails))
    dispatcher.add_handler(CommandHandler("get_phone_numbers", get_phone_numbers))

    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

