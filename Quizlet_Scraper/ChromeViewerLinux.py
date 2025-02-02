"""
Linux OS Only!!
"""
import os
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
import json
import time
from typing import List, Dict
import subprocess

OUTPUT_FILE = "flashcards.json"
# Remove Windows-specific profile path
HOME_PAGE = "https://quizlet.com"

class RenderStealthReader:
    def __init__(self):
        # Enhanced Chrome options for Linux environment
        options = webdriver.ChromeOptions()
        
        # Additional stealth options
        options.add_argument("--headless=new")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-automation')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--window-size={random.randint(1050,1200)},{random.randint(800,1000)}')
        options.add_argument(f"user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Add random plugins count
        options.add_argument(f'--numPlugins={random.randint(3,7)}')
        
        # Linux-specific Chrome configurations
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--remote-debugging-port=9222')
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        try:
            # Configure ChromeDriver service for Linux
            service = webdriver.ChromeService()
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Enhanced stealth configuration
            stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Linux x86_64",  # Updated platform
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                run_on_insecure_origins=True
            )
            
            # Additional WebDriver masking for Linux
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                "platform": "Linux"
            })
            
            # Add more human-like properties
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            """)
            
        except Exception as e:
            print("Error starting chrome driver:", str(e))
            raise e

    def human_like_scroll(self):
        """Implement human-like scrolling behavior"""
        total_height = self.driver.execute_script("return document.body.scrollHeight")
        viewport_height = self.driver.execute_script("return window.innerHeight")
        current_position = 0
        
        while current_position < 1600:
            # Random scroll amount
            scroll_amount = random.randint(300, 700)
            current_position += scroll_amount
            
            # Scroll with random speed
            self.driver.execute_script(f"""
                window.scrollTo({{
                    top: {current_position},
                    behavior: 'smooth'
                }});
            """)
            
            # Random pause between scrolls
            time.sleep(random.uniform(0.5, 2.0))
            
            # Occasionally scroll back up slightly
            if random.random() < 0.2:
                current_position -= random.randint(40, 100)
                self.driver.execute_script(f"window.scrollTo(0, {current_position})")
                time.sleep(random.uniform(0.3, 0.7))

    def open_url(self, url: str, start_at_homepage: bool = True, allow_captcha: bool = False):
        # Randomize initial delay
        time.sleep(random.uniform(1, 3))
        
        # First visit homepage with some random behavior
        if start_at_homepage:
            self.driver.get(HOME_PAGE)
            time.sleep(random.uniform(2, 4))
        
        # Now navigate to the actual page
        self.driver.get(url)
        
        # Wait for page load with random additional delay
        WebDriverWait(self.driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        time.sleep(random.uniform(1, 3))
        
        # Human-like scrolling
        self.human_like_scroll()
        
        if (not allow_captcha and 
            "quizlet" in self.get_active_tab_url() and 
            EC.presence_of_element_located((By.ID, "px-captcha-wrapper"))):
            self.close()
            raise RuntimeError("Captcha Detected despite stealth measures!")

    def simulate_human_behavior(self):
        """Simulate random human-like behavior"""
        actions = ActionChains(self.driver)
        
        # Random mouse movements
        for _ in range(random.randint(3, 7)):
            x = random.randint(0, 700)
            y = random.randint(0, 500)
            actions.move_by_offset(x, y)
            actions.pause(random.uniform(0.1, 0.5))
        
        # Occasionally highlight text
        if random.random() < 0.3:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "span.TermText")
            if elements:
                element = random.choice(elements)
                actions.move_to_element(element)
                actions.click_and_hold()
                actions.pause(random.uniform(0.2, 0.7))
                actions.release()
        
        actions.perform()
        time.sleep(random.uniform(0.5, 2))

    def extract_flashcards(self):
        """Extract flashcards with human-like behavior"""
        flashcards = []
        
        try:
            # Wait for content with random delay
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "section[data-testid='terms-list']"))
            )
            time.sleep(random.uniform(0.5, 2))
            
            # Simulate human behavior before extraction
            # self.simulate_human_behavior()
            
            section = self.driver.find_element(By.CSS_SELECTOR, "section[data-testid='terms-list']")
            term_elements = section.find_elements(By.CSS_SELECTOR, "span.TermText.notranslate.lang-en")
            
            for i in range(0, len(term_elements), 2):
                try:
                    # if random.random() < 0.3:  # Occasionally add delay between extractions
                    #     time.sleep(random.uniform(0.1, 0.5))
                    
                    term = term_elements[i].text.strip()
                    definition = term_elements[i+1].text.strip()
                    
                    if term and definition:
                        flashcard = {
                            'term': term,
                            'definition': definition
                        }
                        flashcards.append(flashcard)
                        
                except Exception as e:
                    print(f"Error extracting card: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error waiting for page elements: {str(e)}")
            
        return flashcards

    
    def close_full_screen_ad(self):
        # Close 
        try:
            # Locate the close button using its class or ID
            close_button = self.driver.find_element(By.CSS_SELECTOR, "a.bx-close.bx-close-link.bx-close-inside")

            # Click the close button
            close_button.click()
            print("Ad closed successfully!")

        except Exception as e:
            print("No ad found or failed to close ad")

    def get_active_tab_url(self) -> str:
        """Get the URL of the currently active tab"""
        return self.driver.current_url

    def save_to_json(self, flashcards: List[Dict[str, str]], output_file=OUTPUT_FILE) -> None:
        """Save the flashcards to a JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({'terms': flashcards}, f, ensure_ascii=False, indent=2)
            print(f"Successfully saved {len(flashcards)} flashcards to {output_file}")
        except Exception as e:
            print(f"Error saving to file: {str(e)}")

    def close(self):
        """Close the WebDriver connection and Chrome Window"""
        self.driver.close()
        self.driver.quit()
        return

    def scan(self):
        """Main function to run the scraper"""
        print("Starting Quizlet Chrome Reader...")
        
        try:
            url = self.get_active_tab_url()
            
            if "quizlet.com" not in url:
                print("Please navigate to a Quizlet page in the active tab")
                return
                
            print(f"Reading flashcards from: {url}")
            flashcards = self.extract_flashcards()
            
            if flashcards:
                self.save_to_json(flashcards)
            else:
                print("No flashcards found on the page")
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            if 'reader' in locals():
                self.close()

