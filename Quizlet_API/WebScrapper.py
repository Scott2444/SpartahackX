#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import time
import random
from typing import List, Dict
from user_agents import parse
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

class QuizletScraper:
    def __init__(self):
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # Configure retries
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def get_random_headers(self):
        """Generate random headers for each request"""
        user_agent = self.ua.random
        return {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'TE': 'Trailers',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Pragma': 'no-cache'
        }
        
    def get_page_content(self, url: str) -> BeautifulSoup:
        """Fetch the page content with error handling and rate limiting."""
        try:
            # Add longer random delay
            time.sleep(random.uniform(3, 7))
            
            # Visit homepage first with initial headers
            headers = self.get_random_headers()
            self.session.get("https://quizlet.com", headers=headers)
            
            # Another delay before main request
            time.sleep(random.uniform(2, 4))
            
            # Make the actual request with new headers
            headers = self.get_random_headers()
            response = self.session.get(url, headers=headers)
            
            # If we get a 403, try again with different headers
            attempts = 0
            while response.status_code == 403 and attempts < 3:
                print(f"Attempt {attempts + 1} failed, retrying...")
                time.sleep(random.uniform(4, 8))
                headers = self.get_random_headers()
                response = self.session.get(url, headers=headers)
                attempts += 1
            
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
            
        except requests.RequestException as e:
            print(f"Error: {str(e)}")
            print("Suggestions:")
            print("1. Try accessing the page in your browser first")
            print("2. Wait a few minutes before trying again")
            print("3. Check if the URL is correct and accessible")
            print("4. Try using a different network connection")
            raise Exception(f"Failed to fetch the page: {str(e)}")

    def extract_flashcards(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract flashcard data from the page using multiple methods."""
        flashcards = []
        
        # Method 1: Try to find data in script tags
        script_tags = soup.find_all('script')
        for script in script_tags:
            if script.string and '"termIdToTermsMap"' in script.string:
                try:
                    start_idx = script.string.find('{')
                    end_idx = script.string.rfind('}') + 1
                    json_str = script.string[start_idx:end_idx]
                    data = json.loads(json_str)
                    
                    if 'termIdToTermsMap' in data:
                        for term_id, term_data in data['termIdToTermsMap'].items():
                            flashcard = {
                                'term': term_data.get('word', ''),
                                'definition': term_data.get('definition', '')
                            }
                            if flashcard['term'] and flashcard['definition']:
                                flashcards.append(flashcard)
                except json.JSONDecodeError:
                    continue
        
        # Method 2: Try to find data in HTML elements
        if not flashcards:
            # Look for various possible class names
            term_pairs = soup.find_all('div', {'class': ['SetPageTerm-content', 
                                                        'SetPageTerms-term', 
                                                        'TermText']})
            for pair in term_pairs:
                term = pair.find('div', {'class': ['SetPageTerm-wordText', 
                                                  'TermText-word', 
                                                  'lang-en']})
                definition = pair.find('div', {'class': ['SetPageTerm-definitionText',
                                                       'TermText-definition',
                                                       'lang-en']})
                if term and definition:
                    flashcard = {
                        'term': term.get_text(strip=True),
                        'definition': definition.get_text(strip=True)
                    }
                    if flashcard['term'] and flashcard['definition']:
                        flashcards.append(flashcard)
        
        if not flashcards:
            raise Exception("No flashcards found. The page structure might have changed or the content is not accessible.")
            
        return flashcards

    def save_to_json(self, flashcards: List[Dict[str, str]], output_file: str):
        """Save the flashcards to a JSON file."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({'flashcards': flashcards}, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise Exception(f"Failed to save JSON file: {str(e)}")

    def scrape(self, url: str, output_file: str = 'flashcards.json'):
        """Main method to scrape flashcards from a Quizlet URL."""
        print(f"Scraping flashcards from {url}...")
        print("This might take a few moments due to anti-bot measures...")
        
        soup = self.get_page_content(url)
        flashcards = self.extract_flashcards(soup)
        self.save_to_json(flashcards, output_file)
        
        print(f"Successfully saved {len(flashcards)} flashcards to {output_file}")
        return flashcards

if __name__ == "__main__":
    scraper = QuizletScraper()
    # url = input("Enter Quizlet URL: ")
    url = "https://quizlet.com/531133429/cse331-flash-cards/"
    # url = "https://youtube.com"
    scraper.scrape(url)