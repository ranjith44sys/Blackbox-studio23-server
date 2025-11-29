

# from flask import Blueprint, request, jsonify, current_app
# from werkzeug.utils import secure_filename
# import os
# import json
# from datetime import datetime
# import uuid
# import base64
# import re
# import requests

# gallery_routes = Blueprint('gallery', __name__)

# # File paths
# DATA_FILE = 'data/galleries.json'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# # Create necessary directories
# os.makedirs('uploads/images', exist_ok=True)
# os.makedirs('data', exist_ok=True)

# def allowed_file(filename):
#     """Check if file extension is allowed"""
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def load_galleries():
#     """Load galleries from JSON file"""
#     if os.path.exists(DATA_FILE):
#         try:
#             with open(DATA_FILE, 'r') as f:
#                 return json.load(f)
#         except json.JSONDecodeError:
#             return []
#     return []

# def save_galleries(galleries):
#     """Save galleries to JSON file"""
#     with open(DATA_FILE, 'w') as f:
#         json.dump(galleries, f, indent=2)

# def upload_to_github(file_content, filename):
#     """
#     Upload image to GitHub repository
#     Returns the raw GitHub URL for the uploaded file
#     """
#     try:
#         repo = current_app.config.get('GITHUB_REPO')
#         branch = current_app.config.get('GITHUB_BRANCH', 'main')
#         token = current_app.config.get('GITHUB_TOKEN')
        
#         if not repo:
#             print("GitHub repo not configured, saving locally")
#             return save_to_local(file_content, filename)
        
#         # GitHub API URL
#         path = f"gallery_images/{filename}"
#         url = f"https://api.github.com/repos/{repo}/contents/{path}"
        
#         # Prepare headers
#         headers = {
#             'Accept': 'application/vnd.github.v3+json',
#         }
#         if token:
#             headers['Authorization'] = f'token {token}'
        
#         # Encode content to base64 for GitHub API
#         content_base64 = base64.b64encode(file_content).decode('utf-8')
        
#         # Create or update file
#         data = {
#             'message': f'Upload image: {filename}',
#             'content': content_base64,
#             'branch': branch
#         }
        
#         # Check if file already exists
#         check_response = requests.get(url, headers=headers)
#         if check_response.status_code == 200:
#             # File exists, get SHA for update
#             data['sha'] = check_response.json()['sha']
        
#         # Upload to GitHub
#         response = requests.put(url, headers=headers, json=data)
        
#         if response.status_code in [200, 201]:
#             # Return raw GitHub URL
#             return f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
#         else:
#             print(f"GitHub upload failed: {response.status_code} - {response.text}")
#             return save_to_local(file_content, filename)
            
#     except Exception as e:
#         print(f"Error uploading to GitHub: {e}")
#         return save_to_local(file_content, filename)

# def save_to_local(file_content, filename):
#     """Fallback: Save to local uploads folder"""
#     try:
#         filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
#         with open(filepath, 'wb') as f:
#             f.write(file_content)
#         return f'/uploads/images/{filename}'
#     except Exception as e:
#         print(f"Error saving locally: {e}")
#         return None

# def save_base64_image(base64_string):
#     """Process base64 image and upload to GitHub"""
#     try:
#         # Extract image format
#         format_match = re.search(r'data:image/(\w+);base64,', base64_string)
#         img_format = format_match.group(1) if format_match else 'png'
        
#         # Remove header from base64 string
#         base64_data = re.sub(r'^data:image/.+;base64,', '', base64_string)
        
#         # Decode base64
#         file_content = base64.b64decode(base64_data)
        
#         # Generate unique filename
#         filename = f"{uuid.uuid4()}.{img_format}"
        
#         # Upload to GitHub (or save locally as fallback)
#         url = upload_to_github(file_content, filename)
        
#         return url
#     except Exception as e:
#         print(f"Error processing base64 image: {e}")
#         return None

# def process_images(images):
#     """Process image list - upload new base64 images to GitHub"""
#     processed_images = []
    
#     for img in images:
#         if img['url'].startswith('data:image'):
#             # New image - upload to GitHub
#             print(f"Processing new image: {img.get('name', 'unnamed')}")
#             saved_url = save_base64_image(img['url'])
#             if saved_url:
#                 processed_images.append({
#                     'id': img['id'],
#                     'url': saved_url,
#                     'name': img['name']
#                 })
#             else:
#                 print(f"Failed to save image: {img.get('name', 'unnamed')}")
#         else:
#             # Already saved image (GitHub URL or local path)
#             processed_images.append(img)
    
#     return processed_images

# # Get all galleries
# @gallery_routes.route('/gallery', methods=['GET'])
# def get_galleries():
#     """Get all galleries"""
#     try:
#         galleries = load_galleries()
#         return jsonify({
#             'success': True,
#             'data': galleries
#         })
#     except Exception as e:
#         print(f"Error in get_galleries: {e}")
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# # Get single gallery by ID
# @gallery_routes.route('/gallery/<gallery_id>', methods=['GET'])
# def get_gallery(gallery_id):
#     """Get a single gallery by ID"""
#     try:
#         galleries = load_galleries()
#         gallery = next((g for g in galleries if g['_id'] == gallery_id), None)
        
