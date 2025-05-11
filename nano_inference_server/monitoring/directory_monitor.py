"""
Directory monitor for watching input directories and processing new images.
Uses watchdog to monitor filesystem events.
"""
import os
import time
import logging
import threading
from typing import Callable, List, Optional
from pathlib import Path
from queue import Queue
import re

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

# Set up logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImageFileEventHandler(FileSystemEventHandler):
    """Watches for image files created in the monitored directory"""
    
    def __init__(self, 
                callback: Callable[[str], None], 
                file_patterns: List[str] = None, 
                queue: Optional[Queue] = None):
        """
        Initialize the event handler.
        
        Args:
            callback: Function to call when a new image is detected
            file_patterns: List of file patterns to match (e.g. ["*.jpg", "*.png"])
            queue: Optional queue to put file paths in for async processing
        """
        self.callback = callback
        self.file_patterns = file_patterns or [r".*\.(jpg|jpeg|png)$"]
        self.file_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.file_patterns]
        self.queue = queue
        super().__init__()
    
    def on_created(self, event):
        """Called when a file is created"""
        if not event.is_directory:
            file_path = event.src_path
            
            # Check if the file matches our patterns
            if any(regex.match(file_path) for regex in self.file_regex):
                logger.info(f"New image detected: {file_path}")
                
                # Add a small delay to ensure the file is fully written
                time.sleep(0.5)
                
                if self.queue:
                    # Add to queue for async processing
                    self.queue.put(file_path)
                    logger.debug(f"Added {file_path} to processing queue")
                else:
                    # Process synchronously
                    self.callback(file_path)


class DirectoryMonitor:
    """Monitors directories for new image files"""
    
    def __init__(self, 
                input_dir: str, 
                callback: Callable[[str], None],
                file_patterns: List[str] = None,
                use_queue: bool = True,
                process_existing: bool = False):
        """
        Initialize the directory monitor.
        
        Args:
            input_dir: Directory to monitor for new images
            callback: Function to call when a new image is detected
            file_patterns: List of file patterns to match
            use_queue: Whether to use a queue for async processing
            process_existing: Whether to process existing files in the directory
        """
        self.input_dir = os.path.abspath(input_dir)
        self.callback = callback
        self.file_patterns = file_patterns or [r".*\.(jpg|jpeg|png)$"]
        self.use_queue = use_queue
        self.process_existing = process_existing
        
        # Create the queue if needed
        self.queue = Queue() if use_queue else None
        
        # Create the observer and event handler
        self.observer = Observer()
        self.event_handler = ImageFileEventHandler(
            callback=self._process_file,
            file_patterns=self.file_patterns,
            queue=self.queue
        )
        
        # Create the worker thread if using a queue
        self.worker_thread = None
        self.stop_event = threading.Event()
        
        # Ensure input directory exists
        if not os.path.exists(self.input_dir):
            logger.info(f"Creating input directory: {self.input_dir}")
            os.makedirs(self.input_dir, exist_ok=True)
        
    def _process_file(self, file_path: str):
        """Process a single file"""
        try:
            self.callback(file_path)
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
    
    def _worker_loop(self):
        """Worker thread for processing queued files"""
        logger.info("Worker thread started")
        while not self.stop_event.is_set():
            try:
                # Get a file from the queue with a timeout
                file_path = self.queue.get(timeout=1.0)
                self._process_file(file_path)
                self.queue.task_done()
            except Exception as e:
                if not isinstance(e, TimeoutError):
                    logger.error(f"Error in worker thread: {str(e)}")
        
        logger.info("Worker thread stopped")
    
    def _process_existing_files(self):
        """Process existing files in the directory"""
        logger.info(f"Processing existing files in {self.input_dir}")
        count = 0
        
        # Compile regex patterns
        patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.file_patterns]
        
        # Walk through the directory
        for root, _, files in os.walk(self.input_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check if the file matches our patterns
                if any(regex.match(file_path) for regex in patterns):
                    logger.info(f"Processing existing file: {file_path}")
                    
                    if self.queue:
                        self.queue.put(file_path)
                    else:
                        self._process_file(file_path)
                    
                    count += 1
        
        logger.info(f"Queued {count} existing files for processing")
    
    def start(self):
        """Start monitoring the directory"""
        # Start the worker thread if using a queue
        if self.use_queue:
            self.stop_event.clear()
            self.worker_thread = threading.Thread(target=self._worker_loop)
            self.worker_thread.daemon = True
            self.worker_thread.start()
        
        # Schedule the directory for monitoring
        self.observer.schedule(self.event_handler, self.input_dir, recursive=True)
        self.observer.start()
        
        logger.info(f"Started monitoring directory: {self.input_dir}")
        
        # Process existing files if requested
        if self.process_existing:
            self._process_existing_files()
    
    def stop(self):
        """Stop monitoring the directory"""
        # Stop the observer
        self.observer.stop()
        self.observer.join()
        
        # Stop the worker thread if using a queue
        if self.use_queue and self.worker_thread:
            self.stop_event.set()
            self.worker_thread.join(timeout=2.0)
        
        logger.info(f"Stopped monitoring directory: {self.input_dir}")


# Example usage
if __name__ == "__main__":
    def process_image(file_path):
        logger.info(f"Processing image: {file_path}")
        # Simulate processing time
        time.sleep(0.5)
        logger.info(f"Finished processing: {file_path}")
    
    # Create and start the monitor
    monitor = DirectoryMonitor(
        input_dir="./test_images",
        callback=process_image,
        process_existing=True
    )
    
    monitor.start()
    
    try:
        logger.info("Press Ctrl+C to stop...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping...")
        monitor.stop() 