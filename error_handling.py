import logging
import requests
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set up logging to log errors to a file
logging.basicConfig(filename='bot_errors.log', level=logging.ERROR)

# Email credentials
from_email = "binancetradingbot6@gmail.com"
app_password = "irnt ezcv smyb btba"
to_emails = ["asad.farooq@gmail.com", "asadfarooqkhan1978@icloud.com"]

# Telegram credentials for notifier_bot (critical alerts)
telegram_bot_token_notifier = '7745017594:AAGRQfXWEQGpGlEpJfOIcDyvNE22eIxccgo'
telegram_chat_id_notifier = '6219509995'

# Telegram credentials for tradealerts_bot (trade alerts)
telegram_bot_token_tradealerts = '7443797598:AAH5Ou3HDYHYQntUbfZyeQ0uIsT3GfKCxsc'
telegram_chat_id_tradealerts = '6219509995'

# Function to make API calls with error handling and retries
def make_safe_api_call(api_function, *args, **kwargs):
    retry_attempts = 3  # Number of retries in case of failure
    for attempt in range(retry_attempts):
        try:
            return api_function(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in API call: {e}")
            if attempt < retry_attempts - 1:
                time.sleep(1)  # Delay before retrying
            else:
                # If retries fail, raise an alert (send notifications)
                send_critical_error_notification(f"API call failed after {retry_attempts} attempts: {e}")
                send_critical_error_email(f"API call failed after {retry_attempts} attempts", e)
                return None

# Function to send Telegram message to the specified bot
def send_telegram_message(message, bot_token, chat_id):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        logging.error(f"Failed to send Telegram message: {e}")

# Function to send critical error notifications via notifier_bot
def send_critical_error_notification(message):
    send_telegram_message(message, telegram_bot_token_notifier, telegram_chat_id_notifier)

# Function to send trade alerts via tradealerts_bot
def send_trade_alert(message):
    send_telegram_message(message, telegram_bot_token_tradealerts, telegram_chat_id_tradealerts)

# Function to send email notification
def send_critical_error_email(subject, error_message):
    try:
        # Set up the email server and login
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, app_password)

        # Create the email content
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ", ".join(to_emails)
        msg['Subject'] = subject

        # Body of the email
        body = f"Error: {error_message}"
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        server.sendmail(from_email, to_emails, msg.as_string())
        server.quit()
    except Exception as e:
        logging.error(f"Failed to send email notification: {e}")

# Function to handle critical errors
def handle_critical_error(message, error):
    # Log the error
    logging.error(f"{message}: {error}")
    # Send Telegram and Email notifications
    send_critical_error_notification(f"{message}: {error}")
    send_critical_error_email(message, error)

