"""Photo storage module for managing captured images."""
import os
import shutil
import logging
from datetime import datetime
import json


class PhotoStorage:
    """Class to handle photo storage operations."""

    def __init__(self, base_dir="photos", max_photos=1000, metadata_file="photo_metadata.json"):
        """Initialize photo storage with base directory.
        
        Args:
            base_dir (str): Base directory for storing photos
            max_photos (int): Maximum number of photos to keep
            metadata_file (str): Filename for metadata storage
        """
        self.base_dir = base_dir
        self.max_photos = max_photos
        self.metadata_file = os.path.join(base_dir, metadata_file)
        self.logger = logging.getLogger(__name__)
        self.metadata = {}
        self.setup()
        
    def setup(self):
        """Create storage directory if it doesn't exist."""
        self.logger.info(f"Setting up photo storage in {self.base_dir}")
        os.makedirs(self.base_dir, exist_ok=True)
        
        # Load existing metadata if it exists
        if os.path.exists(self.metadata_file):
            self.load_metadata()
        
    def load_metadata(self):
        """Load metadata from the metadata file."""
        try:
            with open(self.metadata_file, 'r') as f:
                self.metadata = json.load(f)
            self.logger.info(f"Loaded metadata for {len(self.metadata)} photos")
        except (json.JSONDecodeError, FileNotFoundError) as e:
            self.logger.warning(f"Failed to load metadata: {str(e)}")
            self.metadata = {}
            
    def save_metadata(self):
        """Save metadata to the metadata file."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            self.logger.info(f"Saved metadata for {len(self.metadata)} photos")
        except Exception as e:
            self.logger.error(f"Failed to save metadata: {str(e)}")
    
    def get_date_directory(self, date=None):
        """Get the date directory name in YYYYMMDD format.
        
        Args:
            date (datetime, optional): Date to use, defaults to current date
            
        Returns:
            str: Directory name in YYYYMMDD format
        """
        if date is None:
            date = datetime.now()
        return date.strftime("%Y%m%d")
        
    def generate_filename(self, extension=".jpg"):
        """Generate a unique filename for a photo.
        
        Args:
            extension (str): File extension for the photo
            
        Returns:
            str: Unique filename based on timestamp
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{timestamp}{extension}"
        
    def save_photo(self, photo_data, filename=None, metadata=None):
        """Save photo data to storage.
        
        Args:
            photo_data: Photo data to be saved (bytes or file-like object)
            filename (str, optional): Custom filename, if not provided, one will be generated
            metadata (dict, optional): Additional metadata to store with the photo
            
        Returns:
            str: Path to the saved photo
        """
        # Generate filename if not provided
        if filename is None:
            filename = self.generate_filename()
            
        # Get the full path
        full_path = self.get_photo_path(filename)
        
        # Save the photo data
        self.logger.info(f"Saving photo to {full_path}")
        
        if isinstance(photo_data, bytes):
            # If photo_data is bytes, write directly
            with open(full_path, 'wb') as f:
                f.write(photo_data)
        else:
            # If photo_data is a file path, copy the file
            try:
                if os.path.exists(photo_data):
                    shutil.copy2(photo_data, full_path)
                else:
                    # Assume it's a file-like object
                    with open(full_path, 'wb') as f:
                        f.write(photo_data.read())
            except (AttributeError, TypeError):
                # Last resort: try to write it as string
                with open(full_path, 'w') as f:
                    f.write(str(photo_data))
        
        # Store metadata
        if metadata is None:
            metadata = {}
            
        metadata['timestamp'] = datetime.now().isoformat()
        metadata['filename'] = filename
        metadata['path'] = full_path
        
        self.metadata[filename] = metadata
        self.save_metadata()
        
        # Enforce max photos limit
        self._enforce_max_photos()
        
        return full_path
    
    def _enforce_max_photos(self):
        """Enforce the maximum number of photos by deleting the oldest ones."""
        photo_files = self.list_photos()
        
        if len(photo_files) > self.max_photos:
            # Sort by creation time (oldest first)
            photo_files.sort(key=lambda f: os.path.getctime(self.get_photo_path(f)))
            
            # Calculate how many to delete
            num_to_delete = len(photo_files) - self.max_photos
            self.logger.info(f"Enforcing max photos limit, deleting {num_to_delete} oldest photos")
            
            # Delete oldest photos
            for i in range(num_to_delete):
                self.delete_photo(photo_files[i])
        
    def list_photos(self):
        """List all saved photos.
        
        Returns:
            list: List of photo filenames
        """
        if not os.path.exists(self.base_dir):
            return []
        
        photo_files = []
        
        # Get all directories in the base directory
        all_dirs = [d for d in os.listdir(self.base_dir) 
                   if os.path.isdir(os.path.join(self.base_dir, d))]
        
        # Also include the base directory itself for backward compatibility
        all_dirs.append("")
        
        for dir_name in all_dirs:
            dir_path = os.path.join(self.base_dir, dir_name)
            
            # Skip if not a directory
            if not os.path.isdir(dir_path):
                continue
                
            # Get all files in the directory
            try:
                dir_files = os.listdir(dir_path)
                
                # Filter for image files
                for f in dir_files:
                    if (f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')) and
                        os.path.isfile(os.path.join(dir_path, f))):
                        # Store as dir_name/filename if in a subdirectory
                        if dir_name:
                            photo_files.append(os.path.join(dir_name, f))
                        else:
                            photo_files.append(f)
            except Exception as e:
                self.logger.error(f"Error listing files in {dir_path}: {str(e)}")
                      
        return photo_files
        
    def get_photo_path(self, filename):
        """Get full path for a photo.
        
        Args:
            filename (str): Filename of the photo
            
        Returns:
            str: Full path to the photo
        """
        # Check if filename already includes a directory
        if os.path.dirname(filename):
            # If it already has a directory component, use it as is
            return os.path.join(self.base_dir, filename)
        
        # Get the current date directory
        date_dir = self.get_date_directory()
        date_dir_path = os.path.join(self.base_dir, date_dir)
        
        # Create the date directory if it doesn't exist
        os.makedirs(date_dir_path, exist_ok=True)
        
        # Return the path with the date directory included
        return os.path.join(date_dir_path, filename)
    
    def get_photo_metadata(self, filename):
        """Get metadata for a photo.
        
        Args:
            filename (str): Filename of the photo
            
        Returns:
            dict: Metadata for the photo
        """
        # Extract just the filename without directory for metadata lookup
        base_filename = os.path.basename(filename)
        return self.metadata.get(base_filename, {})
    
    def delete_photo(self, filename):
        """Delete a photo.
        
        Args:
            filename (str): Filename of the photo to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        path = self.get_photo_path(filename)
        
        if os.path.exists(path):
            try:
                os.remove(path)
                
                # Remove from metadata
                base_filename = os.path.basename(filename)
                if base_filename in self.metadata:
                    del self.metadata[base_filename]
                    self.save_metadata()
                
                self.logger.info(f"Deleted photo: {filename}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to delete photo {filename}: {str(e)}")
                
        return False 