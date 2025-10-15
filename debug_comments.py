"""Debug comment analysis specifically"""
import re

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

def is_valid(board, num, pos):
    """Checks whether placing 'num' at 'pos' is valid."""
    row, col = pos

    # Check row
    if num in board[row]:
        return False

    # Check column
    for i in range(9):
        if board[i][col] == num:
            return False

    # Check 3x3 box
    box_x = col // 3
    box_y = row // 3

    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if board[i][j] == num:
                return False

    return True
'''

# Test inline patterns
inline_patterns = [
    r'#\s*(?:Check|Verify|Validate|Test|Handle|Process|Calculate|Compute|Find|Get|Set|Update|Initialize|Create|Return|Add|Remove|Delete|Insert|Append|Store|Save|Load|Parse|Convert|Transform|Print|Display|Show|Iterate|Loop|Search|Sort|Filter|Map|Reduce)',
    r'#\s*(?:row|col|column|index|value|result|output|input|data|temp|array|list|dict|string|number|count|sum|total|min|max|avg|mean),?\s*(?:col|row|index)?',
    r'#\s*\d+\s*(?:means|represents|is|indicates)',
    r'#\s*(?:Solution|Result|Answer|Output|Input)',
    r'#\s*(?:Try|Attempt|Undo|Backtrack|Recursive)',
    r'#\s*(?:Example|Sample|Test|Demo)\s+',
]

inline_explanatory = 0
for pattern in inline_patterns:
    matches = re.findall(pattern, test_code, re.IGNORECASE)
    if matches:
        print(f"Pattern: {pattern}")
        print(f"Matches: {matches}")
        inline_explanatory += len(matches)

print(f"\nTotal inline explanatory comments: {inline_explanatory}")

# Check functions and docstrings
functions = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', test_code)
docstrings = re.findall(r'def\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\):\s*(?:\n\s*)?"""', test_code)

print(f"\nFunctions found: {len(functions)} - {functions}")
print(f"Docstrings found: {len(docstrings)}")
print(f"Perfect documentation: {len(docstrings) == len(functions)}")

