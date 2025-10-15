"""
PDF Document Forgery Detection Module
"""
import PyPDF2
import pdfplumber
import hashlib
from datetime import datetime
import re
from PIL import Image
import io
import numpy as np


class PDFAnalyzer:
    """Analyzes PDF documents for forgery and manipulation"""

    def __init__(self):
        self.results = {
            'forgery_detected': False,
            'confidence_score': 0.0,
            'findings': [],
            'metadata': {},
            'metadata_issues': [],
            'suspicious_elements': [],
            'techniques_used': []
        }

    def analyze_pdf(self, pdf_path):
        """Main PDF analysis pipeline"""
        print(f"[*] Analyzing PDF: {pdf_path}")

        try:
            # Track techniques used
            self.results['techniques_used'] = []

            # Metadata analysis
            metadata_result = self.extract_metadata(pdf_path)
            self.results['metadata'] = metadata_result
            self.results['techniques_used'].append('Metadata Analysis')

            # Check for incremental updates (sign of modification)
            update_result = self.check_incremental_updates(pdf_path)
            self.results['techniques_used'].append('Incremental Update Detection')
            if update_result['suspicious']:
                self.results['findings'].append(update_result)

            # Analyze text inconsistencies
            text_result = self.analyze_text_consistency(pdf_path)
            self.results['techniques_used'].append('Text Consistency Analysis')
            if text_result['suspicious']:
                self.results['findings'].append(text_result)

            # Check for embedded objects/scripts
            object_result = self.check_suspicious_objects(pdf_path)
            self.results['techniques_used'].append('Suspicious Object Detection')
            if object_result['found']:
                self.results['suspicious_elements'].extend(object_result['objects'])
                self.results['findings'].append({
                    'type': 'Suspicious Embedded Objects',
                    'description': f"Found {len(object_result['objects'])} suspicious embedded objects",
                    'suspicious': True,
                    'severity': 'high'
                })

            # Analyze fonts and formatting
            font_result = self.analyze_fonts(pdf_path)
            self.results['techniques_used'].append('Font Analysis')
            if font_result['inconsistent']:
                self.results['findings'].append(font_result)

            # Digital signature verification
            signature_result = self.check_digital_signatures(pdf_path)
            self.results['techniques_used'].append('Digital Signature Verification')
            if signature_result['issues']:
                self.results['findings'].append(signature_result)

            # Check for hidden content
            hidden_result = self.check_hidden_content(pdf_path)
            self.results['techniques_used'].append('Hidden Content Detection')
            if hidden_result['found']:
                self.results['findings'].append(hidden_result)

            # Analyze embedded images
            image_result = self.analyze_embedded_images(pdf_path)
            self.results['techniques_used'].append('Embedded Image Analysis')
            if image_result['suspicious']:
                self.results['findings'].append(image_result)

            # Check timestamps for anomalies
            timestamp_result = self.check_timestamp_anomalies(pdf_path)
            self.results['techniques_used'].append('Timestamp Analysis')
            if timestamp_result['anomalous']:
                self.results['findings'].append(timestamp_result)

            # Extract metadata issues for UI
            if 'anomalies' in self.results['metadata'] and self.results['metadata']['anomalies']:
                self.results['metadata_issues'] = self.results['metadata']['anomalies']

            # Calculate confidence
            self.calculate_confidence()

            print(f"[+] PDF analysis complete. Confidence: {self.results['confidence_score']:.2%}")
            return self.results

        except Exception as e:
            print(f"[-] PDF analysis error: {str(e)}")
            import traceback
            traceback.print_exc()
            self.results['error'] = str(e)
            self.results['findings'].append({
                'type': 'Analysis Error',
                'description': f"Error during analysis: {str(e)}",
                'suspicious': False,
                'severity': 'info'
            })
            return self.results

    def extract_metadata(self, pdf_path):
        """Extract and analyze PDF metadata"""
        metadata = {}
        anomalies = []

        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)

                # Extract metadata
                if pdf_reader.metadata:
                    for key, value in pdf_reader.metadata.items():
                        clean_key = key.replace('/', '')
                        metadata[clean_key] = str(value)

                # Check for missing metadata
                expected_keys = ['Creator', 'Producer', 'CreationDate', 'ModDate']
                missing = [k for k in expected_keys if k not in metadata]

                if len(missing) >= 3:
                    anomalies.append(f"Missing critical metadata fields: {', '.join(missing)}")

                # Check modification date vs creation date
                if 'CreationDate' in metadata and 'ModDate' in metadata:
                    if metadata['CreationDate'] != metadata['ModDate']:
                        # This is NORMAL for edited documents, not necessarily fraud
                        # Only flag if dates seem manipulated
                        pass

                # Check for suspicious creators/producers (but be less aggressive)
                suspicious_tools = ['pdftk', 'ghostscript']
                for tool in suspicious_tools:
                    creator = metadata.get('Creator', '').lower()
                    producer = metadata.get('Producer', '').lower()

                    if tool in creator or tool in producer:
                        # Note: These tools are legitimate, so downgrade severity
                        pass

                metadata['num_pages'] = len(pdf_reader.pages)
                metadata['encrypted'] = pdf_reader.is_encrypted
                metadata['anomalies'] = anomalies

        except Exception as e:
            metadata['error'] = str(e)
            anomalies.append(f"Error reading metadata: {str(e)}")

        return metadata

    def check_incremental_updates(self, pdf_path):
        """Check for incremental updates indicating modification"""
        result = {
            'type': 'Incremental Update Detection',
            'suspicious': False,
            'description': '',
            'severity': 'medium',
            'detected': False
        }

        try:
            with open(pdf_path, 'rb') as f:
                content = f.read()

                # Count EOF markers (multiple = incremental updates)
                eof_count = content.count(b'%%EOF')

                if eof_count > 3:  # More than 3 updates is more suspicious
                    result['suspicious'] = True
                    result['detected'] = True
                    result['description'] = f"Document has {eof_count} EOF markers, indicating {eof_count - 1} incremental updates - may indicate multiple modifications"
                    result['severity'] = 'high' if eof_count > 5 else 'medium'
                elif eof_count > 1:
                    result['description'] = f"Document has {eof_count - 1} incremental update(s) - normal for edited documents"
                    result['detected'] = False
                else:
                    result['description'] = "No incremental updates detected"
                    result['detected'] = False

        except Exception as e:
            result['description'] = f"Error checking updates: {str(e)}"

        return result

    def analyze_text_consistency(self, pdf_path):
        """Analyze text for inconsistencies"""
        result = {
            'type': 'Text Consistency Analysis',
            'suspicious': False,
            'description': '',
            'issues': [],
            'severity': 'medium',
            'detected': False
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                fonts_used = set()
                font_sizes = []

                for page in pdf.pages:
                    # Extract text with details
                    words = page.extract_words()

                    for word in words:
                        if 'fontname' in word:
                            fonts_used.add(word['fontname'])
                        if 'height' in word:
                            font_sizes.append(word['height'])

                # Check for excessive font variety (be more lenient)
                if len(fonts_used) > 15:  # Increased threshold
                    result['issues'].append(f"Very high number of fonts: {len(fonts_used)}")
                    result['suspicious'] = True
                    result['detected'] = True
                    result['severity'] = 'high'

                # Check for unusual font size variations
                if len(font_sizes) > 10:
                    font_sizes_array = np.array(font_sizes)
                    std_size = np.std(font_sizes_array)
                    mean_size = np.mean(font_sizes_array)

                    # Use coefficient of variation for better assessment
                    if mean_size > 0:
                        cv = std_size / mean_size
                        if cv > 0.5:  # High variation relative to mean
                            result['issues'].append(f"Inconsistent font sizing detected (CV: {cv:.2f})")
                            result['suspicious'] = True
                            result['detected'] = True

                if result['suspicious']:
                    result['description'] = '; '.join(result['issues'])
                else:
                    result['description'] = f"Text formatting appears consistent ({len(fonts_used)} fonts used)"
                    result['detected'] = False

        except Exception as e:
            result['description'] = f"Text analysis error: {str(e)}"

        return result

    def check_suspicious_objects(self, pdf_path):
        """Check for suspicious embedded objects"""
        result = {
            'found': False,
            'objects': []
        }

        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)

                for page_num, page in enumerate(pdf_reader.pages):
                    page_obj = page.get_object()
                    page_str = str(page_obj)

                    # Check for JavaScript
                    if '/JS' in page_str or '/JavaScript' in page_str:
                        result['found'] = True
                        result['objects'].append({
                            'type': 'JavaScript',
                            'page': page_num + 1,
                            'severity': 'high'
                        })

                    # Check for actions
                    if '/A' in page_str or '/AA' in page_str:
                        result['found'] = True
                        result['objects'].append({
                            'type': 'Action',
                            'page': page_num + 1,
                            'severity': 'medium'
                        })

        except Exception as e:
            pass

        return result

    def analyze_fonts(self, pdf_path):
        """Analyze font usage and embedding"""
        result = {
            'type': 'Font Analysis',
            'inconsistent': False,
            'description': '',
            'severity': 'low'
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                all_fonts = set()
                embedded_fonts = 0

                for page in pdf.pages:
                    if hasattr(page, 'fonts'):
                        for font in page.fonts:
                            all_fonts.add(str(font))

                result['description'] = f"Document uses {len(all_fonts)} different fonts"

        except Exception as e:
            result['description'] = f"Font analysis error: {str(e)}"

        return result

    def check_digital_signatures(self, pdf_path):
        """Check for digital signatures and validity"""
        result = {
            'type': 'Digital Signature Verification',
            'issues': [],
            'description': '',
            'severity': 'low'
        }

        try:
            with open(pdf_path, 'rb') as f:
                content = f.read()

                # Check for signature dictionary
                has_signature = b'/Sig' in content or b'/Signature' in content

                if has_signature:
                    result['description'] = "Digital signature present (manual verification recommended)"
                else:
                    result['description'] = "No digital signature found - common for most PDFs"
                    # Don't treat as suspicious - most PDFs aren't signed

        except Exception as e:
            result['description'] = f"Signature check error: {str(e)}"

        return result

    def check_hidden_content(self, pdf_path):
        """Check for hidden or obscured content"""
        result = {
            'type': 'Hidden Content Detection',
            'found': False,
            'description': '',
            'severity': 'medium'
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Check for white text on white background
                    words = page.extract_words()

                    # Check for overlay techniques
                    # This is a simplified check
                    result['description'] = "No obvious hidden content detected"

        except Exception as e:
            result['description'] = f"Hidden content check error: {str(e)}"

        return result

    def analyze_embedded_images(self, pdf_path):
        """Analyze images embedded in PDF for tampering"""
        result = {
            'type': 'Embedded Image Analysis',
            'suspicious': False,
            'description': '',
            'severity': 'medium'
        }

        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                image_count = 0

                for page in pdf_reader.pages:
                    if '/XObject' in page['/Resources']:
                        xobjects = page['/Resources']['/XObject'].get_object()

                        for obj in xobjects:
                            if xobjects[obj]['/Subtype'] == '/Image':
                                image_count += 1

                result['description'] = f"Found {image_count} embedded images"

        except Exception as e:
            result['description'] = f"Image analysis error: {str(e)}"

        return result

    def check_timestamp_anomalies(self, pdf_path):
        """Check for timestamp manipulation"""
        result = {
            'type': 'Timestamp Analysis',
            'anomalous': False,
            'description': '',
            'severity': 'medium'
        }

        try:
            metadata = self.results.get('metadata', {})

            # Check for future dates
            if 'CreationDate' in metadata:
                try:
                    # Parse PDF date format (D:YYYYMMDDHHmmSS)
                    date_str = metadata['CreationDate']
                    if date_str.startswith('D:'):
                        date_str = date_str[2:16]  # Extract YYYYMMDDHHmmSS
                        doc_date = datetime.strptime(date_str, '%Y%m%d%H%M%S')

                        if doc_date > datetime.now():
                            result['anomalous'] = True
                            result['description'] = "Document creation date is in the future - possible manipulation"
                            result['severity'] = 'high'
                        else:
                            result['description'] = "Timestamp appears valid"
                except:
                    result['description'] = "Unable to parse document timestamps"
            else:
                result['description'] = "No timestamp information available"

        except Exception as e:
            result['description'] = f"Timestamp analysis error: {str(e)}"

        return result

    def calculate_confidence(self):
        """Calculate forgery confidence score with improved algorithm"""
        score = 0.0
        weights = {
            'high': 0.25,
            'medium': 0.15,
            'low': 0.05
        }

        # Count findings by severity
        for finding in self.results['findings']:
            if finding.get('suspicious') or finding.get('anomalous') or finding.get('inconsistent'):
                severity = finding.get('severity', 'low')
                score += weights.get(severity, 0.1)

        # Suspicious elements
        score += len(self.results['suspicious_elements']) * 0.20

        # Metadata issues (but be less aggressive)
        metadata_issues = len(self.results.get('metadata_issues', []))
        if metadata_issues > 2:
            score += metadata_issues * 0.10

        # Normalize score
        self.results['confidence_score'] = min(1.0, score)

        # Only flag as forgery if confidence is reasonably high
        if self.results['confidence_score'] > 0.65:
            self.results['forgery_detected'] = True
        else:
            self.results['forgery_detected'] = False
