"""
Advanced Image Tampering Detection Module
Implements multiple techniques for high accuracy fraud detection
"""
import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import piexif
import exifread
from scipy import ndimage
from sklearn.cluster import DBSCAN
import imagehash
from datetime import datetime
import json


class ImageTamperingDetector:
    """Comprehensive image tampering detection using multiple techniques"""

    def __init__(self, config, thresholds=None):
        self.config = config
        self.thresholds = thresholds if thresholds else {}
        self.results = {
            'tampering_detected': False,
            'confidence_score': 0.0,
            'techniques_used': [],
            'findings': [],
            'metadata_issues': [],
            'suspicious_regions': []
        }

    def analyze_image(self, image_path):
        """Main analysis pipeline combining multiple detection techniques"""
        print(f"[*] Starting comprehensive analysis on: {image_path}")

        try:
            # Load image
            img_pil = Image.open(image_path)
            img_cv = cv2.imread(image_path)

            # Technique 1: Error Level Analysis (ELA)
            if self.config.get('enable_ela', True):
                ela_result = self.error_level_analysis(image_path)
                self.results['techniques_used'].append('Error Level Analysis')
                if ela_result['suspicious']:
                    self.results['findings'].append(ela_result)

            # Technique 2: Metadata Analysis
            if self.config.get('enable_metadata', True):
                metadata_result = self.analyze_metadata(image_path)
                self.results['techniques_used'].append('Metadata Analysis')
                if metadata_result['anomalies']:
                    self.results['metadata_issues'].extend(metadata_result['anomalies'])

            # Technique 3: Copy-Move Forgery Detection
            if self.config.get('enable_copy_move', True):
                copy_move_result = self.detect_copy_move(img_cv)
                self.results['techniques_used'].append('Copy-Move Detection')
                if copy_move_result['detected']:
                    self.results['findings'].append(copy_move_result)

            # Technique 4: Noise Inconsistency Analysis
            if self.config.get('enable_noise_analysis', True):
                noise_result = self.analyze_noise_patterns(img_cv)
                self.results['techniques_used'].append('Noise Analysis')
                if noise_result['inconsistent']:
                    self.results['findings'].append(noise_result)

            # Technique 5: Double JPEG Compression Detection
            if self.config.get('enable_double_jpeg', True):
                jpeg_result = self.detect_double_jpeg(image_path)
                self.results['techniques_used'].append('JPEG Compression Analysis')
                if jpeg_result['suspicious']:
                    self.results['findings'].append(jpeg_result)

            # Technique 6: Splicing Detection
            splicing_result = self.detect_splicing(img_cv)
            self.results['techniques_used'].append('Splicing Detection')
            if splicing_result['detected']:
                self.results['findings'].append(splicing_result)

            # NEW Technique 7: AI-Generated Image Detection
            ai_result = self.detect_ai_generated(img_cv, image_path)
            self.results['techniques_used'].append('AI-Generated Detection')
            if ai_result['detected']:
                self.results['findings'].append(ai_result)

            # NEW Technique 8: Frequency Domain Analysis
            freq_result = self.analyze_frequency_domain(img_cv)
            self.results['techniques_used'].append('Frequency Domain Analysis')
            if freq_result['suspicious']:
                self.results['findings'].append(freq_result)

            # Calculate overall confidence
            self.calculate_confidence()

            print(f"[+] Analysis complete. Confidence: {self.results['confidence_score']:.2%}")
            return self.results

        except Exception as e:
            print(f"[-] Error during analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            self.results['error'] = str(e)
            return self.results

    def error_level_analysis(self, image_path):
        """ELA - Detects areas with different compression levels"""
        result = {
            'technique': 'Error Level Analysis',
            'suspicious': False,
            'score': 0.0,
            'description': '',
            'regions': []
        }

        try:
            # Open and resave at known quality
            img = Image.open(image_path)

            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Save at quality 90
            temp_path = 'temp/ela_temp.jpg'
            img.save(temp_path, 'JPEG', quality=90)

            # Load both images
            original = cv2.imread(image_path)
            resaved = cv2.imread(temp_path)

            if original is None or resaved is None:
                return result

            # Ensure same size
            if original.shape != resaved.shape:
                resaved = cv2.resize(resaved, (original.shape[1], original.shape[0]))

            # Calculate difference
            ela_image = cv2.absdiff(original, resaved)

            # Convert to grayscale and enhance
            ela_gray = cv2.cvtColor(ela_image, cv2.COLOR_BGR2GRAY)
            ela_enhanced = cv2.equalizeHist(ela_gray)

            # Calculate statistics
            mean_diff = np.mean(ela_enhanced)
            max_diff = np.max(ela_enhanced)
            std_diff = np.std(ela_enhanced)

            # Find suspicious regions (high error areas)
            threshold = self.thresholds.get('ela_threshold', 25)
            _, binary = cv2.threshold(ela_enhanced, threshold, 255, cv2.THRESH_BINARY)

            # Find contours of suspicious areas
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            significant_regions = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Filter small noise
                    x, y, w, h = cv2.boundingRect(contour)
                    significant_regions.append({
                        'x': int(x), 'y': int(y),
                        'width': int(w), 'height': int(h),
                        'area': int(area)
                    })

            # Determine if suspicious
            if max_diff > 30 and len(significant_regions) > 0:
                result['suspicious'] = True
                result['score'] = min(1.0, max_diff / 100.0)
                result['regions'] = significant_regions
                result['description'] = f"Detected {len(significant_regions)} regions with inconsistent compression levels. Max difference: {max_diff:.2f}"
            else:
                result['description'] = "No significant compression anomalies detected"

            # Save ELA visualization
            cv2.imwrite('temp/ela_result.jpg', ela_enhanced)

        except Exception as e:
            result['description'] = f"ELA analysis failed: {str(e)}"

        return result

    def analyze_metadata(self, image_path):
        """Analyze image metadata for tampering signs"""
        result = {
            'technique': 'Metadata Analysis',
            'anomalies': [],
            'metadata': {},
            'score': 0.0
        }

        try:
            # Extract EXIF data
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)

            metadata = {}
            anomaly_count = 0

            # Check for missing expected metadata
            expected_tags = ['Image Make', 'Image Model', 'Image DateTime',
                           'EXIF DateTimeOriginal', 'Image Software']

            missing_tags = []
            for tag in expected_tags:
                if tag in tags:
                    metadata[tag] = str(tags[tag])
                else:
                    missing_tags.append(tag)

            if len(missing_tags) > 3:
                result['anomalies'].append({
                    'type': 'Missing Metadata',
                    'severity': 'medium',
                    'description': f"Missing {len(missing_tags)} expected EXIF tags"
                })
                anomaly_count += 1

            # Check for software editing indicators
            if 'Image Software' in tags:
                software = str(tags['Image Software']).lower()
                editing_tools = ['photoshop', 'gimp', 'paint.net', 'lightroom',
                               'pixlr', 'affinity', 'corel']

                for tool in editing_tools:
                    if tool in software:
                        result['anomalies'].append({
                            'type': 'Editing Software Detected',
                            'severity': 'high',
                            'description': f"Image edited with: {software}",
                            'tool': software
                        })
                        anomaly_count += 1
                        break

            # Check for date inconsistencies
            if 'Image DateTime' in tags and 'EXIF DateTimeOriginal' in tags:
                try:
                    datetime1 = tags['Image DateTime']
                    datetime2 = tags['EXIF DateTimeOriginal']

                    if str(datetime1) != str(datetime2):
                        result['anomalies'].append({
                            'type': 'Date Inconsistency',
                            'severity': 'medium',
                            'description': 'DateTime and DateTimeOriginal do not match'
                        })
                        anomaly_count += 1
                except:
                    pass

            # Check for GPS data manipulation
            gps_tags = [tag for tag in tags.keys() if 'GPS' in tag]
            if len(gps_tags) > 0:
                metadata['GPS_present'] = True

            # Try to detect stripped metadata
            img = Image.open(image_path)
            try:
                exif_dict = piexif.load(img.info.get('exif', b''))
                if not exif_dict or all(not v for v in exif_dict.values()):
                    result['anomalies'].append({
                        'type': 'Stripped Metadata',
                        'severity': 'high',
                        'description': 'EXIF data appears to be stripped or missing'
                    })
                    anomaly_count += 1
            except:
                result['anomalies'].append({
                    'type': 'Invalid Metadata',
                    'severity': 'high',
                    'description': 'EXIF data is corrupted or invalid'
                })
                anomaly_count += 1

            result['metadata'] = metadata
            result['score'] = min(1.0, anomaly_count * 0.25)

        except Exception as e:
            result['anomalies'].append({
                'type': 'Error',
                'severity': 'low',
                'description': f"Metadata extraction error: {str(e)}"
            })

        return result

    def detect_copy_move(self, img):
        """Detect copy-move forgery using feature matching"""
        result = {
            'technique': 'Copy-Move Forgery Detection',
            'detected': False,
            'score': 0.0,
            'matches': 0,
            'description': ''
        }

        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Use SIFT for feature detection
            sift = cv2.SIFT_create()
            keypoints, descriptors = sift.detectAndCompute(gray, None)

            if descriptors is None or len(keypoints) < 10:
                result['description'] = "Insufficient features for copy-move detection"
                return result

            # Match features with themselves
            bf = cv2.BFMatcher()
            matches = bf.knnMatch(descriptors, descriptors, k=2)

            # Find similar regions (excluding self-matches)
            similar_matches = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance and m.queryIdx != m.trainIdx:
                    pt1 = keypoints[m.queryIdx].pt
                    pt2 = keypoints[m.trainIdx].pt

                    # Calculate distance between matched points
                    distance = np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)

                    # If points are far enough apart but similar, suspicious
                    if distance > 50:
                        similar_matches.append((pt1, pt2, distance))

            if len(similar_matches) > 20:
                result['detected'] = True
                result['matches'] = len(similar_matches)
                result['score'] = min(1.0, len(similar_matches) / 100.0)
                result['description'] = f"Detected {len(similar_matches)} suspicious feature matches suggesting copy-move forgery"
            else:
                result['description'] = "No copy-move forgery detected"

        except Exception as e:
            result['description'] = f"Copy-move detection error: {str(e)}"

        return result

    def analyze_noise_patterns(self, img):
        """Analyze noise inconsistencies that indicate tampering"""
        result = {
            'technique': 'Noise Pattern Analysis',
            'inconsistent': False,
            'score': 0.0,
            'description': ''
        }

        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Apply median filter to estimate noise
            median = cv2.medianBlur(gray, 5)
            noise = cv2.absdiff(gray, median)

            # Divide image into blocks
            h, w = noise.shape
            block_size = 64
            noise_variances = []

            for i in range(0, h - block_size, block_size):
                for j in range(0, w - block_size, block_size):
                    block = noise[i:i+block_size, j:j+block_size]
                    variance = np.var(block)
                    noise_variances.append(variance)

            if len(noise_variances) > 0:
                # Calculate statistics
                mean_var = np.mean(noise_variances)
                std_var = np.std(noise_variances)

                # High standard deviation suggests inconsistent noise
                if std_var > mean_var * 0.5:
                    result['inconsistent'] = True
                    result['score'] = min(1.0, std_var / (mean_var + 1e-6) * 0.3)
                    result['description'] = f"Inconsistent noise patterns detected. STD: {std_var:.2f}, Mean: {mean_var:.2f}"
                else:
                    result['description'] = "Noise patterns appear consistent"

        except Exception as e:
            result['description'] = f"Noise analysis error: {str(e)}"

        return result

    def detect_double_jpeg(self, image_path):
        """Detect double JPEG compression artifacts"""
        result = {
            'technique': 'Double JPEG Detection',
            'suspicious': False,
            'score': 0.0,
            'description': ''
        }

        try:
            img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

            # Compute DCT
            dct = cv2.dct(np.float32(img))

            # Analyze DCT coefficient histogram
            hist, bins = np.histogram(dct.flatten(), bins=100)

            # Look for periodic peaks in histogram (sign of double compression)
            peaks = []
            for i in range(1, len(hist) - 1):
                if hist[i] > hist[i-1] and hist[i] > hist[i+1]:
                    peaks.append(i)

            # If we find periodic peaks, it suggests double compression
            if len(peaks) > 5:
                # Check for periodicity
                peak_distances = np.diff(peaks)
                if len(peak_distances) > 0:
                    std_distance = np.std(peak_distances)
                    if std_distance < 5:  # Relatively uniform spacing
                        result['suspicious'] = True
                        result['score'] = 0.7
                        result['description'] = f"Double JPEG compression detected. Found {len(peaks)} periodic peaks"

            if not result['suspicious']:
                result['description'] = "No double JPEG compression detected"

        except Exception as e:
            result['description'] = f"JPEG analysis error: {str(e)}"

        return result

    def detect_splicing(self, img):
        """Detect image splicing using edge and lighting analysis"""
        result = {
            'technique': 'Splicing Detection',
            'detected': False,
            'score': 0.0,
            'description': ''
        }

        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l_channel = lab[:,:,0]

            # Detect edges
            edges = cv2.Canny(l_channel, 100, 200)

            # Analyze lighting consistency
            h, w = l_channel.shape
            block_size = 32
            lighting_values = []

            for i in range(0, h - block_size, block_size):
                for j in range(0, w - block_size, block_size):
                    block = l_channel[i:i+block_size, j:j+block_size]
                    mean_light = np.mean(block)
                    lighting_values.append(mean_light)

            if len(lighting_values) > 0:
                std_lighting = np.std(lighting_values)
                mean_lighting = np.mean(lighting_values)

                # High variation suggests potential splicing
                coefficient_of_variation = std_lighting / (mean_lighting + 1e-6)

                if coefficient_of_variation > 0.3:
                    result['detected'] = True
                    result['score'] = min(1.0, coefficient_of_variation)
                    result['description'] = f"Lighting inconsistencies detected (CV: {coefficient_of_variation:.3f})"
                else:
                    result['description'] = "Lighting appears consistent"

        except Exception as e:
            result['description'] = f"Splicing detection error: {str(e)}"

        return result

    def detect_ai_generated(self, img, image_path):
        """Detect AI-generated images using pattern analysis"""
        result = {
            'technique': 'AI-Generated Image Detection',
            'detected': False,
            'score': 0.0,
            'description': '',
            'indicators': []
        }

        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # AI-generated images often have:
            # 1. Unnaturally smooth textures
            # 2. Perfect symmetry in unnatural places
            # 3. Lack of natural noise
            # 4. Missing or stripped EXIF data

            # Check for unnatural smoothness
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            variance = laplacian.var()

            if variance < 50:  # Very smooth = likely AI
                result['indicators'].append('Unnaturally smooth textures')
                result['score'] += 0.3

            # Check for perfect patterns (AI artifacts)
            # Calculate local binary patterns
            from skimage.feature import local_binary_pattern
            radius = 3
            n_points = 8 * radius
            lbp = local_binary_pattern(gray, n_points, radius, method='uniform')

            # AI images often have repetitive patterns
            hist, _ = np.histogram(lbp.ravel(), bins=np.arange(0, n_points + 3), density=True)
            uniformity = np.sum(hist**2)

            if uniformity > 0.15:  # High uniformity = likely AI
                result['indicators'].append('Repetitive patterns detected (AI artifact)')
                result['score'] += 0.3

            # Check for missing natural camera noise
            noise_std = np.std(gray - cv2.GaussianBlur(gray, (5, 5), 0))
            if noise_std < 5:  # Too clean = likely AI
                result['indicators'].append('Lack of natural camera noise')
                result['score'] += 0.25

            # Check EXIF for AI software signatures
            try:
                with open(image_path, 'rb') as f:
                    tags = exifread.process_file(f, details=False)

                ai_software = ['midjourney', 'stable diffusion', 'dall-e', 'dalle',
                              'ai', 'gan', 'neural', 'synthetic', 'generated']

                if 'Image Software' in tags:
                    software = str(tags['Image Software']).lower()
                    for ai_tool in ai_software:
                        if ai_tool in software:
                            result['indicators'].append(f'AI software detected: {software}')
                            result['score'] += 0.4
                            break

                # AI images often have no camera metadata
                if 'Image Make' not in tags and 'Image Model' not in tags:
                    result['indicators'].append('Missing camera metadata (common in AI images)')
                    result['score'] += 0.15
            except:
                pass

            # Calculate final score
            result['score'] = min(1.0, result['score'])

            if result['score'] > self.thresholds.get('ai_generated_threshold', 0.5):
                result['detected'] = True
                result['description'] = f"AI-GENERATED IMAGE DETECTED! Score: {result['score']:.1%}. Indicators: {', '.join(result['indicators'])}"
            else:
                result['description'] = f"No strong AI-generation indicators (Score: {result['score']:.1%})"

        except Exception as e:
            result['description'] = f"AI detection error: {str(e)}"

        return result

    def analyze_frequency_domain(self, img):
        """Analyze frequency domain for tampering signs"""
        result = {
            'type': 'Frequency Domain Analysis',
            'technique': 'Frequency Domain Analysis',
            'suspicious': False,
            'detected': False,
            'score': 0.0,
            'severity': 'medium',
            'description': ''
        }

        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Perform FFT
            f = np.fft.fft2(gray)
            fshift = np.fft.fftshift(f)
            magnitude_spectrum = 20 * np.log(np.abs(fshift) + 1)

            # Check for periodic patterns (sign of manipulation)
            h, w = magnitude_spectrum.shape
            center = magnitude_spectrum[h//4:3*h//4, w//4:3*w//4]

            # Calculate uniformity
            mean_mag = np.mean(center)
            std_mag = np.std(center)

            # Suspicious if too uniform (edited) or too variable (spliced)
            if std_mag < mean_mag * 0.3 or std_mag > mean_mag * 1.5:
                result['suspicious'] = True
                result['detected'] = True
                result['score'] = 0.6
                result['severity'] = 'high' if std_mag > mean_mag * 1.5 else 'medium'
                result['description'] = f"Abnormal frequency patterns detected (editing/splicing indicators)"
            else:
                result['description'] = "Frequency analysis normal"
                result['severity'] = 'low'

        except Exception as e:
            result['description'] = f"Frequency analysis error: {str(e)}"
            result['severity'] = 'info'

        return result

    def calculate_confidence(self):
        """Calculate overall confidence score with improved sensitivity"""
        scores = []

        # Collect all scores from findings
        for finding in self.results['findings']:
            if 'score' in finding and finding['score'] > 0:
                scores.append(finding['score'])

        # Add metadata score (weighted higher)
        if self.results['metadata_issues']:
            metadata_score = len(self.results['metadata_issues']) * 0.3  # Increased from 0.2
            scores.append(min(1.0, metadata_score))

        if scores:
            # Use weighted average favoring higher scores
            self.results['confidence_score'] = np.mean(scores)

            # Add bonus if multiple techniques flag issues
            if len(scores) >= 3:
                self.results['confidence_score'] = min(1.0, self.results['confidence_score'] * 1.2)

            # Determine if tampering detected (using lowered threshold)
            forgery_threshold = self.thresholds.get('forgery_confidence', 0.35)
            if self.results['confidence_score'] > forgery_threshold:
                self.results['tampering_detected'] = True
        else:
            self.results['confidence_score'] = 0.0
            self.results['tampering_detected'] = False

