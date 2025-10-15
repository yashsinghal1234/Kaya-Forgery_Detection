"""
Configuration settings for Fraud Detection AI Agent
"""
import os

# Application Settings
APP_NAME = "AI Fraud Detection Agent"
VERSION = "1.0.0"
DEBUG = True
SECRET_KEY = os.urandom(24)

# Upload Settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif'}
ALLOWED_PDF_EXTENSIONS = {'pdf'}
ALLOWED_CODE_EXTENSIONS = {'py', 'js', 'java', 'cpp', 'c', 'cs', 'rb', 'go', 'php', 'ts', 'jsx', 'tsx', 'html', 'css', 'sql', 'sh', 'txt'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
MAX_CODE_SIZE = 5 * 1024 * 1024  # 5MB for code files

# Report Settings
REPORT_FOLDER = 'reports'
REPORT_FORMAT = 'pdf'

# Detection Thresholds (LOWERED for higher sensitivity)
THRESHOLDS = {
    'ela_threshold': 15,  # Lowered from 25 - more sensitive to compression differences
    'metadata_anomaly_score': 0.3,  # Lowered from 0.7 - flag more metadata issues
    'forgery_confidence': 0.35,  # Lowered from 0.75 - flag suspicious images earlier
    'copy_move_threshold': 0.6,  # Lowered from 0.85 - detect more copy-move
    'noise_inconsistency': 0.4,  # Lowered from 0.6 - more sensitive to noise patterns
    'ai_generated_threshold': 0.5  # New - for AI-generated image detection
}

# Model Paths
MODEL_PATHS = {
    'tampering_model': 'models/tampering_detector.h5',
    'forgery_model': 'models/forgery_detector.pth'
}

# Analysis Settings
ANALYSIS_CONFIG = {
    'enable_ela': True,
    'enable_metadata': True,
    'enable_copy_move': True,
    'enable_noise_analysis': True,
    'enable_deep_learning': True,
    'enable_double_jpeg': True
}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)
os.makedirs('models', exist_ok=True)
os.makedirs('temp', exist_ok=True)
