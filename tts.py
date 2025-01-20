import datetime
import os
import pyttsx3
import speech_recognition as sr
import webbrowser
import urllib.parse
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import sys
import platform
import subprocess

# Load environment variables
load_dotenv()

class PersonalAssistant:
    def __init__(self):
        """Initialize the personal assistant with necessary configurations."""
        # Configure logging
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(levelname)s: %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('assistant.log')
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Initialize text-to-speech engine
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160)
            self.engine.setProperty('volume', 0.9)
        except Exception as e:
            self.logger.error(f"Text-to-speech initialization error: {e}")
            sys.exit(1)

        # Configure Google Generative AI
        self.gemini_api_key = os.getenv('PUBLIC_GEMINI_API_KEY')
        self._init_generative_ai()

    def _init_generative_ai(self):
        """Initialize Google Generative AI."""
        try:
            if not self.gemini_api_key:
                self.logger.warning("Gemini API key is missing.")
                self.genai_model = None
                return

            genai.configure(api_key=self.gemini_api_key)
            
            generation_config = {
                'temperature': 0.5,
                'top_p': 1,
                'max_output_tokens': 100,
            }

            self.genai_model = genai.GenerativeModel(
                model_name='gemini-1.5-pro',
                generation_config=generation_config,
                system_instruction="""
                You are a helpful AI assistant. 
                Provide clear, concise, and direct responses. 
                Aim to be informative but brief. 
                Use simple language and get straight to the point.
                """
            )
        except Exception as e:
            self.logger.error(f"Generative AI initialization error: {e}")
            self.genai_model = None

    def speak(self, text):
        """Convert text to speech with enhanced error handling."""
        try:
            max_length = 200
            if len(text) > max_length:
                text = text[:max_length] + "..."

            self.logger.info(f"Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Text-to-speech error: {e}")
            print(text)

    def open_website(self, website):
        """Advanced website opening with multiple methods."""
        try:
            # Normalize website name
            website = website.lower().replace(" ", "")
            
            # Predefined website mappings with full URLs
            website_map = {
                "google": "https://www.google.com",
                "youtube": "https://www.youtube.com",
                "github": "https://www.github.com",
                "chatgpt": "https://chat.openai.com",
                "stackoverflow": "https://www.stackoverflow.com",
            }

            # Determine the URL to open
            url = website_map.get(website, f"https://www.{website}.com")

            # Cross-platform website opening
            system = platform.system().lower()
            
            if system == "darwin":  # macOS
                subprocess.run(["open", url])
            elif system == "windows":
                os.startfile(url)
            elif system == "linux":
                subprocess.run(["xdg-open", url])
            else:
                webbrowser.open(url)

            self.speak(f"Opening {website}")
            
        except Exception as e:
            self.speak(f"Could not open {website}")
            self.logger.error(f"Website opening error: {e}")

    def youtube_search(self, query):
        """Advanced YouTube search with multiple opening methods."""
        try:
            # Encode the query for URL
            encoded_query = urllib.parse.quote(query)
            
            # Construct YouTube search URL
            youtube_search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            
            # Cross-platform URL opening
            system = platform.system().lower()
            
            if system == "darwin":  # macOS
                subprocess.run(["open", youtube_search_url])
            elif system == "windows":
                os.startfile(youtube_search_url)
            elif system == "linux":
                subprocess.run(["xdg-open", youtube_search_url])
            else:
                webbrowser.open(youtube_search_url)

            self.speak(f"Searching YouTube for {query}")
        
        except Exception as e:
            self.speak("Could not perform YouTube search")
            self.logger.error(f"YouTube search error: {e}")

    def perform_task(self, command):
        """Enhanced task performance with more capabilities."""
        try:
            # Convert command to lowercase for easier matching
            command = command.lower()

            # Website opening
            if "open" in command:
                website = command.replace("open", "").strip()
                self.open_website(website)
                return

            # YouTube search
            if "play" in command and "on youtube" in command:
                query = command.replace("play", "").replace("on youtube", "").strip()
                self.youtube_search(query)
                return

            # Web search
            if "search" in command:
                query = command.replace("search", "").strip()
                search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                webbrowser.open(search_url)
                self.speak(f"Searching Google for {query}")
                return

            # Image search
            if "show images" in command or "search images" in command:
                query = command.replace("show images", "").replace("search images", "").strip()
                image_search_url = f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote(query)}"
                webbrowser.open(image_search_url)
                self.speak(f"Searching images for {query}")
                return

            # Direct AI interaction if no specific command matches
            ai_response = self.send_ai_message(command)
            return ai_response

        except Exception as e:
            error_msg = f"Error processing command: {e}"
            self.speak(error_msg)
            self.logger.error(error_msg)

    def speak(self, text):
        """Convert text to speech with enhanced error handling."""
        try:
            # Truncate very long responses
            max_length = 200
            if len(text) > max_length:
                text = text[:max_length] + "..."

            self.logger.info(f"Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Text-to-speech error: {e}")
            print(text)  # Fallback to print if speech fails

    def send_ai_message(self, message):
        """Send message to Google Generative AI with comprehensive handling."""
        if not self.genai_model:
            response = "AI assistant is not configured. Please check your API settings."
            self.speak(response)
            return response

        try:
            # Special keywords handling with ultra-concise responses
            special_keywords = {
                "creator": "I was created by Debayudh Basu, a talented developer.",
                "your name": "I'm Ramesh, an AI assistant.",
                "help": "I can help with questions, web searches, and information."
            }

            # Check for special keywords
            lower_case_message = message.lower()
            for keyword, special_response in special_keywords.items():
                if keyword in lower_case_message:
                    self.speak(special_response)
                    return special_response

            # Modify prompt for more concise response
            modified_message = f"Provide a concise, direct answer to: {message}"

            # Start chat session and get response
            chat_session = self.genai_model.start_chat(history=[])
            response = chat_session.send_message(modified_message)
            
            # Speak and return the response
            concise_response = self.summarize_response(response.text)
            self.speak(concise_response)
            return concise_response

        except Exception as e:
            error_response = "Sorry, I couldn't process that request."
            self.speak(error_response)
            self.logger.error(f"AI message error: {e}")
            return error_response

    def summarize_response(self, text):
        """Further summarize the AI response to ensure conciseness."""
        # Remove unnecessary words and trim
        words = text.split()
        trimmed_words = words[:30]  # Limit to first 30 words
        return ' '.join(trimmed_words) + ('...' if len(words) > 30 else '')

    def listen_to_command(self):
        """Advanced voice command listening with multiple error handling."""
        recognizer = sr.Recognizer()
        
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=1)
                
                self.speak("I'm listening. Please speak...")
                print("Listening...")
                
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    command = recognizer.recognize_google(audio).lower()
                    print(f"You said: {command}")
                    return command
                
                except sr.UnknownValueError:
                    self.speak("Sorry, I could not understand what you said. Could you please repeat?")
                    return ""
                
                except sr.RequestError:
                    self.speak("I'm having trouble with the speech recognition service.")
                    return ""
        
        except Exception as e:
            self.speak(f"An unexpected error occurred: {e}")
            self.logger.error(f"Listening error: {e}")
            return ""

    def perform_task(self, command):
        """Perform tasks based on user command with AI integration."""
        try:
            # Web search functionality
            if "search" in command:
                query = command.replace("search", "").strip()
                search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                webbrowser.open(search_url)
                self.speak(f"Searching Google for {query}")
                return

            # Direct AI interaction
            ai_response = self.send_ai_message(command)
            return ai_response

        except Exception as e:
            error_msg = f"Error processing command: {e}"
            self.speak(error_msg)
            self.logger.error(error_msg)

    def run(self):
        """Main method to run the personal assistant with advanced command parsing."""
        self.speak("Hello! I'm your AI assistant. How can I help you today?")
    
        while True:
            command = self.listen_to_command()
        
            if command:
            # Comprehensive exit conditions
                if any(exit_word in command for exit_word in ["exit", "quit", "bye", "goodbye"]):
                    self.speak("Goodbye! Have a great day!")
                    break
            
            # Advanced command parsing
            try:
                # YouTube-specific commands
                if "open youtube" in command:
                    self.open_website("youtube")
                    continue
                
                if "play" in command and "on youtube" in command:
                    # Extract search query for YouTube
                    query = command.replace("play", "").replace("on youtube", "").strip()
                    self.youtube_search(query)
                    continue
                
                # Website opening commands
                website_keywords = [
                    "open google", "open github", "open stackoverflow", 
                    "open chatgpt", "open browser"
                ]
                for keyword in website_keywords:
                    if keyword in command:
                        website = keyword.replace("open", "").strip()
                        self.open_website(website)
                        break
                
                # Image search commands
                if "show images" in command or "search images" in command:
                    query = command.replace("show images", "").replace("search images", "").strip()
                    self.perform_image_search(query)
                    continue
                
                # Web search commands
                if "search" in command and "images" not in command:
                    query = command.replace("search", "").strip()
                    search_url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
                    webbrowser.open(search_url)
                    self.speak(f"Searching Google for {query}")
                    continue
                
                # Time and date related commands
                if "what time" in command or "current time" in command:
                    current_time = datetime.datetime.now().strftime("%I:%M %p")
                    self.speak(f"The current time is {current_time}")
                    continue
                
                if "what date" in command or "current date" in command:
                    current_date = datetime.datetime.now().strftime("%B %d, %Y")
                    self.speak(f"Today's date is {current_date}")
                    continue
                
                # System control commands
                if "screenshot" in command:
                    self.take_screenshot()
                    continue
                
                # Fallback to AI interaction
                ai_response = self.send_ai_message(command)
            
            except Exception as e:
                error_msg = f"Error processing command: {e}"
                self.speak(error_msg)
                self.logger.error(error_msg)

    def take_screenshot(self):
        """Take a screenshot of the current screen."""
        try:
            import pyautogui
            import os
            
            # Create screenshots directory if it doesn't exist
            screenshot_dir = os.path.join(os.path.expanduser("~"), "AI_Assistant_Screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            
            # Generate unique filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshot_dir, f"screenshot_{timestamp}.png")
            
            # Take and save screenshot
            pyautogui.screenshot(screenshot_path)
            
            self.speak(f"Screenshot saved at {screenshot_path}")
        
        except ImportError:
            self.speak("Please install pyautogui to use screenshot functionality")
            self.logger.warning("PyAutoGUI not installed")
        
        except Exception as e:
            self.speak("Could not take screenshot")
            self.logger.error(f"Screenshot error: {e}")


def main():
    try:
        assistant = PersonalAssistant()
        assistant.run()
    except Exception as e:
        print(f"Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()