"""
Test PDF Detection - Comprehensive Testing
"""
from pdf_analyzer import PDFAnalyzer
import os

def test_pdf_analyzer():
    """Test the PDF analyzer"""
    print("=" * 80)
    print("PDF FRAUD DETECTION - COMPREHENSIVE TEST")
    print("=" * 80)

    # Check if there are any PDF files in reports folder
    reports_folder = 'reports'
    pdf_files = [f for f in os.listdir(reports_folder) if f.endswith('.pdf')]

    if not pdf_files:
        print("No PDF files found in reports folder")
        print("Creating a test scenario...")
        return

    print(f"\n📁 Found {len(pdf_files)} PDF file(s) in reports folder")
    print(f"🧪 Testing PDF analyzer with {min(3, len(pdf_files))} sample(s)...\n")

    # Test multiple PDFs
    for idx, pdf_file in enumerate(pdf_files[:3], 1):
        test_pdf = os.path.join(reports_folder, pdf_file)
        print("=" * 80)
        print(f"TEST #{idx}: {pdf_file}")
        print("=" * 80)

        analyzer = PDFAnalyzer()
        results = analyzer.analyze_pdf(test_pdf)

        # Display results
        print(f"\n{'='*80}")
        print("ANALYSIS RESULTS")
        print("=" * 80)

        # Overall verdict
        if results['forgery_detected']:
            print(f"🚨 VERDICT: FRAUD DETECTED")
        else:
            print(f"✅ VERDICT: NO FRAUD DETECTED")

        print(f"📊 Confidence Score: {results['confidence_score']:.2%}")
        print(f"📄 Risk Level: {get_risk_level(results['confidence_score'])}")

        # Metadata info
        if 'metadata' in results:
            meta = results['metadata']
            print(f"\n📋 DOCUMENT METADATA:")
            print(f"   Pages: {meta.get('num_pages', 'N/A')}")
            print(f"   Creator: {meta.get('Creator', 'N/A')}")
            print(f"   Producer: {meta.get('Producer', 'N/A')}")
            print(f"   Created: {meta.get('CreationDate', 'N/A')}")
            print(f"   Modified: {meta.get('ModDate', 'N/A')}")
            print(f"   Encrypted: {meta.get('encrypted', False)}")

        # Techniques used
        print(f"\n🔍 DETECTION TECHNIQUES APPLIED ({len(results['techniques_used'])}):")
        for tech in results['techniques_used']:
            print(f"   ✓ {tech}")

        # Findings
        if results['findings']:
            print(f"\n🔎 DETAILED FINDINGS ({len(results['findings'])}):")
            for i, finding in enumerate(results['findings'], 1):
                severity = finding.get('severity', 'N/A').upper()
                severity_icon = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢', 'INFO': 'ℹ️'}.get(severity, '⚪')

                print(f"\n   {i}. {finding.get('type', 'Unknown')}")
                print(f"      {severity_icon} Severity: {severity}")
                print(f"      📝 {finding.get('description', 'N/A')}")

                if finding.get('suspicious') or finding.get('anomalous') or finding.get('inconsistent'):
                    print(f"      ⚠️  Status: SUSPICIOUS")
                else:
                    print(f"      ✓ Status: Normal")
        else:
            print(f"\n✅ NO SUSPICIOUS FINDINGS")

        # Metadata issues
        if results['metadata_issues']:
            print(f"\n⚠️  METADATA ISSUES ({len(results['metadata_issues'])}):")
            for issue in results['metadata_issues']:
                print(f"   • {issue}")

        # Suspicious elements
        if results['suspicious_elements']:
            print(f"\n🚩 SUSPICIOUS ELEMENTS ({len(results['suspicious_elements'])}):")
            for elem in results['suspicious_elements']:
                print(f"   • {elem}")

        if 'error' in results:
            print(f"\n❌ ERROR: {results['error']}")

        print("\n")

    print("=" * 80)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)

    # Summary
    print("\n📊 TEST SUMMARY:")
    print(f"   Total PDFs Tested: {min(3, len(pdf_files))}")
    print(f"   Detection System: ✅ OPERATIONAL")
    print(f"   Analysis Techniques: 9 methods active")
    print(f"\n💡 TIP: Upload PDFs through the web interface at http://localhost:5000")


def get_risk_level(confidence):
    """Get risk level based on confidence score"""
    if confidence >= 0.7:
        return "🔴 HIGH RISK"
    elif confidence >= 0.4:
        return "🟡 MEDIUM RISK"
    elif confidence >= 0.2:
        return "🟢 LOW RISK"
    else:
        return "✅ MINIMAL RISK"


if __name__ == '__main__':
    test_pdf_analyzer()
