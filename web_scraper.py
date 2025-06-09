#!/usr/bin/env python3
"""
Email Collector from Search Results
A tool to extract email addresses from web search results.

WARNING: Web scraping may violate terms of service. Use responsibly.
Consider using official APIs and respecting rate limits.
"""

import requests
import re
import time
import random
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import csv
from typing import Set, List, Dict
import argparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailCollector:
    def __init__(self, delay_range=(1, 3)):
        """
        Initialize EmailCollector
        
        Args:
            delay_range: Tuple of min and max delay between requests
        """
        self.delay_range = delay_range
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
    def extract_emails_from_text(self, text: str) -> Set[str]:
        """Extract email addresses from text using regex"""
        return set(self.email_pattern.findall(text))
    
    def get_page_content(self, url: str) -> str:
        """Fetch content from a URL with error handling"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return ""
    
    def search_duckduckgo(self, query: str, num_results: int = 10) -> List[str]:
        """
        Search DuckDuckGo for URLs (alternative to Google)
        DuckDuckGo is more permissive for automated searches
        """
        search_url = "https://duckduckgo.com/html/"
        params = {'q': query}
        
        try:
            response = self.session.get(search_url, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            urls = []
            
            # Extract URLs from search results
            for link in soup.find_all('a', {'class': 'result__url'}):
                href = link.get('href')
                if href and href.startswith('http'):
                    urls.append(href)
                    if len(urls) >= num_results:
                        break
                        
            return urls
            
        except Exception as e:
            logger.error(f"Error searching DuckDuckGo: {e}")
            return []
    
    def extract_emails_from_url(self, url: str) -> Set[str]:
        """Extract emails from a specific URL"""
        logger.info(f"Extracting emails from: {url}")
        
        content = self.get_page_content(url)
        if not content:
            return set()
        
        # Parse HTML to get text content
        try:
            soup = BeautifulSoup(content, 'html.parser')
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            text = soup.get_text()
        except Exception:
            # Fallback to raw content if parsing fails
            text = content
        
        emails = self.extract_emails_from_text(text)
        logger.info(f"Found {len(emails)} emails on {url}")
        
        return emails
    
    def collect_emails_from_search(self, query: str, num_results: int = 10, 
                                 max_pages_per_site: int = 3) -> Dict[str, Set[str]]:
        """
        Collect emails from search results
        
        Args:
            query: Search query
            num_results: Number of search results to process
            max_pages_per_site: Maximum pages to check per domain
            
        Returns:
            Dictionary mapping URLs to sets of emails found
        """
        logger.info(f"Starting email collection for query: '{query}'")
        
        # Get search results
        urls = self.search_duckduckgo(query, num_results)
        if not urls:
            logger.warning("No URLs found in search results")
            return {}
        
        results = {}
        processed_domains = {}
        
        for url in urls:
            domain = urlparse(url).netloc
            
            # Limit pages per domain
            if domain in processed_domains:
                if processed_domains[domain] >= max_pages_per_site:
                    continue
                processed_domains[domain] += 1
            else:
                processed_domains[domain] = 1
            
            # Add delay between requests
            time.sleep(random.uniform(*self.delay_range))
            
            emails = self.extract_emails_from_url(url)
            if emails:
                results[url] = emails
        
        return results
    
    def save_results(self, results: Dict[str, Set[str]], filename: str = "collected_emails.csv"):
        """Save results to CSV file"""
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['URL', 'Email'])
            
            for url, emails in results.items():
                for email in emails:
                    writer.writerow([url, email])
        
        logger.info(f"Results saved to {filename}")
    
    def print_summary(self, results: Dict[str, Set[str]]):
        """Print summary of collected emails"""
        total_emails = sum(len(emails) for emails in results.values())
        unique_emails = set()
        for emails in results.values():
            unique_emails.update(emails)
        
        print(f"\n=== EMAIL COLLECTION SUMMARY ===")
        print(f"URLs processed: {len(results)}")
        print(f"Total emails found: {total_emails}")
        print(f"Unique emails: {len(unique_emails)}")
        print(f"\nUnique emails list:")
        for email in sorted(unique_emails):
            print(f"  - {email}")

def main():
    parser = argparse.ArgumentParser(description='Collect emails from web search results')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--results', '-r', type=int, default=10, 
                       help='Number of search results to process (default: 10)')
    parser.add_argument('--output', '-o', default='collected_emails.csv',
                       help='Output CSV file (default: collected_emails.csv)')
    parser.add_argument('--delay', '-d', nargs=2, type=float, default=[1.0, 3.0],
                       help='Delay range between requests in seconds (default: 1 3)')
    parser.add_argument('--max-pages', '-m', type=int, default=3,
                       help='Maximum pages per domain (default: 3)')
    
    args = parser.parse_args()
    
    # Create collector
    collector = EmailCollector(delay_range=tuple(args.delay))
    
    # Collect emails
    results = collector.collect_emails_from_search(
        query=args.query,
        num_results=args.results,
        max_pages_per_site=args.max_pages
    )
    
    if results:
        # Save and display results
        collector.save_results(results, args.output)
        collector.print_summary(results)
    else:
        print("No emails found.")

def interactive_mode():
    """Run the email collector in interactive mode"""
    print("=" * 50)
    print("EMAIL COLLECTOR - INTERACTIVE MODE")
    print("=" * 50)
    print("This tool helps you collect email addresses from web search results.")
    print("Note: Please use responsibly and respect website terms of service.\n")
    
    # Get search query from user
    while True:
        query = input("Enter your search query: ").strip()
        if query:
            break
        print("Please enter a valid search query.")
    
    # Get number of results
    while True:
        try:
            num_results = input("Number of search results to process (default: 10): ").strip()
            num_results = int(num_results) if num_results else 10
            if num_results > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get output filename
    output_file = input("Output filename (default: collected_emails.csv): ").strip()
    output_file = output_file if output_file else "collected_emails.csv"
    
    # Get delay settings
    while True:
        try:
            delay_input = input("Delay between requests in seconds (default: 1-3): ").strip()
            if not delay_input:
                delay_range = (1.0, 3.0)
                break
            elif '-' in delay_input:
                min_delay, max_delay = map(float, delay_input.split('-'))
                delay_range = (min_delay, max_delay)
                break
            else:
                delay = float(delay_input)
                delay_range = (delay, delay)
                break
        except ValueError:
            print("Please enter a valid delay (e.g., '2' or '1-3').")
    
    print(f"\n{'='*30}")
    print("SEARCH CONFIGURATION:")
    print(f"Query: {query}")
    print(f"Results: {num_results}")
    print(f"Output: {output_file}")
    print(f"Delay: {delay_range[0]}-{delay_range[1]} seconds")
    print(f"{'='*30}\n")
    
    # Confirm before starting
    confirm = input("Start email collection? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Operation cancelled.")
        return
    
    # Create collector and start search
    print("\nStarting email collection...")
    collector = EmailCollector(delay_range=delay_range)
    
    try:
        results = collector.collect_emails_from_search(
            query=query,
            num_results=num_results
        )
        
        if results:
            collector.save_results(results, output_file)
            collector.print_summary(results)
            print(f"\nResults have been saved to: {output_file}")
        else:
            print("\nNo emails found with the given search query.")
            print("Try refining your search terms or using different keywords.")
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    # Check if command line arguments are provided
    import sys
    if len(sys.argv) == 1:
        # Run in interactive mode
        interactive_mode()
    else:
        # Run with command line arguments
        main()