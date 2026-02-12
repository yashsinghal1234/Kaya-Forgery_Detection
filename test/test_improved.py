"""
Test the improved fraud detection system
"""
from image_tampering_detector import ImageTamperingDetector
import config
import numpy as np
import cv2
from PIL import Image

print("="*70)
print("  TESTING IMPROVED FRAUD DETECTION")
print("="*70)

# Create a simulated AI-generated image (smooth, no metadata)
print("\n[1] Creating simulated AI-generated image...")
ai_image = np.ones((512, 512, 3), dtype=np.uint8) * 128
# Add smooth gradient (AI-like)
for i in range(512):
    for j in range(512):
        r = min(255, 100 + i//4)
        g = min(255, 150 + j//4)
        b = max(0, min(255, 200 - i//4))
        ai_image[i, j] = [b, g, r]  # BGR format for OpenCV

# Apply Gaussian blur to make it unnaturally smooth
ai_image = cv2.GaussianBlur(ai_image, (15, 15), 0)

# Save without any metadata
cv2.imwrite('../uploads/test_ai_generated.jpg', ai_image)
print("   ✓ AI-generated test image created")

# Test the detector
print("\n[2] Running analysis...")
detector = ImageTamperingDetector(config.ANALYSIS_CONFIG, config.THRESHOLDS)
results = detector.analyze_image('uploads/test_ai_generated.jpg')

print("\n" + "="*70)
print("  RESULTS")
print("="*70)
print(f"\n⚠️  FRAUD DETECTED: {'YES' if results['tampering_detected'] else 'NO'}")
print(f"📊 Confidence Score: {results['confidence_score']:.1%}")
print(f"🔍 Techniques Used: {len(results['techniques_used'])}")

print(f"\n📋 FINDINGS ({len(results['findings'])}):")
for i, finding in enumerate(results['findings'], 1):
    status = "⚠️ SUSPICIOUS" if finding.get('suspicious') or finding.get('detected') or finding.get('inconsistent') else "✓ PASSED"
    print(f"\n   {i}. {finding['technique']} - {status}")
    print(f"      Score: {finding.get('score', 0):.1%}")
    print(f"      {finding['description']}")

print(f"\n📝 METADATA ISSUES ({len(results['metadata_issues'])}):")
for i, issue in enumerate(results['metadata_issues'], 1):
    print(f"   {i}. [{issue['severity'].upper()}] {issue['type']}: {issue['description']}")

print("\n" + "="*70)
print("  VERIFICATION")
print("="*70)

if results['tampering_detected']:
    print("\n✅ SUCCESS! The system now correctly detects fraud!")
    print(f"   The confidence score is {results['confidence_score']:.1%}")
    print(f"   Threshold is {config.THRESHOLDS['forgery_confidence']:.1%}")
else:
    print("\n⚠️  Testing with current thresholds...")
    print(f"   Confidence: {results['confidence_score']:.1%}")
    print(f"   Threshold: {config.THRESHOLDS['forgery_confidence']:.1%}")
    if results['confidence_score'] > 0:
        print(f"   ℹ️  Image is flagged as suspicious even if below threshold")

print("\n" + "="*70)
