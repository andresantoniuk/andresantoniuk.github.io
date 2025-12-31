desc "Clean up generated site and caches"
task :clean do
  puts "Cleaning up..."
  rm_rf ["_site", ".jekyll-cache", ".sass-cache", ".jekyll-metadata"]
  puts "Clean complete."
end

desc "Build the site"
task :build do
  puts "Syncing company blog..."
  system "python3 tools/sync_company_blog.py"
  puts "Generating tags/categories..."
  system "python3 tools/generate_tags_categories.py"
  puts "Building site..."
  system "bundle exec jekyll build"
end

desc "Serve the site locally"
task :serve do
  puts "Serving site..."
  system "bundle exec jekyll serve"
end

desc "Default task: build"
task :default => :build
