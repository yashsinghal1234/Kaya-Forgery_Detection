"""Test metadata analysis"""
from image_tampering_detector import ImageTamperingDetector
import config
import os
import json

detector = ImageTamperingDetector(config.ANALYSIS_CONFIG, config.THRESHOLDS)

# Find a test image
test_images = [f for f in os.listdir('../uploads') if f.endswith(('.jpg', '.jpeg', '.png'))]

if test_images:
    test_img = test_images[0]
    print(f"Testing with: {test_img}")

    result = detector.analyze_image(os.path.join('../uploads', test_img))

    print("\n" + "="*60)
    print("METADATA ISSUES:")
    print("="*60)
    print(f"Number of issues: {len(result.get('metadata_issues', []))}")
    print("\nIssues:")
    print(json.dumps(result.get('metadata_issues', []), indent=2))

    print("\n" + "="*60)
    print("ALL FINDINGS:")
    print("="*60)
    for finding in result.get('findings', []):
        print(f"\n- {finding.get('technique', 'Unknown')}")
        print(f"  Description: {finding.get('description', 'N/A')}")
else:
    print("No test images found in uploads folder")

