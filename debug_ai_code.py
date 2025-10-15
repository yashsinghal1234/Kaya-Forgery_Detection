"""
Test AI-generated code detection
"""
from code_analyzer import CodeAnalyzer

ai_code = """def calculate_fibonacci(n):
    \"\"\"
    This function calculates the Fibonacci sequence.
    
    Args:
        n: The number of elements to generate
    
    Returns:
        A list containing the Fibonacci sequence
    \"\"\"
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[i-1] + fib_sequence[i-2])
    
    return fib_sequence
"""

analyzer = CodeAnalyzer()
results = analyzer.analyze_code(ai_code, 'python')

print("\n" + "="*60)
print("AI-GENERATED CODE ANALYSIS DEBUG")
print("="*60)
print(f"AI Generated: {results['ai_generated']}")
print(f"Confidence: {results['confidence_score']:.1%}")
print(f"\nFindings ({len(results['findings'])}):")
for i, finding in enumerate(results['findings'], 1):
    print(f"\n{i}. {finding['type']}")
    print(f"   Severity: {finding.get('severity', 'N/A')}")
    print(f"   Description: {finding.get('description', 'N/A')[:100]}...")
    print(f"   Detected/Suspicious: {finding.get('suspicious', finding.get('detected', False))}")

