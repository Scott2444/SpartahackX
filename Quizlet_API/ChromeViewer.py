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
            print("See instructions in the comments above.")
            raise e

    def get_active_tab_url(self):
        """Get the URL of the currently active tab"""
        return self.driver.current_url

    def extract_flashcards(self):
        """Extract flashcards from the current page"""
        flashcards = []
        
        # Wait for the flashcard elements to load
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "SetPageTerm-content"))
            )
            
            # Get all flashcard containers
            cards = self.driver.find_elements(By.CLASS_NAME, "SetPageTerm-content")
            
            for card in cards:
                try:
                    # Get term and definition
                    term = card.find_element(By.CLASS_NAME, "SetPageTerm-wordText").text
                    definition = card.find_element(By.CLASS_NAME, "SetPageTerm-definitionText").text
                    
                    if term and definition:
                        flashcards.append({
                            'term': term.strip(),
                            'definition': definition.strip()
                        })
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
        print(f"Currrent URL: {url}")
        
        if "quizlet.com" not in url:
            print("Please navigate to a Quizlet page in the active tab")
            return
            
        print(f"Reading flashcards from: {url}")
        flashcards = reader.extract_flashcards()
        
        if flashcards:
            reader.save_to_json(flashcards)
        else:
            print("No flashcards found on the page")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        if 'reader' in locals():
            reader.close()

if __name__ == "__main__":
    main()