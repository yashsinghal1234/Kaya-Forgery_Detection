"""Debug the code analyzer"""
from code_analyzer import CodeAnalyzer

# Simple test code
test_code = '''def print_board(board):
    """Utility function to print the Sudoku board."""
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("-" * 21)
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print("|", end=" ")
            if j == 8:
                print(board[i][j])
            else:
                print(str(board[i][j]) + " ", end="")

def find_empty(board):
    """Finds an empty cell in the Sudoku board."""
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)  # row, col
    return None
'''

analyzer = CodeAnalyzer()
result = analyzer.analyze_code(test_code, language='python')

print("="*70)
print("DEBUG OUTPUT")
print("="*70)
print(f"AI-Generated: {result['ai_generated']}")
print(f"Confidence: {result['confidence_score']:.2%}")
print(f"\nFindings: {len(result['findings'])}")

for finding in result['findings']:
    print(f"\n{finding['type']}:")
    print(f"  Description: {finding.get('description', 'N/A')}")
    print(f"  Severity: {finding.get('severity', 'N/A')}")

print(f"\nMetrics: {result['code_quality_metrics']}")

