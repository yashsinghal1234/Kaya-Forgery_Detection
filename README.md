# Kaya - AI Forgery Detection Agent

A comprehensive AI-powered system for detecting fraud, tampering, and forgery in images, PDF documents and Code Analysis (to catch AI generated code).

## 🎯 Features

### Image Fraud Detection
- **Error Level Analysis (ELA)** - Detects compression inconsistencies
- **Copy-Move Forgery Detection** - Identifies duplicated regions
- **Metadata Analysis** - Examines EXIF data for manipulation
- **Noise Pattern Analysis** - Detects inconsistent noise patterns
- **Double JPEG Detection** - Identifies multiple compression cycles
- **Splicing Detection** - Finds lighting and edge inconsistencies
- **AI-Generated Detection** - Identifies artificially generated images
- **Frequency Domain Analysis** - FFT-based manipulation detection

### PDF Document Analysis
- **Metadata Examination** - Analyzes document properties
- **Incremental Update Detection** - Identifies document modifications
- **Text Consistency Analysis** - Checks for formatting anomalies
- **Suspicious Object Detection** - Finds embedded scripts/actions
- **Font Analysis** - Examines font usage patterns
- **Digital Signature Verification** - Validates document signatures

### Reporting
- Comprehensive PDF reports with detailed findings
- Visual confidence scoring
- Risk level assessment
- Actionable recommendations
- Professional formatting

## 📊 Code Analysis

### Architecture Overview

**Design Pattern:** MVC (Model-View-Controller)
- **Model:** Detection algorithms and analyzers
- **View:** Flask templates and web interface
- **Controller:** Flask routes and request handlers

### Core Components

#### 1. **app.py** - Flask Application (Main Controller)
- **Lines of Code:** ~200
- **Complexity:** Medium
- **Key Functions:**
  - `upload_file()` - File upload handler with validation
  - `get_results()` - Result retrieval and serialization
  - `download_report()` - Report download endpoint
  - `api_status()` - Health check endpoint

**Technical Highlights:**
- Secure file handling with `werkzeug.utils.secure_filename`
- Session-based caching for analysis results
- RESTful API design
- Error handling with proper HTTP status codes
- File type detection and validation
- Timestamp-based unique filename generation

#### 2. **image_tampering_detector.py** - Image Analysis Engine
- **Estimated Lines:** ~800-1000
- **Complexity:** High
- **Detection Algorithms:**

1. **Error Level Analysis (ELA)**
   - Compares original vs re-compressed image
   - Detects inconsistent compression artifacts
   - Algorithm: JPEG re-compression at quality 90

2. **Copy-Move Forgery Detection**
   - Uses SIFT (Scale-Invariant Feature Transform)
   - FLANN-based feature matching
   - DBSCAN clustering for region detection
   - Threshold: 80% similarity match

3. **Metadata Analysis**
   - EXIF data extraction using `piexif` and `exifread`
   - Timestamp inconsistency detection
   - Software modification tracking
   - GPS data validation

4. **Noise Pattern Analysis**
   - Statistical noise computation
   - Local Binary Pattern (LBP) analysis
   - Region-based noise variance comparison
   - Detects splicing through noise inconsistencies

5. **Double JPEG Detection**
   - DCT (Discrete Cosine Transform) coefficient analysis
   - Histogram periodicity detection
   - Multiple compression artifact identification

6. **Splicing Detection**
   - Canny edge detection
   - Lighting inconsistency analysis
   - Color distribution examination
   - Shadow direction validation

7. **AI-Generated Detection**
   - Perceptual hash comparison
   - Texture smoothness analysis
   - Unnatural pattern detection
   - Statistical regularity checks

8. **Frequency Domain Analysis**
   - Fast Fourier Transform (FFT)
   - High-frequency component analysis
   - Periodic pattern detection

#### 3. **pdf_analyzer.py** - PDF Forensics Module
- **Estimated Lines:** ~400-600
- **Complexity:** Medium-High
- **Analysis Methods:**
  - Binary structure parsing
  - Incremental update detection
  - Object stream analysis
  - JavaScript/action detection
  - Signature validation

