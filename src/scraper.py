import requests
from bs4 import BeautifulSoup
import json
import time
import concurrent.futures
import os

BASE_URL = "https://www.shl.com"
CATALOG_URL = "https://www.shl.com/solutions/products/product-catalog/?start={}&type=1"
OUTPUT_FILE = "data/assessments.json"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_assessment_links():
    links = []
    start = 0
    while True:
        print(f"Fetching page with start={start}...")
        url = CATALOG_URL.format(start)
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"Failed to fetch page: {response.status_code}")
                break
            
            soup = BeautifulSoup(response.content, "html.parser")
            page_links = soup.find_all("a", href=lambda href: href and "/products/product-catalog/view/" in href)
            
            if not page_links:
                print("No more links found.")
                break
            
            # Deduplicate links on the page
            seen_urls = set()
            new_links_count = 0
            for link in page_links:
                href = link['href']
                if href not in seen_urls:
                    seen_urls.add(href)
                    full_url = BASE_URL + href if href.startswith("/") else href
                    links.append({
                        "name": link.get_text(strip=True),
                        "url": full_url
                    })
                    new_links_count += 1
            
            print(f"Found {new_links_count} new links on this page.")
            
            # Check for next page
            next_button = soup.find("a", string="Next")
            if not next_button:
                print("No 'Next' button found. Stopping.")
                break
            
            start += 12  # Pagination step seems to be 12
            time.sleep(1) # Be polite
            
        except Exception as e:
            print(f"Error fetching page: {e}")
            break
            
    return links

def scrape_details(assessment):
    url = assessment['url']
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Extract Description
            # Description is usually in a p tag under a specific section or just the first substantial p
            # Let's try to find the main content area
            main_content = soup.find("main") or soup.find("div", class_="main")
            description = ""
            if main_content:
                # Look for the first paragraph that is not empty and not a link
                paragraphs = main_content.find_all("p")
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 50: # Heuristic: description is likely long
                        description = text
                        break
            
            # Extract Categories
            # Categories might be in breadcrumbs or specific tags
            categories = []
            breadcrumbs = soup.find_all("a", class_="breadcrumbs__link") # Based on inspection
            if breadcrumbs:
                categories = [b.get_text(strip=True) for b in breadcrumbs]
            
            # Extract Test Type (K, P, C, A, B, S)
            # Test Type appears as "Test Type: C P A B" in the page content
            test_type = []
            page_text = soup.get_text()
            import re
            test_type_match = re.search(r'Test Type:\s*([KPCABS\s]+)', page_text)
            if test_type_match:
                # Extract individual letters
                test_type_str = test_type_match.group(1).strip()
                test_type = [t.strip() for t in test_type_str.split() if t.strip() in ['K', 'P', 'C', 'A', 'B', 'S']]
            
            assessment['description'] = description
            assessment['categories'] = categories
            assessment['test_type'] = test_type  # New field
            return assessment
        else:
            print(f"Failed to fetch details for {url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error scraping details for {url}: {e}")
        return None

def main():
    print("Starting scraper...")
    links = get_assessment_links()
    print(f"Total assessments found: {len(links)}")
    
    # Remove duplicates based on URL
    unique_links = {link['url']: link for link in links}.values()
    print(f"Unique assessments: {len(unique_links)}")
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(scrape_details, item): item for item in unique_links}
        for future in concurrent.futures.as_completed(future_to_url):
            data = future.result()
            if data:
                results.append(data)
                if len(results) % 10 == 0:
                    print(f"Scraped {len(results)} items...")
    
    print(f"Scraping complete. Saved {len(results)} items to {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
