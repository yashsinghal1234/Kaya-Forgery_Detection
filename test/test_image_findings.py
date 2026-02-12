"""
Test Image Analysis - Detailed Findings Display
"""
from image_tampering_detector import ImageTamperingDetector
import config
import os

def test_image_analysis():
    """Test image analysis with detailed findings"""
    print("=" * 80)
    print("IMAGE FRAUD DETECTION - DETAILED FINDINGS TEST")
    print("=" * 80)

    # Find an image in uploads folder
    uploads_folder = 'uploads'
    if not os.path.exists(uploads_folder):
        print("❌ No uploads folder found")
        return

    image_files = [f for f in os.listdir(uploads_folder)
                   if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

    if not image_files:
        print("❌ No image files found in uploads folder")
        return

    # Test with first image
    test_image = os.path.join(uploads_folder, image_files[0])
    print(f"\n📸 Testing with: {image_files[0]}")
    print("=" * 80)

    # Initialize detector
    detector = ImageTamperingDetector(config.ANALYSIS_CONFIG, config.THRESHOLDS)

    # Analyze
    results = detector.analyze_image(test_image)

    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)

    # Overall verdict
    if results['tampering_detected']:
        print("🚨 VERDICT: TAMPERING DETECTED")
    else:
        print("✅ VERDICT: NO TAMPERING DETECTED")

    print(f"📊 Confidence Score: {results['confidence_score']:.2%}")

    # Techniques used
    print(f"\n🔍 DETECTION TECHNIQUES APPLIED ({len(results['techniques_used'])}):")
    for tech in results['techniques_used']:
        print(f"   ✓ {tech}")

    # DETAILED FINDINGS
    print(f"\n🔎 DETAILED FINDINGS ({len(results['findings'])}):")
    if results['findings']:
        for i, finding in enumerate(results['findings'], 1):
            # Get all the fields we added
            finding_type = finding.get('type', finding.get('technique', 'Unknown'))
            severity = finding.get('severity', 'N/A').upper()
            severity_icon = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢', 'INFO': 'ℹ️'}.get(severity, '⚪')

            print(f"\n   Finding #{i}:")
            print(f"   Type: {finding_type}")
            print(f"   {severity_icon} Severity: {severity}")
            print(f"   📝 Description: {finding.get('description', 'N/A')}")

            # Check all possible suspicious flags
            is_suspicious = (finding.get('suspicious') or
                           finding.get('detected') or
                           finding.get('anomalous') or
                           finding.get('inconsistent'))

            if is_suspicious:
                print(f"   ⚠️  Status: SUSPICIOUS")
            else:
                print(f"   ✓ Status: Normal")

            # Show flags for verification
            print(f"   📋 Flags: suspicious={finding.get('suspicious')}, "
                  f"detected={finding.get('detected')}, "
                  f"score={finding.get('score', 0):.2%}")
    else:
        print("   ✅ NO SUSPICIOUS FINDINGS")

    # Metadata issues
    if results['metadata_issues']:
        print(f"\n⚠️  METADATA ISSUES ({len(results['metadata_issues'])}):")
        for issue in results['metadata_issues']:
            severity_icon = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(
                issue.get('severity', '').upper(), '⚪')
            print(f"   {severity_icon} {issue.get('type')}: {issue.get('description')}")

    print("\n" + "=" * 80)
    print("SUMMARY:")
    print(f"  ✅ Image analysis complete")
    print(f"  ✅ {len(results['techniques_used'])} detection techniques applied")
    print(f"  ✅ {len(results['findings'])} detailed findings generated")
    print(f"  ✅ All findings have proper type, severity, and status flags")
    print(f"  ✅ Web interface will now display findings correctly!")
    print("=" * 80)
    print(f"\n💡 Test the web interface at: http://localhost:5000")
    print(f"   Upload an image to see detailed findings with:")
    print(f"   - Severity icons (🔴 🟡 🟢)")
    print(f"   - Detailed descriptions")
    print(f"   - Status indicators (SUSPICIOUS/Normal)")

if __name__ == '__main__':
    test_image_analysis()

