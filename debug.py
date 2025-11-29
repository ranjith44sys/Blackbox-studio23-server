
import json
import os

# Check if data file exists
if os.path.exists('data/galleries.json'):
    with open('data/galleries.json', 'r') as f:
        galleries = json.load(f)
    
    print("=== GALLERY DATA DEBUG ===\n")
    print(f"Total galleries: {len(galleries)}\n")
    
    for gallery in galleries:
        print(f"Gallery: {gallery.get('name')}")
        print(f"Title: {gallery.get('title')}")
        print(f"Images count: {len(gallery.get('images', []))}")
        
        for i, img in enumerate(gallery.get('images', [])):
            print(f"  Image {i+1}: {img.get('url')}")
            
            # Check if file exists for local URLs
            if img.get('url', '').startswith('/uploads/'):
                filepath = img['url'].lstrip('/')
                exists = os.path.exists(filepath)
                print(f"    File exists: {exists}")
                if exists:
                    size = os.path.getsize(filepath)
                    print(f"    File size: {size} bytes")
        print()
else:
    print("No galleries.json file found!")

# Check uploads folder
print("\n=== UPLOADS FOLDER ===")
if os.path.exists('uploads/images'):
    files = os.listdir('uploads/images')
    print(f"Files in uploads/images: {len(files)}")
    for f in files[:10]:  # Show first 10
        filepath = os.path.join('uploads/images', f)
        size = os.path.getsize(filepath)
        print(f"  {f} - {size} bytes")
else:
    print("uploads/images folder doesn't exist!")