# Add setup instructions for Render deployment
def setup_chrome_on_render():
    """Install Chrome and ChromeDriver on Render"""
    try:
        # Install Chrome
        subprocess.run([
            'wget', 'https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb'
        ], check=True)
        subprocess.run(['dpkg', '-i', 'google-chrome-stable_current_amd64.deb'], check=True)
        subprocess.run(['apt-get', 'install', '-f', '-y'], check=True)
        
        # Install ChromeDriver
        subprocess.run([
            'wget', 'https://chromedriver.storage.googleapis.com/LATEST_RELEASE'
        ], check=True)
        with open('LATEST_RELEASE') as f:
            version = f.read()
        subprocess.run([
            'wget', f'https://chromedriver.storage.googleapis.com/{version}/chromedriver_linux64.zip'
        ], check=True)
        subprocess.run(['unzip', 'chromedriver_linux64.zip'], check=True)
        subprocess.run(['mv', 'chromedriver', '/usr/local/bin/'], check=True)
        subprocess.run(['chmod', '+x', '/usr/local/bin/chromedriver'], check=True)
        
        print("Chrome and ChromeDriver successfully installed")
    except subprocess.CalledProcessError as e:
        print(f"Error during setup: {str(e)}")
        raise

if __name__ == "__main__":
    # Setup Chrome and ChromeDriver if needed
    if os.environ.get('RENDER'):
        setup_chrome_on_render()
    
    url = "https://quizlet.com/434682915/mkt327-questions-flash-cards/"
    reader = RenderStealthReader()
    reader.open_url(url)
    reader.scan()
    reader.close()