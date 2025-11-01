import telebot
import sqlite3
import random
import logging
import time

# --- BOT SETTINGS ---
# Insert your token obtained from @BotFather.
BOT_TOKEN = ''  # <<< INSERT YOUR TOKEN HERE
# Insert your numerical Telegram User ID to receive notifications.
ADMIN_ID = 0  # <<< INSERT YOUR TELEGRAM ID HERE

# List of swear words to filter (can be extended)
SWEAR_WORDS = ['дурак', 'идиот', 'олух']  # Example

# Warning settings
WARNING_LIMIT = 3

# Captcha settings
CAPTCHA_MIN_NUMBER = 1
CAPTCHA_MAX_NUMBER = 10

# --- INITIALIZATION ---
bot = telebot.TeleBot(BOT_TOKEN)
DB_NAME = 'users.db'

# Logger setup
class TelegramLogHandler(logging.Handler):
    def __init__(self, bot, chat_id):
        super().__init__()
        self.bot = bot
        self.chat_id = chat_id

    def emit(self, record):
        log_entry = self.format(record)
        try:
            self.bot.send_message(self.chat_id, log_entry)
        except telebot.apihelper.ApiTelegramException:
            pass

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Dictionary to store captchas for new users {user_id: correct_answer}
pending_captchas = {}

# --- DATABASE HANDLING ---

def init_db():
    '''Initializes the database and creates the tables if they don't exist.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                is_bot BOOLEAN,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                language_code TEXT,
                join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                warnings INTEGER DEFAULT 0,
                is_verified BOOLEAN DEFAULT 0,
                muted INTEGER DEFAULT 0,
                banned INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_settings (
                chat_id INTEGER PRIMARY KEY,
                welcome_message TEXT,
                rules TEXT,
                delete_links BOOLEAN DEFAULT 0,
                delete_forwards BOOLEAN DEFAULT 0,
                delete_files BOOLEAN DEFAULT 0,
                log_channel INTEGER
            )
        ''')
        conn.commit()

def get_chat_settings(chat_id: int) -> dict:
    '''Gets the settings for a chat.'''
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM chat_settings WHERE chat_id = ?', (chat_id,))
        result = cursor.fetchone()
        return dict(result) if result else {}

def set_welcome_message_db(chat_id: int, message: str):
    '''Sets the welcome message for a chat.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO chat_settings (chat_id, welcome_message) VALUES (?, ?)',
            (chat_id, message)
        )
        conn.commit()

def set_rules_db(chat_id: int, rules: str):
    '''Sets the rules for a chat.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE chat_settings SET rules = ? WHERE chat_id = ?',
            (rules, chat_id)
        )
        conn.commit()

def set_delete_links_db(chat_id: int, delete_links: bool):
    '''Sets the delete links setting for a chat.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE chat_settings SET delete_links = ? WHERE chat_id = ?',
            (delete_links, chat_id)
        )
        conn.commit()

def set_delete_forwards_db(chat_id: int, delete_forwards: bool):
    '''Sets the delete forwards setting for a chat.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE chat_settings SET delete_forwards = ? WHERE chat_id = ?',
            (delete_forwards, chat_id)
        )
        conn.commit()

def set_delete_files_db(chat_id: int, delete_files: bool):
    '''Sets the delete files setting for a chat.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE chat_settings SET delete_files = ? WHERE chat_id = ?',
            (delete_files, chat_id)
        )
        conn.commit()

def set_log_channel_db(chat_id: int, log_channel: int):
    '''Sets the log channel for a chat.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE chat_settings SET log_channel = ? WHERE chat_id = ?',
            (log_channel, chat_id)
        )
        conn.commit()

def add_or_update_user(user: telebot.types.User):
    '''Adds a new user or updates an existing one.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            'SELECT * FROM users WHERE user_id = ?', (user.id,)
        )
        if cursor.fetchone() is None:
            cursor.execute(
                '''INSERT INTO users (user_id, is_bot, first_name, last_name, username, language_code)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (user.id, user.is_bot, user.first_name, user.last_name, user.username, user.language_code)
            )
        else:
            cursor.execute(
                '''UPDATE users SET first_name = ?, last_name = ?, username = ?
                   WHERE user_id = ?''',
                (user.first_name, user.last_name, user.username, user.id)
            )
        conn.commit()

def get_user(user_id: int) -> dict:
    '''Gets a user from the database.'''
    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return dict(result) if result else {}

