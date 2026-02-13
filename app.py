"""
AI Fraud Detection Agent - Main Application
Web interface for uploading and analyzing documents for fraud detection
"""
import os
import sys


def _maybe_reexec_with_venv():
    """Ensure app.py runs in the local venv when available."""
    venv_python = os.path.join(
        os.path.dirname(__file__), ".venv312", "Scripts", "python.exe"
    )
    if not os.path.exists(venv_python):
        return

    already = os.environ.get("KAYA_VENV_REEXEC") == "1"
    current = os.path.abspath(sys.executable).lower()
    target = os.path.abspath(venv_python).lower()
    if not already and current != target:
        os.environ["KAYA_VENV_REEXEC"] = "1"
        os.execv(venv_python, [venv_python] + sys.argv)


_maybe_reexec_with_venv()

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import config
from image_tampering_detector import ImageTamperingDetector
from pdf_analyzer import PDFAnalyzer
from code_analyzer import CodeAnalyzer
from report_generator import ReportGenerator
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER


# Global storage for analysis results
analysis_cache = {}


def allowed_file(filename, file_type='image'):
    """Check if file extension is allowed"""
    if file_type == 'image':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'pdf':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_PDF_EXTENSIONS
    elif file_type == 'code':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_CODE_EXTENSIONS
    return False


def get_file_type(filename):
    """Determine file type from extension"""
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in config.ALLOWED_IMAGE_EXTENSIONS:
        return 'image'
    elif ext in config.ALLOWED_PDF_EXTENSIONS:
        return 'pdf'
    elif ext in config.ALLOWED_CODE_EXTENSIONS:
        return 'code'
    return None