#         if gallery:
#             return jsonify({
#                 'success': True,
#                 'data': gallery
#             })
#         else:
#             return jsonify({
#                 'success': False,
#                 'error': 'Gallery not found'
#             }), 404
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# # Create new gallery
# @gallery_routes.route('/gallery', methods=['POST'])
# def create_gallery():
#     """Create a new gallery and upload images to GitHub"""
#     try:
#         data = request.get_json()
#         print(f"Received gallery creation request: {data.get('name', 'unnamed')}")

#         # Validate required fields
#         if not data:
#             return jsonify({'success': False, 'error': 'No data received'}), 400

#         if not data.get('name') or not data.get('title'):
#             return jsonify({
#                 'success': False,
#                 'error': 'Both name and title are required'
#             }), 400

#         # Validate images
#         images = data.get('images', [])
#         if not isinstance(images, list):
#             return jsonify({'success': False, 'error': 'Images must be an array'}), 400

#         if len(images) == 0:
#             return jsonify({'success': False, 'error': 'At least one image is required'}), 400

#         # Generate ID
#         gallery_id = str(uuid.uuid4())

#         # Process Images (Upload to GitHub or save locally)
#         print(f"Processing {len(images)} images...")
#         processed_images = process_images(images)
        
#         if len(processed_images) == 0:
#             return jsonify({'success': False, 'error': 'Failed to process images'}), 500

#         print(f"Successfully processed {len(processed_images)} images")

#         # Create gallery object
#         gallery = {
#             '_id': gallery_id,
#             'name': data['name'],
#             'title': data['title'],
#             'description': data.get('description', ''),
#             'collageFormat': data.get('collageFormat', 'grid'),
#             'fontStyle': data.get('fontStyle', 'sans'),
#             'colorTheme': data.get('colorTheme', 'elegant'),
#             'images': processed_images,
#             'createdAt': datetime.now().isoformat(),
#             'updatedAt': datetime.now().isoformat()
#         }

#         # Save to JSON
#         galleries = load_galleries()
#         galleries.append(gallery)
#         save_galleries(galleries)

#         print(f"Gallery created successfully: {gallery_id}")

#         return jsonify({'success': True, 'data': gallery}), 201

#     except Exception as e:
#         import traceback
#         print(f"Error in create_gallery: {traceback.format_exc()}")
#         return jsonify({'success': False, 'error': str(e)}), 500

# # Update gallery
# @gallery_routes.route('/gallery/<gallery_id>', methods=['PUT'])
# def update_gallery(gallery_id):
#     """Update an existing gallery"""
#     try:
#         data = request.get_json()
#         galleries = load_galleries()
        
#         # Find gallery
#         gallery_index = None
#         for i, g in enumerate(galleries):
#             if g['_id'] == gallery_id:
#                 gallery_index = i
#                 break
        
#         if gallery_index is None:
#             return jsonify({
#                 'success': False,
#                 'error': 'Gallery not found'
#             }), 404
        
#         # Process images
#         print(f"Updating gallery: {gallery_id}")
#         processed_images = process_images(data.get('images', []))
        
#         # Update gallery
#         galleries[gallery_index].update({
#             'name': data.get('name', galleries[gallery_index]['name']),
#             'title': data.get('title', galleries[gallery_index]['title']),
#             'description': data.get('description', ''),
#             'collageFormat': data.get('collageFormat', 'grid'),
#             'fontStyle': data.get('fontStyle', 'sans'),
#             'colorTheme': data.get('colorTheme', 'elegant'),
#             'images': processed_images,
#             'updatedAt': datetime.now().isoformat()
#         })
        
#         save_galleries(galleries)
        
#         print(f"Gallery updated successfully: {gallery_id}")
        
#         return jsonify({
#             'success': True,
#             'data': galleries[gallery_index]
#         })
#     except Exception as e:
#         import traceback
#         print(f"Error in update_gallery: {traceback.format_exc()}")
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# # Delete gallery
# @gallery_routes.route('/gallery/<gallery_id>', methods=['DELETE'])
# def delete_gallery(gallery_id):
#     """Delete a gallery (images remain in GitHub/local storage)"""
#     try:
#         galleries = load_galleries()
        
#         # Find and remove gallery
#         gallery_to_delete = None
#         for i, g in enumerate(galleries):
#             if g['_id'] == gallery_id:
#                 gallery_to_delete = galleries.pop(i)
#                 break
        
#         if gallery_to_delete is None:
#             return jsonify({
#                 'success': False,
#                 'error': 'Gallery not found'
#             }), 404
        
#         # Note: Images are NOT deleted from GitHub
#         # Only local images can be cleaned up if needed
        
#         save_galleries(galleries)
        
#         print(f"Gallery deleted: {gallery_id}")
        
