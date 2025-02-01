"""
Instructions

Start Chrome with this command:
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 -incognito

All other chrome tabs and applications must be closed.

"""



from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

class QuizletChromeReader:
    def __init__(self):
        # Set up Chrome options to connect to existing browser
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        # Connect to the existing Chrome instance
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print("Error connecting to Chrome. Make sure Chrome is running with remote debugging enabled.")
            raise e

    def get_active_tab_url(self):
        """Get the URL of the currently active tab"""
        return self.driver.current_url

    def extract_flashcards(self):
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
                        print(f"Found flashcard: {flashcard}")  # Debug print
                        flashcards.append(flashcard)
                        
                except Exception as e:
                    print(f"Error extracting card: {str(e)}")
                    continue


        except Exception as e:
            print(f"Error waiting for page elements: {str(e)}")
            
        return flashcards

    def save_to_json(self, flashcards, output_file='flashcards.json'):
        """Save the flashcards to a JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({'flashcards': flashcards}, f, ensure_ascii=False, indent=2)
            print(f"Successfully saved {len(flashcards)} flashcards to {output_file}")
        except Exception as e:
            print(f"Error saving to file: {str(e)}")

    def close(self):
        """Close the WebDriver connection"""
        self.driver.quit()

def main():
    """Main function to run the scraper"""
    print("Starting Quizlet Chrome Reader...")
    
    try:
        reader = QuizletChromeReader()
        url = reader.get_active_tab_url()
        
        if "quizlet.com" not in url:
            print("Please navigate to a Quizlet page in the active tab")
            return
            
        print(f"Reading flashcards from: {url}")
        flashcards = reader.extract_flashcards()
        
        if flashcards:
            reader.save_to_json(flashcards)
            print(f"Found {len(flashcards)} flashcards!")
        else:
            print("No flashcards found on the page")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if 'reader' in locals():
            reader.close()

if __name__ == "__main__":
    main()