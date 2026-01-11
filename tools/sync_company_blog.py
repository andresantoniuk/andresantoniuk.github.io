#!/usr/bin/env python3
"""
JAAB Company Blog Sync Script
Fetches blog entries from jaab.tech/blog/ by scraping the HTML
"""

import requests
import yaml
import os
import re
from urllib.parse import urljoin
from datetime import datetime

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("BeautifulSoup not found. Please install it with: pip install beautifulsoup4")
    exit(1)

BLOG_URL = "https://jaab.tech/blog/"

def clean_text(text):
    """Clean up whitespace"""
    if not text:
        return ""
    return ' '.join(text.split())

def detect_language(text):
    """Simple language detection"""
    if not text:
        return "es"
        
    spanish_words = {'el', 'la', 'de', 'que', 'en', 'es', 'un', 'una', 'los', 'las'}
    english_words = {'the', 'of', 'and', 'a', 'to', 'in', 'is', 'for', 'on', 'with'}
    
    text_lower = text.lower()
    words = set(re.findall(r'\w+', text_lower))
    
    spanish_score = len(words.intersection(spanish_words))
    english_score = len(words.intersection(english_words))
    
    return "en" if english_score > spanish_score else "es"

def fetch_blog_entries():
    """Scrape blog entries from jaab.tech/blog/"""
    print(f"Fetching blog index from: {BLOG_URL}")
    
    try:
        response = requests.get(BLOG_URL, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        posts_grid = soup.find('div', id='blog-posts-grid')
        if not posts_grid:
            print("Could not find blog-posts-grid in HTML")
            return []
            
        entries = []
        cards = posts_grid.find_all('a', class_='blog-card')
        
        print(f"Found {len(cards)} blog cards")
        
        for card in cards:
            # URL
            relative_url = card.get('href')
            full_url = urljoin(BLOG_URL, relative_url)
            
            # Title
            title_tag = card.find(class_='blog-card-title')
            title = clean_text(title_tag.text) if title_tag else "No Title"
            
            # Date
            date_tag = card.find('time')
            date_str = ""
            if date_tag and date_tag.get('datetime'):
                # Format: 2025-12-10T00:00:00+00:00
                dt_str = date_tag.get('datetime')
                try:
                    # Parse ISO format (strip timezone for simplicity or keep it)
                    dt = datetime.fromisoformat(dt_str)
                    date_str = dt.strftime('%Y-%m-%d')
                except ValueError:
                    date_str = clean_text(date_tag.text)
            else:
                 # Fallback to current date or text parsing if needed
                 date_str = datetime.now().strftime('%Y-%m-%d')
            
            # Excerpt
            excerpt_tag = card.find(class_='blog-card-excerpt')
            excerpt = clean_text(excerpt_tag.text) if excerpt_tag else ""
            
            # Image
            img_tag = card.find('img')
            image_url = ""
            if img_tag and img_tag.get('src'):
                image_url = urljoin(BLOG_URL, img_tag.get('src'))
            else:
                image_url = "https://jaab.tech/assets/images/logo.png"
                
            # Language
            lang = detect_language(excerpt + " " + title)

            entry_data = {
                'title': title,
                'url': full_url,
                'date': date_str,
                'excerpt': excerpt,
                'language': lang,
                'source': 'JAAB Company Blog',
                'external': True,
                'image': image_url
            }
            entries.append(entry_data)
            
        return entries
        
    except Exception as e:
        print(f"Error scraping blog: {e}")
        return []

def save_company_blog_data(entries):
    """Save blog entries to Jekyll data file"""
    if not entries:
        print("No entries to save")
        return
    
    # Create _data directory if it doesn't exist
    os.makedirs('_data', exist_ok=True)
    
    # Save to _data/company_blog.yml
    with open('_data/company_blog.yml', 'w', encoding='utf-8') as f:
        yaml.dump(entries, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    print(f"Saved {len(entries)} company blog entries to _data/company_blog.yml")

def main():
    """Main function"""
    print("🔄 Syncing JAAB Company Blog (Scraping Mode)...")
    
    # Fetch blog entries
    entries = fetch_blog_entries()
    
    if entries:
        # Save to Jekyll data files
        save_company_blog_data(entries)
        
        # Print summary
        print(f"\n✅ Successfully synced {len(entries)} blog entries:")
        for entry in entries:
            print(f"  - {entry['title']} ({entry['date']})")
    else:
        print("❌ No blog entries found")
    
    print("\n🎉 Company blog sync completed!")

if __name__ == "__main__":
    main()