#         return jsonify({
#             'success': True,
#             'message': 'Gallery deleted successfully'
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# # Health check
# @gallery_routes.route('/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return jsonify({
#         'success': True,
#         'message': 'Gallery API is running',
#         'timestamp': datetime.now().isoformat()
#     })

#---------------------------------------------------------------------
# from flask import Blueprint, request, jsonify, current_app
# from werkzeug.utils import secure_filename
# import os
# import json
# from datetime import datetime
# import uuid
# import base64
# import re
# import requests

# gallery_routes = Blueprint('gallery', __name__)

# # File paths
# DATA_FILE = 'data/galleries.json'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# # Create necessary directories
# os.makedirs('uploads/images', exist_ok=True)
# os.makedirs('data', exist_ok=True)

# def allowed_file(filename):
#     """Check if file extension is allowed"""
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def load_galleries():
#     """Load galleries from JSON file"""
#     if os.path.exists(DATA_FILE):
#         try:
#             with open(DATA_FILE, 'r') as f:
#                 return json.load(f)
#         except json.JSONDecodeError:
#             return []
#     return []

# def save_galleries(galleries):
#     """Save galleries to JSON file"""
#     with open(DATA_FILE, 'w') as f:
#         json.dump(galleries, f, indent=2)

# def upload_to_github(file_content, filename):
#     """
#     Upload image to GitHub repository
#     Returns the raw GitHub URL for the uploaded file
#     """
#     try:
#         repo = current_app.config.get('GITHUB_REPO')
#         branch = current_app.config.get('GITHUB_BRANCH', 'main')
#         token = current_app.config.get('GITHUB_TOKEN')
        
#         # If GitHub not configured, save locally
#         if not repo or repo == '':
#             print("GitHub repo not configured, saving locally")
#             return save_to_local(file_content, filename)
        
#         # GitHub API URL
#         path = f"gallery_images/{filename}"
#         url = f"https://api.github.com/repos/{repo}/contents/{path}"
        
#         # Prepare headers
#         headers = {
#             'Accept': 'application/vnd.github.v3+json',
#         }
#         if token:
#             headers['Authorization'] = f'token {token}'
        
#         # Encode content to base64 for GitHub API
#         content_base64 = base64.b64encode(file_content).decode('utf-8')
        
#         # Create or update file
#         data = {
#             'message': f'Upload image: {filename}',
#             'content': content_base64,
#             'branch': branch
#         }
        
#         # Check if file already exists
#         check_response = requests.get(url, headers=headers)
#         if check_response.status_code == 200:
#             # File exists, get SHA for update
#             data['sha'] = check_response.json()['sha']
        
#         # Upload to GitHub
#         response = requests.put(url, headers=headers, json=data)
        
#         if response.status_code in [200, 201]:
#             # Return raw GitHub URL
#             return f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
#         else:
#             print(f"GitHub upload failed: {response.status_code} - {response.text}")
#             return save_to_local(file_content, filename)
            
#     except Exception as e:
#         print(f"Error uploading to GitHub: {e}")
#         return save_to_local(file_content, filename)

# def save_to_local(file_content, filename):
#     """Fallback: Save to local uploads folder"""
#     try:
#         filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
#         with open(filepath, 'wb') as f:
#             f.write(file_content)
#         return f'/uploads/images/{filename}'
#     except Exception as e:
#         print(f"Error saving locally: {e}")
#         return None

# def save_base64_image(base64_string):
#     """Process base64 image and upload to GitHub"""
#     try:
#         # Extract image format
#         format_match = re.search(r'data:image/(\w+);base64,', base64_string)
#         img_format = format_match.group(1) if format_match else 'png'
        
#         # Remove header from base64 string
#         base64_data = re.sub(r'^data:image/.+;base64,', '', base64_string)
        
#         # Decode base64
#         file_content = base64.b64decode(base64_data)
        
#         # Generate unique filename
#         filename = f"{uuid.uuid4()}.{img_format}"
        
#         # Upload to GitHub (or save locally as fallback)
#         url = upload_to_github(file_content, filename)
        
#         return url
#     except Exception as e:
#         print(f"Error processing base64 image: {e}")
#         return None

# def process_images(images):
#     """Process image list - upload new base64 images to GitHub"""
#     processed_images = []
    
#     for img in images:
#         if img['url'].startswith('data:image'):
#             # New image - upload to GitHub
#             print(f"Processing new image: {img.get('name', 'unnamed')}")
#             saved_url = save_base64_image(img['url'])
#             if saved_url:
#                 processed_images.append({
#                     'id': img['id'],
#                     'url': saved_url,
#                     'name': img['name']
#                 })
#             else:
#                 print(f"Failed to save image: {img.get('name', 'unnamed')}")
#         else:
#             # Already saved image (GitHub URL or local path)
#             processed_images.append(img)
    
#     return processed_images

