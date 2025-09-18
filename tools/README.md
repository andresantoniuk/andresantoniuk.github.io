# LinkedIn Article Importer for Jekyll

A reliable tool to convert LinkedIn exported HTML articles to Jekyll Markdown posts for your blog.

## 🚀 Features

- ✅ **Reliable Content Extraction**: Uses LinkedIn's official data export (no web scraping!)
- 🖼️ **Image Processing**: Downloads and saves images locally with proper Jekyll paths
- 🔗 **Link Processing**: Converts HTML links to Markdown format
- 👥 **Mention Processing**: Preserves people and company mentions as links
- 🏷️ **Tag Extraction**: Automatically extracts article tags and hashtags
- 🌐 **Multilingual Support**: English and Spanish posts with proper frontmatter
- 📁 **Organized Storage**: Images saved in `assets/img/posts/{article-slug}/`
- 🎯 **Perfect Formatting**: Preserves paragraphs, lists, bold, italic, and headings
- 🐛 **Debug Mode**: Comprehensive logging for troubleshooting
- 🎯 **Robust Error Handling**: Graceful handling of various HTML structures

## 📋 Prerequisites

- **Python 3.7+**
- **Internet connection** (for downloading images)

## 🛠️ Installation

1. **Install Python dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Make the script executable:**
   ```bash
   chmod +x import_linkedin_html.sh
   ```

## 🚀 Quick Start

### Step 1: Export Your LinkedIn Articles

1. Go to [LinkedIn Data Export](https://www.linkedin.com/mypreferences/d/download-my-data)
2. Select "Articles" from the data types
3. Download your data
4. Extract the HTML files from the Articles folder

### Step 2: Convert to Jekyll Markdown

```bash
# English article
./tools/import_linkedin_html.sh "/path/to/article.html" en

# Spanish article
./tools/import_linkedin_html.sh "/path/to/article.html" es

# With debug output
./tools/import_linkedin_html.sh "/path/to/article.html" en --debug
```

### Bulk Import (Multiple Articles)

```bash
# Import all articles at once
./tools/bulk_import_simple.sh
```

### Direct Python Usage

```bash
# Basic
python3 tools/linkedin_html_parser.py "/path/to/article.html" en

# With debug
python3 tools/linkedin_html_parser.py "/path/to/article.html" es --debug
```

## 📁 File Structure

```
tools/
├── linkedin_html_parser.py    # Main Python parser
├── import_linkedin_html.sh    # Easy-to-use wrapper script
├── bulk_import_simple.sh      # Bulk import script for multiple articles
├── requirements.txt           # Python dependencies
└── README.md                  # This documentation
```

## 📄 Generated Post Format

```yaml
---
title: "Your LinkedIn Article Title"
date: 2025-01-15
author: Author Name
lang: en
alt_lang: es
translation_id: article-title
categories: [linkedin-import]
tags: []
linkedin_url: https://www.linkedin.com/pulse/...
---

---

> **Originally published on LinkedIn**  
> This article was originally published on [LinkedIn](https://www.linkedin.com/pulse/...). The content has been imported and formatted for this blog while preserving the original author's voice and message.

---

[Full article content in Markdown format with proper formatting]
```

## 🖼️ Image Storage

- **Location**: `assets/img/posts/{article-slug}/image-name.jpg`
- **Reference**: `![Alt text]({{ '/assets/img/posts/article-slug/image.jpg' | relative_url }})`
- **Organization**: Each article gets its own subdirectory for images

## 🔧 Troubleshooting

### Common Issues

1. **"HTML file not found"**
   - Check the file path is correct
   - Ensure the file exists and is readable

2. **"No content found"**
   - Try with `--debug` flag to see detailed logs
   - Check if the HTML file is properly formatted

3. **"Permission denied"**
   - Make the script executable: `chmod +x import_linkedin_html.sh`

4. **"Images not downloading"**
   - Check your internet connection
   - Verify the image URLs are accessible

### Debug Mode

Use the `--debug` flag to get detailed logging:

```bash
./tools/import_linkedin_html.sh "/path/to/article.html" en --debug
```

This will show:
- HTML parsing progress
- Content extraction steps
- Image download progress
- Error details

## 🎯 How It Works

1. **HTML Parsing**: Uses BeautifulSoup to parse LinkedIn's exported HTML files
2. **Content Extraction**: Extracts title, author, date, and main content
3. **Markdown Conversion**: Converts HTML to properly formatted Markdown
4. **Image Processing**: Downloads images and creates proper Jekyll references
5. **Front Matter Generation**: Creates Jekyll-compatible front matter
6. **File Output**: Saves the result as a Jekyll Markdown post

## 🔍 Content Extraction Strategies

The parser uses multiple strategies to ensure it gets the actual article content:

1. **HTML Structure Analysis**: Looks for article content in divs and paragraphs
2. **Image Processing**: Handles both inline and figure images
3. **Link Preservation**: Maintains all links with proper Markdown formatting
4. **Formatting Preservation**: Keeps bold, italic, lists, and headings intact

## ⚠️ Important Notes

1. **LinkedIn Export Required**: This tool requires LinkedIn's official data export
2. **File Format**: Works with LinkedIn's exported HTML files
3. **Content Quality**: Preserves the original formatting and structure
4. **Image Processing**: Images are downloaded locally and referenced properly in Jekyll
5. **Multilingual Support**: Supports both English and Spanish articles

## 🤝 Contributing

If you encounter issues or have improvements:

1. Check the debug output first
2. Verify the HTML file is properly formatted
3. Test with different articles
4. Report issues with debug logs

## 🎉 Success Stories

The parser successfully extracts:
- ✅ Full article content with perfect formatting
- ✅ Proper Jekyll frontmatter
- ✅ Image references and downloads
- ✅ Link preservation
- ✅ Multilingual support
- ✅ Clean, readable Markdown

## 🆚 Why This Approach is Better

**Old Web Scraping Approach:**
- ❌ Unreliable (LinkedIn changes frequently)
- ❌ Complex (handles splash screens, dynamic content)
- ❌ Slow (requires browser automation)
- ❌ Fragile (breaks when LinkedIn updates)

**New HTML Export Approach:**
- ✅ Reliable (uses official LinkedIn export)
- ✅ Simple (parses static HTML files)
- ✅ Fast (no browser automation needed)
- ✅ Robust (works with any LinkedIn export)

---

**Happy importing! 🚀**