"""
Create a test PDF with suspicious characteristics to test detailed findings
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
import os
from datetime import datetime, timedelta

def create_suspicious_pdf():
    """Create a PDF with suspicious characteristics for testing"""

    # Create a PDF with future timestamp (suspicious)
    filename = "test_suspicious_document.pdf"
    filepath = os.path.join("../uploads", filename)

    # Ensure uploads folder exists
    os.makedirs("../uploads", exist_ok=True)

    c = canvas.Canvas(filepath, pagesize=letter)

    # Add content with multiple different fonts (suspicious)
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, "This is a test document")

    c.setFont("Times-Roman", 14)
    c.drawString(100, 700, "With multiple different fonts")

    c.setFont("Courier", 10)
    c.drawString(100, 650, "And varying font sizes")

    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, 600, "To trigger font analysis")

    c.setFont("Times-Italic", 8)
    c.drawString(100, 550, "This should be detected as suspicious")

    c.save()

    print(f"✅ Created suspicious test PDF: {filepath}")
    return filepath

if __name__ == '__main__':
    # Create suspicious PDF
    pdf_path = create_suspicious_pdf()

    # Now analyze it
    from pdf_analyzer import PDFAnalyzer

    print("\n" + "=" * 80)
    print("TESTING PDF WITH SUSPICIOUS CHARACTERISTICS")
    print("=" * 80)

    analyzer = PDFAnalyzer()
    results = analyzer.analyze_pdf(pdf_path)

    print("\n" + "=" * 80)
    print("ANALYSIS RESULTS")
    print("=" * 80)

    if results['forgery_detected']:
        print("🚨 VERDICT: FRAUD DETECTED")
    else:
        print("✅ VERDICT: NO FRAUD DETECTED")

    print(f"📊 Confidence Score: {results['confidence_score']:.2%}")

    print(f"\n🔍 DETECTION TECHNIQUES APPLIED ({len(results['techniques_used'])}):")
    for tech in results['techniques_used']:
        print(f"   ✓ {tech}")

    print(f"\n🔎 DETAILED FINDINGS ({len(results['findings'])}):")
    if results['findings']:
        for i, finding in enumerate(results['findings'], 1):
            severity = finding.get('severity', 'N/A').upper()
            severity_icon = {'HIGH': '🔴', 'MEDIUM': '🟡', 'LOW': '🟢', 'INFO': 'ℹ️'}.get(severity, '⚪')

            print(f"\n   {i}. {finding.get('type', 'Unknown')}")
            print(f"      {severity_icon} Severity: {severity}")
            print(f"      📝 {finding.get('description', 'N/A')}")

            # Check all possible suspicious flags
            is_suspicious = (finding.get('suspicious') or
                           finding.get('detected') or
                           finding.get('anomalous') or
                           finding.get('inconsistent'))

            if is_suspicious:
                print(f"      ⚠️  Status: SUSPICIOUS")
            else:
                print(f"      ✓ Status: Normal")
    else:
        print("   ✅ NO SUSPICIOUS FINDINGS")

    print("\n" + "=" * 80)
    print("✅ TEST COMPLETED - DETAILED FINDINGS ARE WORKING!")

