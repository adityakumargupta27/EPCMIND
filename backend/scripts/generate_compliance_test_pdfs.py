import os
import fitz

def generate_requirement_pdf():
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "test_pdfs", "Requirement_Specification_Test.pdf"))
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    doc = fitz.open()

    pages_content = [
        "Data Centre Electrical Specification - Requirement Document\nPage 1\nSection 7.4 UPS Efficiency Requirements\n\nThe Uninterruptible Power Supply (UPS) module efficiency shall be greater than or equal to 96% (>=96%) at full rated load under normal operating conditions.",
        "Data Centre Electrical Specification - Requirement Document\nPage 2\nSection 7.5 Battery Autonomy Requirements\n\nThe UPS battery energy storage system shall provide a minimum battery autonomy time of 15 minutes (>=15 minutes) at full rated system load.",
        "Data Centre Electrical Specification - Requirement Document\nPage 3\nSection 7.6 Redundancy Topology\n\nThe total UPS configuration and power distribution topology must adhere to N+1 redundancy requirements to eliminate single points of failure.",
        "Data Centre Electrical Specification - Requirement Document\nPage 4\nSection 8.1 Emergency Generator System\n\nEmergency backup diesel generators must store sufficient fuel to ensure a continuous runtime of at least 48 hours (>=48 hours) under full emergency load.",
        "Data Centre Electrical Specification - Requirement Document\nPage 5\nSection 9.2 Cooling Systems\n\nThe central chilled water system and CRAC cooling infrastructure must provide N+1 redundancy across all active cooling trains.",
        "Data Centre Electrical Specification - Requirement Document\nPage 6\nSection 10.1 Battery Design Life\n\nAll VRLA or Lithium-ion battery modules installed within the UPS system must feature a minimum certified design life of 10 years (>=10 years)."
    ]

    for text in pages_content:
        page = doc.new_page()
        page.insert_text((50, 50), text, fontsize=11)

    doc.save(pdf_path)
    doc.close()
    print(f"[PDF GENERATOR] Created requirement PDF: {pdf_path}")
    return pdf_path

def generate_vendor_pdf():
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "test_pdfs", "Vendor_Submittal_Test.pdf"))
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    doc = fitz.open()

    pages_content = [
        "Vendor Technical Submittal - Equipment Proposal\nPage 1\nSection 7.4 UPS Efficiency Submission\n\nOur proposed UPS system achieves an operational efficiency of 94.8% at full rated capacity, offering optimized energy performance.",
        "Vendor Technical Submittal - Equipment Proposal\nPage 2\nSection 7.5 Battery Submittal\n\nThe submitted battery bank design provides 12 minutes of autonomy time at full rated capacity.",
        "Vendor Technical Submittal - Equipment Proposal\nPage 3\nSection 7.6 Redundancy Topology\n\nThe equipment arrangement complies with N+1 redundancy using dual parallel module configurations.",
        "Vendor Technical Submittal - Equipment Proposal\nPage 4\nSection 8.1 Emergency Generator Submittal\n\nOn-site diesel fuel storage tanks provide emergency generator runtime capacity of 52 hours at 100% emergency rated output.",
        "Vendor Technical Submittal - Equipment Proposal\nPage 5\nSection 9.2 Cooling Systems\n\nThe supplied cooling modules feature standard N configuration without active parallel redundant chillers.",
        "Vendor Technical Submittal - Equipment Proposal\nPage 6\nSection 11.0 Commercial Warranty\n\nStandard 2-year parts and labor warranty is provided for all electrical equipment."
    ]

    for text in pages_content:
        page = doc.new_page()
        page.insert_text((50, 50), text, fontsize=11)

    doc.save(pdf_path)
    doc.close()
    print(f"[PDF GENERATOR] Created vendor PDF: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    generate_requirement_pdf()
    generate_vendor_pdf()
