"""
AI-Generated Code Detection Module
Detects whether code is written by humans or AI using multiple techniques
"""
import re
import ast
import os
from collections import Counter
from datetime import datetime
import hashlib


class CodeAnalyzer:
    """Comprehensive code analysis for AI-generated detection"""

    def __init__(self):
        self.results = {
            'ai_generated': False,
            'confidence_score': 0.0,
            'techniques_used': [],
            'findings': [],
            'suspicious_patterns': [],
            'code_quality_metrics': {}
        }

    def analyze_code(self, code_text, language='auto'):
        """Main analysis pipeline for code detection"""
        print(f"[*] Starting code analysis...")

        if language == 'auto':
            language = self.detect_language(code_text)

        self.results['language'] = language

        # Technique 1: Comment Pattern Analysis
        comment_result = self.analyze_comments(code_text, language)
        self.results['techniques_used'].append('Comment Pattern Analysis')
        if comment_result['suspicious']:
            self.results['findings'].append(comment_result)

        # Technique 2: Code Structure Analysis
        structure_result = self.analyze_structure(code_text, language)
        self.results['techniques_used'].append('Code Structure Analysis')
        if structure_result['suspicious']:
            self.results['findings'].append(structure_result)

        # Technique 3: Naming Convention Analysis
        naming_result = self.analyze_naming_patterns(code_text, language)
        self.results['techniques_used'].append('Naming Convention Analysis')
        if naming_result['suspicious']:
            self.results['findings'].append(naming_result)

        # Technique 4: AI-Specific Patterns Detection
        ai_pattern_result = self.detect_ai_patterns(code_text, language)
        self.results['techniques_used'].append('AI Pattern Detection')
        if ai_pattern_result['detected']:
            self.results['findings'].append(ai_pattern_result)

        # Technique 5: Code Complexity Analysis
        complexity_result = self.analyze_complexity(code_text, language)
        self.results['techniques_used'].append('Complexity Analysis')
        self.results['code_quality_metrics'] = complexity_result['metrics']
        if complexity_result['suspicious']:
            self.results['findings'].append(complexity_result)

        # Technique 6: Consistency Analysis
        consistency_result = self.analyze_consistency(code_text, language)
        self.results['techniques_used'].append('Consistency Analysis')
        if consistency_result['suspicious']:
            self.results['findings'].append(consistency_result)

        # Calculate overall confidence
        self.calculate_confidence()

        print(f"[+] Code analysis complete. AI-generated confidence: {self.results['confidence_score']:.2%}")
        return self.results

    def detect_language(self, code_text):
        """Detect programming language from code"""
        # Simple heuristic-based detection
        if 'def ' in code_text and 'import ' in code_text:
            return 'python'
        elif 'function' in code_text or 'const ' in code_text or 'let ' in code_text:
            return 'javascript'
        elif 'public class' in code_text or 'public static void' in code_text:
            return 'java'
        elif '#include' in code_text or 'int main' in code_text:
            return 'c/c++'
        elif 'using System' in code_text or 'namespace' in code_text:
            return 'c#'
        else:
            return 'unknown'

    def analyze_comments(self, code_text, language):
        """Analyze comment patterns that indicate AI generation"""
        result = {
            'type': 'Comment Analysis',
            'suspicious': False,
            'description': '',
            'severity': 'low'
        }

        # AI-generated code often has very structured, overly-explanatory comments
        ai_comment_indicators = [
            r'This function (?:is used to|will|does)',  # Very formal explanations
            r'Initialize the (?:variable|parameter|function)',
            r'Define (?:a|the) (?:class|function|method)',
            r'Import (?:necessary|required) (?:libraries|modules)',
            r'Set up the (?:configuration|parameters|variables)',
            r'Create (?:a|an) instance of',
            r'Iterate through (?:the|each)',
            r'Return the (?:result|value|output)',
            r'Calculate the',
            r'Append to the',
            r'Note:',
            r'Example:',
            r'Args:',
            r'Returns:',
            r'Parameters:',
            r'Raises:',
            r'Yields:',
        ]

        suspicious_count = 0
        total_comments = 0

        # Count comments based on language
        if language == 'python':
            comments = re.findall(r'#.*$|""".*?"""|\'\'\'.*?\'\'\'', code_text, re.MULTILINE | re.DOTALL)
        elif language in ['javascript', 'java', 'c/c++', 'c#']:
            comments = re.findall(r'//.*$|/\*.*?\*/', code_text, re.MULTILINE | re.DOTALL)
        else:
            comments = re.findall(r'#.*$|//.*$|/\*.*?\*/', code_text, re.MULTILINE)

        total_comments = len(comments)

        for comment in comments:
            for pattern in ai_comment_indicators:
                if re.search(pattern, comment, re.IGNORECASE):
                    suspicious_count += 1
                    break

        # Check for overly detailed comments
        if total_comments > 0:
            comment_ratio = suspicious_count / total_comments
            if comment_ratio > 0.4:  # Raised threshold - need strong evidence
                result['suspicious'] = True
                result['severity'] = 'high'
                result['description'] = f'Found {suspicious_count} AI-style comments out of {total_comments} total comments ({comment_ratio:.0%}). AI-generated code often contains overly formal, structured explanations.'

        # Check for inline comments that explain every line (strong AI indicator)
        inline_comments = re.findall(r'#\s*(?:Initialize|Calculate|Return|Iterate|Append|Create|Set)\s+(?:the|a|an)', code_text, re.IGNORECASE)
        if len(inline_comments) > 3:  # Raised from 5 - this is a STRONG indicator
            result['suspicious'] = True
            result['severity'] = 'critical'  # Upgraded to critical
            result['description'] = f'Found {len(inline_comments)} AI-style inline explanatory comments. This is a strong indicator of AI generation.'

        # Check for excessive commenting - but only if it's also AI-style
        lines = code_text.split('\n')
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        comment_line_ratio = total_comments / max(len(lines), 1)

        # Only flag if we have BOTH excessive comments AND they're AI-style
        if comment_line_ratio > 0.35 and suspicious_count > 0:
            result['suspicious'] = True
            result['severity'] = 'high'
            if not result['description']:
                result['description'] = f'Excessive AI-style commenting detected ({comment_line_ratio:.0%} of lines).'

        return result

    def analyze_structure(self, code_text, language):
        """Analyze code structure patterns"""
        result = {
            'type': 'Code Structure Analysis',
            'suspicious': False,
            'description': '',
            'severity': 'medium'
        }

        lines = code_text.split('\n')

        # Check for overly uniform line lengths (AI tends to be very consistent)
        # BUT only if it's suspiciously perfect AND there are many lines
        line_lengths = [len(line.rstrip()) for line in lines if line.strip()]
        if line_lengths and len(line_lengths) > 20:  # Increased from 10 - need more lines
            avg_length = sum(line_lengths) / len(line_lengths)
            variance = sum((x - avg_length) ** 2 for x in line_lengths) / len(line_lengths)

            # Very low variance suggests AI (too perfect) - but need VERY low variance
            if variance < 30 and len(line_lengths) > 30:  # Much stricter - was 50
                result['suspicious'] = True
                result['description'] = 'Code has unnaturally uniform line lengths (variance: {:.1f}), suggesting AI generation. '.format(variance)

        # Check for excessive blank lines (AI adds them for readability)
        # This is actually a stronger indicator
        blank_lines = sum(1 for line in lines if not line.strip())
        if len(lines) > 20 and blank_lines / max(len(lines), 1) > 0.30:  # Raised from 0.25
            result['suspicious'] = True
            result['severity'] = 'high'
            result['description'] += 'Excessive blank lines for readability ({:.0%}), typical of AI. '.format(blank_lines / len(lines))

        return result

    def analyze_naming_patterns(self, code_text, language):
        """Analyze variable and function naming patterns"""
        result = {
            'type': 'Naming Convention Analysis',
            'suspicious': False,
            'description': '',
            'severity': 'medium'
        }

        # AI often uses very descriptive, consistent naming
        if language == 'python':
            # Find function names
            functions = re.findall(r'def ([a-zA-Z_][a-zA-Z0-9_]*)', code_text)
            # Find variable names
            variables = re.findall(r'\b([a-z_][a-z0-9_]*)\s*=', code_text)
        elif language in ['javascript', 'java', 'c#']:
            functions = re.findall(r'function\s+([a-zA-Z_][a-zA-Z0-9_]*)|([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code_text)
            variables = re.findall(r'\b(?:var|let|const)\s+([a-zA-Z_][a-zA-Z0-9_]*)', code_text)
        else:
            return result

        # Flatten if needed
        if functions and isinstance(functions[0], tuple):
            functions = [f for tup in functions for f in tup if f]

        all_names = functions + variables

        if all_names:
            # Check for overly descriptive names (AI loves these)
            long_names = [name for name in all_names if len(name) > 15]
            if len(long_names) / len(all_names) > 0.3:  # 30% are very long
                result['suspicious'] = True
                result['description'] = 'Overly descriptive variable/function names detected. '

            # Check for perfect snake_case or camelCase consistency (AI is very consistent)
            snake_case = sum(1 for name in all_names if '_' in name and name.islower())
            camel_case = sum(1 for name in all_names if '_' not in name and any(c.isupper() for c in name[1:]))

            if (snake_case / len(all_names) > 0.9 or camel_case / len(all_names) > 0.9):
                result['suspicious'] = True
                result['description'] += 'Perfect naming convention consistency, uncommon in human-written code. '

        return result

    def detect_ai_patterns(self, code_text, language):
        """Detect specific patterns common in AI-generated code"""
        result = {
            'type': 'AI-Specific Pattern Detection',
            'detected': False,
            'description': '',
            'severity': 'high'
        }

        ai_signatures = []

        # Pattern 1: Excessive error handling
        if language == 'python':
            try_blocks = len(re.findall(r'\btry:', code_text))
            except_blocks = len(re.findall(r'\bexcept:', code_text))
            if try_blocks > 3 and try_blocks == except_blocks:
                ai_signatures.append('Excessive try-except blocks')

        # Pattern 2: Overly generic variable names with numbers
        generic_vars = re.findall(r'\b(temp|tmp|var|val|data|item|element|obj|result)[\d]+\b', code_text)
        if len(generic_vars) > 3:
            ai_signatures.append(f'Generic numbered variables: {set(generic_vars)}')

        # Pattern 3: Placeholder comments
        placeholders = re.findall(r'#\s*(?:TODO|FIXME|NOTE|XXX|HACK):', code_text, re.IGNORECASE)
        if len(placeholders) > 2:
            ai_signatures.append('Multiple placeholder comments')

        # Pattern 4: Code generated markers (sometimes AI leaves these)
        markers = [
            'generated by', 'auto-generated', 'AI-generated',
            'do not modify', 'automatically created',
            'copilot', 'chatgpt', 'claude', 'gpt-'
        ]
        for marker in markers:
            if marker.lower() in code_text.lower():
                ai_signatures.append(f'AI marker found: "{marker}"')
                result['severity'] = 'critical'

        # Pattern 5: Overly perfect example data
        if re.search(r'example|sample|test.*data', code_text, re.IGNORECASE):
            example_count = len(re.findall(r'example|sample', code_text, re.IGNORECASE))
            if example_count > 3:
                ai_signatures.append('Excessive example/sample data references')

        # Pattern 6: Docstring patterns
        if language == 'python':
            docstrings = re.findall(r'"""(.*?)"""', code_text, re.DOTALL)
            if len(docstrings) > 0:
                # Check for overly structured docstrings
                structured = sum(1 for doc in docstrings if 'Args:' in doc or 'Returns:' in doc or 'Parameters:' in doc)
                if structured / len(docstrings) > 0.7:
                    ai_signatures.append('Overly structured docstrings')

        if ai_signatures:
            result['detected'] = True
            result['description'] = 'AI-specific patterns found: ' + ', '.join(ai_signatures)

        return result

    def analyze_complexity(self, code_text, language):
        """Analyze code complexity metrics"""
        result = {
            'type': 'Code Complexity Analysis',
            'suspicious': False,
            'description': '',
            'metrics': {},
            'severity': 'low'
        }

        lines = [l for l in code_text.split('\n') if l.strip()]

        # Calculate metrics
        result['metrics']['total_lines'] = len(lines)
        result['metrics']['code_lines'] = len([l for l in lines if l.strip() and not l.strip().startswith(('#', '//'))])

        # AI code tends to have moderate complexity, not too simple, not too complex
        if language == 'python':
            # Count control structures
            control_structures = len(re.findall(r'\b(if|for|while|elif|else)\b', code_text))
            functions = len(re.findall(r'\bdef\s+', code_text))

            result['metrics']['control_structures'] = control_structures
            result['metrics']['functions'] = functions

            if functions > 0:
                avg_complexity = control_structures / functions
                # AI tends to create functions with moderate, consistent complexity
                if 2 < avg_complexity < 5 and functions > 3:
                    result['suspicious'] = True
                    result['description'] = 'Functions have suspiciously uniform complexity levels. '

        return result

    def analyze_consistency(self, code_text, language):
        """Analyze code consistency patterns"""
        result = {
            'type': 'Code Consistency Analysis',
            'suspicious': False,
            'description': '',
            'severity': 'low'  # Lowered from medium - this is a weak indicator alone
        }

        # Check indentation consistency (AI is very consistent)
        # NOTE: Most Python code has consistent indentation (PEP 8), so this alone is NOT a good indicator
        lines = code_text.split('\n')
        indent_sizes = []

        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                if indent > 0:
                    indent_sizes.append(indent)

        # REMOVED: Perfect indentation is normal in Python, not an AI indicator
        # Only flag if there are OTHER suspicious signs along with perfect consistency

        # Check quote usage consistency (AI picks one style and sticks to it)
        single_quotes = code_text.count("'")
        double_quotes = code_text.count('"')

        # Only flag if EXTREMELY consistent AND there are many quotes
        if single_quotes + double_quotes > 20:  # Raised from 10
            ratio = max(single_quotes, double_quotes) / (single_quotes + double_quotes)
            if ratio > 0.98:  # Raised from 0.95 - need VERY high consistency
                result['suspicious'] = True
                result['severity'] = 'low'  # Keep it low - this is weak evidence alone
                result['description'] = 'Extremely consistent quote style ({:.0%}), rare in human code. '.format(ratio)

        return result

    def check_indentation_consistency(self, lines):
        """Check if indentation is perfectly consistent"""
        indent_pattern = None
        consistent = True

        for line in lines:
            if line.strip():
                spaces = len(line) - len(line.lstrip())
                if spaces > 0:
                    if indent_pattern is None:
                        indent_pattern = spaces
                    elif spaces % indent_pattern != 0:
                        consistent = False
                        break

        return consistent

    def calculate_confidence(self):
        """Calculate overall confidence score for AI generation"""
        if not self.results['findings']:
            self.results['ai_generated'] = False
            self.results['confidence_score'] = 0.0
            return

        # Weight different findings (OPTIMIZED for accurate detection)
        weights = {
            'Comment Analysis': 0.30,  # Increased - highly indicative
            'Code Structure Analysis': 0.08,
            'Naming Convention Analysis': 0.12,
            'AI-Specific Pattern Detection': 0.40,  # Highest - most reliable
            'Code Complexity Analysis': 0.03,
            'Code Consistency Analysis': 0.07
        }

        severity_scores = {
            'low': 0.30,
            'medium': 0.60,
            'high': 0.85,       # Increased
            'critical': 1.0
        }

        total_score = 0.0
        total_weight = 0.0

        for finding in self.results['findings']:
            finding_type = finding['type']
            severity = finding.get('severity', 'medium')

            if finding_type in weights:
                weight = weights[finding_type]
                score = severity_scores.get(severity, 0.5)
                total_score += weight * score
                total_weight += weight

        # Normalize
        if total_weight > 0:
            self.results['confidence_score'] = min(total_score / total_weight, 1.0)
        else:
            self.results['confidence_score'] = 0.0

        # Set detection flag with LOWERED threshold for better sensitivity
        self.results['ai_generated'] = self.results['confidence_score'] > 0.45  # Lowered from 0.55
