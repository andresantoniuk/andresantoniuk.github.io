import os
import glob
import re
import yaml

# Configuration
POSTS_DIRS = ['_posts', '_posts-es']
TAGS_DIR = 'tags'
CATEGORIES_DIR = 'categories'

def parse_frontmatter(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract YAML frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if match:
        try:
            return yaml.safe_load(match.group(1))
        except yaml.YAMLError:
            return {}
    return {}

def get_all_taxonomies():
    all_tags = set()
    all_categories = set()
    
    files = []
    for d in POSTS_DIRS:
        files.extend(glob.glob(os.path.join(d, '*.md')))
        
    for f in files:
        data = parse_frontmatter(f)
        if not data:
            continue
            
        tags = data.get('tags', [])
        categories = data.get('categories', [])
        
        # Normalize to list if string
        if isinstance(tags, str): tags = [tags]
        if isinstance(categories, str): categories = [categories]
        
        # Add to sets
        if tags:
            for t in tags: all_tags.add(t)
        if categories:
            for c in categories: all_categories.add(c)
            
    return all_tags, all_categories

def generate_files(items, output_dir, layout_type, type_key):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Get existing files to remove obsolete ones
    existing_files = set(glob.glob(os.path.join(output_dir, '*.md')))
    generated_files = set()
    
    for item in items:
        safe_name = item.lower().replace(' ', '-') # Basic slugification
        filename = os.path.join(output_dir, f"{safe_name}.md")
        generated_files.add(filename)
        
        content = f"""---
layout: {layout_type}
title: "{item.capitalize()}"
{type_key}: {item}
permalink: /{output_dir}/{safe_name}/
---
"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
            
    # Clean up obsolete
    for f in existing_files:
        if f not in generated_files:
            os.remove(f)
            print(f"Removed obsolete: {f}")

def main():
    tags, categories = get_all_taxonomies()
    
    print(f"Found {len(tags)} tags and {len(categories)} categories.")
    
    generate_files(tags, TAGS_DIR, 'tag-custom', 'tag')
    print("Tags generated.")
    
    generate_files(categories, CATEGORIES_DIR, 'category-custom', 'category')
    print("Categories generated.")

if __name__ == "__main__":
    main()