# # Get all galleries
# @gallery_routes.route('/gallery', methods=['GET'])
# def get_galleries():
#     """Get all galleries"""
#     try:
#         galleries = load_galleries()
#         return jsonify({
#             'success': True,
#             'data': galleries
#         })
#     except Exception as e:
#         print(f"Error in get_galleries: {e}")
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# # Get single gallery by ID
# @gallery_routes.route('/gallery/<gallery_id>', methods=['GET'])
# def get_gallery(gallery_id):
#     """Get a single gallery by ID"""
#     try:
#         galleries = load_galleries()
#         gallery = next((g for g in galleries if g['_id'] == gallery_id), None)
        
#         if gallery:
#             return jsonify({
#                 'success': True,
#                 'data': gallery
#             })
#         else:
#             return jsonify({
#                 'success': False,
#                 'error': 'Gallery not found'
#             }), 404
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# # Create new gallery
# @gallery_routes.route('/gallery', methods=['POST'])
# def create_gallery():
#     """Create a new gallery and upload images to GitHub"""
#     try:
#         data = request.get_json()
#         print(f"Received gallery creation request: {data.get('name', 'unnamed')}")

#         # Validate required fields
#         if not data:
#             return jsonify({'success': False, 'error': 'No data received'}), 400

#         if not data.get('name') or not data.get('title'):
#             return jsonify({
#                 'success': False,
#                 'error': 'Both name and title are required'
#             }), 400

#         # Validate images
#         images = data.get('images', [])
#         if not isinstance(images, list):
#             return jsonify({'success': False, 'error': 'Images must be an array'}), 400

#         if len(images) == 0:
#             return jsonify({'success': False, 'error': 'At least one image is required'}), 400

#         # Generate ID
#         gallery_id = str(uuid.uuid4())

#         # Process Images (Upload to GitHub or save locally)
#         print(f"Processing {len(images)} images...")
#         processed_images = process_images(images)
        
#         if len(processed_images) == 0:
#             return jsonify({'success': False, 'error': 'Failed to process images'}), 500

#         print(f"Successfully processed {len(processed_images)} images")

#         # Create gallery object
#         gallery = {
#             '_id': gallery_id,
#             'name': data['name'],
#             'title': data['title'],
#             'description': data.get('description', ''),
#             'collageFormat': data.get('collageFormat', 'grid'),
#             'fontStyle': data.get('fontStyle', 'sans'),
#             'colorTheme': data.get('colorTheme', 'elegant'),
#             'images': processed_images,
#             'createdAt': datetime.now().isoformat(),
#             'updatedAt': datetime.now().isoformat()
#         }

#         # Save to JSON
#         galleries = load_galleries()
#         galleries.append(gallery)
#         save_galleries(galleries)

#         print(f"Gallery created successfully: {gallery_id}")

#         return jsonify({'success': True, 'data': gallery}), 201

#     except Exception as e:
#         import traceback
#         print(f"Error in create_gallery: {traceback.format_exc()}")
#         return jsonify({'success': False, 'error': str(e)}), 500

# # Update gallery
# @gallery_routes.route('/gallery/<gallery_id>', methods=['PUT'])
# def update_gallery(gallery_id):
#     """Update an existing gallery"""
#     try:
#         data = request.get_json()
#         galleries = load_galleries()
        
#         # Find gallery
#         gallery_index = None
#         for i, g in enumerate(galleries):
#             if g['_id'] == gallery_id:
#                 gallery_index = i
#                 break
        
#         if gallery_index is None:
#             return jsonify({
#                 'success': False,
#                 'error': 'Gallery not found'
#             }), 404
        
#         # Process images
#         print(f"Updating gallery: {gallery_id}")
#         processed_images = process_images(data.get('images', []))
        
#         # Update gallery
#         galleries[gallery_index].update({
#             'name': data.get('name', galleries[gallery_index]['name']),
#             'title': data.get('title', galleries[gallery_index]['title']),
#             'description': data.get('description', ''),
#             'collageFormat': data.get('collageFormat', 'grid'),
#             'fontStyle': data.get('fontStyle', 'sans'),
#             'colorTheme': data.get('colorTheme', 'elegant'),
#             'images': processed_images,
#             'updatedAt': datetime.now().isoformat()
#         })
        
#         save_galleries(galleries)
        
#         print(f"Gallery updated successfully: {gallery_id}")
        
#         return jsonify({
#             'success': True,
#             'data': galleries[gallery_index]
#         })
#     except Exception as e:
#         import traceback
#         print(f"Error in update_gallery: {traceback.format_exc()}")
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# # Delete gallery
# @gallery_routes.route('/gallery/<gallery_id>', methods=['DELETE'])
# def delete_gallery(gallery_id):
#     """Delete a gallery (images remain in GitHub/local storage)"""
#     try:
#         galleries = load_galleries()
        
#         # Find and remove gallery
#         gallery_to_delete = None
#         for i, g in enumerate(galleries):
#             if g['_id'] == gallery_id:
#                 gallery_to_delete = galleries.pop(i)
#                 break
        
