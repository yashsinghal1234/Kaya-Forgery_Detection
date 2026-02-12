"""
ML-Based Code Analyzer
Uses machine learning to detect AI-generated code with high accuracy
"""
import re
import ast
import os
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from collections import Counter
import json
from datetime import datetime


class MLCodeAnalyzer:
    """Machine Learning-based code analyzer for AI detection"""

    def __init__(self, model_path='models/code_detector_v1.pkl'):
        self.model_path = model_path
        self.model = None
        self.vectorizer = None
        self.scaler = None
        self.feature_names = []
        
        # Try to load pre-trained model
        if os.path.exists(model_path):
            self.load_model()
        else:
            print("[!] No pre-trained model found. Use train() method to train a new model.")
            self.initialize_model()
    
    def initialize_model(self):
        """Initialize a new ML model"""
        self.model = GradientBoostingClassifier(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            token_pattern=r'\b\w+\b'
        )
        self.scaler = StandardScaler()
    
    def extract_features(self, code_text, language='python'):
        """Extract comprehensive features from code"""
        features = {}
        
        # 1. Basic Code Metrics
        features['code_length'] = len(code_text)
        features['line_count'] = len(code_text.split('\n'))
        features['avg_line_length'] = features['code_length'] / max(features['line_count'], 1)
        
        # 2. Comment Analysis
        comment_patterns = {
            'python': r'#.*$',
            'javascript': r'//.*$|/\*[\s\S]*?\*/',
            'java': r'//.*$|/\*[\s\S]*?\*/',
            'c/c++': r'//.*$|/\*[\s\S]*?\*/',
            'c#': r'//.*$|/\*[\s\S]*?\*/'
        }
        
        pattern = comment_patterns.get(language, r'#.*$')
        comments = re.findall(pattern, code_text, re.MULTILINE)
        features['comment_count'] = len(comments)
        features['comment_ratio'] = len(''.join(comments)) / max(features['code_length'], 1)
        
        # AI-generated code tends to have more descriptive comments
        features['avg_comment_length'] = np.mean([len(c) for c in comments]) if comments else 0
        features['has_docstring'] = 1 if '"""' in code_text or "'''" in code_text else 0
        
        # 3. Structural Complexity
        features['indentation_levels'] = self._count_indentation_levels(code_text)
        features['blank_line_ratio'] = code_text.count('\n\n') / max(features['line_count'], 1)
        
        # 4. Function/Class Analysis
        if language == 'python':
            try:
                tree = ast.parse(code_text)
                features['function_count'] = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
                features['class_count'] = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
                features['import_count'] = len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))])
            except:
                features['function_count'] = code_text.count('def ')
                features['class_count'] = code_text.count('class ')
                features['import_count'] = code_text.count('import ')
        else:
            features['function_count'] = len(re.findall(r'\bfunction\b|\bdef\b|\bpublic\s+\w+\s+\w+\(', code_text))
            features['class_count'] = len(re.findall(r'\bclass\b', code_text))
            features['import_count'] = len(re.findall(r'\bimport\b|\busing\b|\b#include\b', code_text))
        
        # 5. Naming Convention Analysis
        identifiers = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', code_text)
        if identifiers:
            features['avg_identifier_length'] = np.mean([len(i) for i in identifiers])
            features['camel_case_ratio'] = sum(1 for i in identifiers if re.match(r'^[a-z]+([A-Z][a-z]*)+$', i)) / len(identifiers)
            features['snake_case_ratio'] = sum(1 for i in identifiers if '_' in i) / len(identifiers)
            features['all_caps_ratio'] = sum(1 for i in identifiers if i.isupper()) / len(identifiers)
        else:
            features['avg_identifier_length'] = 0
            features['camel_case_ratio'] = 0
            features['snake_case_ratio'] = 0
            features['all_caps_ratio'] = 0
        
        # 6. AI-Specific Patterns
        ai_indicators = [
            r'example usage',
            r'note:',
            r'alternatively',
            r'you can also',
            r'this function',
            r'this method',
            r'this class',
            r'helper function',
            r'utility function',
            r'main function'
        ]
        features['ai_phrase_count'] = sum(1 for pattern in ai_indicators if re.search(pattern, code_text.lower()))
        
        # 7. Code Consistency
        features['consistent_indentation'] = self._check_indentation_consistency(code_text)
        features['whitespace_consistency'] = self._check_whitespace_consistency(code_text)
        
        # 8. Keyword Density
        keywords = ['if', 'else', 'for', 'while', 'return', 'class', 'def', 'function', 'var', 'const', 'let']
        features['keyword_density'] = sum(code_text.count(kw) for kw in keywords) / max(features['code_length'], 1)
        
        # 9. Error Handling
        features['try_catch_count'] = len(re.findall(r'\btry\b|\bcatch\b|\bexcept\b|\bfinally\b', code_text))
        features['error_handling_ratio'] = features['try_catch_count'] / max(features['function_count'], 1)
        
        # 10. Documentation Quality
        features['has_type_hints'] = 1 if re.search(r'->\s*\w+|:\s*\w+\s*=', code_text) else 0
        features['has_inline_comments'] = 1 if re.search(r'[^\n]*#[^\n]+', code_text) else 0
        
        return features
    
    def _count_indentation_levels(self, code_text):
        """Count maximum indentation levels"""
        max_indent = 0
        for line in code_text.split('\n'):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                max_indent = max(max_indent, indent // 4 + 1)  # Assuming 4 spaces per level
        return max_indent
    
    def _check_indentation_consistency(self, code_text):
        """Check if indentation is consistent (AI code tends to be very consistent)"""
        indents = []
        for line in code_text.split('\n'):
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indents.append(indent)
        
        if not indents:
            return 1
        
        # Check if indents are multiples of a base unit (2 or 4 spaces)
        indent_set = set(indents)
        if all(i % 4 == 0 for i in indent_set):
            return 1  # Very consistent (AI-like)
        elif all(i % 2 == 0 for i in indent_set):
            return 0.8  # Fairly consistent
        else:
            return 0.5  # Inconsistent (human-like)
    
    def _check_whitespace_consistency(self, code_text):
        """Check whitespace around operators (AI is very consistent)"""
        # Check spaces around operators
        operators_with_space = len(re.findall(r'\s[\+\-\*\/\%]\s', code_text))
        operators_without_space = len(re.findall(r'\S[\+\-\*\/\%]\S', code_text))
        
        total = operators_with_space + operators_without_space
        if total == 0:
            return 1
        
        # AI code tends to always have spaces around operators
        return operators_with_space / total
    
    def analyze(self, code_text, language='python'):
        """Analyze code and return AI detection results"""
        if self.model is None:
            return self._fallback_analysis(code_text, language)
        
        # Extract features
        features = self.extract_features(code_text, language)
        
        # Prepare feature vector
        feature_vector = np.array([[features[name] for name in self.feature_names]])
        
        # Get TF-IDF features
        try:
            tfidf_features = self.vectorizer.transform([code_text]).toarray()
            combined_features = np.hstack([feature_vector, tfidf_features])
            combined_features = self.scaler.transform(combined_features)
        except:
            combined_features = feature_vector
        
        # Predict
        prediction = self.model.predict(combined_features)[0]
        probability = self.model.predict_proba(combined_features)[0]
        
        # Build detailed results
        results = {
            'ai_generated': bool(prediction),
            'confidence_score': probability[1],  # Probability of AI-generated
            'human_probability': probability[0],
            'techniques_used': ['ML Feature Analysis', 'TF-IDF Text Analysis', 'Structural Pattern Recognition'],
            'findings': [],
            'features': features,
            'language': language
        }
        
        # Generate detailed findings
        results['findings'] = self._generate_findings(features, probability[1])
        
        return results
    
    def _fallback_analysis(self, code_text, language):
        """Fallback heuristic analysis when model is not available"""
        features = self.extract_features(code_text, language)
        
        # Simple scoring based on features
        ai_score = 0
        findings = []
        
        # High comment ratio
        if features['comment_ratio'] > 0.15:
            ai_score += 0.2
            findings.append({
                'type': 'Comment Analysis',
                'description': f"High comment ratio ({features['comment_ratio']:.2%}) - typical of AI-generated code",
                'severity': 'medium'
            })
        
        # Perfect indentation
        if features['consistent_indentation'] > 0.95:
            ai_score += 0.15
            findings.append({
                'type': 'Consistency Analysis',
                'description': "Perfect indentation consistency detected - common in AI code",
                'severity': 'low'
            })
        
        # AI phrases
        if features['ai_phrase_count'] > 2:
            ai_score += 0.25
            findings.append({
                'type': 'AI Pattern Detection',
                'description': f"Found {features['ai_phrase_count']} AI-typical phrases",
                'severity': 'high'
            })
        
        # Long identifiers
        if features['avg_identifier_length'] > 15:
            ai_score += 0.1
            findings.append({
                'type': 'Naming Analysis',
                'description': "Very descriptive variable names - AI characteristic",
                'severity': 'low'
            })
        
        # Perfect whitespace
        if features['whitespace_consistency'] > 0.95:
            ai_score += 0.1
        
        return {
            'ai_generated': ai_score > 0.5,
            'confidence_score': min(ai_score, 1.0),
            'techniques_used': ['Heuristic Analysis', 'Pattern Matching'],
            'findings': findings,
            'features': features,
            'language': language
        }
    
    def _generate_findings(self, features, ai_probability):
        """Generate detailed findings based on features"""
        findings = []
        
        # Comment analysis
        if features['comment_ratio'] > 0.15:
            findings.append({
                'type': 'Comment Density',
                'description': f"Comment ratio: {features['comment_ratio']:.1%}. AI-generated code typically has {'>15%' if features['comment_ratio'] > 0.15 else '<15%'} comments.",
                'severity': 'medium' if features['comment_ratio'] > 0.15 else 'low',
                'suspicious': features['comment_ratio'] > 0.15
            })
        
        # Consistency
        if features['consistent_indentation'] > 0.9:
            findings.append({
                'type': 'Code Consistency',
                'description': f"Perfect indentation consistency score: {features['consistent_indentation']:.2f}. AI-generated code is typically very consistent.",
                'severity': 'medium',
                'suspicious': True
            })
        
        # AI phrases
        if features['ai_phrase_count'] > 0:
            findings.append({
                'type': 'AI Pattern Detection',
                'description': f"Detected {features['ai_phrase_count']} AI-typical phrases (e.g., 'example usage', 'helper function', 'note:')",
                'severity': 'high',
                'suspicious': features['ai_phrase_count'] > 2
            })
        
        # Naming conventions
        if features['avg_identifier_length'] > 12:
            findings.append({
                'type': 'Naming Conventions',
                'description': f"Average identifier length: {features['avg_identifier_length']:.1f} characters. AI tends to use more descriptive names.",
                'severity': 'low',
                'suspicious': features['avg_identifier_length'] > 15
            })
        
        # Structure
        if features['function_count'] > 0:
            lines_per_function = features['line_count'] / features['function_count']
            if 15 < lines_per_function < 50:
                findings.append({
                    'type': 'Function Structure',
                    'description': f"Average {lines_per_function:.1f} lines per function. Well-structured, typical of AI optimization.",
                    'severity': 'low',
                    'suspicious': True
                })
        
        # Error handling
        if features['error_handling_ratio'] > 0.5:
            findings.append({
                'type': 'Error Handling',
                'description': f"High error handling ratio ({features['error_handling_ratio']:.1%}). AI-generated code often includes comprehensive error handling.",
                'severity': 'medium',
                'suspicious': True
            })
        
        return findings
    
    def train(self, dataset_path='datasets/training'):
        """Train the model on a dataset"""
        print("[*] Loading training data...")
        X_train, y_train, X_val, y_val = self._load_dataset(dataset_path)
        
        if len(X_train) == 0:
            print("[!] No training data found. Please add code samples to the dataset directory.")
            return False
        
        print(f"[*] Training on {len(X_train)} samples...")
        
        # Extract features for all samples
        features_list = []
        texts = []
        
        for code, label in zip(X_train, y_train):
            features = self.extract_features(code)
            features_list.append(features)
            texts.append(code)
        
        # Store feature names
        self.feature_names = list(features_list[0].keys())
        
        # Convert to arrays
        X_features = np.array([[f[name] for name in self.feature_names] for f in features_list])
        
        # TF-IDF vectorization
        tfidf_features = self.vectorizer.fit_transform(texts).toarray()
        
        # Combine features
        X_combined = np.hstack([X_features, tfidf_features])
        X_combined = self.scaler.fit_transform(X_combined)
        
        # Train model
        self.model.fit(X_combined, y_train)
        
        # Validate
        if len(X_val) > 0:
            print("[*] Validating model...")
            val_features = []
            val_texts = []
            
            for code, label in zip(X_val, y_val):
                features = self.extract_features(code)
                val_features.append([features[name] for name in self.feature_names])
                val_texts.append(code)
            
            X_val_features = np.array(val_features)
            tfidf_val = self.vectorizer.transform(val_texts).toarray()
            X_val_combined = np.hstack([X_val_features, tfidf_val])
            X_val_combined = self.scaler.transform(X_val_combined)
            
            predictions = self.model.predict(X_val_combined)
            accuracy = accuracy_score(y_val, predictions)
            precision, recall, f1, _ = precision_recall_fscore_support(y_val, predictions, average='binary')
            
            print(f"[+] Validation Accuracy: {accuracy:.2%}")
            print(f"[+] Precision: {precision:.2%}, Recall: {recall:.2%}, F1: {f1:.2%}")
        
        # Save model
        self.save_model()
        print(f"[+] Model saved to {self.model_path}")
        
        return True
    
    def _load_dataset(self, dataset_path):
        """Load code samples from dataset directory"""
        X_train, y_train = [], []
        X_val, y_val = [], []
        
        # Load training data
        human_path = os.path.join(dataset_path, 'human_written')
        ai_path = os.path.join(dataset_path, 'ai_generated')
        
        # Load human-written code
        if os.path.exists(human_path):
            for root, dirs, files in os.walk(human_path):
                for file in files:
                    if file.endswith(('.py', '.js', '.java', '.cpp', '.cs')):
                        with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                            code = f.read()
                            if len(code) > 50:  # Minimum code length
                                X_train.append(code)
                                y_train.append(0)  # Human = 0
        
        # Load AI-generated code
        if os.path.exists(ai_path):
            for root, dirs, files in os.walk(ai_path):
                for file in files:
                    if file.endswith(('.py', '.js', '.java', '.cpp', '.cs')):
                        with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                            code = f.read()
                            if len(code) > 50:
                                X_train.append(code)
                                y_train.append(1)  # AI = 1
        
        # Load validation data
        val_path = dataset_path.replace('training', 'validation')
        if os.path.exists(val_path):
            human_val = os.path.join(val_path, 'human_written')
            ai_val = os.path.join(val_path, 'ai_generated')
            
            for root, dirs, files in os.walk(human_val):
                for file in files:
                    if file.endswith(('.py', '.js', '.java', '.cpp', '.cs')):
                        with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                            code = f.read()
                            if len(code) > 50:
                                X_val.append(code)
                                y_val.append(0)
            
            for root, dirs, files in os.walk(ai_val):
                for file in files:
                    if file.endswith(('.py', '.js', '.java', '.cpp', '.cs')):
                        with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                            code = f.read()
                            if len(code) > 50:
                                X_val.append(code)
                                y_val.append(1)
        
        return X_train, y_train, X_val, y_val
    
    def save_model(self):
        """Save trained model to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'vectorizer': self.vectorizer,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'metadata': {
                'trained_date': datetime.now().isoformat(),
                'version': '1.0'
            }
        }
        
        with open(self.model_path, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self):
        """Load trained model from disk"""
        try:
            with open(self.model_path, 'rb') as f:
                model_data = pickle.load(f)
                
            self.model = model_data['model']
            self.vectorizer = model_data['vectorizer']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            
            print(f"[+] Loaded pre-trained model from {self.model_path}")
            print(f"[+] Model version: {model_data['metadata']['version']}")
            return True
        except Exception as e:
            print(f"[!] Error loading model: {e}")
            return False
