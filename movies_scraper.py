Skip to content
Files
Commands
Search
Packager files
Config files
This is codes not working only Processing not show movies so please fit fully funcations this codes

22 minutes ago
AS

daishrishan

AI
Absolutely! Let me propose what we'll build for you.

22 minutes ago
I'll help you fix the movie search functionality in your Telegram bot. The main issue appears to be in the search and display functions. We'll need to modify the code to properly handle the movie search and display results.

Build the initial prototype
Add movie rating and description
daishrishan approved the plan
Checkpoint made
21 minutes ago
•
Free
Checkpoint after starting plan
Build the initial prototype

Started
21 minutes ago

AI

AI

AI
I'll help fix the movie search functionality. First, let's install the required dependencies and then make the necessary code improvements.

20 minutes ago

AI
To run the Telegram bot, we need your Telegram Bot Token.
You can get this from BotFather on Telegram:

Open Telegram and search for @BotFather
Send /newbot command and follow the instructions
Copy the token provided by BotFather
This token will be used to authenticate your bot with Telegram's servers.
Please provide the token to continue.

Secrets
Key
Value
TOKEN
7509023356:AAElrsJJib7EYC8jgrN3mYz1yHr35V8O7gQ
Using TOKEN
Would you like to save this Secret to your Account Secrets so you can easily access it in other Apps?
Secret saved to account
19 minutes ago

AI
I've made several improvements to fix the movie search functionality:

Improved error handling in the scraper code
Added better logging for debugging
Enhanced user feedback in the Telegram bot
Fixed dependency issues
We're now waiting for your Telegram bot token to test if everything works properly. Once you provide the token through the secrets prompt, we can verify the functionality.

18 minutes ago
Checkpoint made
18 minutes ago
•
Implement Telegram movie search bot with movie search and details display. Includes setup for deployment on Replit.
Add a database to store user data
Without a database, your app's user data may be lost when the app is stopped.

AI
Can you access the /setwebhook endpoint and verify if it returns a success or error message?

18 minutes ago
provide the codes to changes all

10 minutes ago
AS

daishrishan

AI
I'll help you update the code to improve the movie search functionality. I'll explain what changes I'll make to each file.

10 minutes ago
Checkpoint made
9 minutes ago
•
Improve error handling and enhance movie search functionality. Add centralized error handling and improve search result display.

AI
Can you check if the /setwebhook endpoint is accessible and returns a webhook setup message?

9 minutes ago
Paused (Agent is waiting for your response)

Message Agent…
Created logger.py
import logging
import sys

def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logger()

Created movies_scraper.py
import requests
            movie_details = {}
            
            # Extract title
            title_elem = soup.find("div", {'class': 'mvic-desc'})
            if title_elem and title_elem.h3:
                movie_details["title"] = title_elem.h3.text.strip()
            
            # Extract image
            img_elem = soup.find("div", {'class': 'mvic-thumb'})
            if img_elem and 'data-bg' in img_elem.attrs:
                movie_details["img"] = img_elem['data-bg']
            
            # Extract download links
            links = soup.find_all("a", {'rel': 'noopener', 'data-wpel-link': 'internal'})
            final_links = {}
            
            for link in links:
                if link.text and link['href']:
                    final_links[link.text.strip()] = link['href']
            
            movie_details["links"] = final_links
            
            logger.info(f"Successfully fetched details for movie ID: {movie_id}")
            return movie_details
            
        except Exception as e:
            logger.error(f"Error getting movie details: {str(e)}")
            return None

scraper = MovieScraper()
search_movies = scraper.search_movies
get_movie = scraper.get_movie

Created index.py
import os
            update = Update.de_json(request.json, bot)
            dispatcher = Dispatcher(bot, None, workers=0, use_context=True)
            
            # Register handlers
            dispatcher.add_handler(CommandHandler('start', welcome))
            dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, find_movie))
            dispatcher.add_handler(CallbackQueryHandler(movie_result))
            
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

Added support for python-3.11
Dependencies
Installed flask, flask-sqlalchemy, psycopg2, email_validator, gunicorn
Dependencies
Installed trafilatura
Dependencies
Installed beautifulsoup4==4.11.1, python-telegram-bot==13.14, requests==2.28.1, Flask==2.0.3, Werkzeug==2.0.3
Dependencies
Configured Telegram Bot Server to run python index.py
Telegram Bot Server
Installed requests, beautifulsoup4, python-telegram-bot==13.14, flask
The main issues I observe:

Missing dependencies: requests, beautifulsoup4, python-telegram-bot
The scraper code needs improvements for better error handling
Need to ensure proper version compatibility between Flask and other dependencies
Let's first install the required packages:

Dependencies
Edited movies_scraper.py
Now that we have installed the dependencies, let's modify the scraper code to improve error handling and reliability:

-42
+33
            search_url = f"{self.base_url}/?s={query.replace(' ', '+')}"
            
            response = self.session.get(search_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            movies = soup.find_all("a", {'class': 'ml-mask jt'})
            
            for idx, movie in enumerate(movies):
                if not movie:
                    continue
                    
                movie_info = self._extract_movie_info(movie, idx)
Edited index.py
Now let's update the index.py file to improve error handling and user feedback:

-14
+17
-4
+4
        return
    
    send_typing_action(update)
    query = update.message.text.strip()
    search_results = update.message.reply_text("🔍 Searching for movies...")
    
    try:
        logger.info(f"Searching for movie: {query}")
        movies_list = search_movies(query)
        
        if not movies_list:
            search_results.edit_text("Sorry 🙏, No Results Found!\nPlease check the spelling or try another movie name.")
            return
Configured Telegram Bot Server to run python index.py
Now let's set up the workflow to run the bot:

Telegram Bot Server
Restarted Telegram Bot Server
Restarted the workflow after making changes.

Telegram Bot Server
Configured Telegram Bot Server to run python index.py
The workflow needs to be reconfigured to:

Wait for port 5000 (Flask server)
Ensure proper initialization
Allow web application feedback to work
I'll update the workflow configuration first.

Telegram Bot Server
Took a screenshot
Screenshot
Edited movies_scraper.py
Let's enhance the code with these improvements:

Better error handling and validation
Improved movie search and data extraction
Structured response formatting
Proper logging and debugging
Starting with movies_scraper.py as it's the core functionality:

-17
+44
-5
+25
        self.timeout = 10
        self.max_retries = 3
        self.retry_delay = 1
    def _make_request(self, url: str) -> Optional[str]:
        """Make HTTP request with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                continue
Edited index.py
Now, let's update the index.py file to improve error handling and user experience:

-17
+34
-2
+12
def handle_error(update, error_message: str, log_message: str = None):
    """Centralized error handling"""
    if log_message:
        logger.error(log_message)
    if hasattr(update, 'message'):
        update.message.reply_text(error_message)
    elif hasattr(update, 'callback_query'):
        update.callback_query.message.reply_text(error_message)
def send_typing_action(update):
    """Send typing action to show the bot is processing"""
    """Send typing action to indicate processing"""
    try:
        update.message.chat.send_action(action="typing")
        chat_id = update.message.chat_id if update.message else update.callback_query.message.chat_id
Configured Telegram Bot Server to run python index.py
Let's verify if the updated code works properly by restarting the workflow and checking the functionality.

Telegram Bot Server
Took a screenshot
Screenshot
The agent needs your feedback.
/setwebhook

Deploy to production
Publish a live, stable, public version of your App, unaffected by the changes you make in the workspace. Learn more.
Scale up and down to meet demand exactly
Automatically scales from zero to any level of demand, making it inexpensive for most apps and effortless when you go viral.
Compute units are billed at $0.00000125 per compute unit.
Suitable for web apps and stateless APIs.
import requests
                    continue

                self.url_list[movie_id] = movie_href
                movies_list.append({
                    "id": movie_id,
                    "title": info_span.text.strip()
                })

            logger.info(f"Found {len(movies_list)} movies for query: {query}")
            return movies_list

        except Exception as e:
            logger.error(f"Error in search_movies: {str(e)}")
            return []

    def get_movie(self, movie_id: str) -> Optional[Dict]:
        """Get detailed information about a specific movie"""
        try:
            if movie_id not in self.url_list:
                logger.error(f"Movie ID {movie_id} not found in URL list")
                return None

            movie_url = self.url_list[movie_id]
            html_content = self._make_request(movie_url)

            if not html_content:
                logger.error(f"Failed to fetch movie details for ID: {movie_id}")
                return None

            soup = BeautifulSoup(html_content, "html.parser")
            movie_details = {
                "title": "Unknown Title",
                "img": None,
                "links": {}
            }

            # Extract title
            title_elem = soup.find("div", {'class': 'mvic-desc'})
            if title_elem and title_elem.h3:
                movie_details["title"] = title_elem.h3.text.strip()

            # Extract image
            img_elem = soup.find("div", {'class': 'mvic-thumb'})
            if img_elem and img_elem.get('data-bg'):
                movie_details["img"] = img_elem['data-bg']

            # Extract download links
            links = soup.find_all("a", {'rel': 'noopener', 'data-wpel-link': 'internal'})
            for link in links:
                if link.text and link.get('href'):
                    movie_details["links"][link.text.strip()] = link['href']

get_movie = scraper.get_movie
- Replit
