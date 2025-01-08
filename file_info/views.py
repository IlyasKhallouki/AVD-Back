import os
import json
import pandas as pd
from typing import Optional
from django.http import JsonResponse
from pydantic import BaseModel, ValidationError
from django.views.decorators.csrf import csrf_exempt

UPLOAD_DIR = "uploaded_files"
USER_FILES_PATH = os.path.join(UPLOAD_DIR, "user_files.json")


# Pydantic models for validation
class FileOperationRequest(BaseModel):
    token: str
    file_name: str


class LineColumnRequest(FileOperationRequest):
    number: int  # Line/column number
    is_column: bool  # True for column, False for line
    range_end: Optional[int] = None  # Optional end for range selection


# Helper function to validate ownership and file existence
def validate_file(token, file_name):
    with open(USER_FILES_PATH, 'r') as user_files_file:
        user_files = json.load(user_files_file)

    if token not in user_files or file_name not in user_files[token]:
        return None, JsonResponse({'error': 'File not found or unauthorized access'}, status=403)

    file_path = os.path.join(UPLOAD_DIR, file_name)
    if not os.path.exists(file_path):
        return None, JsonResponse({'error': 'File does not exist'}, status=404)

    return file_path, None


# Endpoint 1: .describe()
@csrf_exempt
def describe_csv(request):
    if request.method == 'POST':
        try:
            data = FileOperationRequest(
                token=request.POST['token'],
                file_name=request.POST['file_name']
            )
            file_path, error = validate_file(data.token, data.file_name)
            if error:
                return error

            df = pd.read_csv(file_path)
            return JsonResponse(df.describe().to_dict())
        except ValidationError as e:
            return JsonResponse({'error': e.errors()}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# Endpoint 3: head(5)
@csrf_exempt
def head_csv(request):
    if request.method == 'POST':
        try:
            data = FileOperationRequest(
                token=request.POST['token'],
                file_name=request.POST['file_name']
            )
            file_path, error = validate_file(data.token, data.file_name)
            if error:
                return error

            df = pd.read_csv(file_path)
            return JsonResponse(df.head(5).to_dict(orient='records'))
        except ValidationError as e:
            return JsonResponse({'error': e.errors()}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# Endpoint 4: Column Names
@csrf_exempt
def column_names(request):
    if request.method == 'POST':
        try:
            data = FileOperationRequest(
                token=request.POST['token'],
                file_name=request.POST['file_name']
            )
            file_path, error = validate_file(data.token, data.file_name)
            if error:
                return error

            df = pd.read_csv(file_path)
            return JsonResponse({'columns': df.columns.tolist()})
        except ValidationError as e:
            return JsonResponse({'error': e.errors()}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# Endpoint 5: .shape
@csrf_exempt
def shape_csv(request):
    if request.method == 'POST':
        try:
            data = FileOperationRequest(
                token=request.POST['token'],
                file_name=request.POST['file_name']
            )
            file_path, error = validate_file(data.token, data.file_name)
            if error:
                return error

            df = pd.read_csv(file_path)
            return JsonResponse({'shape': df.shape})
        except ValidationError as e:
            return JsonResponse({'error': e.errors()}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


# Endpoint 6: Specific Rows/Columns or Ranges
@csrf_exempt
def get_rows_or_columns(request):
    if request.method == 'POST':
        try:
            range_end = request.POST.get('range_end', '').strip()
            range_end = int(range_end) if range_end else None
            
            data = LineColumnRequest(
                token=request.POST['token'],
                file_name=request.POST['file_name'],
                number=int(request.POST['number']),
                is_column=request.POST['is_column'].lower() == 'true',
                range_end=range_end
            )
            file_path, error = validate_file(data.token, data.file_name)
            if error:
                return error

            df = pd.read_csv(file_path)
            if data.is_column:
                if data.range_end is None:
                    return JsonResponse({df.columns[data.number]: df.iloc[:, data.number].tolist()})
                else:
                    return JsonResponse({
                        f"columns_{data.number}_to_{data.range_end}": df.iloc[:, data.number:data.range_end].to_dict()
                    })
            else:
                if data.range_end is None:
                    return JsonResponse({df.index[data.number]: df.iloc[data.number].to_dict()})
                else:
                    return JsonResponse({
                        f"rows_{data.number}_to_{data.range_end}": df.iloc[data.number:data.range_end].to_dict(orient='records')
                    })
        except ValidationError as e:
            return JsonResponse({'error': e.errors()}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
def aggregate_csv_info(request):
    if request.method == 'POST':
        try:
            # Validate the incoming request
            data = FileOperationRequest(
                token=request.POST['token'],
                file_name=request.POST['file_name']
            )
            file_path, error = validate_file(data.token, data.file_name)
            if error:
                return error

            # Read the CSV
            df = pd.read_csv(file_path)


            # Prepare the aggregated response
            response = {
                "describe": df.describe().to_dict(),
                "head": df.head(5).to_dict(orient='records'),
                "columns": df.columns.tolist(),
                "shape": df.shape
            }

            return JsonResponse(response)
        except ValidationError as e:
            return JsonResponse({'error': e.errors()}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