#         if gallery_to_delete is None:
#             return jsonify({
#                 'success': False,
#                 'error': 'Gallery not found'
#             }), 404
        
#         # Note: Images are NOT deleted from GitHub
#         # Only local images can be cleaned up if needed
        
#         save_galleries(galleries)
        
#         print(f"Gallery deleted: {gallery_id}")
        
#         return jsonify({
#             'success': True,
#             'message': 'Gallery deleted successfully'
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# # Health check
# @gallery_routes.route('/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return jsonify({
#         'success': True,
#         'message': 'Gallery API is running',
#         'timestamp': datetime.now().isoformat()
#     })




# from flask import Blueprint, request, jsonify, current_app
# from werkzeug.utils import secure_filename
# import os
# import json
# from datetime import datetime
# import uuid
# import base64
# import re
# import requests

# gallery_routes = Blueprint('gallery', __name__)

# # File paths
# DATA_FILE = 'data/galleries.json'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# # Create necessary directories
# os.makedirs('uploads/images', exist_ok=True)
# os.makedirs('data', exist_ok=True)

# def allowed_file(filename):
#     """Check if file extension is allowed"""
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# def load_galleries():
#     """Load galleries from JSON file"""
#     if os.path.exists(DATA_FILE):
#         try:
#             with open(DATA_FILE, 'r') as f:
#                 return json.load(f)
#         except json.JSONDecodeError:
#             return []
#     return []

# def save_galleries(galleries):
#     """Save galleries to JSON file"""
#     with open(DATA_FILE, 'w') as f:
#         json.dump(galleries, f, indent=2)

# def upload_to_github(file_content, filename):
#     """
#     Upload image to GitHub repository
#     Returns the raw GitHub URL for the uploaded file
#     """
#     try:
#         repo = current_app.config.get('GITHUB_REPO')
#         branch = current_app.config.get('GITHUB_BRANCH', 'main')
#         token = current_app.config.get('GITHUB_TOKEN')
        
#         # If GitHub not configured, save locally
#         if not repo or repo == '':
#             print("GitHub repo not configured, saving locally")
#             return save_to_local(file_content, filename)
        
#         # GitHub API URL
#         path = f"gallery_images/{filename}"
#         url = f"https://api.github.com/repos/{repo}/contents/{path}"
        
#         # Prepare headers
#         headers = {
#             'Accept': 'application/vnd.github.v3+json',
#         }
#         if token:
#             headers['Authorization'] = f'token {token}'
        
#         # Encode content to base64 for GitHub API
#         content_base64 = base64.b64encode(file_content).decode('utf-8')
        
#         # Create or update file
#         data = {
#             'message': f'Upload image: {filename}',
#             'content': content_base64,
#             'branch': branch
#         }
        
#         # Check if file already exists
#         check_response = requests.get(url, headers=headers)
#         if check_response.status_code == 200:
#             # File exists, get SHA for update
#             data['sha'] = check_response.json()['sha']
        
#         # Upload to GitHub
#         response = requests.put(url, headers=headers, json=data)
        
#         if response.status_code in [200, 201]:
#             # Return raw GitHub URL
#             return f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
#         else:
#             print(f"GitHub upload failed: {response.status_code} - {response.text}")
#             return save_to_local(file_content, filename)
            
#     except Exception as e:
#         print(f"Error uploading to GitHub: {e}")
#         return save_to_local(file_content, filename)

# def save_to_local(file_content, filename):
#     """Fallback: Save to local uploads folder"""
#     try:
#         filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
#         with open(filepath, 'wb') as f:
#             f.write(file_content)
#         # Return path without /api prefix since it's added by blueprint
#         return f'/uploads/images/{filename}'
#     except Exception as e:
#         print(f"Error saving locally: {e}")
#         return None

# def save_base64_image(base64_string):
#     """Process base64 image and upload to GitHub"""
#     try:
#         # Extract image format
#         format_match = re.search(r'data:image/(\w+);base64,', base64_string)
#         img_format = format_match.group(1) if format_match else 'png'
        
#         # Remove header from base64 string
#         base64_data = re.sub(r'^data:image/.+;base64,', '', base64_string)
        
#         # Decode base64
#         file_content = base64.b64decode(base64_data)
        
#         # Generate unique filename
#         filename = f"{uuid.uuid4()}.{img_format}"
        
#         # Upload to GitHub (or save locally as fallback)
#         url = upload_to_github(file_content, filename)
        
#         return url
#     except Exception as e:
#         print(f"Error processing base64 image: {e}")
#         return None

# def process_images(images):
#     """Process image list - upload new base64 images to GitHub"""
#     processed_images = []
    
#     for img in images:
#         if img['url'].startswith('data:image'):
#             # New image - upload to GitHub
#             print(f"Processing new image: {img.get('name', 'unnamed')}")
#             saved_url = save_base64_image(img['url'])
#             if saved_url:
#                 processed_images.append({
#                     'id': img['id'],
#                     'url': saved_url,
#                     'name': img['name']
#                 })
#             else:
#                 print(f"Failed to save image: {img.get('name', 'unnamed')}")
#         else:
#             # Already saved image (GitHub URL or local path)
#             processed_images.append(img)
    
