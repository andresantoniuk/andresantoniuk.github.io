#!/usr/bin/env python3
"""
LinkedIn HTML Article Parser
Parse LinkedIn exported HTML files and convert to Jekyll Markdown
"""

import os
import re
import sys
import argparse
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin
import time

from bs4 import BeautifulSoup
from slugify import slugify
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LinkedInHTMLParser:
    def __init__(self, debug=False):
        self.debug = debug
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
        
    def log(self, message):
        """Log message if debug mode is enabled"""
        if self.debug:
            print(f"[DEBUG] {message}")
    
    def setup_driver(self):
        """Setup Selenium Chrome driver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            self.log(f"Error setting up Chrome driver: {e}")
            return False
    
    def cleanup_driver(self):
        """Cleanup Selenium driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def fetch_header_image_from_linkedin(self, linkedin_url):
        """Fetch header image from live LinkedIn article"""
        try:
            if not self.setup_driver():
                return None
            
            self.log(f"Fetching header image from LinkedIn: {linkedin_url}")
            self.driver.get(linkedin_url)
            
            # Wait for the page to load
            time.sleep(3)
            
            # Look for header image - try multiple selectors
            header_image_url = None
            
            # Strategy 1: Look for article cover image
            try:
                cover_img = self.driver.find_element(By.CSS_SELECTOR, 'img[data-media-urn*="article-cover_image"]')
                header_image_url = cover_img.get_attribute('src')
                self.log(f"Found cover image: {header_image_url}")
            except:
                pass
            
            # Strategy 2: Look for the first large image in the article
            if not header_image_url:
                try:
                    images = self.driver.find_elements(By.TAG_NAME, 'img')
                    for img in images:
                        src = img.get_attribute('src')
                        if src and 'media.licdn.com' in src and 'article-cover_image' in src:
                            header_image_url = src
                            self.log(f"Found header image: {header_image_url}")
                            break
                except:
                    pass
            
            # Strategy 3: Look for any large image at the top of the article
            if not header_image_url:
                try:
                    images = self.driver.find_elements(By.CSS_SELECTOR, 'article img, .article-content img, .post-content img')
                    for img in images:
                        src = img.get_attribute('src')
                        if src and 'media.licdn.com' in src:
                            # Check if it's a reasonable size (not a small icon)
                            try:
                                width = img.get_attribute('width')
                                height = img.get_attribute('height')
                                if width and height and int(width) > 200 and int(height) > 200:
                                    header_image_url = src
                                    self.log(f"Found large image: {header_image_url}")
                                    break
                            except:
                                pass
                except:
                    pass
            
            return header_image_url
            
        except Exception as e:
            self.log(f"Error fetching header image from LinkedIn: {e}")
            return None
        finally:
            self.cleanup_driver()
    
    def capture_x_post_screenshot(self, x_url, post_slug, post_index):
        """Capture a screenshot of an X post"""
        try:
            if not self.setup_driver():
                return None
            
            self.log(f"Capturing screenshot of X post: {x_url}")
            self.driver.get(x_url)
            
            # Wait for the page to load
            time.sleep(5)
            
            # Check if the post is available (not deleted/suspended/private)
            page_source = self.driver.page_source.lower()
            
            # More specific indicators for unavailable posts
            unavailable_indicators = [
                'this post is not available',
                'this tweet is not available', 
                'tweet unavailable',
                'post unavailable',
                'this account is suspended',
                'this account is private',
                'tweet not found',
                'post not found',
                'unable to load this tweet',
                'unable to load this post',
                'this tweet has been deleted',
                'this post has been deleted'
            ]
            
            # Check for specific error patterns that indicate unavailability
            error_patterns = [
                'this tweet is unavailable' in page_source,
                'this post is unavailable' in page_source,
                'esta página no existe' in page_source,  # Spanish: "this page doesn't exist"
                'intenta hacer otra búsqueda' in page_source,  # Spanish: "try another search"
                'don\'t fret' in page_source and 'try again' in page_source,  # English error pattern
                'give it another shot' in page_source and 'try again' in page_source
            ]
            
            # Check for error messages that indicate unavailability
            has_error_message = any(indicator in page_source for indicator in unavailable_indicators) or any(error_patterns)
            
            # Also check for the specific "something went wrong" pattern but only if there's no actual tweet content
            has_something_wrong = 'something went wrong' in page_source and 'try reloading' in page_source
            has_tweet_content = 'data-testid="tweet"' in page_source or 'article[role="article"]' in page_source
            
            # Post is unavailable if it has error indicators but no tweet content
            if has_error_message or (has_something_wrong and not has_tweet_content):
                self.log(f"X post is not available: {x_url}")
                return None
            
            # Try to find the main tweet/post element
            tweet_element = None
            try:
                # Try different selectors for the tweet content
                selectors = [
                    '[data-testid="tweet"]',
                    'article[role="article"]',
                    '[data-testid="tweetText"]',
                    '.tweet',
                    '[data-testid="primaryColumn"]'
                ]
                
                for selector in selectors:
                    try:
                        tweet_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if tweet_element:
                            self.log(f"Found tweet element with selector: {selector}")
                            break
                    except:
                        continue
                
                if not tweet_element:
                    # Check if we're on a valid tweet page by looking for tweet-specific content
                    if 'data-testid="tweet"' not in page_source and 'article[role="article"]' not in page_source:
                        self.log(f"No tweet content found, post may be unavailable: {x_url}")
                        return None
                    
                    # Fallback: take screenshot of the entire page
                    tweet_element = self.driver.find_element(By.TAG_NAME, 'body')
                    self.log("Using body element as fallback")
                
            except Exception as e:
                self.log(f"Error finding tweet element: {e}")
                return None
            
            # Take screenshot of the tweet element
            screenshot_path = f"assets/img/posts/{post_slug}/x_post_{post_index}.png"
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            
            # Scroll to the element to ensure it's visible
            self.driver.execute_script("arguments[0].scrollIntoView(true);", tweet_element)
            time.sleep(2)
            
            # Take screenshot
            tweet_element.screenshot(screenshot_path)
            
            self.log(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            self.log(f"Error capturing X post screenshot: {e}")
            return None
        finally:
            self.cleanup_driver()
    
    def fetch_linkedin_links(self, linkedin_url):
        """Fetch people and company links from live LinkedIn article"""
        try:
            if not self.setup_driver():
                return {}
            
            self.log(f"Fetching LinkedIn links from: {linkedin_url}")
            self.driver.get(linkedin_url)
            
            # Wait for the page to load
            time.sleep(5)
            
            links_map = {}
            
            # Find all links in the article
            try:
                # Look for links within the article content - try multiple selectors
                selectors = [
                    'article a',
                    '.article-content a', 
                    '.post-content a',
                    '[data-testid="main-feed-activity"] a',
                    'a[href*="linkedin.com"]',
                    'a[href*="linkedin.com/in/"]',
                    'a[href*="linkedin.com/company/"]',
                    'a[href*="linkedin.com/school/"]'
                ]
                
                all_links = []
                for selector in selectors:
                    try:
                        links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        all_links.extend(links)
                    except:
                        continue
                
                # Remove duplicates
                seen_links = set()
                unique_links = []
                for link in all_links:
                    try:
                        href = link.get_attribute('href')
                        if href and href not in seen_links:
                            seen_links.add(href)
                            unique_links.append(link)
                    except:
                        continue
                
                for link in unique_links:
                    try:
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        
                        if href and ('linkedin.com/in/' in href or 'linkedin.com/company/' in href or 'linkedin.com/school/' in href):
                            # Try to get the name from various attributes
                            name = text
                            if not name:
                                name = link.get_attribute('title') or ''
                            if not name:
                                name = link.get_attribute('aria-label') or ''
                            if not name:
                                # Try to extract name from the URL
                                if '/in/' in href:
                                    name = href.split('/in/')[-1].split('?')[0].replace('-', ' ').title()
                                elif '/company/' in href:
                                    name = href.split('/company/')[-1].split('?')[0].replace('-', ' ').title()
                                elif '/school/' in href:
                                    name = href.split('/school/')[-1].split('?')[0].replace('-', ' ').title()
                            
                            if name:
                                # Clean up the name
                                name = name.strip()
                                if name and name not in links_map:
                                    links_map[name] = href
                                    self.log(f"Found LinkedIn link: {name} -> {href}")
                                    
                                    # Create additional variations for better matching
                                    # Add the name without special characters
                                    clean_name = name.replace(' ', '').replace('-', '').replace('_', '').lower()
                                    if clean_name != name.lower() and clean_name not in links_map:
                                        links_map[clean_name] = href
                                    
                                    # Add first name + last name combination
                                    name_parts = name.split()
                                    if len(name_parts) >= 2:
                                        first_last = f"{name_parts[0]} {name_parts[-1]}"
                                        if first_last != name and first_last not in links_map:
                                            links_map[first_last] = href
                                    
                                    # Add abbreviation (first initial + last name)
                                    if len(name_parts) >= 2:
                                        abbreviation = name_parts[0][0].lower() + name_parts[-1].lower()
                                        if abbreviation not in links_map:
                                            links_map[abbreviation] = href
                                    
                                    # Add full name without spaces
                                    no_spaces = name.replace(' ', '')
                                    if no_spaces != name and no_spaces not in links_map:
                                        links_map[no_spaces] = href
                            
                    except Exception as e:
                        continue
                        
            except Exception as e:
                self.log(f"Error finding LinkedIn links: {e}")
            
            return links_map
            
        except Exception as e:
            self.log(f"Error fetching LinkedIn links: {e}")
            return {}
        finally:
            self.cleanup_driver()
    
    def parse_html_file(self, html_file_path, language='en'):
        """Parse a LinkedIn exported HTML file"""
        try:
            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract metadata
            title = self.extract_title(soup)
            author = self.extract_author(soup)
            date = self.extract_date(soup)
            original_url = self.extract_original_url(soup)
            
            # Extract content
            content = self.extract_content(soup, original_url)
            
            if not content:
                self.log("No content found")
                return None
            
            # Fetch LinkedIn links from live article
            linkedin_links = {}
            if original_url:
                linkedin_links = self.fetch_linkedin_links(original_url)
                self.log(f"Fetched {len(linkedin_links)} LinkedIn links from live article")
            
            # Create post slug
            post_slug = slugify(title)
            
            # Process images
            content = self.process_images(content, post_slug)
            
            # Process X post screenshots
            content = self.process_x_post_screenshots(content, post_slug)
            
            # Process LinkedIn links
            content = self.process_linkedin_links(content, linkedin_links)
            
            # Add original source quote
            content = self.add_original_source_quote(content, original_url, language)
            
            # Create front matter
            front_matter = self.create_front_matter(title, author, date, language, original_url)
            
            # Combine front matter and content
            markdown_content = f"{front_matter}\n\n{content}"
            
            return {
                'content': markdown_content,
                'filename': f"{date}-{post_slug}.md",
                'slug': post_slug
            }
            
        except Exception as e:
            self.log(f"Error parsing HTML file: {e}")
            return None
    
    def extract_title(self, soup):
        """Extract article title"""
        try:
            # Try h1 first
            h1 = soup.find('h1')
            if h1:
                title = h1.get_text().strip()
                if title:
                    # Clean up quotes and special characters
                    title = title.strip('"').strip("'").replace('"', '').replace("'", '')
                    return title
            
            # Try title tag
            title_tag = soup.find('title')
            if title_tag:
                title = title_tag.get_text().strip()
                if title:
                    # Clean up quotes and special characters
                    title = title.strip('"').strip("'").replace('"', '').replace("'", '')
                    return title
            
            return "Untitled Article"
        except Exception as e:
            self.log(f"Error extracting title: {e}")
            return "Untitled Article"
    
    def extract_author(self, soup):
        """Extract article author from the HTML structure"""
        try:
            # Look for author information in the HTML
            # LinkedIn exports usually don't include author in the HTML, so we'll use a default
            return "Juan Andrés Antoniuk"  # Default author
        except Exception as e:
            self.log(f"Error extracting author: {e}")
            return "Unknown Author"
    
    def extract_date(self, soup):
        """Extract article publication date"""
        try:
            # Look for published date
            published = soup.find('p', class_='published')
            if published:
                date_text = published.get_text().strip()
                # Extract date from "Published on 2025-09-09 13:00"
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                if date_match:
                    return date_match.group(1)
            
            # Fallback to created date
            created = soup.find('p', class_='created')
            if created:
                date_text = created.get_text().strip()
                # Extract date from "Created on 2025-09-08 23:12"
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_text)
                if date_match:
                    return date_match.group(1)
            
            return datetime.now().strftime("%Y-%m-%d")
        except Exception as e:
            self.log(f"Error extracting date: {e}")
            return datetime.now().strftime("%Y-%m-%d")
    
    def extract_original_url(self, soup):
        """Extract original LinkedIn URL"""
        try:
            # Look for the original URL in h1 link
            h1 = soup.find('h1')
            if h1:
                link = h1.find('a')
                if link:
                    return link.get('href', '')
            
            return ""
        except Exception as e:
            self.log(f"Error extracting original URL: {e}")
            return ""
    
    def extract_content(self, soup, linkedin_url=None):
        """Extract main article content and header image"""
        try:
            # Find the main content div - look for the div that contains the actual content
            content_div = None
            
            # Try to find the content div after the header elements
            body = soup.find('body')
            if body:
                # Look for the div that contains paragraphs (the main content)
                for div in body.find_all('div'):
                    if div.find('p'):
                        content_div = div
                        break
            
            # Fallback to first div if no content div found
            if not content_div:
                content_div = soup.find('div')
            
            if not content_div:
                return None
            
            # Look for a working header image
            header_img = None
            header_image_url = None
            
            # Check if there's a broken header image URL in the HTML
            has_broken_header = False
            all_images = soup.find_all('img')
            for img in all_images:
                src = img.get('src', '')
                if src and 'media.licdn.com' in src:
                    # Check if this is a broken header image URL
                    if 'mediaD4D12AQ' in src and not ('article-cover_image' in src or 'article-inline_image' in src):
                        self.log(f"[DEBUG] Found broken header image URL: {src}")
                        has_broken_header = True
                        break
            
            # If there's a broken header image, try to fetch the original from LinkedIn
            if has_broken_header and linkedin_url:
                self.log("[DEBUG] Found broken header image in HTML, fetching original from LinkedIn...")
                header_image_url = self.fetch_header_image_from_linkedin(linkedin_url)
                
                if header_image_url:
                    # Create a new img tag with the fetched URL
                    header_img = soup.new_tag('img')
                    header_img['src'] = header_image_url
                    header_img['alt'] = 'Article header image'
                    header_img['title'] = 'Article header image'
                    self.log(f"[DEBUG] Fetched original header image from LinkedIn: {header_image_url}")
                else:
                    self.log("[DEBUG] Failed to fetch header image from LinkedIn, using first working image from HTML")
                    # Fallback to first working image
                    for img in all_images:
                        src = img.get('src', '')
                        if src and 'media.licdn.com' in src and ('article-cover_image' in src or 'article-inline_image' in src):
                            header_img = img
                            header_image_url = src
                            self.log(f"[DEBUG] Using first working image from HTML: {src}")
                            break
            else:
                # No broken header image, use the first working image from HTML
                for img in all_images:
                    src = img.get('src', '')
                    if src and 'media.licdn.com' in src and ('article-cover_image' in src or 'article-inline_image' in src):
                        header_img = img
                        header_image_url = src
                        self.log(f"[DEBUG] Found working header image in HTML: {src}")
                        break
            
            if header_img:
                # Create a div container for the header image
                header_div = soup.new_tag('div', **{'class': 'header-image'})
                header_div.append(header_img)  # Keep the img tag inside the div
                content_div.insert(0, header_div)
            else:
                self.log("[DEBUG] No header image found")
            
            # Convert to markdown
            markdown = self.convert_to_markdown(content_div)
            
            return markdown
            
        except Exception as e:
            self.log(f"Error extracting content: {e}")
            return None
    
    def convert_to_markdown(self, element):
        """Convert HTML element to Markdown"""
        markdown = ""
        
        # Store image URLs for later download
        self.image_urls = []
        
        # Store X post URLs for screenshot capture
        self.x_post_urls = []
        
        # Process the main content div recursively
        markdown = self.process_element_recursive(element)
        
        # Clean up the markdown
        markdown = re.sub(r'\n\s*\n\s*\n+', '\n\n', markdown)  # Multiple newlines to double
        markdown = re.sub(r'[ \t]+', ' ', markdown)  # Clean up spaces
        
        return markdown.strip()
    
    def process_element_recursive(self, element):
        """Recursively process HTML elements to Markdown"""
        markdown = ""
        
        # Handle text nodes (NavigableString)
        if isinstance(element, str):
            text = element.strip()
            if text:
                markdown += text + " "
            return markdown
        
        # Handle different element types
        if element.name == 'img':
            src = element.get('src', '')
            alt = element.get('alt', '')
            title = element.get('title', '')
            
            # Check if this is a header image (in a header-image div)
            is_header_image = False
            parent = element.parent
            while parent:
                if hasattr(parent, 'get') and parent.get('class') and 'header-image' in parent.get('class'):
                    is_header_image = True
                    break
                parent = parent.parent
            
            # Also check if this is the first image in the content (likely header)
            if not is_header_image and 'article-cover_image' in src:
                is_header_image = True
            
            if src and (self.is_relevant_image(src, alt, title) or is_header_image):
                # Use title as alt if available, otherwise use alt, otherwise use a descriptive default
                if title:
                    image_alt = title
                elif alt:
                    image_alt = alt
                else:
                    # Use a more descriptive default based on image position
                    if is_header_image:
                        image_alt = "Article header image"
                    else:
                        image_alt = f"Article image {len(self.image_urls) + 1}"
                
                markdown += f"\n\n![{image_alt}]({src})\n\n"
                self.image_urls.append((image_alt, src))
        
        elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            text = self.get_element_text_with_formatting(element)
            if text:
                level = int(element.name[1])
                markdown += f"\n\n{'#' * level} {text}\n\n"
        
        elif element.name == 'p':
            text = self.get_element_text_with_formatting(element)
            if text:
                markdown += f"{text}\n\n"
        
        elif element.name == 'ul':
            for li in element.find_all('li', recursive=False):
                # Process each list item with proper formatting
                li_text = self.process_list_item(li)
                if li_text:
                    markdown += f"- {li_text}\n"
            markdown += "\n"
        
        elif element.name == 'ol':
            for i, li in enumerate(element.find_all('li', recursive=False), 1):
                text = self.get_element_text_with_formatting(li)
                if text:
                    markdown += f"{i}. {text}\n"
            markdown += "\n"
        
        elif element.name == 'blockquote':
            text = self.get_element_text_with_formatting(element)
            if text:
                markdown += f"> {text}\n\n"
        
        elif element.name == 'span':
            # Handle span elements - check for iframe children
            iframes = element.find_all('iframe')
            if iframes:
                # Process iframe children
                for iframe in iframes:
                    src = iframe.get('src', '')
                    if 'youtube.com' in src or 'youtu.be' in src:
                        # Extract video ID from YouTube URL
                        video_id = self.extract_youtube_video_id(src)
                        if video_id:
                            markdown += f"\n\n[![YouTube Video](https://img.youtube.com/vi/{video_id}/maxresdefault.jpg)](https://www.youtube.com/watch?v={video_id})\n\n"
                        else:
                            markdown += f"\n\n[🎥 YouTube Video]({src})\n\n"
                    else:
                        # Other iframe content
                        markdown += f"\n\n[Embedded Content]({src})\n\n"
            else:
                # Regular span - get text content
                text = self.get_element_text_with_formatting(element)
                if text:
                    markdown += text
        
        elif element.name == 'iframe':
            # Handle iframe elements (YouTube videos, etc.)
            src = element.get('src', '')
            if 'youtube.com' in src or 'youtu.be' in src:
                # Extract video ID from YouTube URL
                video_id = self.extract_youtube_video_id(src)
                if video_id:
                    markdown += f"\n\n[![YouTube Video](https://img.youtube.com/vi/{video_id}/maxresdefault.jpg)](https://www.youtube.com/watch?v={video_id})\n\n"
                else:
                    markdown += f"\n\n[🎥 YouTube Video]({src})\n\n"
            else:
                # Other iframe content
                markdown += f"\n\n[Embedded Content]({src})\n\n"
        
        elif element.name == 'a':
            # Handle standalone embedded social media posts
            if 'class' in element.attrs and 'embedded' in element.get('class', []):
                href = element.get('href', '')
                link_text = element.get_text()
                if href and link_text:
                    if 'twitter.com' in href or 'x.com' in href:
                        # Store X post URL for screenshot capture
                        self.x_post_urls.append(href)
                        post_index = len(self.x_post_urls)
                        
                        # Create a placeholder that will be replaced with screenshot
                        markdown += f"\n\n> **🐦 X Post**\n> \n> {link_text}\n> \n> [View on X]({href})\n\n"
                    elif 'youtube.com' in href or 'youtu.be' in href:
                        # Handle YouTube videos
                        # Extract video ID from YouTube URL
                        video_id = self.extract_youtube_video_id(href)
                        if video_id:
                            markdown += f"\n\n[![YouTube Video](https://img.youtube.com/vi/{video_id}/maxresdefault.jpg)]({href})\n\n"
                        else:
                            markdown += f"\n\n[🎥 YouTube Video: {link_text}]({href})\n\n"
                    else:
                        # Other embedded posts
                        markdown += f"[{link_text}]({href})\n\n"
            else:
                # Regular link - process with formatting
                text = self.get_element_text_with_formatting(element)
                if text:
                    markdown += f"{text}\n\n"
        
        elif element.name == 'figure':
            # Handle figure elements (usually contain images)
            for img in element.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '')
                title = img.get('title', '')
                
                if src and self.is_relevant_image(src, alt, title):
                    # Use title as alt if available, otherwise use alt, otherwise use a descriptive default
                    if title:
                        image_alt = title
                    elif alt:
                        image_alt = alt
                    else:
                        # Use a more descriptive default based on image position
                        image_alt = f"Article image {len(self.image_urls) + 1}"
                    
                    markdown += f"\n\n![{image_alt}]({src})\n\n"
                    self.image_urls.append((image_alt, src))
        
        elif element.name == 'div':
            # Only process divs that don't contain other block elements
            if not element.find(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'ul', 'ol', 'blockquote', 'figure']):
                text = self.get_element_text_with_formatting(element)
                if text and len(text) > 50:
                    markdown += f"{text}\n\n"
            else:
                # Process child elements
                for child in element.children:
                    if hasattr(child, 'name'):
                        markdown += self.process_element_recursive(child)
        
        else:
            # For other elements, process their children
            for child in element.children:
                if hasattr(child, 'name') and child.name is not None:
                    markdown += self.process_element_recursive(child)
                elif isinstance(child, str):
                    # Handle text nodes
                    text = child.strip()
                    if text:
                        markdown += text + " "
        
        return markdown
    
    def get_element_text_with_formatting(self, element):
        """Get element text while preserving formatting"""
        text = ""
        
        for child in element.children:
            if isinstance(child, str):
                text += child
            elif child.name in ['strong', 'b']:
                text += f"**{child.get_text()}**"
            elif child.name in ['em', 'i']:
                text += f"*{child.get_text()}*"
            elif child.name == 'a':
                href = child.get('href', '')
                link_text = child.get_text()
                if href and link_text:
                    # Check if this is an embedded social media post
                    if 'class' in child.attrs and 'embedded' in child.get('class', []):
                        # This is an embedded social media post (Twitter/X, etc.)
                        if 'twitter.com' in href or 'x.com' in href:
                            # Store X post URL for screenshot capture
                            self.x_post_urls.append(href)
                            post_index = len(self.x_post_urls)
                            
                            # Create a placeholder that will be replaced with screenshot
                            text += f"\n\n> **🐦 X Post**\n> \n> {link_text}\n> \n> [View on X]({href})\n\n"
                        elif 'youtube.com' in href or 'youtu.be' in href:
                            # Handle YouTube videos
                            video_id = self.extract_youtube_video_id(href)
                            if video_id:
                                text += f"\n\n[![YouTube Video](https://img.youtube.com/vi/{video_id}/maxresdefault.jpg)]({href})\n\n"
                            else:
                                text += f"\n\n[🎥 YouTube Video: {link_text}]({href})\n\n"
                        else:
                            # Other embedded posts
                            text += f"[{link_text}]({href})"
                    else:
                        # Regular link
                        text += f"[{link_text}]({href})"
                elif link_text:
                    # Handle LinkedIn mention links (no href) - create LinkedIn search link
                    # Replace pipe characters with a different character to prevent Markdown table parsing issues
                    escaped_text = link_text.replace('|', '•')
                    # Clean the link text for URL encoding - remove pipe characters and extra spaces
                    clean_link_text = link_text.replace('|', ' ').replace('  ', ' ').strip()
                    search_url = f"https://linkedin.com/search/results/companies/?keywords={clean_link_text.replace(' ', '%20')}"
                    text += f"[{escaped_text}]({search_url})"
            elif child.name == 'iframe':
                # Handle iframe elements (YouTube videos, etc.)
                src = child.get('src', '')
                if 'youtube.com' in src or 'youtu.be' in src:
                    # Extract video ID from YouTube URL
                    video_id = self.extract_youtube_video_id(src)
                    if video_id:
                        text += f"\n\n[![YouTube Video](https://img.youtube.com/vi/{video_id}/maxresdefault.jpg)](https://www.youtube.com/watch?v={video_id})\n\n"
                    else:
                        text += f"\n\n[🎥 YouTube Video]({src})\n\n"
                else:
                    # Other iframe content
                    text += f"\n\n[Embedded Content]({src})\n\n"
            elif child.name == 'span':
                # Handle span elements - check for iframe children
                iframes = child.find_all('iframe')
                if iframes:
                    # Process iframe children
                    for iframe in iframes:
                        src = iframe.get('src', '')
                        if 'youtube.com' in src or 'youtu.be' in src:
                            # Extract video ID from YouTube URL
                            video_id = self.extract_youtube_video_id(src)
                            if video_id:
                                text += f"\n\n[![YouTube Video](https://img.youtube.com/vi/{video_id}/maxresdefault.jpg)](https://www.youtube.com/watch?v={video_id})\n\n"
                            else:
                                text += f"\n\n[🎥 YouTube Video]({src})\n\n"
                        else:
                            # Other iframe content
                            text += f"\n\n[Embedded Content]({src})\n\n"
                else:
                    # Regular span - get text content
                    text += child.get_text()
            else:
                # For other elements, get their text content
                text += child.get_text()
        
        return text.strip()
    
    def process_list_item(self, li_element):
        """Process a list item with proper formatting"""
        text = ""
        
        for child in li_element.children:
            if isinstance(child, str):
                text += child
            elif child.name == 'p':
                # Process paragraph content within list item
                text += self.get_element_text_with_formatting(child)
            elif child.name in ['strong', 'b']:
                text += f"**{child.get_text()}**"
            elif child.name in ['em', 'i']:
                text += f"*{child.get_text()}*"
            elif child.name == 'a':
                href = child.get('href', '')
                link_text = child.get_text()
                if href and link_text:
                    # Check if this is an embedded social media post
                    if 'class' in child.attrs and 'embedded' in child.get('class', []):
                        # This is an embedded social media post (Twitter/X, etc.)
                        if 'twitter.com' in href or 'x.com' in href:
                            # Store X post URL for screenshot capture
                            self.x_post_urls.append(href)
                            post_index = len(self.x_post_urls)
                            
                            # Create a placeholder that will be replaced with screenshot
                            text += f"\n\n> **🐦 X Post**\n> \n> {link_text}\n> \n> [View on X]({href})\n\n"
                        elif 'youtube.com' in href or 'youtu.be' in href:
                            # Handle YouTube videos
                            video_id = self.extract_youtube_video_id(href)
                            if video_id:
                                text += f"\n\n[![YouTube Video](https://img.youtube.com/vi/{video_id}/maxresdefault.jpg)]({href})\n\n"
                            else:
                                text += f"\n\n[🎥 YouTube Video: {link_text}]({href})\n\n"
                        else:
                            # Other embedded posts
                            text += f"[{link_text}]({href})"
                    else:
                        # Regular link
                        text += f"[{link_text}]({href})"
                elif link_text:
                    # Handle LinkedIn mention links (no href) - create LinkedIn search link
                    # Replace pipe characters with a different character to prevent Markdown table parsing issues
                    escaped_text = link_text.replace('|', '•')
                    # Clean the link text for URL encoding - remove pipe characters and extra spaces
                    clean_link_text = link_text.replace('|', ' ').replace('  ', ' ').strip()
                    search_url = f"https://linkedin.com/search/results/companies/?keywords={clean_link_text.replace(' ', '%20')}"
                    text += f"[{escaped_text}]({search_url})"
            elif child.name == 'iframe':
                # Handle iframe elements (YouTube videos, etc.)
                src = child.get('src', '')
                if 'youtube.com' in src or 'youtu.be' in src:
                    # Extract video ID from YouTube URL
                    video_id = self.extract_youtube_video_id(src)
                    if video_id:
                        text += f"\n\n[![YouTube Video](https://img.youtube.com/vi/{video_id}/maxresdefault.jpg)](https://www.youtube.com/watch?v={video_id})\n\n"
                    else:
                        text += f"\n\n[🎥 YouTube Video]({src})\n\n"
                else:
                    # Other iframe content
                    text += f"\n\n[Embedded Content]({src})\n\n"
            elif child.name == 'span':
                # Handle span elements - check for iframe children
                iframes = child.find_all('iframe')
                if iframes:
                    # Process iframe children
                    for iframe in iframes:
                        src = iframe.get('src', '')
                        if 'youtube.com' in src or 'youtu.be' in src:
                            # Extract video ID from YouTube URL
                            video_id = self.extract_youtube_video_id(src)
                            if video_id:
                                text += f"\n\n[![YouTube Video](https://img.youtube.com/vi/{video_id}/maxresdefault.jpg)](https://www.youtube.com/watch?v={video_id})\n\n"
                            else:
                                text += f"\n\n[🎥 YouTube Video]({src})\n\n"
                        else:
                            # Other iframe content
                            text += f"\n\n[Embedded Content]({src})\n\n"
                else:
                    # Regular span - get text content
                    text += child.get_text()
            else:
                # For other elements, get their text content
                text += child.get_text()
        
        return text.strip()
    
    def process_images(self, content, post_slug):
        """Process and download images from content"""
        try:
            # Create images directory
            img_dir = Path(f"assets/img/posts/{post_slug}")
            img_dir.mkdir(parents=True, exist_ok=True)
            
            # Use the stored image URLs from convert_to_markdown
            if not hasattr(self, 'image_urls'):
                self.log("No images found to process")
                return content
            
            self.log(f"Found {len(self.image_urls)} images to process")
            
            for i, (alt_text, img_url) in enumerate(self.image_urls, 1):
                try:
                    # Download image
                    response = self.session.get(img_url, timeout=30)
                    if response.status_code == 200:
                        # Save image with special naming for header images
                        if "header image" in alt_text.lower() or "badges" in alt_text.lower():
                            img_filename = "header_image.jpg"
                        else:
                            img_filename = f"image_{i}.jpg"
                        
                        img_path = img_dir / img_filename
                        
                        with open(img_path, 'wb') as f:
                            f.write(response.content)
                        
                        # Update content with local path
                        local_path = f"{{{{ '/assets/img/posts/{post_slug}/{img_filename}' | relative_url }}}}"
                        content = content.replace(img_url, local_path)
                        
                        self.log(f"Downloaded image: {img_filename}")
                    else:
                        self.log(f"Failed to download image: {img_url}")
                        # For header images, keep the original URL as fallback instead of removing
                        if "header image" in alt_text.lower() or "badges" in alt_text.lower():
                            self.log(f"Keeping header image with original URL: {img_url}")
                        else:
                            # Remove the broken image reference from content for non-header images
                            content = content.replace(f"![{alt_text}]({img_url})", "")
                        
                except Exception as e:
                    self.log(f"Error downloading image {img_url}: {e}")
                    # For header images, keep the original URL as fallback instead of removing
                    if "header image" in alt_text.lower() or "badges" in alt_text.lower():
                        self.log(f"Keeping header image with original URL: {img_url}")
                    else:
                        # Remove the broken image reference from content for non-header images
                        content = content.replace(f"![{alt_text}]({img_url})", "")
            
            return content
            
        except Exception as e:
            self.log(f"Error processing images: {e}")
            return content
    
    def process_x_post_screenshots(self, content, post_slug):
        """Process and capture screenshots of X posts"""
        try:
            if not hasattr(self, 'x_post_urls') or not self.x_post_urls:
                self.log("No X posts found to process")
                return content
            
            self.log(f"Found {len(self.x_post_urls)} X posts to capture")
            
            for i, x_url in enumerate(self.x_post_urls, 1):
                try:
                    # Capture screenshot
                    screenshot_path = self.capture_x_post_screenshot(x_url, post_slug, i)
                    
                    if screenshot_path:
                        # Create relative path for Jekyll
                        relative_path = f"{{{{ '/assets/img/posts/{post_slug}/x_post_{i}.png' | relative_url }}}}"
                        
                        # Replace the X post blockquote with image + link
                        old_blockquote = f"> **🐦 X Post**\n> \n> {x_url}\n> \n> [View on X]({x_url})"
                        new_content = f"**🐦 X Post**\n\n![X Post Screenshot]({relative_path})\n\n[View on X]({x_url})"
                        
                        content = content.replace(old_blockquote, new_content)
                        self.log(f"Replaced X post {i} with screenshot")
                    else:
                        # X post is not available, keep just the link
                        old_blockquote = f"> **🐦 X Post**\n> \n> {x_url}\n> \n> [View on X]({x_url})"
                        new_content = f"**🐦 X Post**\n\n[X Post Link]({x_url})"
                        
                        content = content.replace(old_blockquote, new_content)
                        self.log(f"X post {i} not available, kept as link only: {x_url}")
                        
                except Exception as e:
                    self.log(f"Error processing X post {i}: {e}")
                    continue
            
            return content
            
        except Exception as e:
            self.log(f"Error processing X post screenshots: {e}")
            return content
    
    def process_linkedin_links(self, content, linkedin_links):
        """Replace search URLs with actual LinkedIn profile/company URLs"""
        try:
            if not linkedin_links:
                self.log("No LinkedIn links to process")
                return content
            
            # First, create a comprehensive mapping of all possible name variations to LinkedIn URLs
            all_name_mappings = {}
            
            # Build comprehensive name mappings for all LinkedIn links
            for name, actual_url in linkedin_links.items():
                # Clean the name for better matching (remove numbers, extra spaces, etc.)
                clean_name = name.split()[0] + " " + " ".join(name.split()[1:]) if len(name.split()) > 1 else name
                clean_name = clean_name.split(" 6")[0].split(" 5")[0].split(" 3")[0].split(" 1")[0].split(" 0")[0]
                
                # Create comprehensive variations of the name for matching
                name_variations = set()
                
                # Add original name and clean name
                name_variations.add(name)
                name_variations.add(clean_name)
                
                # Add variations with different separators
                for separator in [" ", "-", "_", "."]:
                    name_variations.add(name.replace(" ", separator))
                    name_variations.add(clean_name.replace(" ", separator))
                
                # Add URL-encoded variations
                for variation in list(name_variations):
                    name_variations.add(variation.replace(" ", "%20"))
                    name_variations.add(variation.replace(" ", "%20").replace("|", "%20"))
                
                # Add variations with pipe character handling
                for variation in list(name_variations):
                    name_variations.add(variation.replace("|", " "))
                    name_variations.add(variation.replace("|", "%20"))
                
                # Add first name + last name variations
                if len(name.split()) >= 2:
                    first_name = name.split()[0]
                    last_name = name.split()[-1]
                    name_variations.add(f"{first_name} {last_name}")
                    name_variations.add(f"{first_name}%20{last_name}")
                
                # Add variations with common name patterns
                for variation in list(name_variations):
                    # Handle common name patterns like "José Miguel" -> "Jose Miguel"
                    variation_ascii = variation.replace("é", "e").replace("á", "a").replace("í", "i").replace("ó", "o").replace("ú", "u")
                    if variation_ascii != variation:
                        name_variations.add(variation_ascii)
                        name_variations.add(variation_ascii.replace(" ", "%20"))
                
                # Add partial name matches (first name only, last name only)
                if len(name.split()) >= 2:
                    first_name = name.split()[0]
                    last_name = name.split()[-1]
                    name_variations.add(first_name)
                    name_variations.add(last_name)
                    name_variations.add(first_name.replace(" ", "%20"))
                    name_variations.add(last_name.replace(" ", "%20"))
                
                # Add variations with common name abbreviations and patterns
                for variation in list(name_variations):
                    # Handle common name patterns like "José Miguel Piquer" -> "Jpiquer"
                    if len(variation.split()) >= 2:
                        first_initial = variation.split()[0][0].lower()
                        last_name = variation.split()[-1].lower()
                        abbreviated = first_initial + last_name
                        name_variations.add(abbreviated)
                        name_variations.add(abbreviated.replace(" ", "%20"))
                    
                    # Handle cases where names might be concatenated
                    if " " in variation:
                        concatenated = variation.replace(" ", "").lower()
                        name_variations.add(concatenated)
                        name_variations.add(concatenated.replace(" ", "%20"))
                    
                    # Handle cases where names might be partially concatenated
                    if len(variation.split()) >= 2:
                        first_name = variation.split()[0].lower()
                        last_name = variation.split()[-1].lower()
                        partial_concat = first_name + last_name
                        name_variations.add(partial_concat)
                        name_variations.add(partial_concat.replace(" ", "%20"))
                
                # Store all variations for this LinkedIn link
                for variation in name_variations:
                    if variation.strip():
                        all_name_mappings[variation] = actual_url
            
            # Add specific mappings for known cases
            specific_mappings = {
                "Universidad de Chile": "Uchile/",
                "Javier Borkenztain": "Borky", 
                "Minsait Payments": "Nuek Co"
            }
            
            # Add these specific mappings to our comprehensive mapping
            for search_name, linkedin_name in specific_mappings.items():
                if linkedin_name in all_name_mappings:
                    all_name_mappings[search_name] = all_name_mappings[linkedin_name]
                    self.log(f"Added specific mapping: {search_name} -> {linkedin_name}")
            
            # Now use the comprehensive mapping to replace search URLs
            # Look for all possible search URL patterns and try to match them
            import re
            
            # Find all search URLs in the content
            search_url_pattern = r'https://linkedin\.com/search/results/(?:people|companies)/\?keywords=([^)]+)'
            search_matches = re.findall(search_url_pattern, content)
            
            for search_keywords in search_matches:
                # Decode the keywords
                decoded_keywords = search_keywords.replace('%20', ' ').replace('%C3%A1', 'á').replace('%C3%A9', 'é').replace('%C3%AD', 'í').replace('%C3%B3', 'ó').replace('%C3%BA', 'ú')
                
                # Try to find a match in our comprehensive mapping
                best_match = None
                best_match_url = None
                
                # Try exact matches first
                if decoded_keywords in all_name_mappings:
                    best_match = decoded_keywords
                    best_match_url = all_name_mappings[decoded_keywords]
                else:
                    # Try fuzzy matching
                    for variation, url in all_name_mappings.items():
                        # Check if the search keywords match this variation
                        if self._names_match(decoded_keywords, variation):
                            best_match = variation
                            best_match_url = url
                            break
                
                if best_match and best_match_url:
                    # Replace the search URL with the actual LinkedIn URL
                    search_url = f'https://linkedin.com/search/results/people/?keywords={search_keywords}'
                    if search_url in content:
                        content = content.replace(search_url, best_match_url)
                        self.log(f"Replaced search URL with actual LinkedIn URL: {decoded_keywords} -> {best_match}")
                    else:
                        search_url = f'https://linkedin.com/search/results/companies/?keywords={search_keywords}'
                        if search_url in content:
                            content = content.replace(search_url, best_match_url)
                            self.log(f"Replaced search URL with actual LinkedIn URL: {decoded_keywords} -> {best_match}")
            
            return content
            
        except Exception as e:
            self.log(f"Error processing LinkedIn links: {e}")
            return content
    
    def _names_match(self, name1, name2):
        """Check if two names match using various fuzzy matching techniques"""
        if not name1 or not name2:
            return False
        
        # Normalize names
        n1 = name1.lower().replace(" ", "").replace("-", "").replace("_", "").replace(".", "")
        n2 = name2.lower().replace(" ", "").replace("-", "").replace("_", "").replace(".", "")
        
        # Exact match
        if n1 == n2:
            return True
        
        # One contains the other (with minimum length)
        if (n1 in n2 and len(n1) >= 3) or (n2 in n1 and len(n2) >= 3):
            return True
        
        # Check if they share significant parts (first name + last name)
        n1_parts = name1.lower().split()
        n2_parts = name2.lower().split()
        
        if len(n1_parts) >= 2 and len(n2_parts) >= 2:
            # Check if first and last names match
            if n1_parts[0] == n2_parts[0] and n1_parts[-1] == n2_parts[-1]:
                return True
            
            # Check if one is an abbreviation of the other
            if len(n1_parts) >= 2 and len(n2_parts) == 1:
                # n1 is "José Miguel Piquer", n2 is "jpiquer"
                if n1_parts[0][0] + n1_parts[-1] == n2_parts[0]:
                    return True
            elif len(n2_parts) >= 2 and len(n1_parts) == 1:
                # n2 is "José Miguel Piquer", n1 is "jpiquer"
                if n2_parts[0][0] + n2_parts[-1] == n1_parts[0]:
                    return True
        
        # Check for more complex abbreviation patterns
        if len(n1_parts) >= 2 and len(n2_parts) == 1:
            # Try different abbreviation patterns
            # "José Miguel Piquer" -> "jpiquer" (first initial + last name)
            if n1_parts[0][0] + n1_parts[-1] == n2_parts[0]:
                return True
            # "José Miguel Piquer" -> "jmpiquer" (first two initials + last name)
            if len(n1_parts) >= 3 and n1_parts[0][0] + n1_parts[1][0] + n1_parts[-1] == n2_parts[0]:
                return True
            # "José Miguel Piquer" -> "jmp" (first two initials + last name first 3 chars)
            if len(n1_parts) >= 3 and n1_parts[0][0] + n1_parts[1][0] + n1_parts[-1][:3] == n2_parts[0]:
                return True
        elif len(n2_parts) >= 2 and len(n1_parts) == 1:
            # Same patterns in reverse
            if n2_parts[0][0] + n2_parts[-1] == n1_parts[0]:
                return True
            if len(n2_parts) >= 3 and n2_parts[0][0] + n2_parts[1][0] + n2_parts[-1] == n1_parts[0]:
                return True
            if len(n2_parts) >= 3 and n2_parts[0][0] + n2_parts[1][0] + n2_parts[-1][:3] == n1_parts[0]:
                return True
        
        return False
    
    def extract_youtube_video_id(self, url):
        """Extract YouTube video ID from various YouTube URL formats"""
        import re
        
        # Normalize URL - handle protocol-relative URLs
        if url.startswith('//'):
            url = 'https:' + url
        
        # Pattern for youtube.com/watch?v=VIDEO_ID
        match = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
        
        # Pattern for youtube.com/embed/VIDEO_ID
        match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
        
        return None
    
    def add_original_source_quote(self, content, url, language):
        """Add quote at beginning explaining article was originally published on LinkedIn"""
        if language == 'en':
            quote = f"""---

> This article was originally published on [LinkedIn]({url}).

---"""
        else:  # Spanish
            quote = f"""---

> Este artículo fue publicado originalmente en [LinkedIn]({url}).

---"""
        
        return quote + "\n\n" + content
    
    def is_relevant_image(self, src, alt, title):
        """Check if image is relevant to the article content"""
        # Skip images with common UI URLs (but allow media.licdn.com for article images)
        if any(ui_url in src.lower() for ui_url in [
            'linkedin.com/static', 'static.licdn.com'
        ]):
            return False
        
        # Skip very small images (likely icons) - check file size
        try:
            response = self.session.head(src, timeout=5)
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) < 10000:  # Less than 10KB
                return False
        except:
            pass
        
        return True
    
    def create_front_matter(self, title, author, date, language, url):
        """Create Jekyll front matter"""
        # Create translation_id from title
        translation_id = slugify(title)
        
        # Determine alt_lang
        alt_lang = 'es' if language == 'en' else 'en'
        
        # Quote title if it contains special characters that need escaping in YAML
        if any(char in title for char in [':', '"', "'", '\\', '|', '>', '&', '*', '!', '%', '@', '`', '#']):
            quoted_title = f'"{title}"'
        else:
            quoted_title = title
        
        front_matter = f"""---
title: {quoted_title}
date: {date}
author: andresantoniuk
lang: {language}
alt_lang: {alt_lang}
translation_id: {translation_id}
categories: ["linkedin-import"]
tags: []
linkedin_url: {url}
---"""
        
        return front_matter


def main():
    parser = argparse.ArgumentParser(description='Parse LinkedIn exported HTML files and convert to Jekyll Markdown')
    parser.add_argument('html_file', help='Path to LinkedIn exported HTML file')
    parser.add_argument('language', choices=['en', 'es'], default='en', help='Language (en or es)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    parser = LinkedInHTMLParser(debug=args.debug)
    result = parser.parse_html_file(args.html_file, args.language)
    
    if result:
        # Write to file - use correct directory based on language
        output_dir = "_posts-es" if args.language == 'es' else "_posts"
        output_path = f"{output_dir}/{result['filename']}"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result['content'])
        
        print(f"Article parsed successfully: {output_path}")
        print(f"Title: {result['slug']}")
    else:
        print("Failed to parse article")
        sys.exit(1)


if __name__ == "__main__":
    main()