def get_user_status(user_id: int) -> bool:
    '''Checks if a user is verified.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT is_verified FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return bool(result[0]) if result else False

def set_user_verified(user_id: int):
    '''Marks a user as verified.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_verified = 1 WHERE user_id = ?', (user_id,))
        conn.commit()

def add_warning(user_id: int) -> int:
    '''Adds a warning to a user and returns the new count.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET warnings = warnings + 1 WHERE user_id = ?', (user_id,))
        conn.commit()
        cursor.execute('SELECT warnings FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

def mute_user_db(user_id: int, mute_time: int):
    '''Mutes a user for a specified amount of time.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET muted = ? WHERE user_id = ?', (int(time.time()) + mute_time, user_id))
        conn.commit()

def unmute_user_db(user_id: int):
    '''Unmutes a user.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET muted = 0 WHERE user_id = ?', (user_id,))
        conn.commit()

def ban_user_db(user_id: int):
    '''Bans a user.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET banned = 1 WHERE user_id = ?', (user_id,))
        conn.commit()

def unban_user_db(user_id: int):
    '''Unbans a user.'''
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET banned = 0 WHERE user_id = ?', (user_id,))
        conn.commit()

# --- BOT LOGIC ---

def is_admin(user_id: int, chat_id: int) -> bool:
    '''Checks if a user is an administrator of a chat.'''
    try:
        return bot.get_chat_member(chat_id, user_id).status in ['administrator', 'creator']
    except telebot.apihelper.ApiTelegramException:
        return False

@bot.message_handler(commands=['start'])
def handle_start(message: telebot.types.Message):
    '''Handles the /start command in a private chat.'''
    if message.chat.type == 'private':
        bot.reply_to(message, 'This bot is intended for use in groups.')

@bot.message_handler(commands=['setwelcome'])
def set_welcome_message(message: telebot.types.Message):
    '''Sets the welcome message for the chat.'''
    if not is_admin(message.from_user.id, message.chat.id):
        bot.reply_to(message, 'Only administrators can use this command.')
        return

    welcome_message = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ''
    if welcome_message:
        set_welcome_message_db(message.chat.id, welcome_message)
        bot.reply_to(message, f'Welcome message updated to: "{welcome_message}"')
    else:
        bot.reply_to(message, 'Please provide a welcome message. Usage: /setwelcome <message>')

@bot.message_handler(commands=['setrules'])
def set_rules(message: telebot.types.Message):
    '''Sets the rules for the chat.'''
    if not is_admin(message.from_user.id, message.chat.id):
        bot.reply_to(message, 'Only administrators can use this command.')
        return

    rules = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else ''
    if rules:
        set_rules_db(message.chat.id, rules)
        bot.reply_to(message, f'Rules updated to: "{rules}"')
    else:
        bot.reply_to(message, 'Please provide the rules. Usage: /setrules <rules>')

@bot.message_handler(commands=['rules'])
def show_rules(message: telebot.types.Message):
    '''Shows the rules of the chat.'''
    chat_settings = get_chat_settings(message.chat.id)
    rules = chat_settings.get('rules', 'No rules have been set for this chat yet.')
    bot.reply_to(message, rules)

@bot.message_handler(commands=['mute'])
def mute_user(message: telebot.types.Message):
    '''Mutes a user for a specified amount of time.'''
    if not is_admin(message.from_user.id, message.chat.id):
        bot.reply_to(message, 'Only administrators can use this command.')
        return

    try:
        user_id = message.reply_to_message.from_user.id
        mute_time = int(message.text.split()[1])
        mute_user_db(user_id, mute_time)
        bot.reply_to(message, f'User {user_id} has been muted for {mute_time} seconds.')
    except (AttributeError, IndexError, ValueError):
        bot.reply_to(message, 'Usage: /mute <time_in_seconds> (reply to a message)')

@bot.message_handler(commands=['ban'])
def ban_user(message: telebot.types.Message):
    '''Bans a user from the chat.'''
    if not is_admin(message.from_user.id, message.chat.id):
        bot.reply_to(message, 'Only administrators can use this command.')
        return

    try:
        user_id = message.reply_to_message.from_user.id
        ban_user_db(user_id)
        bot.kick_chat_member(message.chat.id, user_id)
        bot.reply_to(message, f'User {user_id} has been banned.')
    except AttributeError:
        bot.reply_to(message, 'Usage: /ban (reply to a message)')

