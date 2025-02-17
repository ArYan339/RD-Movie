import os
from io import BytesIO
import requests
from flask import Flask, request, Response
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler, Dispatcher
from movies_scraper import search_movies, get_movie

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

# Telegram bot handlers
def welcome(update, context) -> None:
    update.message.reply_text(f"Hello {update.message.from_user.first_name}, Welcome to RD Movie.\n"
                             f"🔥 Download Your Favourite Movies For 💯 Free And 🍿 Enjoy it.")
    update.message.reply_text("👇 Enter Movie Name 👇")

def find_movie(update, context):
    if not update.message.text:
        update.message.reply_text("Please enter a valid movie name.")
        return
    
    search_results = update.message.reply_text("Processing...")
    query = update.message.text
    
    try:
        movies_list = search_movies(query)
        
        if movies_list and len(movies_list) > 0:
            keyboards = []
            for movie in movies_list:
                if 'title' in movie and 'id' in movie:
                    keyboard = InlineKeyboardButton(movie["title"], callback_data=movie["id"])
                    keyboards.append([keyboard])
            
            if keyboards:
                reply_markup = InlineKeyboardMarkup(keyboards)
                search_results.edit_text('Search Results...', reply_markup=reply_markup)
            else:
                search_results.edit_text('No valid movie results found. Try another search term.')
        else:
            search_results.edit_text('Sorry 🙏, No Result Found!\nCheck If You Have Misspelled The Movie Name or try another movie.')
    except Exception as e:
        print(f"Error in find_movie: {e}")
        search_results.edit_text(f'Sorry, an error occurred while searching. Please try again later.')

def movie_result(update, context) -> None:
    query = update.callback_query
    try:
        query.answer()  # Answer the callback query to stop the loading animation
        
        query.message.reply_text(f"Fetching movie details...")
        s = get_movie(query.data)
        
        if not s:
            query.message.reply_text("Error: Could not fetch movie details.")
            return
        
        if 'img' in s and s['img']:
            try:
                response = requests.get(s["img"])
                if response.status_code == 200:
                    img = BytesIO(response.content)
                    query.message.reply_photo(photo=img, caption=f"🎥 {s['title']}")
                else:
                    query.message.reply_text(f"Error loading image (HTTP {response.status_code})")
                    query.message.reply_text(f"🎥 {s['title']}")
            except Exception as e:
                print(f"Error loading image: {e}")
                query.message.reply_text(f"Error loading image: {e}")
                query.message.reply_text(f"🎥 {s['title']}")
        else:
            query.message.reply_text(f"🎥 {s['title']}")
        
        links = s.get("links", {})
        if links:
            link = ""
            for i in links:
                link += "🎬" + i + "\n" + links[i] + "\n\n"
            caption = f"⚡ Fast Download Links :-\n\n{link}"
            if len(caption) > 4095:
                for x in range(0, len(caption), 4095):
                    query.message.reply_text(text=caption[x:x+4095])
            else:
                query.message.reply_text(text=caption)
        else:
            query.message.reply_text("No download links found for this movie.")
    except Exception as e:
        print(f"Error in movie_result: {e}")
        query.message.reply_text(f"Sorry, an error occurred while fetching movie details: {str(e)[:100]}...")

# Flask routes
@app.route('/', methods=['GET'])
def index():
    return 'Hello World! RD Movie Bot is running.'

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
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
    else:
        return Response('Invalid request', status=400)

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    webhook_url = f"{URL}/webhook"
    s = bot.setWebhook(webhook_url)
    if s:
        return f"webhook setup ok. Webhook URL: {webhook_url}"
    else:
        return "webhook setup failed"

# For local development
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
