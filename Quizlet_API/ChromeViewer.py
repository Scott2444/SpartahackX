"""
Windows OS Only!!
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
import random

OUTPUT_FILE = "Quizlet_API/flashcards.json"
PATH_TO_PROFILE = r"C:\Users\scott\AppData\Local\Google\Chrome\User Data\Default"
HOME_PAGE = ""

class QuizletStealthReader:
    def __init__(self):
        # Enhanced Chrome options
        options = webdriver.ChromeOptions()
        
        # Additional stealth options
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-automation')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--window-size={random.randint(1050,1200)},{random.randint(800,1000)}')
        options.add_argument(f'--user-data-dir={PATH_TO_PROFILE}')
        options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Add random plugins count
        options.add_argument(f'--numPlugins={random.randint(3,7)}')
        
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        try:
            self.driver = webdriver.Chrome(options=options)
            
            # Enhanced stealth configuration
            stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                run_on_insecure_origins=True
            )
            
            # Additional WebDriver masking
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                "platform": "Windows"
            })
            
            # Add more human-like properties
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            """)
            
        except Exception as e:
            print("Error starting chrome driver.")
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

    def open_url(self, url: str, allow_captcha: bool = False):
        # Randomize initial delay
        time.sleep(random.uniform(1, 3))
        
        # First visit homepage with some random behavior
        self.driver.get("https://quizlet.com")
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
    

if __name__ == "__main__":
    url = "https://quizlet.com/434682915/mkt327-questions-flash-cards/?funnelUUID=158f1531-5bde-47f7-b2c2-bcbf1c67d0ec"
    # url = "https://vercel.com/"
    reader = QuizletStealthReader()
    reader.open_url(url, allow_captcha=True)
    reader.scan()

    # print("Finished")
    # print("Press any key to close window...")
    # input()

    reader.close()