def get_file_size_readable(size_bytes):
    """Convert bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/documentation')
def documentation():
    """Documentation page"""
    return render_template('docs.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and initiate analysis"""

    # Check if it's a code text submission or file upload
    if 'code_text' in request.form and request.form['code_text'].strip():
        # Handle code text submission
        code_text = request.form['code_text']
        language = request.form.get('language', 'auto')
        generate_report = request.form.get('generate_report', 'false').lower() == 'true'

        # Save code to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        code_filename = f"{timestamp}_code.txt"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], code_filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(code_text)

        file_size = len(code_text.encode('utf-8'))
        file_info = {
            'filename': 'Code Submission',
            'unique_filename': code_filename,
            'type': 'code',
            'size': get_file_size_readable(file_size),
            'size_bytes': file_size,
            'upload_time': datetime.now().isoformat(),
            'analysis_type': 'Code Analysis (AI Detection)',
            'language': language
        }

        try:
            print(f"[*] Starting code analysis for text submission")
            analyzer = CodeAnalyzer()
            analysis_results = analyzer.analyze_code(code_text, language)

            # Add file info to results
            analysis_results['file_info'] = file_info

            # Generate report only if requested
            if generate_report:
                report_gen = ReportGenerator(config.REPORT_FOLDER)
                report_path = report_gen.generate_report(analysis_results, file_info)
                analysis_results['report_path'] = report_path
                analysis_results['report_filename'] = os.path.basename(report_path)
            else:
                analysis_results['report_path'] = None
                analysis_results['report_filename'] = None

            # Cache results
            analysis_id = code_filename
            analysis_cache[analysis_id] = analysis_results

            return jsonify({
                'success': True,
                'analysis_id': analysis_id,
                'message': 'Code analysis completed successfully'
            })

        except Exception as e:
            print(f"[-] Error during code analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Code analysis failed: {str(e)}'}), 500

    # Handle file upload
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Check if report generation is requested
    generate_report = request.form.get('generate_report', 'false').lower() == 'true'

    # Determine file type
    file_type = get_file_type(file.filename)

    if not file_type:
        return jsonify({'error': 'Invalid file type. Please upload an image, PDF, or code file.'}), 400

    # Save file
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)

    # Get file info
    file_size = os.path.getsize(filepath)
    file_info = {
        'filename': filename,
        'unique_filename': unique_filename,
        'type': file_type,
        'size': get_file_size_readable(file_size),
        'size_bytes': file_size,
        'upload_time': datetime.now().isoformat(),
        'analysis_type': 'Image Analysis' if file_type == 'image' else ('PDF Document Analysis' if file_type == 'pdf' else 'Code Analysis (AI Detection)')
    }

    try:
        # Perform analysis based on file type
        if file_type == 'image':
            print(f"[*] Starting image analysis for: {filename}")
            detector = ImageTamperingDetector(config.ANALYSIS_CONFIG, config.THRESHOLDS)
            analysis_results = detector.analyze_image(filepath)
        elif file_type == 'pdf':
            print(f"[*] Starting PDF analysis for: {filename}")
            analyzer = PDFAnalyzer()
            analysis_results = analyzer.analyze_pdf(filepath)
        else:  # code
            print(f"[*] Starting code analysis for: {filename}")
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                code_text = f.read()
            analyzer = CodeAnalyzer()
            analysis_results = analyzer.analyze_code(code_text)

        # Add file info to results
        analysis_results['file_info'] = file_info

        # Generate report only if requested
        if generate_report:
            report_gen = ReportGenerator(config.REPORT_FOLDER)
            report_path = report_gen.generate_report(analysis_results, file_info)
            analysis_results['report_path'] = report_path
            analysis_results['report_filename'] = os.path.basename(report_path)
        else:
            analysis_results['report_path'] = None
            analysis_results['report_filename'] = None

        # Cache results
        analysis_id = unique_filename
        analysis_cache[analysis_id] = analysis_results

        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'message': 'Analysis completed successfully'
        })

    except Exception as e:
        print(f"[-] Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500


@app.route('/results/<analysis_id>')
def get_results(analysis_id):
    """Get analysis results"""

    if analysis_id not in analysis_cache:
        return jsonify({'error': 'Results not found'}), 404

    results = analysis_cache[analysis_id]

    # Determine if this is code analysis or image/pdf analysis
    file_type = results.get('file_info', {}).get('type', '')

    # For code analysis, map ai_generated to tampering_detected
    if file_type == 'code':
        tampering_detected = results.get('ai_generated', False)
    else:
        tampering_detected = results.get('tampering_detected', False) or results.get('forgery_detected', False)

    # Prepare results for JSON serialization
    clean_results = {
        'tampering_detected': tampering_detected,
        'confidence_score': results.get('confidence_score', 0.0),
        'techniques_used': results.get('techniques_used', []),
        'findings': results.get('findings', []),
        'metadata_issues': results.get('metadata_issues', []),
        'suspicious_elements': results.get('suspicious_elements', []),
        'suspicious_patterns': results.get('suspicious_patterns', []),
        'code_quality_metrics': results.get('code_quality_metrics', {}),
        'file_info': results.get('file_info', {}),
        'report_filename': results.get('report_filename', ''),
        'ai_generated': results.get('ai_generated', False),  # Include for code analysis
        'language': results.get('language', '')
    }

    return jsonify(clean_results)


@app.route('/download_report/<report_filename>')
def download_report(report_filename):
    """Download generated report"""

    report_path = os.path.join(config.REPORT_FOLDER, secure_filename(report_filename))

    if not os.path.exists(report_path):
        return jsonify({'error': 'Report not found'}), 404

    return send_file(report_path, as_attachment=True, download_name=report_filename)


@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy'}), 200


@app.route('/api/status')
def api_status():
    """API health check"""
    return jsonify({
        'status': 'online',
        'version': config.VERSION,
        'app_name': config.APP_NAME,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("=" * 60)
    print(f"  {config.APP_NAME} v{config.VERSION}")
    print("=" * 60)
    print("[*] Initializing application...")
    print(f"[*] Upload folder: {config.UPLOAD_FOLDER}")
    print(f"[*] Report folder: {config.REPORT_FOLDER}")
    print("[+] Application ready!")
    print("[*] Starting web server...")
    print(f"[*] Port: {port}")
    print("=" * 60)
    print("\nOpen your browser and go to:")
    print(f"   http://localhost:{port}")
    print("\n   or")
    print(f"   http://127.0.0.1:{port}")
    print("\n" + "=" * 60)

    app.run(debug=config.DEBUG, host='0.0.0.0', port=port)
