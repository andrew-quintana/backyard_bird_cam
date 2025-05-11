"""
Result storage for bird detection inference results.
Handles storing, retrieving, and managing results in a structured way.
"""
import os
import json
import time
import logging
import sqlite3
import datetime
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ResultStorage:
    """Handles storage and retrieval of inference results"""
    
    def __init__(self, base_dir: str, db_path: Optional[str] = None,
                 max_results: int = 1000, 
                 organize_by_date: bool = True):
        """
        Initialize the result storage.
        
        Args:
            base_dir: Base directory for storing results
            db_path: Path to the SQLite database (if None, one will be created in base_dir)
            max_results: Maximum number of results to keep
            organize_by_date: Whether to organize results by date
        """
        self.base_dir = os.path.abspath(base_dir)
        self.max_results = max_results
        self.organize_by_date = organize_by_date
        
        # Set up directories
        self.images_dir = os.path.join(self.base_dir, "images")
        self.annotated_dir = os.path.join(self.base_dir, "annotated")
        self.results_dir = os.path.join(self.base_dir, "results")
        
        # Create directories if they don't exist
        for directory in [self.base_dir, self.images_dir, self.annotated_dir, self.results_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Set up database
        if db_path is None:
            self.db_path = os.path.join(self.base_dir, "results.db")
        else:
            self.db_path = os.path.abspath(db_path)
            
        self._init_database()
    
    def _init_database(self):
        """Initialize the SQLite database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create detections table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                image_path TEXT NOT NULL,
                annotated_path TEXT,
                result_path TEXT,
                bird_detected BOOLEAN,
                bird_count INTEGER,
                has_species BOOLEAN,
                species TEXT,
                confidence REAL,
                processing_time REAL,
                source TEXT
            )
            ''')
            
            # Create index on timestamp for faster retrieval
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON detections(timestamp)')
            
            conn.commit()
            conn.close()
            
            logger.info(f"Database initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def _get_paths(self, image_path: str, result_id: Optional[str] = None) -> Tuple[str, str, str]:
        """
        Get paths for storing an image, its annotated version, and results
        
        Args:
            image_path: Path to the original image
            result_id: Optional ID to use for the result
            
        Returns:
            Tuple of (stored_image_path, annotated_path, result_path)
        """
        # Generate a unique ID if not provided
        if result_id is None:
            result_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Extract filename
        filename = os.path.basename(image_path)
        base_name, ext = os.path.splitext(filename)
        
        # Create subdirectories if organizing by date
        if self.organize_by_date:
            subdir = datetime.datetime.now().strftime("%Y-%m-%d")
            img_dir = os.path.join(self.images_dir, subdir)
            ann_dir = os.path.join(self.annotated_dir, subdir)
            res_dir = os.path.join(self.results_dir, subdir)
            
            for directory in [img_dir, ann_dir, res_dir]:
                os.makedirs(directory, exist_ok=True)
        else:
            img_dir = self.images_dir
            ann_dir = self.annotated_dir
            res_dir = self.results_dir
        
        # Generate paths
        stored_image_path = os.path.join(img_dir, f"{base_name}_{result_id}{ext}")
        annotated_path = os.path.join(ann_dir, f"{base_name}_{result_id}_annotated{ext}")
        result_path = os.path.join(res_dir, f"{base_name}_{result_id}.json")
        
        return stored_image_path, annotated_path, result_path
    
    def save_result(self, 
                   image_path: str, 
                   detections: List[Dict], 
                   annotated_path: Optional[str] = None,
                   metadata: Optional[Dict] = None,
                   processing_time: Optional[float] = None,
                   copy_original: bool = True) -> Dict:
        """
        Save detection results
        
        Args:
            image_path: Path to the original image
            detections: List of detection dictionaries
            annotated_path: Path to the annotated image (if available)
            metadata: Additional metadata to store
            processing_time: Processing time in seconds
            copy_original: Whether to copy the original image to storage
            
        Returns:
            Dictionary with paths and result info
        """
        try:
            # Generate paths
            timestamp = datetime.datetime.now().isoformat()
            result_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            stored_image_path, default_annotated_path, result_path = self._get_paths(image_path, result_id)
            
            # Use provided annotated path or default
            if annotated_path is None:
                annotated_path = default_annotated_path
            
            # Copy original image if requested
            if copy_original and os.path.exists(image_path):
                shutil.copy2(image_path, stored_image_path)
                logger.debug(f"Copied original image to {stored_image_path}")
            
            # Extract detection info
            bird_detected = len(detections) > 0
            bird_count = len(detections)
            
            # Get species info if available
            species_list = []
            max_confidence = 0.0
            
            for detection in detections:
                if "class_name" in detection and detection["class_name"] != "bird":
                    species_list.append(detection["class_name"])
                
                if "confidence" in detection and detection["confidence"] > max_confidence:
                    max_confidence = detection["confidence"]
            
            has_species = len(species_list) > 0
            species = ", ".join(set(species_list))
            
            # Prepare result data
            result_data = {
                "timestamp": timestamp,
                "image_path": os.path.abspath(stored_image_path),
                "annotated_path": os.path.abspath(annotated_path),
                "result_path": os.path.abspath(result_path),
                "bird_detected": bird_detected,
                "bird_count": bird_count,
                "has_species": has_species,
                "species": species,
                "confidence": max_confidence,
                "detections": detections,
                "processing_time": processing_time,
                "metadata": metadata or {}
            }
            
            # Save result JSON
            with open(result_path, 'w') as f:
                json.dump(result_data, f, indent=2)
            
            # Save to database
            self._save_to_database(result_data)
            
            # Cleanup old results if needed
            self._cleanup_old_results()
            
            return result_data
            
        except Exception as e:
            logger.error(f"Error saving results: {str(e)}")
            # Return minimal info on error
            return {
                "timestamp": datetime.datetime.now().isoformat(),
                "error": str(e),
                "image_path": image_path
            }
    
    def _save_to_database(self, result_data: Dict):
        """Save result data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO detections (
                timestamp, 
                image_path, 
                annotated_path, 
                result_path, 
                bird_detected, 
                bird_count, 
                has_species, 
                species, 
                confidence, 
                processing_time,
                source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result_data["timestamp"],
                result_data["image_path"],
                result_data["annotated_path"],
                result_data["result_path"],
                result_data["bird_detected"],
                result_data["bird_count"],
                result_data["has_species"],
                result_data["species"],
                result_data["confidence"],
                result_data["processing_time"],
                result_data.get("metadata", {}).get("source", "unknown")
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
    
    def _cleanup_old_results(self):
        """Clean up old results if we've exceeded max_results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get count of results
            cursor.execute('SELECT COUNT(*) FROM detections')
            count = cursor.fetchone()[0]
            
            if count > self.max_results:
                # Calculate how many to delete
                to_delete = count - self.max_results
                
                # Get the oldest results to delete
                cursor.execute('''
                SELECT id, image_path, annotated_path, result_path 
                FROM detections 
                ORDER BY timestamp ASC 
                LIMIT ?
                ''', (to_delete,))
                
                old_results = cursor.fetchall()
                
                # Delete files and database entries
                for result in old_results:
                    result_id, img_path, ann_path, res_path = result
                    
                    # Delete files if they exist
                    for path in [img_path, ann_path, res_path]:
                        if path and os.path.exists(path):
                            try:
                                os.remove(path)
                            except Exception as e:
                                logger.warning(f"Could not delete {path}: {str(e)}")
                    
                    # Delete database entry
                    cursor.execute('DELETE FROM detections WHERE id = ?', (result_id,))
                
                conn.commit()
                logger.info(f"Cleaned up {len(old_results)} old results")
            
            conn.close()
            
        except Exception as e:
            logger.error(f"Error cleaning up old results: {str(e)}")
    
    def get_recent_results(self, limit: int = 100, 
                          bird_only: bool = False, 
                          with_species: bool = False) -> List[Dict]:
        """
        Get recent detection results
        
        Args:
            limit: Maximum number of results to return
            bird_only: Only include results with birds detected
            with_species: Only include results with species identification
            
        Returns:
            List of result dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            cursor = conn.cursor()
            
            query = '''
            SELECT * FROM detections
            '''
            
            conditions = []
            if bird_only:
                conditions.append('bird_detected = 1')
            if with_species:
                conditions.append('has_species = 1')
            
            if conditions:
                query += ' WHERE ' + ' AND '.join(conditions)
            
            query += ''' 
            ORDER BY timestamp DESC
            LIMIT ?
            '''
            
            cursor.execute(query, (limit,))
            results = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting recent results: {str(e)}")
            return []
    
    def get_result_by_id(self, result_id: int) -> Optional[Dict]:
        """
        Get a specific result by its ID
        
        Args:
            result_id: ID of the result to get
            
        Returns:
            Result dictionary or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM detections WHERE id = ?', (result_id,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                # Load the full JSON result file if available
                result = dict(row)
                if result.get("result_path") and os.path.exists(result["result_path"]):
                    try:
                        with open(result["result_path"], 'r') as f:
                            full_result = json.load(f)
                            # Merge with database result (database fields take precedence)
                            full_result.update(result)
                            result = full_result
                    except Exception as e:
                        logger.warning(f"Could not load result file: {str(e)}")
                
                return result
            else:
                return None
            
        except Exception as e:
            logger.error(f"Error getting result by ID: {str(e)}")
            return None
    
    def search_results(self, 
                      query: str = None,
                      start_date: str = None,
                      end_date: str = None,
                      min_confidence: float = None,
                      species: str = None,
                      limit: int = 100) -> List[Dict]:
        """
        Search for results with various filters
        
        Args:
            query: Text search query
            start_date: Start date in ISO format
            end_date: End date in ISO format
            min_confidence: Minimum confidence threshold
            species: Species name to search for
            limit: Maximum number of results to return
            
        Returns:
            List of matching result dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query_parts = []
            params = []
            
            if query:
                query_parts.append("(species LIKE ? OR source LIKE ?)")
                params.extend([f"%{query}%", f"%{query}%"])
            
            if start_date:
                query_parts.append("timestamp >= ?")
                params.append(start_date)
            
            if end_date:
                query_parts.append("timestamp <= ?")
                params.append(end_date)
            
            if min_confidence is not None:
                query_parts.append("confidence >= ?")
                params.append(min_confidence)
            
            if species:
                query_parts.append("species LIKE ?")
                params.append(f"%{species}%")
            
            base_query = "SELECT * FROM detections"
            if query_parts:
                base_query += " WHERE " + " AND ".join(query_parts)
            
            base_query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(base_query, params)
            results = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching results: {str(e)}")
            return []
    
    def get_stats(self) -> Dict:
        """
        Get statistics about detection results
        
        Returns:
            Dictionary with statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Total detections
            cursor.execute('SELECT COUNT(*) FROM detections')
            stats["total_detections"] = cursor.fetchone()[0]
            
            # Bird detections
            cursor.execute('SELECT COUNT(*) FROM detections WHERE bird_detected = 1')
            stats["bird_detections"] = cursor.fetchone()[0]
            
            # Species identified
            cursor.execute('SELECT COUNT(*) FROM detections WHERE has_species = 1')
            stats["species_identified"] = cursor.fetchone()[0]
            
            # Average confidence
            cursor.execute('SELECT AVG(confidence) FROM detections WHERE bird_detected = 1')
            avg_confidence = cursor.fetchone()[0]
            stats["average_confidence"] = avg_confidence if avg_confidence else 0.0
            
            # Most common species
            cursor.execute('''
            SELECT species, COUNT(*) as count
            FROM detections
            WHERE has_species = 1
            GROUP BY species
            ORDER BY count DESC
            LIMIT 5
            ''')
            stats["top_species"] = [{"species": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # Detection counts by date
            cursor.execute('''
            SELECT substr(timestamp, 1, 10) as date, COUNT(*) as count
            FROM detections
            GROUP BY date
            ORDER BY date DESC
            LIMIT 7
            ''')
            stats["recent_counts"] = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            conn.close()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"error": str(e)} 