#### 4. **report_generator.py** - Report Creation System
- **Estimated Lines:** ~300-500
- **Complexity:** Medium
- **Features:**
  - PDF generation using ReportLab
  - Visual confidence meters
  - Color-coded risk levels
  - Detailed finding tables
  - Professional formatting

### Code Quality Metrics

**Modularity:**
- 4 main modules with clear separation of concerns
- Each module handles specific functionality
- Low coupling, high cohesion

**Error Handling:**
- Try-catch blocks for file operations
- Graceful degradation on analysis failures
- User-friendly error messages
- Logging for debugging

**Security:**
- File type whitelist validation
- Size limit enforcement (16MB default)
- Secure filename sanitization
- No external data transmission
- Temporary file cleanup

**Performance:**
- Caching mechanism for results
- Efficient numpy array operations
- Optimized image processing pipelines
- Lazy loading of analysis modules

### Algorithm Complexity

| Algorithm | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| ELA | O(n) | O(n) |
| SIFT Detection | O(n log n) | O(k) where k = keypoints |
| DBSCAN Clustering | O(n²) | O(n) |
| FFT Analysis | O(n log n) | O(n) |
| Noise Analysis | O(n) | O(n) |
| Metadata Parsing | O(m) | O(m) where m = metadata fields |

### Data Flow

1. **Upload** → File validation → Secure storage
2. **Detection** → Algorithm execution → Finding aggregation
3. **Scoring** → Confidence calculation → Risk assessment
4. **Reporting** → PDF generation → Download delivery

### Configuration Management

**config.py** - Centralized Settings
- Detection thresholds per algorithm
- File size and type restrictions
- Folder path configurations
- Debug and logging settings
- Analysis technique toggles

## 📋 Requirements

- Python 3.8+
- See `requirements.txt` for all dependencies

## 🚀 Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Create necessary directories (automatically created on first run):
- `uploads/` - Temporary file storage
- `reports/` - Generated reports
- `models/` - ML models (future use)
- `temp/` - Temporary processing files

## 💻 Usage

### Start the Web Application

```bash
python app.py
```

Then open your browser to: `http://localhost:5000`

### Web Interface

1. **Upload** - Drag & drop or browse for an image/PDF
2. **Analyze** - Click "Start Analysis" button
3. **Review** - View detailed results and confidence scores
4. **Download** - Get comprehensive PDF report

### Supported File Types

**Images:**
- PNG, JPG, JPEG, BMP, TIFF, GIF

**Documents:**
- PDF

## 🧑‍💻 Code Analysis

### Coding Analysis Feature

The system now supports code analysis to detect whether uploaded code files are AI-generated or human-written. This feature is accessible via the web interface and works for Python source files. The analysis uses a combination of:
- Statistical code metrics
- Syntax and style pattern recognition
- Known AI code generation signatures
- Comparison with human coding practices

**Supported File Types:**
- .py (Python)

**How it Works:**
1. Upload a code file via the web interface.
2. The system analyzes the code using multiple techniques.
3. Results indicate whether the code is likely AI-generated or human-written, with confidence scores and detailed findings.
4. Findings are included in the downloadable report.

**Techniques Used:**
- Token frequency analysis
- Comment and docstring style checks
- Code structure and indentation patterns
- Use of common AI-generated code templates
- Statistical outlier detection

**Limitations:**
- Currently supports Python code only
- Accuracy depends on code length and style
- Results are probabilistic, not absolute

---

## 🛠️ Libraries and Tech Stack

**Core Libraries:**
- OpenCV, PIL, scikit-image, NumPy, SciPy, imagehash, piexif, exifread, scikit-learn
- Flask (web framework)
- ReportLab (PDF generation)
- Standard Python libraries (os, json, datetime, etc.)

**Tech Stack:**
- Python 3.x
- Flask (backend & web server)
- HTML/CSS/JS (frontend)
- Windows OS

---

...existing code...

