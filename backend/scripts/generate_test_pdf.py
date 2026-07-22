import os
import fitz  # PyMuPDF

OUTPUT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "UPS_Technical_Specification_Test.pdf"))

def create_test_pdf():
    doc = fitz.open()

    pages_content = [
        # Page 1
        "DOCUMENT: Bengaluru Hyperscale Data Centre - UPS Technical Specification (R01)\n"
        "SECTION 7.4: UPS EFFICIENCY REQUIREMENTS\n\n"
        "1. Executive Summary: This specification defines technical parameters for all Uninterruptible Power Supply (UPS) units.\n"
        "2. Efficiency Baseline: The minimum required UPS efficiency is 96% across operating loads from 50% to 100%.\n"
        "3. High Efficiency Mode: Equipment capable of eco-mode operation must still maintain a double-conversion efficiency of at least 96%.\n"
        "4. Heat Rejection: Thermal dissipation calculations must be derived based on the 96% efficiency baseline.",

        # Page 2
        "DOCUMENT: Bengaluru Hyperscale Data Centre - UPS Technical Specification (R01)\n"
        "SECTION 7.5: BATTERY STORAGE AND AUTONOMY\n\n"
        "1. Battery Autonomy Requirement: The battery system shall provide a minimum of 15 minutes of autonomy at full rated 48 MW load.\n"
        "2. Cell Chemistry: Lithium-ion battery racks rated for fast discharge capability.\n"
        "3. Runtime Compliance: Submittals featuring autonomy below 15 minutes shall be rejected as non-compliant.",

        # Page 3
        "DOCUMENT: Bengaluru Hyperscale Data Centre - UPS Technical Specification (R01)\n"
        "SECTION 7.6: SYSTEM REDUNDANCY AND TOPOLOGY\n\n"
        "1. Redundancy Configuration: The UPS system topology shall be configured for N+1 redundancy.\n"
        "2. Fault Isolation: Each parallel UPS module shall include independent static bypass switches and isolation breakers.\n"
        "3. Concurrent Maintainability: System topology must ensure full concurrent maintainability without taking down IT loads.",

        # Page 4
        "DOCUMENT: Bengaluru Hyperscale Data Centre - UPS Technical Specification (R01)\n"
        "SECTION 8.1: EMERGENCY GENERATOR SYSTEMS\n\n"
        "1. Fuel Autonomy Baseline: Generator diesel fuel storage capacity must guarantee a minimum generator runtime of 48 hours.\n"
        "2. Fuel Transfer System: Dual redundant transfer pumps with day tank automatic fill capability.\n"
        "3. Continuous Rating: Generators must be rated for continuous mission-critical standby service.",

        # Page 5
        "DOCUMENT: Bengaluru Hyperscale Data Centre - UPS Technical Specification (R01)\n"
        "SECTION 9.2: COOLING SYSTEM SPECIFICATIONS\n\n"
        "1. Cooling Redundancy: Data hall cooling system configuration must maintain N+1 redundancy for all chiller units and CRAH modules.\n"
        "2. Temperature Setpoints: Supply air temperature to be maintained at 24°C ± 1°C.\n"
        "3. Chilled Water Loop: Dual ring header topology for pipework fault isolation."
    ]

    for text in pages_content:
        page = doc.new_page(width=595, height=842) # A4 size
        rect = fitz.Rect(50, 50, 545, 792)
        page.insert_textbox(rect, text, fontsize=12, fontname="helv")

    doc.save(OUTPUT_PATH)
    doc.close()
    print(f"Generated test PDF at: {OUTPUT_PATH}")
    return OUTPUT_PATH

if __name__ == "__main__":
    create_test_pdf()
