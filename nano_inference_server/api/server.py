"""
Flask web server for serving bird detection results.
Includes API for retrieving results, statistics, and images.
"""
import os
import json
import time
import logging
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Union
from functools import wraps
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
from flask import Flask, request, jsonify, send_file, abort, Response, render_template, url_for, redirect
from flask_cors import CORS
import threading
import datetime
import re

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import storage and image processing modules
# We'll assume these are in the right import path
from nano_inference_server.storage.result_storage import ResultStorage
from nano_inference_server.inference.model import ModelHandler


class APIServer:
    """Flask API server for bird detection results"""
    
    def __init__(self, 
                 storage: ResultStorage,
                 model: Optional[ModelHandler] = None,
                 config: Dict = None):
        """
        Initialize the API server.
        
        Args:
            storage: ResultStorage instance
            model: Optional ModelHandler instance for on-demand inference
            config: Server configuration dictionary
        """
        self.storage = storage
        self.model = model
        self.config = config or {}
        
        # Default configuration
        self.default_config = {
            "host": "0.0.0.0",
            "port": 5000,
            "debug": False,
            "access_key": None,  # API key for authentication
            "rate_limit": 100,  # Requests per minute
            "allowed_origins": ["*"],  # CORS allowed origins
            "upload_folder": os.path.join(storage.base_dir, "uploads"),
            "max_content_length": 16 * 1024 * 1024,  # 16 MB
            "templates_folder": os.path.join(os.path.dirname(__file__), "templates"),
            "use_v0_ui": True,  # Enable the V0.dev UI
            "v0_ui_primary": False  # Use V0.dev UI as the primary interface
        }
        
        # Merge provided config with defaults
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
        
        # Create upload folder if it doesn't exist
        if not os.path.exists(self.config["upload_folder"]):
            os.makedirs(self.config["upload_folder"], exist_ok=True)
        
        # Initialize Flask app
        self.app = Flask("bird_detection_api", 
                         template_folder=self.config["templates_folder"])
        
        # Configure app
        self.app.config["UPLOAD_FOLDER"] = self.config["upload_folder"]
        self.app.config["MAX_CONTENT_LENGTH"] = self.config["max_content_length"]
        
        # Setup CORS
        CORS(self.app, resources={r"/api/*": {"origins": self.config["allowed_origins"]}})
        
        # Rate limiting data
        self.request_counts = {}
        
        # Setup routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        # API routes
        self.app.add_url_rule("/api/results", "results", self._handle_results, methods=["GET"])
        self.app.add_url_rule("/api/results/<int:result_id>", "result", self._handle_result, methods=["GET"])
        self.app.add_url_rule("/api/search", "search", self._handle_search, methods=["GET"])
        self.app.add_url_rule("/api/stats", "stats", self._handle_stats, methods=["GET"])
        self.app.add_url_rule("/api/upload", "upload", self._handle_upload, methods=["POST"])
        
        # Image serving routes (with sanitized paths)
        self.app.add_url_rule("/images/<path:filename>", "serve_image", self._serve_image, methods=["GET"])
        
        # V0.dev UI routes (if enabled)
        if self.config.get("use_v0_ui", False):
            self.app.add_url_rule("/v0", "v0_ui", self._handle_v0_ui, methods=["GET"])
            self.app.add_url_rule("/v0/<path:subpath>", "v0_ui_subpath", self._handle_v0_ui, methods=["GET"])
            
            # When V0 UI is set as primary, redirect root to /v0
            if self.config.get("v0_ui_primary", False):
                self.app.add_url_rule("/", "root_redirect", lambda: redirect("/v0"), methods=["GET"])
            else:
                # Standard web interface
                self.app.add_url_rule("/", "index", self._handle_index, methods=["GET"])
        else:
            # Standard web interface
            self.app.add_url_rule("/", "index", self._handle_index, methods=["GET"])
            
        # Standard web interface routes (always available)
        self.app.add_url_rule("/gallery", "gallery", self._handle_gallery, methods=["GET"])
        self.app.add_url_rule("/details/<int:result_id>", "details", self._handle_details, methods=["GET"])
        
        # Error handlers
        self.app.register_error_handler(404, self._handle_404)
        self.app.register_error_handler(500, self._handle_500)
    
    def _rate_limit_check(self, request):
        """Check if request exceeds rate limit"""
        if not self.config.get("rate_limit"):
            return True
        
        # Get client IP
        client_ip = request.remote_addr
        current_time = time.time()
        time_window = current_time - 60  # 1 minute window
        
        # Initialize or clean up old requests
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        # Remove old requests
        self.request_counts[client_ip] = [t for t in self.request_counts[client_ip] if t > time_window]
        
        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.config["rate_limit"]:
            return False
        
        # Add current request
        self.request_counts[client_ip].append(current_time)
        return True
    
    def _auth_required(self, f):
        """Decorator for routes that require authentication"""
        @wraps(f)
        def decorated(*args, **kwargs):
            # Check rate limit first
            if not self._rate_limit_check(request):
                return jsonify({"error": "Rate limit exceeded"}), 429
            
            # Check if authentication is required
            if not self.config.get("access_key"):
                return f(*args, **kwargs)
            
            # Check API key
            api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
            if not api_key or api_key != self.config["access_key"]:
                return jsonify({"error": "Unauthorized"}), 401
            
            return f(*args, **kwargs)
        return decorated
    
    def _sanitize_path(self, filename):
        """Sanitize a path to prevent directory traversal attacks"""
        if filename is None:
            return None
        
        # Use secure_filename for the basename
        base = secure_filename(os.path.basename(filename))
        
        # Get the directory and sanitize it (no .. or absolute paths)
        directory = os.path.dirname(filename)
        if directory:
            # Remove leading / and replace .. with _
            directory = re.sub(r'\.\.', '_', directory)
            directory = directory.lstrip('/')
            return os.path.join(directory, base)
        
        return base
    
    # API route handlers
    
    @_auth_required
    def _handle_results(self):
        """Handle GET /api/results"""
        try:
            limit = int(request.args.get("limit", 20))
            offset = int(request.args.get("offset", 0))
            
            # Add validation
            if limit <= 0 or limit > 100:
                limit = 20
            if offset < 0:
                offset = 0
            
            # Get filters
            bird_only = request.args.get("bird_only", "").lower() == "true"
            with_species = request.args.get("with_species", "").lower() == "true"
            
            # Get results
            results = self.storage.get_recent_results(
                limit=limit + offset,
                bird_only=bird_only,
                with_species=with_species
            )
            
            # Apply offset
            results = results[offset:offset + limit]
            
            # Only return essential fields for list view
            simplified = []
            for result in results:
                simplified.append({
                    "id": result["id"],
                    "timestamp": result["timestamp"],
                    "bird_detected": result["bird_detected"],
                    "bird_count": result["bird_count"],
                    "species": result["species"],
                    "confidence": result["confidence"],
                    "image_path": f"/images/{os.path.basename(result['image_path'])}",
                    "annotated_path": f"/images/{os.path.basename(result['annotated_path'])}" if result["annotated_path"] else None
                })
            
            return jsonify({
                "success": True,
                "results": simplified,
                "count": len(simplified),
                "total_count": self.storage.get_stats().get("total_detections", 0)
            })
            
        except Exception as e:
            logger.error(f"Error handling results request: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @_auth_required
    def _handle_result(self, result_id):
        """Handle GET /api/results/<result_id>"""
        try:
            result = self.storage.get_result_by_id(result_id)
            
            if not result:
                return jsonify({"error": "Result not found"}), 404
            
            # Update image paths for API
            if result.get("image_path"):
                result["image_url"] = f"/images/{os.path.basename(result['image_path'])}"
            
            if result.get("annotated_path"):
                result["annotated_url"] = f"/images/{os.path.basename(result['annotated_path'])}"
            
            return jsonify({
                "success": True,
                "result": result
            })
            
        except Exception as e:
            logger.error(f"Error handling result request: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @_auth_required
    def _handle_search(self):
        """Handle GET /api/search"""
        try:
            # Get search parameters
            query = request.args.get("q")
            start_date = request.args.get("start_date")
            end_date = request.args.get("end_date")
            species = request.args.get("species")
            
            limit = int(request.args.get("limit", 20))
            if limit <= 0 or limit > 100:
                limit = 20
            
            # Handle confidence threshold
            min_confidence = None
            if request.args.get("min_confidence"):
                try:
                    min_confidence = float(request.args.get("min_confidence"))
                except ValueError:
                    pass
            
            # Search results
            results = self.storage.search_results(
                query=query,
                start_date=start_date,
                end_date=end_date,
                min_confidence=min_confidence,
                species=species,
                limit=limit
            )
            
            # Simplify results for API
            simplified = []
            for result in results:
                simplified.append({
                    "id": result["id"],
                    "timestamp": result["timestamp"],
                    "bird_detected": result["bird_detected"],
                    "bird_count": result["bird_count"],
                    "species": result["species"],
                    "confidence": result["confidence"],
                    "image_path": f"/images/{os.path.basename(result['image_path'])}",
                    "annotated_path": f"/images/{os.path.basename(result['annotated_path'])}" if result["annotated_path"] else None
                })
            
            return jsonify({
                "success": True,
                "results": simplified,
                "count": len(simplified)
            })
            
        except Exception as e:
            logger.error(f"Error handling search request: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @_auth_required
    def _handle_stats(self):
        """Handle GET /api/stats"""
        try:
            stats = self.storage.get_stats()
            return jsonify({
                "success": True,
                "stats": stats
            })
            
        except Exception as e:
            logger.error(f"Error handling stats request: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    @_auth_required
    def _handle_upload(self):
        """Handle POST /api/upload for on-demand inference"""
        try:
            # Check if model is available
            if not self.model:
                return jsonify({"error": "On-demand inference not available"}), 400
            
            # Check for file
            if "file" not in request.files:
                return jsonify({"error": "No file provided"}), 400
            
            file = request.files["file"]
            
            # Check empty filename
            if file.filename == "":
                return jsonify({"error": "No file selected"}), 400
            
            # Check file type
            if not self._allowed_file(file.filename):
                return jsonify({"error": "File type not allowed"}), 400
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(self.app.config["UPLOAD_FOLDER"], unique_filename)
            file.save(filepath)
            
            # Run inference
            start_time = time.time()
            detections = self.model.detect(filepath)
            processing_time = time.time() - start_time
            
            # Annotate image if detections found
            annotated_path = None
            if detections:
                annotated_path = self.model.annotate_image(filepath, detections)
            
            # Save result
            metadata = {
                "source": "upload",
                "original_filename": filename,
                "user_agent": request.user_agent.string,
                "remote_addr": request.remote_addr
            }
            
            result = self.storage.save_result(
                image_path=filepath,
                detections=detections,
                annotated_path=annotated_path,
                metadata=metadata,
                processing_time=processing_time
            )
            
            # Return result
            return jsonify({
                "success": True,
                "result_id": result.get("id"),
                "detections": detections,
                "processing_time": processing_time,
                "image_url": f"/images/{os.path.basename(result['image_path'])}",
                "annotated_url": f"/images/{os.path.basename(result['annotated_path'])}" if result.get("annotated_path") else None
            })
            
        except Exception as e:
            logger.error(f"Error handling upload: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    def _serve_image(self, filename):
        """Serve an image file with sanitized path"""
        try:
            # Sanitize the filename
            safe_filename = self._sanitize_path(filename)
            
            # Construct search paths
            search_paths = [
                os.path.join(self.storage.images_dir, safe_filename),
                os.path.join(self.storage.annotated_dir, safe_filename),
                os.path.join(self.config["upload_folder"], safe_filename)
            ]
            
            # If date-based folders are used, also search in dated folders
            if self.storage.organize_by_date:
                for date_dir in os.listdir(self.storage.images_dir):
                    if os.path.isdir(os.path.join(self.storage.images_dir, date_dir)):
                        search_paths.append(os.path.join(self.storage.images_dir, date_dir, safe_filename))
                
                for date_dir in os.listdir(self.storage.annotated_dir):
                    if os.path.isdir(os.path.join(self.storage.annotated_dir, date_dir)):
                        search_paths.append(os.path.join(self.storage.annotated_dir, date_dir, safe_filename))
            
            # Find the first matching file
            for path in search_paths:
                if os.path.isfile(path) and os.access(path, os.R_OK):
                    return send_file(path)
            
            # If no file found, return 404
            abort(404)
            
        except Exception as e:
            logger.error(f"Error serving image: {str(e)}")
            abort(500)
    
    def _allowed_file(self, filename):
        """Check if file extension is allowed"""
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    # Web interface handlers
    
    def _handle_index(self):
        """Handle GET / for web interface"""
        try:
            stats = self.storage.get_stats()
            recent_results = self.storage.get_recent_results(limit=5)
            
            # Format results for template
            for result in recent_results:
                if result.get("image_path"):
                    result["image_url"] = f"/images/{os.path.basename(result['image_path'])}"
                if result.get("annotated_path"):
                    result["annotated_url"] = f"/images/{os.path.basename(result['annotated_path'])}"
            
            return render_template(
                "index.html", 
                stats=stats, 
                recent_results=recent_results,
                page="index"
            )
            
        except Exception as e:
            logger.error(f"Error handling index request: {str(e)}")
            return render_template("error.html", error=str(e))
    
    def _handle_gallery(self):
        """Handle GET /gallery for web interface"""
        try:
            # Get pagination parameters
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 12))
            
            # Validate
            if page < 1:
                page = 1
            if per_page < 1 or per_page > 50:
                per_page = 12
            
            # Calculate offset
            offset = (page - 1) * per_page
            
            # Get filters
            bird_only = request.args.get("bird_only", "").lower() == "true"
            with_species = request.args.get("with_species", "").lower() == "true"
            
            # Get results
            results = self.storage.get_recent_results(
                limit=per_page,
                bird_only=bird_only,
                with_species=with_species
            )
            
            # Get total count for pagination
            stats = self.storage.get_stats()
            total_count = stats.get("total_detections", 0)
            
            # Format results for template
            for result in results:
                if result.get("image_path"):
                    result["image_url"] = f"/images/{os.path.basename(result['image_path'])}"
                if result.get("annotated_path"):
                    result["annotated_url"] = f"/images/{os.path.basename(result['annotated_path'])}"
            
            # Calculate pagination details
            total_pages = (total_count + per_page - 1) // per_page
            has_prev = page > 1
            has_next = page < total_pages
            
            return render_template(
                "gallery.html",
                results=results,
                page=page,
                per_page=per_page,
                total_pages=total_pages,
                total_count=total_count,
                has_prev=has_prev,
                has_next=has_next,
                bird_only=bird_only,
                with_species=with_species,
                page_name="gallery"
            )
            
        except Exception as e:
            logger.error(f"Error handling gallery request: {str(e)}")
            return render_template("error.html", error=str(e))
    
    def _handle_details(self, result_id):
        """Handle GET /details/<result_id> for web interface"""
        try:
            result = self.storage.get_result_by_id(result_id)
            
            if not result:
                return render_template("error.html", error="Result not found"), 404
            
            # Format paths for template
            if result.get("image_path"):
                result["image_url"] = f"/images/{os.path.basename(result['image_path'])}"
            if result.get("annotated_path"):
                result["annotated_url"] = f"/images/{os.path.basename(result['annotated_path'])}"
            
            return render_template(
                "details.html", 
                result=result,
                page_name="details"
            )
            
        except Exception as e:
            logger.error(f"Error handling details request: {str(e)}")
            return render_template("error.html", error=str(e))
    
    def _handle_v0_ui(self, subpath=None):
        """Handle V0.dev UI requests"""
        try:
            # Path to the V0.dev UI build directory
            v0_ui_dir = os.path.join(os.path.dirname(__file__), "v0_ui", "out")
            
            # If the V0 UI hasn't been built yet, return an error page
            if not os.path.exists(v0_ui_dir):
                return render_template(
                    "error.html", 
                    error=("V0.dev UI has not been built yet. "
                          "Please run 'cd nano_inference_server/api/v0_ui && npm run build' first.")
                )
                
            # Determine which file to serve
            if subpath is None:
                # Serve the index.html file for the root path
                filepath = os.path.join(v0_ui_dir, "index.html")
            else:
                # Sanitize the subpath to prevent directory traversal
                safe_subpath = self._sanitize_path(subpath)
                filepath = os.path.join(v0_ui_dir, safe_subpath)
                
                # If the path doesn't exist, try adding .html
                if not os.path.exists(filepath) and not os.path.isdir(filepath):
                    if not filepath.endswith(".html"):
                        html_filepath = filepath + ".html"
                        if os.path.exists(html_filepath):
                            filepath = html_filepath
                
                # If it's a directory, look for index.html
                if os.path.isdir(filepath):
                    filepath = os.path.join(filepath, "index.html")
            
            # Check if the file exists and is readable
            if os.path.isfile(filepath) and os.access(filepath, os.R_OK):
                # Determine the correct MIME type
                mimetype, _ = mimetypes.guess_type(filepath)
                return send_file(filepath, mimetype=mimetype)
            
            # If the file doesn't exist, return a 404 error
            return self._handle_404(None)
            
        except Exception as e:
            logger.error(f"Error serving V0.dev UI: {str(e)}")
            return self._handle_500(e)
    
    # Error handlers
    
    def _handle_404(self, error):
        """Handle 404 errors"""
        if request.path.startswith("/api/"):
            return jsonify({"error": "Not found"}), 404
        return render_template("error.html", error="Page not found"), 404
    
    def _handle_500(self, error):
        """Handle 500 errors"""
        if request.path.startswith("/api/"):
            return jsonify({"error": "Server error"}), 500
        return render_template("error.html", error="Server error"), 500
    
    def run(self, **kwargs):
        """Run the Flask server"""
        # Override config with kwargs
        run_config = {
            "host": self.config["host"],
            "port": self.config["port"],
            "debug": self.config["debug"]
        }
        run_config.update(kwargs)
        
        logger.info(f"Starting API server on {run_config['host']}:{run_config['port']}")
        self.app.run(**run_config)


# Example usage
if __name__ == "__main__":
    storage = ResultStorage(base_dir="./data")
    try:
        model = ModelHandler(model_path="./models/model.pb")
    except Exception as e:
        logger.warning(f"Could not load model: {str(e)}")
        model = None
    
    config = {
        "port": 5050,
        "debug": True,
        "access_key": None  # No authentication in development
    }
    
    server = APIServer(storage=storage, model=model, config=config)
    server.run() 