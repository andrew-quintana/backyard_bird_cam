# Bird Camera Cloud Integration Guide

This guide outlines the complete workflow for integrating the Raspberry Pi Bird Camera with cloud services for storage, ML inference, and web UI display.

## Overall Architecture

![Architecture Overview](https://via.placeholder.com/800x400?text=Bird+Camera+Cloud+Architecture)

The system consists of three main components:
1. **Raspberry Pi Bird Camera** - Captures photos and uploads to cloud storage
2. **Cloud Storage** - Stores photos and metadata
3. **Hugging Face UI** - Web interface for viewing photos and analysis

## 1. ML Training and Model Hosting on Hugging Face

### Model Training

```python
# Example of training a bird classifier (use locally or on Google Colab)
from transformers import AutoImageProcessor, AutoModelForImageClassification
from datasets import load_dataset
import torch

# Load your bird dataset
dataset = load_dataset("your-username/bird-photos-dataset")

# Prepare model and processor
model_name = "google/vit-base-patch16-224"
processor = AutoImageProcessor.from_pretrained(model_name)
model = AutoModelForImageClassification.from_pretrained(
    model_name,
    num_labels=len(dataset["train"].features["label"].names)
)

# Training setup
# ... training code ...

# Save model
model.save_pretrained("./bird-classifier")
processor.save_pretrained("./bird-classifier")
```

### Pushing Model to Hugging Face Hub

```python
from huggingface_hub import login, push_to_hub

# Login to Hugging Face
login()

# Push model and processor to hub
model.push_to_hub("your-username/bird-classifier")
processor.push_to_hub("your-username/bird-classifier")
```

## 2. Photo Storage in Cloud Services

### AWS S3 Implementation

```python
# On Raspberry Pi
import boto3
import json
import os
from datetime import datetime

# AWS S3 Client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)

def upload_photo_to_s3(photo_path, metadata):
    """Upload a photo and its metadata to S3."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(photo_path)
    
    # Upload photo
    s3_client.upload_file(
        photo_path,
        'your-bird-photos-bucket',
        f'photos/{filename}'
    )
    
    # Upload metadata
    s3_client.put_object(
        Bucket='your-bird-photos-bucket',
        Key=f'metadata/{filename.replace(".jpg", ".json")}',
        Body=json.dumps(metadata),
        ContentType='application/json'
    )
    
    return f"s3://your-bird-photos-bucket/photos/{filename}"
```

### Google Cloud Storage Implementation

```python
# Alternative implementation using Google Cloud Storage
from google.cloud import storage
import json
import os

# GCS Client
storage_client = storage.Client()
bucket = storage_client.bucket('your-bird-photos-bucket')

def upload_photo_to_gcs(photo_path, metadata):
    """Upload a photo and its metadata to Google Cloud Storage."""
    filename = os.path.basename(photo_path)
    
    # Upload photo
    blob = bucket.blob(f'photos/{filename}')
    blob.upload_from_filename(photo_path)
    
    # Upload metadata
    metadata_blob = bucket.blob(f'metadata/{filename.replace(".jpg", ".json")}')
    metadata_blob.upload_from_string(
        json.dumps(metadata),
        content_type='application/json'
    )
    
    return f"gs://your-bird-photos-bucket/photos/{filename}"
```

### Integration with Bird Camera Code

In the `src/uploader/s3_uploader.py` file:

```python
class S3Uploader:
    def __init__(self, bucket_name, aws_access_key=None, aws_secret_key=None):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key or os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=aws_secret_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
        )
    
    def upload(self, photo_path, metadata):
        """Upload a photo and its metadata to S3."""
        # ... implementation ...
```

## 3. Hugging Face Spaces UI Implementation

### Setting Up the Space

1. Create a new Space on Hugging Face
   - Go to huggingface.co/spaces
   - Click "Create new Space"
   - Select Gradio as the SDK
   - Choose a name like "bird-camera-viewer"

2. Configure requirements:
   ```
   # requirements.txt
   gradio>=3.50.0
   boto3>=1.28.0
   pillow>=10.0.0
   requests>=2.31.0
   python-dotenv>=1.0.0
   ```

### Gradio App Implementation

```python
import gradio as gr
import boto3
import json
import io
import os
from PIL import Image
from datetime import datetime, timedelta
import dotenv

# Load environment variables
dotenv.load_dotenv()

# AWS S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
)
BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'your-bird-photos-bucket')

def get_photo_metadata(photo_key):
    """Get metadata for a photo from S3."""
    metadata_key = f"metadata/{os.path.basename(photo_key).replace('.jpg', '.json')}"
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=metadata_key)
        metadata = json.loads(response['Body'].read().decode('utf-8'))
        return metadata
    except Exception as e:
        print(f"Error retrieving metadata: {e}")
        return {}

def fetch_photos(start_date=None, end_date=None, species=None, limit=50):
    """Fetch photos from S3 with optional filtering."""
    if start_date is None:
        start_date = datetime.now() - timedelta(days=7)
    if end_date is None:
        end_date = datetime.now()
    
    # List objects in the photos directory
    response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix='photos/',
        MaxKeys=100  # Adjust as needed
    )
    
    photos = []
    for item in response.get('Contents', []):
        photo_key = item['Key']
        metadata = get_photo_metadata(photo_key)
        
        # Apply filters
        if metadata:
            # Date filter
            if 'timestamp' in metadata:
                photo_date = datetime.strptime(metadata['timestamp'], '%Y%m%d_%H%M%S')
                if photo_date < start_date or photo_date > end_date:
                    continue
            
            # Species filter
            if species and metadata.get('species') != species and species != 'All':
                continue
            
            # Get the photo
            try:
                response = s3_client.get_object(Bucket=BUCKET_NAME, Key=photo_key)
                photo_data = response['Body'].read()
                photo = Image.open(io.BytesIO(photo_data))
                
                # Add to results
                photos.append((photo, f"{metadata.get('species', 'Unknown')} - {metadata.get('timestamp', 'Unknown')}"))
            except Exception as e:
                print(f"Error retrieving photo {photo_key}: {e}")
        
        # Limit results
        if len(photos) >= limit:
            break
    
    return photos

def get_all_species():
    """Get a list of all unique bird species in the dataset."""
    all_species = set(['All'])  # Always include 'All' option
    
    # List objects in the metadata directory
    response = s3_client.list_objects_v2(
        Bucket=BUCKET_NAME,
        Prefix='metadata/',
        MaxKeys=1000  # Adjust as needed
    )
    
    for item in response.get('Contents', []):
        try:
            metadata_key = item['Key']
            response = s3_client.get_object(Bucket=BUCKET_NAME, Key=metadata_key)
            metadata = json.loads(response['Body'].read().decode('utf-8'))
            if 'species' in metadata:
                all_species.add(metadata['species'])
        except Exception as e:
            print(f"Error processing metadata {metadata_key}: {e}")
    
    return sorted(list(all_species))

# Gradio Interface
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    gr.Markdown("# Bird Camera Viewer")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Filters
            with gr.Box():
                gr.Markdown("### Filters")
                date_range = gr.DateRangeSlider(
                    label="Date Range",
                    value=[datetime.now() - timedelta(days=7), datetime.now()],
                    minimum_value=datetime.now() - timedelta(days=90)
                )
                species_dropdown = gr.Dropdown(
                    choices=get_all_species(),
                    label="Bird Species",
                    value="All"
                )
                refresh_btn = gr.Button("Refresh Photos")
        
        with gr.Column(scale=3):
            # Photo Gallery
            gallery = gr.Gallery(
                label="Bird Photos",
                show_label=True,
                elem_id="gallery",
                columns=3,
                rows=4,
                object_fit="contain",
                height="600px"
            )
            
            # Photo details
            selected_photo = gr.Image(label="Selected Photo", visible=False)
            photo_details = gr.Markdown(label="Photo Details")
    
    # Event handlers
    refresh_btn.click(
        fetch_photos,
        inputs=[
            lambda: date_range.value[0] if date_range.value else None,
            lambda: date_range.value[1] if date_range.value else None,
            species_dropdown
        ],
        outputs=[gallery]
    )
    
    # Initialize gallery
    demo.load(
        fn=fetch_photos,
        inputs=None,
        outputs=[gallery]
    )
    
    # Show details when photo is selected
    gallery.select(
        fn=lambda evt: (...),  # Implementation for displaying photo details
        inputs=[gr.SelectData()],
        outputs=[selected_photo, photo_details]
    )

# Launch app
demo.launch()
```

## 4. Optional: Using Hugging Face Inference API

```python
from huggingface_hub import InferenceApi
import requests
from PIL import Image
import io

def classify_with_huggingface(image_path):
    """Classify a bird image using Hugging Face Inference API."""
    # Option 1: Using InferenceApi
    inference = InferenceApi(
        repo_id="your-username/bird-classifier",
        token=os.environ.get("HF_API_TOKEN")
    )
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    
    result = inference(image_bytes)
    return result

    # Option 2: Using direct API calls
    """
    API_URL = "https://api-inference.huggingface.co/models/your-username/bird-classifier"
    headers = {"Authorization": f"Bearer {os.environ.get('HF_API_TOKEN')}"}
    
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        
    response = requests.post(API_URL, headers=headers, data=image_bytes)
    return response.json()
    """
```

## 5. Complete Workflow Integration

### On the Raspberry Pi

1. Capture photo when motion is detected
2. Optionally perform local inference if resources allow
3. Upload photo and metadata to cloud storage
4. Log the event and clean up local storage as needed

### In the Cloud

1. Photos and metadata are stored in AWS S3 or Google Cloud Storage
2. Hugging Face hosts the ML model for cloud-based inference
3. Hugging Face Spaces hosts the web UI for viewing photos

### For End Users

1. Visit the Hugging Face Spaces URL to access the bird camera viewer
2. Use filters to find specific bird species or time periods
3. View and download high-quality bird photos

## Security Considerations

1. Use environment variables for all credentials
2. Set up proper IAM policies for cloud storage access
3. Consider using Hugging Face private repositories for sensitive models
4. Implement rate limiting on the Spaces app if needed

## Cost Considerations

1. AWS S3 / Google Cloud Storage: Pay only for storage used and data transfer
2. Hugging Face Model Hosting: Free for public models
3. Hugging Face Spaces: Free for basic usage
4. Hugging Face Inference API: Free tier available, then pay per request 