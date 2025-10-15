# Quick Installation Guide

## Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

## Step 2: Run the Application
```bash
python app.py
```

## Step 3: Open Browser
Navigate to: http://localhost:5000

## Quick Test
1. Upload any image (JPG/PNG) or PDF document
2. Click "Start Analysis"
3. Review the fraud detection results
4. Download the comprehensive PDF report

## System Capabilities

### ✅ What This System Detects:

**Image Tampering:**
- Photoshopped/edited regions
- Copy-pasted areas
- Compression artifacts
- Metadata manipulation
- Noise inconsistencies
- Lighting mismatches

**PDF Forgery:**
- Modified documents
- Stripped metadata
- Embedded malicious scripts
- Font inconsistencies
- Incremental modifications

### 🎯 High Accuracy Features:
- 6+ detection algorithms for images
- Multiple verification techniques
- Statistical analysis
- Metadata forensics
- Comprehensive reporting

### 📊 Output:
- Real-time web interface
- Confidence score (0-100%)
- Risk level assessment
- Detailed findings per technique
- Professional PDF report

## Troubleshooting

**If you get import errors:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

**If port 5000 is busy:**
Edit `app.py` and change the port number in the last line.

**For Windows:**
Just double-click `start.bat`
@echo off
echo ================================================
echo   AI Fraud Detection Agent - Quick Start
echo ================================================
echo.
echo [1/3] Installing Python dependencies...
echo.
pip install -r requirements.txt
echo.
echo [2/3] Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "reports" mkdir reports
if not exist "models" mkdir models
if not exist "temp" mkdir temp
if not exist "templates" mkdir templates
echo.
echo [3/3] Starting application...
echo.
echo ================================================
echo   Application will start on http://localhost:5000
echo   Press Ctrl+C to stop the server
echo ================================================
echo.
python app.py
pause

