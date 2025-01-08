import os
import json
import random
import string
from django.http import JsonResponse
from pydantic import BaseModel, ValidationError
from django.views.decorators.csrf import csrf_exempt

UPLOAD_DIR = "uploaded_files"
USER_FILES_PATH = os.path.join(UPLOAD_DIR, "user_files.json")

# Ensure directories and the tracking file exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
if not os.path.exists(USER_FILES_PATH):
    with open(USER_FILES_PATH, 'w') as f:
        json.dump({}, f) 

class FileUploadRequest(BaseModel):
    file: bytes  # The uploaded file in bytes
    token: str  # User token (custom token generated in the front)

@csrf_exempt
def upload_file(request):
    if request.method == 'POST':
        try:
            # Validate incoming data
            data = FileUploadRequest(
                file=request.FILES['file'].read(),
                token=request.POST['token']
            )

            # Generate a random filename
            random_name = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
            file_path = os.path.join(UPLOAD_DIR, random_name)

            # Save the uploaded file
            with open(file_path, 'wb') as f:
                f.write(data.file)

            # Save metadata
            meta_data = {
                "owner_token": data.token,
                "original_name": request.FILES['file'].name,
            }
            meta_path = f"{file_path}.meta.json"
            with open(meta_path, 'w') as meta_file:
                json.dump(meta_data, meta_file)

            # Update the user files tracking
            with open(USER_FILES_PATH, 'r+') as user_files_file:
                user_files = json.load(user_files_file)
                if data.token not in user_files:
                    user_files[data.token] = []
                user_files[data.token].append(random_name)
                user_files_file.seek(0)
                json.dump(user_files, user_files_file, indent=4)
                user_files_file.truncate()

            return JsonResponse({
                "message": "File uploaded successfully",
                "random_name": random_name,
                "original_name": meta_data["original_name"]
            })
        except ValidationError as e:
            return JsonResponse({'error': e.errors()}, status=400)
        except KeyError:
            return JsonResponse({'error': 'Missing file or token'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

