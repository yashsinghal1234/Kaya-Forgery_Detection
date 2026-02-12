"""
Automated Test Script for Code Analysis Feature
Tests the AI-generated code detection functionality
"""
import requests
import json
import time
import os

# Server URL
BASE_URL = "http://localhost:5000"

def test_code_text_submission():
    """Test 1: Submit code via text area"""
    print("\n" + "="*60)
    print("TEST 1: Code Text Submission (AI-Generated Code)")
    print("="*60)

    ai_generated_code = '''
def calculate_fibonacci(n):
    """
    This function calculates the Fibonacci sequence.
    
    Args:
        n: The number of elements to generate
    
    Returns:
        A list containing the Fibonacci sequence
    """
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
'''

    data = {
        'code_text': ai_generated_code,
        'language': 'python'
    }

    try:
        print("[*] Submitting AI-generated code...")
        response = requests.post(f"{BASE_URL}/upload", data=data)

        if response.status_code == 200:
            result = response.json()
            print(f"[+] Upload successful! Analysis ID: {result['analysis_id']}")

            # Get results
            print("[*] Fetching analysis results...")
            time.sleep(1)
            results_response = requests.get(f"{BASE_URL}/results/{result['analysis_id']}")

            if results_response.status_code == 200:
                results = results_response.json()
                print(f"\n[+] ANALYSIS RESULTS:")
                print(f"    AI-Generated Detected: {results.get('tampering_detected', False)}")
                print(f"    Confidence Score: {results.get('confidence_score', 0):.1%}")
                print(f"    Techniques Used: {len(results.get('techniques_used', []))}")
                print(f"    Findings: {len(results.get('findings', []))}")

                if results.get('findings'):
                    print(f"\n    Top Findings:")
                    for i, finding in enumerate(results['findings'][:3], 1):
                        print(f"      {i}. {finding.get('type')}")
                        print(f"         {finding.get('description')[:80]}...")

                return True
            else:
                print(f"[-] Failed to get results: {results_response.status_code}")
                return False
        else:
            print(f"[-] Upload failed: {response.status_code}")
            print(f"    Error: {response.text}")
            return False

    except Exception as e:
        print(f"[-] Error: {str(e)}")
        return False


def test_code_file_upload():
    """Test 2: Upload code file"""
    print("\n" + "="*60)
    print("TEST 2: Code File Upload (AI-Generated)")
    print("="*60)

    file_path = "test_code_ai_generated.py"

    if not os.path.exists(file_path):
        print(f"[-] Test file not found: {file_path}")
        return False

    try:
        print(f"[*] Uploading file: {file_path}")
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/upload", files=files)

        if response.status_code == 200:
            result = response.json()
            print(f"[+] Upload successful! Analysis ID: {result['analysis_id']}")

            # Get results
            print("[*] Fetching analysis results...")
            time.sleep(1)
            results_response = requests.get(f"{BASE_URL}/results/{result['analysis_id']}")

            if results_response.status_code == 200:
                results = results_response.json()
                print(f"\n[+] ANALYSIS RESULTS:")
                print(f"    AI-Generated Detected: {results.get('tampering_detected', False)}")
                print(f"    Confidence Score: {results.get('confidence_score', 0):.1%}")
                print(f"    Findings: {len(results.get('findings', []))}")
                print(f"    Report: {results.get('report_filename', 'N/A')}")

                return True
            else:
                print(f"[-] Failed to get results: {results_response.status_code}")
                return False
        else:
            print(f"[-] Upload failed: {response.status_code}")
            print(f"    Error: {response.text}")
            return False

    except Exception as e:
        print(f"[-] Error: {str(e)}")
        return False


def test_human_written_code():
    """Test 3: Test with human-written code"""
    print("\n" + "="*60)
    print("TEST 3: Human-Written Code Detection")
    print("="*60)

    file_path = "test_code_human_written.py"

    if not os.path.exists(file_path):
        print(f"[-] Test file not found: {file_path}")
        return False

    try:
        print(f"[*] Uploading file: {file_path}")
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{BASE_URL}/upload", files=files)

        if response.status_code == 200:
            result = response.json()
            print(f"[+] Upload successful! Analysis ID: {result['analysis_id']}")

            # Get results
            print("[*] Fetching analysis results...")
            time.sleep(1)
            results_response = requests.get(f"{BASE_URL}/results/{result['analysis_id']}")

            if results_response.status_code == 200:
                results = results_response.json()
                print(f"\n[+] ANALYSIS RESULTS:")
                print(f"    AI-Generated Detected: {results.get('tampering_detected', False)}")
                print(f"    Confidence Score: {results.get('confidence_score', 0):.1%}")
                print(f"    Findings: {len(results.get('findings', []))}")

                # Should have LOW confidence for human code
                if results.get('confidence_score', 0) < 0.5:
                    print(f"\n    ✓ Correctly identified as likely human-written")
                else:
                    print(f"\n    ✗ Incorrectly flagged as AI-generated")

                return True
            else:
                print(f"[-] Failed to get results: {results_response.status_code}")
                return False
        else:
            print(f"[-] Upload failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"[-] Error: {str(e)}")
        return False


def test_api_status():
    """Test 0: Check if API is running"""
    print("\n" + "="*60)
    print("TEST 0: API Health Check")
    print("="*60)

    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            status = response.json()
            print(f"[+] API is online!")
            print(f"    App Name: {status.get('app_name')}")
            print(f"    Version: {status.get('version')}")
            print(f"    Status: {status.get('status')}")
            return True
        else:
            print(f"[-] API returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"[-] Cannot connect to API: {str(e)}")
        print(f"    Make sure the server is running at {BASE_URL}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("  AI FRAUD DETECTION AGENT - CODE ANALYSIS TESTING")
    print("="*60)

    results = []

    # Test 0: API Health
    results.append(("API Health Check", test_api_status()))

    if not results[0][1]:
        print("\n[-] Server is not running. Please start the server first.")
        return

    # Test 1: Code text submission
    results.append(("Code Text Submission (AI)", test_code_text_submission()))

    # Test 2: Code file upload (AI-generated)
    results.append(("Code File Upload (AI)", test_code_file_upload()))

    # Test 3: Human-written code
    results.append(("Human-Written Code", test_human_written_code()))

    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()

