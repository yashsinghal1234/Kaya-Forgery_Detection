"""
Quick test to see what's being detected in human code
"""
from code_analyzer import CodeAnalyzer

human_code = """def fib(n):
    if n<2:
        return n
    a,b=0,1
    for _ in range(n-1):
        a,b=b,a+b
    return b

def fact(num):
    res=1
    for i in range(2,num+1):
        res*=i
    return res

# some helper funcs
def is_prime(x):
    if x<2: return False
    for i in range(2,int(x**0.5)+1):
        if x%i==0:
            return False
    return True

def get_primes(limit):
    primes=[]
    for n in range(2,limit):
        if is_prime(n):
            primes.append(n)
    return primes
"""

analyzer = CodeAnalyzer()
results = analyzer.analyze_code(human_code, 'python')

print("\n" + "="*60)
print("HUMAN CODE ANALYSIS DEBUG")
print("="*60)
print(f"AI Generated: {results['ai_generated']}")
print(f"Confidence: {results['confidence_score']:.1%}")
print(f"\nFindings ({len(results['findings'])}):")
for i, finding in enumerate(results['findings'], 1):
    print(f"\n{i}. {finding['type']}")
    print(f"   Severity: {finding.get('severity', 'N/A')}")
    print(f"   Description: {finding.get('description', 'N/A')}")
    print(f"   Suspicious: {finding.get('suspicious', finding.get('detected', False))}")

