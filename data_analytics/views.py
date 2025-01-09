from pydantic import BaseModel, Field
from typing import Optional
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
import os

UPLOAD_DIR = "uploaded_files"
USER_FILES_PATH = os.path.join(UPLOAD_DIR, "user_files.json")


# Pydantic model for request validation
class VisualizationRequest(BaseModel):
    token: str
    file_name: str
    plot_type: str
    column_x: Optional[str] = None
    column_y: Optional[str] = None
    column_z: Optional[str] = None  # Additional optional column for 3rd variable
    filter_data: Optional[str] = None  # Optional filter for query


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


# Function to generate a plot and return it as base64 image
def generate_plot(df, plot_type, column_x=None, column_y=None, column_z=None, filter_data=None):
    if filter_data:
        df = df.query(filter_data)

    plt.figure(figsize=(10, 6))

    # Histogram plot
    if plot_type == 'histogram':
        sns.histplot(df[column_x], kde=True)
        plt.title(f"Histogram of {column_x}")

    # Scatter plot with optional third variable for color or size
    elif plot_type == 'scatter':
        if column_z:  # Use the third variable for color or size
            sns.scatterplot(x=df[column_x], y=df[column_y], hue=df[column_z], palette='viridis')
            plt.title(f"Scatter plot of {column_x} vs {column_y} colored by {column_z}")
        else:
            sns.scatterplot(x=df[column_x], y=df[column_y])
            plt.title(f"Scatter plot of {column_x} vs {column_y}")

    # Bar plot with optional third variable for color
    elif plot_type == 'bar':
        if column_z:  # Use the third variable for color
            sns.barplot(x=df[column_x], y=df[column_y], hue=df[column_z])
            plt.title(f"Bar plot of {column_x} vs {column_y} grouped by {column_z}")
        else:
            sns.barplot(x=df[column_x], y=df[column_y])
            plt.title(f"Bar plot of {column_x} vs {column_y}")

    # Line plot with optional third variable for color
    elif plot_type == 'line':
        if column_z:  # Use the third variable for color
            sns.lineplot(x=df[column_x], y=df[column_y], hue=df[column_z])
            plt.title(f"Line plot of {column_x} vs {column_y} colored by {column_z}")
        else:
            sns.lineplot(x=df[column_x], y=df[column_y])
            plt.title(f"Line plot of {column_x} vs {column_y}")

    # Heatmap for correlation, only numerical data considered
    elif plot_type == 'heatmap':
        # Select only numerical columns for correlation matrix
        numerical_df = df.select_dtypes(include='number')
        correlation = numerical_df.corr()
        sns.heatmap(correlation, annot=True, cmap='coolwarm')
        plt.title("Correlation Heatmap")

    # Convert plot to PNG and then to base64
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    
    return img_str


# View for generating different types of visualizations
@csrf_exempt
def visualize_data(request):
    if request.method == 'POST':
        try:
            token = request.POST['token']
            file_name = request.POST['file_name']
            plot_type = request.POST['plot_type']
            column_x = request.POST.get('column_x', None)
            column_y = request.POST.get('column_y', None)
            column_z = request.POST.get('column_z', None)  # Optional third column
            filter_data = request.POST.get('filter_data', None)

            # Validate file existence and ownership
            file_path, error = validate_file(token, file_name)
            if error:
                return error

            # Read the CSV file
            df = pd.read_csv(file_path)

            # Check if columns are valid
            if column_x and column_x not in df.columns:
                return JsonResponse({'error': f'{column_x} is not a valid column in the dataset'}, status=400)
            if column_y and column_y not in df.columns:
                return JsonResponse({'error': f'{column_y} is not a valid column in the dataset'}, status=400)
            if column_z and column_z not in df.columns:
                return JsonResponse({'error': f'{column_z} is not a valid column in the dataset'}, status=400)

            # Generate the plot based on user preferences
            img_str = generate_plot(df, plot_type, column_x, column_y, column_z, filter_data)

            # Return the image as base64
            return JsonResponse({'image': img_str})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
