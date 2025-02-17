import os
from io import BytesIO
import requests
from flask import Flask, request, Response
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
from movies_scraper import search_movies, get_movie
from logger import logger

# Configuration
TOKEN = os.getenv("TOKEN")
if not TOKEN:
    raise ValueError("No TOKEN provided. Set the TOKEN environment variable.")

URL = os.getenv("VERCEL_URL", "")
if URL:
    URL = f"https://{URL}"
else:
    URL = os.getenv("CUSTOM_URL", "https://your-app-url.vercel.app")

bot = Bot(TOKEN)
app = Flask(__name__)

def handle_error(update, error_message: str, log_message: str = None):
    """Centralized error handling"""
    if log_message:
        logger.error(log_message)
    if hasattr(update, 'message'):
        update.message.reply_text(error_message)
    elif hasattr(update, 'callback_query'):
        update.callback_query.message.reply_text(error_message)

def send_typing_action(update):
    """Send typing action to indicate processing"""
    try:
        chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
        bot.send_chat_action(chat_id=chat_id, action="typing")
    except Exception as e:
        logger.error(f"Error sending typing action: {e}")

def welcome(update, context) -> None:
    """Handle the /start command"""
    try:
        welcome_message = (
            f"Hello {update.message.from_user.first_name}, Welcome to RD Movie.\n"
            f"🔥 Download Your Favourite Movies For 💯 Free And 🍿 Enjoy it."
        )
        update.message.reply_text(welcome_message)
        update.message.reply_text("👇 Enter Movie Name 👇")
        logger.info(f"Sent welcome message to user: {update.message.from_user.id}")
    except Exception as e:
        handle_error(update, "An error occurred. Please try again.", f"Error in welcome handler: {e}")

def find_movie(update, context):
    """Handle movie search requests"""
    if not update.message or not update.message.text:
        handle_error(update, "Please enter a valid movie name.")
        return

    send_typing_action(update)
    query = update.message.text.strip()
    search_results = update.message.reply_text("🔍 Searching for movies...")

    try:
        logger.info(f"Searching for movie: {query}")
        movies_list = search_movies(query)

        if not movies_list:
            search_results.edit_text(
                "Sorry 🙏, No Results Found!\n"
                "Please check the spelling or try another movie name."
            )
            return

        keyboards = []
        for movie in movies_list:
            if 'title' in movie and 'id' in movie:
                keyboard = InlineKeyboardButton(
                    text=movie["title"],
                    callback_data=movie["id"]
                )
                keyboards.append([keyboard])

        if keyboards:
            reply_markup = InlineKeyboardMarkup(keyboards)
            search_results.edit_text(
                '🎬 Search Results:\nClick on a movie to get download links',
                reply_markup=reply_markup
            )
        else:
            search_results.edit_text("No valid results found. Please try another search.")

    except Exception as e:
        handle_error(update, "An error occurred while searching. Please try again.", f"Error in find_movie: {e}")
        if search_results:
            search_results.edit_text("An error occurred while searching. Please try again later.")

def movie_result(update, context) -> None:
    """Handle movie selection and display download links"""
    query = update.callback_query
    if not query or not query.message:
        return

    try:
        query.answer()
        send_typing_action(update)
        processing_msg = query.message.reply_text("🎬 Fetching movie details...")

        movie_details = get_movie(query.data)
        if not movie_details:
            processing_msg.edit_text("Sorry, couldn't fetch movie details. Please try again.")
            return

        # Send movie poster if available
        title_sent = False
        if movie_details.get('img'):
            try:
                response = requests.get(movie_details["img"], timeout=10)
                if response.status_code == 200:
                    img = BytesIO(response.content)
                    query.message.reply_photo(
                        photo=img,
                        caption=f"🎥 {movie_details['title']}"
                    )
                    title_sent = True
            except Exception as e:
                logger.error(f"Error sending movie poster: {e}")

        if not title_sent:
            query.message.reply_text(f"🎥 {movie_details['title']}")

        # Send download links
        links = movie_details.get("links", {})
        if links:
            link_text = "⚡ Download Links:\n\n"
            for title, url in links.items():
                link_text += f"🎬 {title}\n{url}\n\n"

            # Split long messages if needed
            if len(link_text) > 4096:
                for x in range(0, len(link_text), 4096):
                    query.message.reply_text(text=link_text[x:x+4096])
            else:
                query.message.reply_text(text=link_text)
        else:
            query.message.reply_text("No download links available for this movie.")

        processing_msg.delete()

    except Exception as e:
        handle_error(update, "An error occurred. Please try again.", f"Error in movie_result: {e}")

# Flask routes
@app.route('/')
def index():
    return 'RD Movie Bot is running!'

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming updates from Telegram"""
    if request.headers.get('content-type') == 'application/json':
        try:
            update = Update.de_json(request.json, bot)

            # Create dispatcher
            dispatcher = Dispatcher(bot, None, workers=0, use_context=True)

            # Register handlers
            dispatcher.add_handler(CommandHandler('start', welcome))
            dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, find_movie))
            dispatcher.add_handler(CallbackQueryHandler(movie_result))

            # Process update
            dispatcher.process_update(update)
            return Response('ok', status=200)
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return Response(str(e), status=500)
    else:
        return Response('Invalid request', status=400)

@app.route('/setwebhook')
def set_webhook():
    """Set the Telegram webhook URL"""
    webhook_url = f"{URL}/webhook"
    try:
        success = bot.setWebhook(webhook_url)
        if success:
            logger.info(f"Webhook set successfully: {webhook_url}")
            return f"Webhook setup successful. URL: {webhook_url}"
        else:
            logger.error("Webhook setup failed")
            return "Webhook setup failed"
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return f"Error setting webhook: {str(e)}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
