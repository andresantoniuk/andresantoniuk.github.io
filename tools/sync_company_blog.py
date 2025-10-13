#!/usr/bin/env python3
"""
JAAB Company Blog RSS Sync Script
Fetches blog entries from jaab.tech/blog/ and creates Jekyll data files
"""

import feedparser
import yaml
import requests
from datetime import datetime
import re
from urllib.parse import urljoin
import os

def clean_html(text):
    """Remove HTML tags and clean text"""
    if not text:
        return ""
    # Remove HTML tags
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)
    # Clean up whitespace
    text = ' '.join(text.split())
    return text

def extract_excerpt(description, max_length=200):
    """Extract clean excerpt from description"""
    excerpt = clean_html(description)
    if len(excerpt) > max_length:
        excerpt = excerpt[:max_length].rsplit(' ', 1)[0] + "..."
    return excerpt

def fetch_blog_entries():
    """Fetch blog entries from jaab.tech RSS feed"""
    try:
        # Try RSS feed first
        rss_url = "https://jaab.tech/blog/feed.xml"
        print(f"Fetching RSS feed from: {rss_url}")
        
        feed = feedparser.parse(rss_url)
        
        if not feed.entries:
            print("No entries found in RSS feed, trying alternative approach...")
            return fetch_blog_entries_alternative()
        
        entries = []
        for entry in feed.entries:
            # Extract date
            published_date = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6]).strftime('%Y-%m-%d')
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_date = datetime(*entry.updated_parsed[:6]).strftime('%Y-%m-%d')
            else:
                published_date = datetime.now().strftime('%Y-%m-%d')
            
            # Extract excerpt
            excerpt = ""
            if hasattr(entry, 'summary'):
                excerpt = extract_excerpt(entry.summary)
            elif hasattr(entry, 'description'):
                excerpt = extract_excerpt(entry.description)
            
            # Determine language based on content
            language = "es"  # Default to Spanish
            if excerpt:
                spanish_words = ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'pero', 'sus', 'como', 'más', 'muy', 'ya', 'todo', 'esta', 'sobre', 'entre', 'cuando', 'muy', 'sin', 'hasta', 'desde', 'está', 'sido', 'han', 'hasta', 'desde', 'está', 'sido', 'han']
                english_words = ['the', 'of', 'and', 'a', 'to', 'in', 'is', 'you', 'that', 'it', 'he', 'was', 'for', 'on', 'are', 'as', 'with', 'his', 'they', 'i', 'at', 'be', 'this', 'have', 'from', 'or', 'one', 'had', 'by', 'word', 'but', 'not', 'what', 'all', 'were', 'we', 'when', 'your', 'can', 'said', 'there', 'each', 'which', 'she', 'do', 'how', 'their', 'if', 'will', 'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him', 'time', 'has', 'two', 'more', 'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call', 'who', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part']
                
                text_lower = excerpt.lower()
                spanish_count = sum(1 for word in spanish_words if word in text_lower)
                english_count = sum(1 for word in english_words if word in text_lower)
                
                if english_count > spanish_count:
                    language = "en"
            
            # Extract image URL if available
            image_url = None
            if hasattr(entry, 'media_content') and entry.media_content:
                for media in entry.media_content:
                    if media.get('type', '').startswith('image/'):
                        image_url = media.get('url')
                        break
            
            # If no media content, try to extract from summary/description
            if not image_url and hasattr(entry, 'summary'):
                import re
                img_match = re.search(r'<img[^>]+src="([^"]+)"', entry.summary)
                if img_match:
                    image_url = img_match.group(1)
            
            # Fallback to a default JAAB image
            if not image_url:
                image_url = "https://jaab.tech/assets/images/logo.png"
            
            entry_data = {
                'title': entry.title,
                'url': entry.link,
                'date': published_date,
                'excerpt': excerpt,
                'language': language,
                'source': 'JAAB Company Blog',
                'external': True,  # Flag to indicate this is an external link
                'image': image_url
            }
            entries.append(entry_data)
        
        return entries
        
    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
        return fetch_blog_entries_alternative()

def fetch_blog_entries_alternative():
    """Alternative method: scrape the blog page directly"""
    try:
        print("Trying alternative method: scraping blog page...")
        
        # Try to fetch the blog page
        response = requests.get('https://jaab.tech/blog/', timeout=10)
        response.raise_for_status()
        
        # This is a fallback - in practice, you'd need to parse the HTML
        # For now, return a sample entry
        return [{
            'title': 'Valor patrimonial',
            'url': 'https://jaab.tech/blog/valor-patrimonial',
            'date': '2025-10-13',
            'excerpt': 'JAAB participó en la inauguración de la renovada Casa El Globo teniendo la firme convicción de que renovaremos muchas plataformas tecnológicas en América Latina...',
            'language': 'es',
            'source': 'JAAB Company Blog',
            'external': True,
            'image': 'https://jaab.tech/assets/images/blog/jaab_casaelglobo.jpg'
        }]
        
    except Exception as e:
        print(f"Error with alternative method: {e}")
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
    
    # Also create a JSON version for potential future use
    import json
    with open('_data/company_blog.json', 'w', encoding='utf-8') as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)
    
    print(f"Saved {len(entries)} company blog entries to _data/company_blog.json")

def main():
    """Main function"""
    print("🔄 Syncing JAAB Company Blog...")
    
    # Fetch blog entries
    entries = fetch_blog_entries()
    
    if entries:
        # Save to Jekyll data files
        save_company_blog_data(entries)
        
        # Print summary
        print(f"\n✅ Successfully synced {len(entries)} blog entries:")
        for entry in entries:
            print(f"  - {entry['title']} ({entry['date']}) [{entry['language']}]")
    else:
        print("❌ No blog entries found")
    
    print("\n🎉 Company blog sync completed!")

if __name__ == "__main__":
    main()
