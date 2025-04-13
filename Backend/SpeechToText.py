from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt
import time

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-US")  # Default to English if not set

# Constants
MAX_SILENCE_CHECKS = 3  # Number of silent checks before stopping
SILENCE_CHECK_INTERVAL = 0.5  # Seconds between checks
PAGE_LOAD_TIMEOUT = 2  # Seconds to wait for page load
MAX_WORDS_BEFORE_STOP = 15  # Stop after this many words

# Generate HTML code with improved speech recognition
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Enhanced Speech Recognition</title>
    <style>
        #output {
            min-height: 20px;
            border: 1px solid #ccc;
            padding: 10px;
            margin-top: 10px;
            white-space: pre-wrap;
        }
        button {
            padding: 8px 16px;
            margin: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <button id="start">Start Recognition</button>
    <button id="end">Stop Recognition</button>
    <div id="output"></div>
    <script>
        const output = document.getElementById('output');
        let recognition;
        let isRecognizing = false;
        let finalTranscript = '';
        
        function resetRecognition() {
            if (recognition) {
                recognition.stop();
            }
            finalTranscript = '';
            output.textContent = '';
            isRecognizing = false;
        }
        
        function startRecognition() {
            if (isRecognizing) return;
            
            resetRecognition();
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.maxAlternatives = 1;
            recognition.lang = 'LANG_PLACEHOLDER';
            
            recognition.onstart = () => isRecognizing = true;
            
            recognition.onresult = (event) => {
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                // Update the output with both final and interim results
                output.innerHTML = finalTranscript + (interimTranscript ? `<i style="color:#666;">${interimTranscript}</i>` : '');
            };
            
            recognition.onerror = (event) => {
                console.error('Recognition error:', event.error);
                if (event.error === 'no-speech') {
                    output.innerHTML = finalTranscript + '<i style="color:red;">No speech detected</i>';
                }
            };
            
            recognition.onend = () => isRecognizing && recognition.start();
            
            recognition.start();
        }
        
        function stopRecognition() {
            isRecognizing = false;
            recognition && recognition.stop();
            return finalTranscript.trim();
        }
        
        document.getElementById('start').addEventListener('click', startRecognition);
        document.getElementById('end').addEventListener('click', stopRecognition);
    </script>
</body>
</html>'''

class SpeechRecognition:
    def __init__(self):
        self.driver = self._init_driver()
        self.temp_dir = self._setup_directories()
        
    def _init_driver(self):
        """Initialize and configure Chrome WebDriver"""
        chrome_options = Options()
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36")
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        chrome_options.add_argument("--use-fake-device-for-media-stream")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        return driver
    
    def _setup_directories(self):
        """Create necessary directories and files"""
        current_dir = os.getcwd()
        os.makedirs("Data", exist_ok=True)
        os.makedirs(f"{current_dir}/Frontend/Files", exist_ok=True)
        return f"{current_dir}/Frontend/Files"
    
    def _generate_html_file(self):
        """Generate and save the HTML file with the current language"""
        html_content = HTML_TEMPLATE.replace("'LANG_PLACEHOLDER'", f"'{InputLanguage}'")
        with open("Data/Voice.html", "w") as f:
            f.write(html_content)
        return f"file:///{os.getcwd()}/Data/Voice.html"
    
    def set_assistant_status(self, status):
        """Update the assistant status file"""
        with open(f'{self.temp_dir}/Status.data', "w", encoding='utf-8') as file:
            file.write(status)
    
    @staticmethod
    def query_modifier(query):
        """Clean and format the recognized query"""
        if not query.strip():
            return ""
            
        query = query.lower().strip()
        question_words = {
            "how", "what", "who", "where", "when", "why", 
            "which", "whose", "whom", "can you", "what's", 
            "where's", "how's", "is", "are", "do", "does", "did"
        }
        
        # Check if query is a question
        first_word = query.split()[0] if query else ""
        is_question = (first_word in question_words or 
                      any(f" {word} " in f" {query} " for word in question_words))
        
        # Clean punctuation
        query = query.rstrip('.?!')
        
        # Add appropriate punctuation
        query = query.capitalize() + ("?" if is_question else ".")
        
        return query
    
    @staticmethod
    def universal_translator(text):
        """Translate text to English if needed"""
        if not text.strip() or InputLanguage.lower().startswith("en"):
            return text
        
        try:
            return mt.translate(text, "en", "auto").capitalize()
        except Exception as e:
            print(f"Translation error: {e}")
            return text.capitalize()
    
    def speech_recognition(self):
        """Perform speech recognition and return processed text"""
        page_url = self._generate_html_file()
        
        try:
            self.driver.get(page_url)
            time.sleep(0.5)  # Reduced wait time
            
            # Start recognition
            self.driver.find_element(By.ID, "start").click()
            print("Listening...")
            
            last_text = ""
            silence_count = 0
            output_element = self.driver.find_element(By.ID, "output")
            
            while True:
                try:
                    current_text = output_element.text
                    
                    # Check for new speech
                    if current_text and current_text != last_text:
                        last_text = current_text
                        silence_count = 0
                        print(f"Current: {current_text}")
                    
                    # Check stopping conditions
                    word_count = len(last_text.split())
                    if (silence_count >= MAX_SILENCE_CHECKS and last_text) or word_count >= MAX_WORDS_BEFORE_STOP:
                        self.driver.find_element(By.ID, "end").click()
                        print(f"Final text: {last_text}")
                        
                        if not InputLanguage.lower().startswith("en"):
                            self.set_assistant_status("Translating...")
                            last_text = self.universal_translator(last_text)
                        
                        return self.query_modifier(last_text)
                    
                    silence_count += 1
                    time.sleep(SILENCE_CHECK_INTERVAL)
                    
                except Exception as e:
                    print(f"Error during recognition: {e}")
                    self.driver.find_element(By.ID, "end").click()
                    return ""
                    
        except Exception as e:
            print(f"Error initializing recognition: {e}")
            return ""
    
    def close(self):
        """Clean up resources"""
        self.driver.quit()

if __name__ == "__main__":
    recognizer = SpeechRecognition()
    try:
        while True:
            print("\nReady for voice input...")
            text = recognizer.speech_recognition()
            if text:
                print(f"\nProcessed output: {text}")
            else:
                print("No speech detected or error occurred")
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        recognizer.close()