@bot.message_handler(commands=['report'])
def report_to_admins(message: telebot.types.Message):
    '''Reports a message to the admins.'''
    if message.reply_to_message:
        reported_message = message.reply_to_message
        reporter = message.from_user
        
        report_text = f"Report from @{reporter.username} (ID: {reporter.id})\n"
        report_text += f"Reported message from @{reported_message.from_user.username} (ID: {reported_message.from_user.id}):\n"
        report_text += reported_message.text
        
        bot.forward_message(ADMIN_ID, message.chat.id, reported_message.message_id)
        bot.reply_to(message, "The message has been reported to the administrators.")
    else:
        bot.reply_to(message, "Please reply to a message to report it.")

@bot.message_handler(commands=['deletelinks'])
def set_delete_links(message: telebot.types.Message):
    '''Enables or disables the deletion of links in the chat.'''
    if not is_admin(message.from_user.id, message.chat.id):
        bot.reply_to(message, 'Only administrators can use this command.')
        return

    try:
        status = message.text.split()[1].lower()
        if status == 'on':
            set_delete_links_db(message.chat.id, True)
            bot.reply_to(message, 'Link deletion is now enabled.')
        elif status == 'off':
            set_delete_links_db(message.chat.id, False)
            bot.reply_to(message, 'Link deletion is now disabled.')
        else:
            bot.reply_to(message, 'Usage: /deletelinks <on/off>')
    except IndexError:
        bot.reply_to(message, 'Usage: /deletelinks <on/off>')

@bot.message_handler(commands=['deleteforwards'])
def set_delete_forwards(message: telebot.types.Message):
    '''Enables or disables the deletion of forwarded messages in the chat.'''
    if not is_admin(message.from_user.id, message.chat.id):
        bot.reply_to(message, 'Only administrators can use this command.')
        return

    try:
        status = message.text.split()[1].lower()
        if status == 'on':
            set_delete_forwards_db(message.chat.id, True)
            bot.reply_to(message, 'Forwarded message deletion is now enabled.')
        elif status == 'off':
            set_delete_forwards_db(message.chat.id, False)
            bot.reply_to(message, 'Forwarded message deletion is now disabled.')
        else:
            bot.reply_to(message, 'Usage: /deleteforwards <on/off>')
    except IndexError:
        bot.reply_to(message, 'Usage: /deleteforwards <on/off>')

@bot.message_handler(commands=['deletefiles'])
def set_delete_files(message: telebot.types.Message):
    '''Enables or disables the deletion of files in the chat.'''
    if not is_admin(message.from_user.id, message.chat.id):
        bot.reply_to(message, 'Only administrators can use this command.')
        return

    try:
        status = message.text.split()[1].lower()
        if status == 'on':
            set_delete_files_db(message.chat.id, True)
            bot.reply_to(message, 'File deletion is now enabled.')
        elif status == 'off':
            set_delete_files_db(message.chat.id, False)
            bot.reply_to(message, 'File deletion is now disabled.')
        else:
            bot.reply_to(message, 'Usage: /deletefiles <on/off>')
    except IndexError:
        bot.reply_to(message, 'Usage: /deletefiles <on/off>')

@bot.message_handler(commands=['setlogchannel'])
def set_log_channel(message: telebot.types.Message):
    '''Sets the log channel for the chat.'''
    if not is_admin(message.from_user.id, message.chat.id):
        bot.reply_to(message, 'Only administrators can use this command.')
        return

    try:
        log_channel = int(message.text.split()[1])
        set_log_channel_db(message.chat.id, log_channel)
        logger.addHandler(TelegramLogHandler(bot, log_channel))
        bot.reply_to(message, f'Log channel updated to: {log_channel}')
    except (IndexError, ValueError):
        bot.reply_to(message, 'Please provide a valid channel ID. Usage: /setlogchannel <channel_id>')

@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message: telebot.types.Message):
    '''Sends a captcha to a new user.'''
    chat_settings = get_chat_settings(message.chat.id)
    welcome_message_template = chat_settings.get('welcome_message', 'Welcome, {user_name}!\nTo be able to write in the chat, please solve the equation: {num1} + {num2} = ?')

    for user in message.new_chat_members:
        add_or_update_user(user)
        
        # Create captcha
        num1 = random.randint(CAPTCHA_MIN_NUMBER, CAPTCHA_MAX_NUMBER)
        num2 = random.randint(CAPTCHA_MIN_NUMBER, CAPTCHA_MAX_NUMBER)
        correct_answer = num1 + num2
        pending_captchas[user.id] = correct_answer

        welcome_message = welcome_message_template.format(
            user_name=user.first_name,
            num1=num1,
            num2=num2
        )

        try:
            bot.send_message(message.chat.id, welcome_message)
        except telebot.apihelper.ApiTelegramException as e:
            logger.error(f'Error sending captcha: {e}')

