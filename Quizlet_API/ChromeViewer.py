"""
Windows Only!!

Instructions

Start Chrome with this command:
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 -incognito

All other chrome tabs and applications must be closed.

"""
OUTPUT_FILE = "Quizlet_API/flashcards.json"
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
args = ["--remote-debugging-port=9222", "-incognito"]


import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from typing import List, Dict
import subprocess

class QuizletChromeReader:
    def __init__(self):
        # Kill all Chrome processes on Windows
        os.system("taskkill /F /IM chrome.exe")

        # Run Chrome in debugger
        subprocess.Popen([chrome_path] + args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Set up Chrome options to connect to existing browser
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        # Connect to the existing Chrome instance
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print("Error connecting to Chrome. Make sure Chrome is running with remote debugging enabled.")
            raise e
    
    def __del__(self):
        # Close chrome on destruction
        try:
            self.close()
        except Exception as e:
            pass
    
    def open_url(self, url: str):
        # Open URL provided
        try:
            time.sleep(0.5)
            self.driver.get(url)
        except Exception as e:
            print("Invalid URL. Please double check your input. Closing Chrome...")
            self.close()
            raise e
        
        scroll_script = """
        let scrollInterval = setInterval(() => {
            window.scrollBy(0, 14); // Adjust scroll step for smoothness
            if (window.innerHeight + window.scrollY >= document.body.scrollHeight) {
                clearInterval(scrollInterval); // Stop when reaching bottom
            }
        }, 20); // Adjust interval speed
        """
        WebDriverWait(self.driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
        self.driver.execute_script(scroll_script)
        print("URL Loaded")

        # Detect Bot Detector that cannot be bypassed
        if "quizlet" in self.get_active_tab_url() and EC.presence_of_element_located((By.ID, "px-captcha-wrapper")):
            self.close()
            raise RuntimeError("Captcha Detected. It knows we aren't a human!")
    
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

    def extract_flashcards(self) -> List[Dict[str, str]]:
        """Extract flashcards from the current page"""
        flashcards = []
        
        # Wait for the flashcard elements to load
        try:
            # Wait for any span with class TermText to be present
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "section[data-testid='terms-list']"))
            )

            # Small delay to ensure all cards are loaded
            time.sleep(2)

            # Find the section containing all the terms
            section = self.driver.find_element(By.CSS_SELECTOR, "section[data-testid='terms-list']")

            # Find all term and definition spans within that section
            term_elements = section.find_elements(By.CSS_SELECTOR, "span.TermText.notranslate.lang-en")

            # Iterate through the found terms and definitions
            flashcards = []
            for i in range(0, len(term_elements), 2):  # Assuming terms and definitions alternate
                try:
                    # Each term is at an even index and its corresponding definition is at the next (odd) index
                    term = term_elements[i].text.strip()
                    definition = term_elements[i+1].text.strip()

                    # Store the flashcard if both term and definition exist
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

    def save_to_json(self, flashcards: List[Dict[str, str]], output_file=OUTPUT_FILE) -> None:
        """Save the flashcards to a JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({'flashcards': flashcards}, f, ensure_ascii=False, indent=2)
            print(f"Successfully saved {len(flashcards)} flashcards to {output_file}")
        except Exception as e:
            print(f"Error saving to file: {str(e)}")

    def close(self):
        """Close the WebDriver connection and Chrome Window"""
        self.driver.close()
        self.driver.quit()

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
    url = "https://quizlet.com/502297860/realidades-2-ch8a-vocabulario-flash-cards/?funnelUUID=0b3274f9-c572-4a34-9e30-bb47cd670840"
    # url = "https://vercel.com/"
    reader = QuizletChromeReader()
    reader.open_url(url)
    reader.scan()
    reader.close()

    print("Finished")