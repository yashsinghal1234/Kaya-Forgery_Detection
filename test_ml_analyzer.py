"""
Test Script for ML Code Analyzer
Test the trained model with sample code
"""
from ml_code_analyzer import MLCodeAnalyzer
from code_analyzer import CodeAnalyzer


def test_human_code():
    """Test with typical human-written code"""
    code = '''
def process_data(data):
    result=[]
    for item in data:
        if item>0:
            result.append(item*2)
    return result

def check_status(id):
    items=get_all()
    for i in items:
        if i['id']==id:
            return i['status']
    return 'unknown'
'''
    
    print("\n" + "="*60)
    print("Testing with Human-Written Code Sample:")
    print("="*60)
    print(code)
    print("="*60)
    
    analyzer = CodeAnalyzer()
    results = analyzer.analyze_code(code, 'python')
    
    print(f"\n[Result] AI-Generated: {results['ai_generated']}")
    print(f"[Result] Confidence Score: {results['confidence_score']:.2%}")
    print(f"[Result] Techniques Used: {', '.join(results['techniques_used'])}")
    print(f"\n[Findings] {len(results['findings'])} issues detected:")
    for finding in results['findings']:
        print(f"  • {finding.get('type', 'Unknown')}: {finding.get('description', 'No description')}")


def test_ai_code():
    """Test with typical AI-generated code"""
    code = '''
def process_data_items(data_list):
    """
    Process a list of data items by doubling positive values.
    
    Args:
        data_list (list): A list of numeric values to process
        
    Returns:
        list: A list containing doubled positive values
        
    Example:
        >>> process_data_items([1, -2, 3, 4])
        [2, 6, 8]
    """
    result = []
    
    for item in data_list:
        if item > 0:
            result.append(item * 2)
    
    return result


def check_status_by_id(item_id):
    """
    Check the status of an item by its unique identifier.
    
    Args:
        item_id: The unique identifier of the item
        
    Returns:
        str: The status of the item, or 'unknown' if not found
        
    Note:
        This function retrieves all items and searches for a match.
        Consider using a database query for better performance.
    """
    items = get_all()
    
    for item in items:
        if item.get('id') == item_id:
            return item.get('status', 'unknown')
    
    return 'unknown'
'''
    
    print("\n" + "="*60)
    print("Testing with AI-Generated Code Sample:")
    print("="*60)
    print(code)
    print("="*60)
    
    analyzer = CodeAnalyzer()
    results = analyzer.analyze_code(code, 'python')
    
    print(f"\n[Result] AI-Generated: {results['ai_generated']}")
    print(f"[Result] Confidence Score: {results['confidence_score']:.2%}")
    print(f"[Result] Techniques Used: {', '.join(results['techniques_used'])}")
    print(f"\n[Findings] {len(results['findings'])} issues detected:")
    for finding in results['findings']:
        print(f"  • {finding.get('type', 'Unknown')}: {finding.get('description', 'No description')}")


def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║         ML Code Analyzer - Test Script                   ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    try:
        # Test human code
        test_human_code()
        
        # Test AI code
        test_ai_code()
        
        print("\n" + "="*60)
        print("[✓] Testing completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"\n[X] Error during testing: {e}")
        print("[!] Make sure the model is trained first: python train_model.py")


if __name__ == '__main__':
    main()
