#!/bin/bash

# Simple LinkedIn Articles Bulk Import Script
# This script deletes all articles and re-imports them automatically

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to delete all imported LinkedIn articles
delete_all_articles() {
    print_status "Deleting all imported LinkedIn articles..."
    
    # Count articles before deletion
    local count_before=$(find _posts _posts-es -name "*.md" -type f 2>/dev/null | wc -l)
    
    # Delete from _posts directory
    if [ -d "_posts" ]; then
        find _posts -name "*.md" -type f -delete
        print_status "Deleted articles from _posts/"
    fi
    
    # Delete from _posts-es directory
    if [ -d "_posts-es" ]; then
        find _posts-es -name "*.md" -type f -delete
        print_status "Deleted articles from _posts-es/"
    fi
    
    # Delete associated images
    if [ -d "assets/img/posts" ]; then
        rm -rf assets/img/posts/*
        print_status "Deleted associated images from assets/img/posts/"
    fi
    
    local count_after=$(find _posts _posts-es -name "*.md" -type f 2>/dev/null | wc -l)
    local deleted=$((count_before - count_after))
    
    print_success "Deleted $deleted articles and their associated images"
}

# Function to import all articles
import_all_articles() {
    print_status "Importing all articles..."
    
    # Article list with correct filenames and languages
    local articles=(
        "1|20140616145504-9925762--literalmente-el-silencio-puede-matar.html|es"
        "2|20140629225138-9925762-la-causa-de-los-pueblos-no-admite-la-menor-demora.html|es"
        "4|20140815135847-9925762--wearen-ideas-que-valen-la-pena-difundir.html|es"
        "5|20140828053544-9925762--ceibaidiotizados.html|es"
        "6|20140928004949-9925762--tulatam.html|en"
        "7|20141010173926-9925762--ateneopresidenciables.html|es"
        "8|20141105162709-9925762--votodigital2020.html|es"
        "9|cerveza-fr├нa-juan-andr├йs-antoniuk-upozf.html|es"
        "10|devops-paap-dodrj2018-juan-andr├йs-antoniuk-buchtik.html|en"
        "11|fintech-10-a├▒os-juan-andr├йs-antoniuk-7tlkf.html|es"
        "12|my-journey-jpos-elastic-juan-andr├йs-antoniuk-buchtik.html|en"
        "13|nuevodesaf├нo-juan-andr├йs-antoniuk-76quf.html|es"
        "14|nuevos-rumbos-juan-andr├йs-antoniuk-u2qif.html|es"
        "15|semana-santa-en-mi-pa├нs-laico-juan-andr├йs-antoniuk-buchtik.html|es"
        "16|techevents-europe-2025-juan-andr├йs-antoniuk-cvv3f.html|en"
    )
    
    local success_count=0
    local error_count=0
    
    for article in "${articles[@]}"; do
        IFS='|' read -r order_id filename language <<< "$article"
        
        print_status "Importing article $order_id: $filename ($language)..."
        
        # Run the import script
        if tools/import_linkedin_html.sh "/home/andresa/Documents/ln/Articles/Articles/$filename" "$language" >/dev/null 2>&1; then
            print_success "Article $order_id imported successfully"
            ((success_count++))
        else
            print_error "Failed to import article $order_id"
            ((error_count++))
        fi
        
        echo "----------------------------------------"
    done
    
    print_success "Import completed: $success_count successful, $error_count failed"
}

# Main execution
echo "=========================================="
echo "LinkedIn Articles Bulk Import Script"
echo "=========================================="
echo "This script will:"
echo "1. Delete all existing LinkedIn articles"
echo "2. Import all 16 articles with latest fixes"
echo "=========================================="
echo

print_warning "Starting bulk import process..."

# Step 1: Delete all articles
delete_all_articles
echo

# Step 2: Import all articles
import_all_articles
echo

print_success "Bulk import process completed!"
print_status "Check your _posts/ and _posts-es/ directories for the imported articles."