#     return processed_images

# # Get all galleries
# @gallery_routes.route('/gallery', methods=['GET'])
# def get_galleries():
#     """Get all galleries"""
#     try:
#         galleries = load_galleries()
#         return jsonify({
#             'success': True,
#             'data': galleries
#         })
#     except Exception as e:
#         print(f"Error in get_galleries: {e}")
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# # Get single gallery by ID
# @gallery_routes.route('/gallery/<gallery_id>', methods=['GET'])
# def get_gallery(gallery_id):
#     """Get a single gallery by ID"""
#     try:
#         galleries = load_galleries()
#         gallery = next((g for g in galleries if g['_id'] == gallery_id), None)
        
#         if gallery:
#             return jsonify({
#                 'success': True,
#                 'data': gallery
#             })
#         else:
#             return jsonify({
#                 'success': False,
#                 'error': 'Gallery not found'
#             }), 404
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# # Create new gallery
# @gallery_routes.route('/gallery', methods=['POST'])
# def create_gallery():
#     """Create a new gallery and upload images to GitHub"""
#     try:
#         data = request.get_json()
#         print(f"Received gallery creation request: {data.get('name', 'unnamed')}")

#         # Validate required fields
#         if not data:
#             return jsonify({'success': False, 'error': 'No data received'}), 400

#         if not data.get('name') or not data.get('title'):
#             return jsonify({
#                 'success': False,
#                 'error': 'Both name and title are required'
#             }), 400

#         # Validate images
#         images = data.get('images', [])
#         if not isinstance(images, list):
#             return jsonify({'success': False, 'error': 'Images must be an array'}), 400

#         if len(images) == 0:
#             return jsonify({'success': False, 'error': 'At least one image is required'}), 400

#         # Generate ID
#         gallery_id = str(uuid.uuid4())

#         # Process Images (Upload to GitHub or save locally)
#         print(f"Processing {len(images)} images...")
#         processed_images = process_images(images)
        
#         if len(processed_images) == 0:
#             return jsonify({'success': False, 'error': 'Failed to process images'}), 500

#         print(f"Successfully processed {len(processed_images)} images")

#         # Create gallery object
#         gallery = {
#             '_id': gallery_id,
#             'name': data['name'],
#             'title': data['title'],
#             'description': data.get('description', ''),
#             'collageFormat': data.get('collageFormat', 'grid'),
#             'fontStyle': data.get('fontStyle', 'sans'),
#             'colorTheme': data.get('colorTheme', 'elegant'),
#             'images': processed_images,
#             'createdAt': datetime.now().isoformat(),
#             'updatedAt': datetime.now().isoformat()
#         }

#         # Save to JSON
#         galleries = load_galleries()
#         galleries.append(gallery)
#         save_galleries(galleries)

#         print(f"Gallery created successfully: {gallery_id}")

#         return jsonify({'success': True, 'data': gallery}), 201

#     except Exception as e:
#         import traceback
#         print(f"Error in create_gallery: {traceback.format_exc()}")
#         return jsonify({'success': False, 'error': str(e)}), 500

# # Update gallery
# @gallery_routes.route('/gallery/<gallery_id>', methods=['PUT'])
# def update_gallery(gallery_id):
#     """Update an existing gallery"""
#     try:
#         data = request.get_json()
#         galleries = load_galleries()
        
#         # Find gallery
#         gallery_index = None
#         for i, g in enumerate(galleries):
#             if g['_id'] == gallery_id:
#                 gallery_index = i
#                 break
        
#         if gallery_index is None:
#             return jsonify({
#                 'success': False,
#                 'error': 'Gallery not found'
#             }), 404
        
#         # Process images
#         print(f"Updating gallery: {gallery_id}")
#         processed_images = process_images(data.get('images', []))
        
#         # Update gallery
#         galleries[gallery_index].update({
#             'name': data.get('name', galleries[gallery_index]['name']),
#             'title': data.get('title', galleries[gallery_index]['title']),
#             'description': data.get('description', ''),
#             'collageFormat': data.get('collageFormat', 'grid'),
#             'fontStyle': data.get('fontStyle', 'sans'),
#             'colorTheme': data.get('colorTheme', 'elegant'),
#             'images': processed_images,
#             'updatedAt': datetime.now().isoformat()
#         })
        
#         save_galleries(galleries)
        
#         print(f"Gallery updated successfully: {gallery_id}")
        
#         return jsonify({
#             'success': True,
#             'data': galleries[gallery_index]
#         })
#     except Exception as e:
#         import traceback
#         print(f"Error in update_gallery: {traceback.format_exc()}")
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# # Delete gallery
# @gallery_routes.route('/gallery/<gallery_id>', methods=['DELETE'])
# def delete_gallery(gallery_id):
#     """Delete a gallery (images remain in GitHub/local storage)"""
#     try:
#         galleries = load_galleries()
        