def check_captcha(message: telebot.types.Message) -> bool:
    '''Checks the captcha for a user.'''
    user = message.from_user
    if user.id in pending_captchas:
        try:
            if int(message.text) == pending_captchas[user.id]:
                set_user_verified(user.id)
                del pending_captchas[user.id]
                try:
                    bot.reply_to(message, 'Correct! You can now send messages.')
                except telebot.apihelper.ApiTelegramException as e:
                    logger.error(f'Error sending reply: {e}')
            else:
                try:
                    bot.reply_to(message, 'Incorrect answer. Please try again.')
                except telebot.apihelper.ApiTelegramException as e:
                    logger.error(f'Error sending reply: {e}')
        except (ValueError, TypeError):
            try:
                bot.reply_to(message, 'Please enter a number in response to the captcha.')
            except telebot.apihelper.ApiTelegramException as e:
                logger.error(f'Error sending reply: {e}')
        return True  # User is in the process of solving the captcha
    return False  # Captcha not for this user

def check_swear_words(message: telebot.types.Message) -> bool:
    '''Checks a message for swear words.'''
    user = message.from_user
    for word in SWEAR_WORDS:
        if word in message.text.lower():
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except telebot.apihelper.ApiTelegramException as e:
                logger.error(f'Error deleting message: {e}')
            warnings = add_warning(user.id)
            
            try:
                bot.send_message(
                    message.chat.id,
                    f'@ {user.username}, please follow the chat rules. '
                    f'You have been issued a warning ({warnings}/{WARNING_LIMIT}).'
                )
            except telebot.apihelper.ApiTelegramException as e:
                logger.error(f'Error sending warning: {e}')

            if warnings >= WARNING_LIMIT:
                try:
                    bot.send_message(
                        ADMIN_ID,
                        f'User @{user.username} (ID: {user.id}) '
                        f'has reached the warning limit ({warnings}).'
                    )
                except telebot.apihelper.ApiTelegramException as e:
                    logger.error(f'Error sending admin notification: {e}')
            return True  # Swear word found
    return False  # No swear words found

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message: telebot.types.Message):
    '''Handles all incoming messages.'''
    user = get_user(message.from_user.id)
    if not user:
        add_or_update_user(message.from_user)
        user = get_user(message.from_user.id)

    if user.get('banned'):
        return

    if user.get('muted') and user.get('muted') > int(time.time()):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            logger.error(f'Error deleting message: {e}')
        return

    chat_settings = get_chat_settings(message.chat.id)
    if not is_admin(message.from_user.id, message.chat.id):
        if chat_settings.get('delete_links') and message.entities and any(e.type in ['url', 'text_link'] for e in message.entities):
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except telebot.apihelper.ApiTelegramException as e:
                logger.error(f'Error deleting message: {e}')
            return

        if chat_settings.get('delete_forwards') and message.forward_from:
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except telebot.apihelper.ApiTelegramException as e:
                logger.error(f'Error deleting message: {e}')
            return

        if chat_settings.get('delete_files') and message.document:
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except telebot.apihelper.ApiTelegramException as e:
                logger.error(f'Error deleting message: {e}')
            return

    if check_captcha(message):
        return

    # If the user is not verified (old member who has not passed the captcha)
    if not get_user_status(user.get('user_id')):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except telebot.apihelper.ApiTelegramException as e:
            logger.error(f'Error deleting message: {e}')
        return

    if check_swear_words(message):
        return

# --- BOT START ---
if __name__ == '__main__':
    if not BOT_TOKEN or BOT_TOKEN == '':
        logger.error('Error: Bot token not specified. Please edit the file and specify the BOT_TOKEN.')
    elif not ADMIN_ID or ADMIN_ID == 0:
        logger.error('Error: Admin ID not specified. Please edit the file and specify the ADMIN_ID.')
    else:
        logger.info('Initializing database...')
        init_db()
        logger.info('Database ready.')
        logger.info('Starting bot...')
        bot.polling(none_stop=True)