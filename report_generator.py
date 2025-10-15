"""
Report Generation Module
Creates comprehensive PDF reports of fraud detection analysis
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os


class ReportGenerator:
    """Generates detailed fraud detection reports"""

    def __init__(self, report_folder='reports'):
        self.report_folder = report_folder
        os.makedirs(report_folder, exist_ok=True)

    def generate_report(self, analysis_results, file_info):
        """Generate comprehensive report"""

        # Create filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"fraud_detection_report_{timestamp}.pdf"
        report_path = os.path.join(self.report_folder, report_filename)

        # Create PDF
        doc = SimpleDocTemplate(report_path, pagesize=letter,
                              topMargin=0.75*inch, bottomMargin=0.75*inch)

        # Container for elements
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )

        # Title
        title = Paragraph("AI FRAUD DETECTION ANALYSIS REPORT", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))

        # Executive Summary
        elements.append(Paragraph("EXECUTIVE SUMMARY", heading_style))

        summary_data = [
            ['Report Date:', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ['File Analyzed:', file_info.get('filename', 'N/A')],
            ['File Type:', file_info.get('type', 'N/A')],
            ['File Size:', file_info.get('size', 'N/A')],
            ['Analysis Type:', file_info.get('analysis_type', 'N/A')]
        ]

        summary_table = Table(summary_data, colWidths=[2*inch, 4*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))

        # Overall Result
        elements.append(Paragraph("ANALYSIS RESULT", heading_style))

        # Handle different result types (image/pdf tampering vs code AI detection)
        is_code_analysis = file_info.get('type') == 'code'

        if is_code_analysis:
            fraud_detected = analysis_results.get('ai_generated', False)
            status = "AI-GENERATED CODE DETECTED" if fraud_detected else "LIKELY HUMAN-WRITTEN CODE"
        else:
            fraud_detected = analysis_results.get('tampering_detected', False) or \
                            analysis_results.get('forgery_detected', False)
            status = "FRAUD DETECTED" if fraud_detected else "NO FRAUD DETECTED"

        status_color = colors.red if fraud_detected else colors.green
        confidence = analysis_results.get('confidence_score', 0.0)

        result_data = [
            ['Status:', status],
            ['Confidence Score:', f"{confidence:.1%}"],
            ['Risk Level:', self._get_risk_level(confidence)]
        ]

        result_table = Table(result_data, colWidths=[2*inch, 4*inch])
        result_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (1, 0), (1, 0), status_color),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))

        elements.append(result_table)
        elements.append(Spacer(1, 0.3*inch))

        # Techniques Used
        if 'techniques_used' in analysis_results:
            elements.append(Paragraph("DETECTION TECHNIQUES APPLIED", heading_style))

            techniques_text = "<br/>".join([f"• {tech}" for tech in analysis_results['techniques_used']])
            elements.append(Paragraph(techniques_text, styles['Normal']))
            elements.append(Spacer(1, 0.2*inch))

        # Detailed Findings
        if analysis_results.get('findings'):
            elements.append(Paragraph("DETAILED FINDINGS", heading_style))

            for idx, finding in enumerate(analysis_results['findings'], 1):
                finding_title = f"Finding #{idx}: {finding.get('type', finding.get('technique', 'Unknown'))}"
                elements.append(Paragraph(finding_title, styles['Heading3']))

                finding_text = f"<b>Description:</b> {finding.get('description', 'N/A')}<br/>"

                if 'score' in finding:
                    finding_text += f"<b>Confidence:</b> {finding['score']:.1%}<br/>"

                if 'severity' in finding:
                    finding_text += f"<b>Severity:</b> {finding['severity'].upper()}<br/>"

                if finding.get('suspicious') or finding.get('detected') or finding.get('inconsistent'):
                    finding_text += "<b>Status:</b> <font color='red'>SUSPICIOUS</font>"
                else:
                    finding_text += "<b>Status:</b> <font color='green'>PASSED</font>"

                elements.append(Paragraph(finding_text, styles['Normal']))
                elements.append(Spacer(1, 0.15*inch))

        # Code Quality Metrics (for code analysis)
        if 'code_quality_metrics' in analysis_results and analysis_results['code_quality_metrics']:
            elements.append(Paragraph("CODE QUALITY METRICS", heading_style))

            metrics = analysis_results['code_quality_metrics']
            metrics_data = []
            for key, value in metrics.items():
                metrics_data.append([key.replace('_', ' ').title(), str(value)])

            if metrics_data:
                metrics_table = Table(metrics_data, colWidths=[2*inch, 4*inch])
                metrics_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]))
                elements.append(metrics_table)
                elements.append(Spacer(1, 0.2*inch))

        # Metadata Issues
        if analysis_results.get('metadata_issues'):
            elements.append(Paragraph("METADATA ANOMALIES", heading_style))

            for issue in analysis_results['metadata_issues']:
                issue_text = f"<b>Type:</b> {issue.get('type', 'N/A')}<br/>"
                issue_text += f"<b>Severity:</b> {issue.get('severity', 'N/A').upper()}<br/>"
                issue_text += f"<b>Description:</b> {issue.get('description', 'N/A')}"

                elements.append(Paragraph(issue_text, styles['Normal']))
                elements.append(Spacer(1, 0.1*inch))

        # PDF Specific Results
        if 'metadata' in analysis_results and analysis_results.get('analysis_type') == 'pdf':
            elements.append(PageBreak())
            elements.append(Paragraph("PDF DOCUMENT ANALYSIS", heading_style))

            metadata = analysis_results['metadata']
            if metadata:
                pdf_data = []
                for key, value in metadata.items():
                    if key != 'anomalies' and not isinstance(value, (list, dict)):
                        pdf_data.append([str(key), str(value)])

                if pdf_data:
                    pdf_table = Table(pdf_data, colWidths=[2*inch, 4*inch])
                    pdf_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ]))
                    elements.append(pdf_table)

        # Recommendations
        elements.append(PageBreak())
        elements.append(Paragraph("RECOMMENDATIONS", heading_style))

        recommendations = self._generate_recommendations(analysis_results, fraud_detected, is_code_analysis)
        for rec in recommendations:
            elements.append(Paragraph(f"• {rec}", styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))

        # Footer
        elements.append(Spacer(1, 0.5*inch))
        footer_text = """
        <para align=center>
        <b>--- End of Report ---</b><br/>
        This report was automatically generated by AI Fraud Detection Agent v1.0<br/>
        For questions or concerns, please contact your security administrator.
        </para>
        """
        elements.append(Paragraph(footer_text, styles['Normal']))

        # Build PDF
        doc.build(elements)

        print(f"[+] Report generated: {report_path}")
        return report_path

    def _get_risk_level(self, confidence):
        """Determine risk level from confidence score"""
        if confidence >= 0.8:
            return "CRITICAL"
        elif confidence >= 0.6:
            return "HIGH"
        elif confidence >= 0.4:
            return "MEDIUM"
        elif confidence >= 0.2:
            return "LOW"
        else:
            return "MINIMAL"

    def _generate_recommendations(self, results, fraud_detected, is_code_analysis=False):
        """Generate recommendations based on analysis"""
        recommendations = []

        if is_code_analysis:
            if fraud_detected:
                recommendations.append("CODE APPEARS TO BE AI-GENERATED: Multiple AI patterns detected.")
                recommendations.append("Review the code carefully for logic errors or security vulnerabilities.")
                recommendations.append("Verify that the code meets your organization's quality standards.")
                recommendations.append("Consider having a senior developer review the implementation.")
                recommendations.append("If this was submitted as original work, discuss AI usage policies.")
            else:
                recommendations.append("Code appears to be human-written based on current analysis.")
                recommendations.append("However, advanced AI tools can sometimes evade detection.")
                recommendations.append("Consider code review and testing as additional verification.")
                recommendations.append("Maintain documentation of development process.")
        else:
            if fraud_detected:
                recommendations.append("IMMEDIATE ACTION REQUIRED: The analyzed document shows signs of tampering or forgery.")
                recommendations.append("Do NOT use this document for official purposes until verified by a forensic expert.")
                recommendations.append("Preserve the original file and all metadata for potential legal proceedings.")
                recommendations.append("Contact the document issuer to obtain a verified authentic copy.")
                recommendations.append("Consider reporting this incident to relevant authorities if fraud is suspected.")
            else:
                recommendations.append("No obvious signs of fraud detected in the preliminary analysis.")
                recommendations.append("However, this analysis does not guarantee 100% authenticity.")
                recommendations.append("For critical applications, consider additional verification methods.")
                recommendations.append("Maintain secure storage and handling of the document.")

        # Specific recommendations based on findings
        if results.get('metadata_issues'):
            recommendations.append("Review metadata anomalies listed above - they may indicate manipulation.")

        if results.get('suspicious_elements'):
            recommendations.append("Suspicious embedded elements detected - exercise caution when opening.")

        return recommendations