#         # Find and remove gallery
#         gallery_to_delete = None
#         for i, g in enumerate(galleries):
#             if g['_id'] == gallery_id:
#                 gallery_to_delete = galleries.pop(i)
#                 break
        
#         if gallery_to_delete is None:
#             return jsonify({
#                 'success': False,
#                 'error': 'Gallery not found'
#             }), 404
        
#         # Note: Images are NOT deleted from GitHub
#         # Only local images can be cleaned up if needed
        
#         save_galleries(galleries)
        
#         print(f"Gallery deleted: {gallery_id}")
        
#         return jsonify({
#             'success': True,
#             'message': 'Gallery deleted successfully'
#         })
#     except Exception as e:
#         return jsonify({
#             'success': False,
#             'error': str(e)
#         }), 500

# # Health check
# @gallery_routes.route('/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return jsonify({
#         'success': True,
#         'message': 'Gallery API is running',
#         'timestamp': datetime.now().isoformat()
#     })

from flask import Blueprint, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import uuid
import base64
import re
import requests

gallery_routes = Blueprint('gallery', __name__)

# File paths
DATA_FILE = 'data/galleries.json'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create necessary directories
os.makedirs('uploads/images', exist_ok=True)
os.makedirs('data', exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_galleries():
    """Load galleries from JSON file"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_galleries(galleries):
    """Save galleries to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(galleries, f, indent=2)

def upload_to_github(file_content, filename):
    """
    Upload image to GitHub repository
    Returns the raw GitHub URL for the uploaded file
    """
    try:
        repo = current_app.config.get('GITHUB_REPO')
        branch = current_app.config.get('GITHUB_BRANCH', 'main')
        token = current_app.config.get('GITHUB_TOKEN')
        
        # If GitHub not configured, save locally
        if not repo or repo == '':
            print("GitHub repo not configured, saving locally")
            return save_to_local(file_content, filename)
        
        # GitHub API URL
        path = f"gallery_images/{filename}"
        url = f"https://api.github.com/repos/{repo}/contents/{path}"
        
        # Prepare headers
        headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        if token:
            headers['Authorization'] = f'token {token}'
        
        # Encode content to base64 for GitHub API
        content_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Create or update file
        data = {
            'message': f'Upload image: {filename}',
            'content': content_base64,
            'branch': branch
        }
        
        # Check if file already exists
        check_response = requests.get(url, headers=headers)
        if check_response.status_code == 200:
            # File exists, get SHA for update
            data['sha'] = check_response.json()['sha']
        
        # Upload to GitHub
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code in [200, 201]:
            # Return raw GitHub URL
            return f"https://raw.githubusercontent.com/{repo}/{branch}/{path}"
        else:
            print(f"GitHub upload failed: {response.status_code} - {response.text}")
            return save_to_local(file_content, filename)
            
    except Exception as e:
        print(f"Error uploading to GitHub: {e}")
        return save_to_local(file_content, filename)

def save_to_local(file_content, filename):
    """Fallback: Save to local uploads folder"""
    try:
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        with open(filepath, 'wb') as f:
            f.write(file_content)
        # Return path without /api prefix since it's added by blueprint
        return f'/uploads/images/{filename}'
    except Exception as e:
        print(f"Error saving locally: {e}")
        return None

def save_base64_image(base64_string):
    """Process base64 image and upload to GitHub"""
    try:
        # Extract image format
        format_match = re.search(r'data:image/(\w+);base64,', base64_string)
        img_format = format_match.group(1) if format_match else 'png'
        
        # Remove header from base64 string
        base64_data = re.sub(r'^data:image/.+;base64,', '', base64_string)
        
        # Decode base64
        file_content = base64.b64decode(base64_data)
        
        # Generate unique filename
        filename = f"{uuid.uuid4()}.{img_format}"
        
        # Upload to GitHub (or save locally as fallback)
        url = upload_to_github(file_content, filename)
        
        return url
    except Exception as e:
        print(f"Error processing base64 image: {e}")
        return None

def process_images(images):
    """Process image list - upload new base64 images to GitHub"""
    processed_images = []
    
    for img in images:
        if img['url'].startswith('data:image'):
            # New image - upload to GitHub
            print(f"Processing new image: {img.get('name', 'unnamed')}")
            saved_url = save_base64_image(img['url'])
            if saved_url:
                processed_images.append({
                    'id': img['id'],
                    'url': saved_url,
                    'name': img['name']
                })
            else:
                print(f"Failed to save image: {img.get('name', 'unnamed')}")
        else:
            # Already saved image (GitHub URL or local path)
            processed_images.append(img)
    
    return processed_images

# Get all galleries
@gallery_routes.route('/gallery', methods=['GET'])
def get_galleries():
    """Get all galleries"""
    try:
        galleries = load_galleries()
        return jsonify({
            'success': True,
            'data': galleries
        })
    except Exception as e:
        print(f"Error in get_galleries: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Get single gallery by ID
@gallery_routes.route('/gallery/<gallery_id>', methods=['GET'])
def get_gallery(gallery_id):
    """Get a single gallery by ID"""
    try:
        galleries = load_galleries()
        gallery = next((g for g in galleries if g['_id'] == gallery_id), None)
        
        if gallery:
            return jsonify({
                'success': True,
                'data': gallery
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Gallery not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Create new gallery
@gallery_routes.route('/gallery', methods=['POST'])
def create_gallery():
    """Create a new gallery and upload images to GitHub"""
    try:
        data = request.get_json()
        print(f"Received gallery creation request: {data.get('name', 'unnamed')}")

        # Validate required fields
        if not data:
            return jsonify({'success': False, 'error': 'No data received'}), 400

        if not data.get('name') or not data.get('title'):
            return jsonify({
                'success': False,
                'error': 'Both name and title are required'
            }), 400

        # Validate images
        images = data.get('images', [])
        if not isinstance(images, list):
            return jsonify({'success': False, 'error': 'Images must be an array'}), 400

        if len(images) == 0:
            return jsonify({'success': False, 'error': 'At least one image is required'}), 400

        # Generate ID
        gallery_id = str(uuid.uuid4())

        # Process Images (Upload to GitHub or save locally)
        print(f"Processing {len(images)} images...")
        processed_images = process_images(images)
        
        if len(processed_images) == 0:
            return jsonify({'success': False, 'error': 'Failed to process images'}), 500

        print(f"Successfully processed {len(processed_images)} images")

        # Create gallery object
        gallery = {
            '_id': gallery_id,
            'name': data['name'],
            'title': data['title'],
            'description': data.get('description', ''),
            'collageFormat': data.get('collageFormat', 'grid'),
            'fontStyle': data.get('fontStyle', 'sans'),
            'colorTheme': data.get('colorTheme', 'elegant'),
            'images': processed_images,
            'createdAt': datetime.now().isoformat(),
            'updatedAt': datetime.now().isoformat()
        }

        # Save to JSON
        galleries = load_galleries()
        galleries.append(gallery)
        save_galleries(galleries)

        print(f"Gallery created successfully: {gallery_id}")

        return jsonify({'success': True, 'data': gallery}), 201

    except Exception as e:
        import traceback
        print(f"Error in create_gallery: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Update gallery
@gallery_routes.route('/gallery/<gallery_id>', methods=['PUT'])
def update_gallery(gallery_id):
    """Update an existing gallery"""
    try:
        data = request.get_json()
        galleries = load_galleries()
        
        # Find gallery
        gallery_index = None
        for i, g in enumerate(galleries):
            if g['_id'] == gallery_id:
                gallery_index = i
                break
        
        if gallery_index is None:
            return jsonify({
                'success': False,
                'error': 'Gallery not found'
            }), 404
        
        # Process images
        print(f"Updating gallery: {gallery_id}")
        processed_images = process_images(data.get('images', []))
        
        # Update gallery
        galleries[gallery_index].update({
            'name': data.get('name', galleries[gallery_index]['name']),
            'title': data.get('title', galleries[gallery_index]['title']),
            'description': data.get('description', ''),
            'collageFormat': data.get('collageFormat', 'grid'),
            'fontStyle': data.get('fontStyle', 'sans'),
            'colorTheme': data.get('colorTheme', 'elegant'),
            'images': processed_images,
            'updatedAt': datetime.now().isoformat()
        })
        
        save_galleries(galleries)
        
        print(f"Gallery updated successfully: {gallery_id}")
        
        return jsonify({
            'success': True,
            'data': galleries[gallery_index]
        })
    except Exception as e:
        import traceback
        print(f"Error in update_gallery: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Delete gallery
@gallery_routes.route('/gallery/<gallery_id>', methods=['DELETE'])
def delete_gallery(gallery_id):
    """Delete a gallery (images remain in GitHub/local storage)"""
    try:
        galleries = load_galleries()
        
        # Find and remove gallery
        gallery_to_delete = None
        for i, g in enumerate(galleries):
            if g['_id'] == gallery_id:
                gallery_to_delete = galleries.pop(i)
                break
        
        if gallery_to_delete is None:
            return jsonify({
                'success': False,
                'error': 'Gallery not found'
            }), 404
        
        # Note: Images are NOT deleted from GitHub
        # Only local images can be cleaned up if needed
        
        save_galleries(galleries)
        
        print(f"Gallery deleted: {gallery_id}")
        
        return jsonify({
            'success': True,
            'message': 'Gallery deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Health check
@gallery_routes.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'Gallery API is running',
        'timestamp': datetime.now().isoformat()
    })

# Serve uploaded images
@gallery_routes.route('/uploads/images/<filename>', methods=['GET'])
def serve_image(filename):
    """Serve images from the local uploads folder"""
    try:
        upload_folder = os.path.join(current_app.root_path, 'uploads', 'images')
        return send_from_directory(upload_folder, filename)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404
