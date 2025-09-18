#!/bin/bash

# LinkedIn HTML Article Importer
# Parse LinkedIn exported HTML files and convert to Jekyll Markdown

set -e

# Configuration
PYTHON_SCRIPT="linkedin_html_parser.py"
REQUIREMENTS_FILE="tools/requirements.txt"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

# Check if HTML file is provided
if [ $# -lt 1 ]; then
    print_error "Usage: $0 <html_file> [language] [--debug]"
    print_error "Example: $0 '/path/to/article.html' en --debug"
    exit 1
fi

# Parse arguments
HTML_FILE="$1"
ARTICLE_LANG="${2:-en}"
DEBUG_FLAG=""

# Check for debug flag
if [ "$3" = "--debug" ] || [ "$2" = "--debug" ]; then
    DEBUG_FLAG="--debug"
    if [ "$2" = "--debug" ]; then
        ARTICLE_LANG="en"  # Default language if debug is second argument
    fi
fi

# Validate language
if [ "$ARTICLE_LANG" != "en" ] && [ "$ARTICLE_LANG" != "es" ]; then
    print_error "Language must be 'en' or 'es'"
    exit 1
fi

# Check if HTML file exists
if [ ! -f "$HTML_FILE" ]; then
    print_error "HTML file not found: $HTML_FILE"
    exit 1
fi

# Print header
print_status "🔗 LinkedIn HTML Article Importer"
print_status "=================================="
print_status "HTML File: $HTML_FILE"
print_status "Language: $ARTICLE_LANG"

# Install Python dependencies
print_status "\nInstalling Python dependencies from $REQUIREMENTS_FILE..."
pip3 install -r "$REQUIREMENTS_FILE" --quiet

# Run the Python parser
print_status ""
python3 "tools/$PYTHON_SCRIPT" "$HTML_FILE" "$ARTICLE_LANG" $DEBUG_FLAG
if [ $? -ne 0 ]; then
    print_error "Error: LinkedIn HTML parsing failed."
    exit 1
fi

print_success "\n✅ Import completed!"
if [ "$ARTICLE_LANG" = "es" ]; then
    print_success "📁 Check the _posts-es/ directory for your new article"
else
    print_success "📁 Check the _posts/ directory for your new article"
fi
print_success "🖼️  Images have been saved to assets/img/posts/"
