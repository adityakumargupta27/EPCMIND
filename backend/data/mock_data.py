mock_project = {
    "name": "Bengaluru Hyperscale Data Centre",
    "code": "BLR-DC-01",
    "location": "Bengaluru, Karnataka, India",
    "facilityType": "Hyperscale Data Centre",
    "capacity": "48 MW",
    "tier": "Tier III",
    "phase": "MEP Installation & Commissioning",
    "progress": 72,
    "health": 78,
    "status": "At Risk",
    "completion": "September 2026",
}

health_breakdown = [
    {"name": "Schedule Health", "value": 74},
    {"name": "Quality Health", "value": 88},
    {"name": "Procurement Health", "value": 61},
    {"name": "Engineering Health", "value": 84},
    {"name": "Commissioning Readiness", "value": 69},
]

progress_breakdown = [
    {"name": "Civil Works", "value": 100},
    {"name": "Electrical", "value": 76},
    {"name": "Mechanical", "value": 69},
    {"name": "Cooling Systems", "value": 64},
    {"name": "IT Infrastructure", "value": 58},
    {"name": "Commissioning", "value": 34},
]

project_team = [
    {"name": "Arjun Mehta", "role": "Project Manager"},
    {"name": "Priya Sharma", "role": "Engineering Lead"},
    {"name": "Rahul Verma", "role": "Electrical Lead"},
    {"name": "Neha Rao", "role": "Quality Manager"},
    {"name": "Vikram Singh", "role": "Commissioning Manager"},
]

disciplines = [
    {"name": "Civil", "progress": 100, "health": 95},
    {"name": "Electrical", "progress": 76, "health": 82},
    {"name": "Mechanical", "progress": 69, "health": 78},
    {"name": "Cooling", "progress": 64, "health": 71},
    {"name": "Fire & Life Safety", "progress": 58, "health": 84},
    {"name": "ICT", "progress": 48, "health": 80},
    {"name": "Commissioning", "progress": 34, "health": 69},
]

equipment_list = [
    {"id": "UPS-04", "type": "UPS", "status": "Delayed", "severity": "CRITICAL"},
    {"id": "CH-02", "type": "Chiller", "status": "On Track", "severity": "NORMAL"},
    {"id": "GEN-03", "type": "Generator", "status": "Delivered", "severity": "NORMAL"},
    {"id": "SWGR-02", "type": "Switchgear", "status": "Installation", "severity": "MONITOR"},
]

mock_documents = [
    {
        "id": "DOC-001",
        "name": "Electrical Design Specification",
        "category": "Engineering Specification",
        "revision": "R04",
        "uploaded": "18 Jul 2026",
        "uploadedBy": "Priya Sharma",
        "status": "Approved",
        "aiIndex": "Indexed",
        "discipline": "Electrical",
        "summary": "Defines electrical design criteria for the 48 MW facility including UPS redundancy (N+1), minimum UPS efficiency of 96% at 50–100% load, and battery autonomy of at least 15 minutes."
    },
    {
        "id": "DOC-002",
        "name": "UPS Technical Specification",
        "category": "Equipment Specification",
        "revision": "R02",
        "uploaded": "15 Jul 2026",
        "uploadedBy": "Rahul Verma",
        "status": "Approved",
        "aiIndex": "Indexed",
        "discipline": "Electrical",
        "summary": "Technical specification for UPS units UPS-01 through UPS-06."
    },
    {
        "id": "DOC-003",
        "name": "UPS Vendor Submittal",
        "category": "Vendor Submittal",
        "revision": "R01",
        "uploaded": "19 Jul 2026",
        "uploadedBy": "Rahul Verma",
        "status": "Under Review",
        "aiIndex": "Indexed",
        "discipline": "Electrical",
        "summary": "Vendor submittal for UPS-04. Efficiency stated at 94.8%. Battery autonomy 12 minutes."
    },
    {
        "id": "DOC-004",
        "name": "Cooling System Specification",
        "category": "Engineering Specification",
        "revision": "R03",
        "uploaded": "12 Jul 2026",
        "uploadedBy": "Priya Sharma",
        "status": "Approved",
        "aiIndex": "Indexed",
        "discipline": "Mechanical"
    },
    {
        "id": "DOC-005",
        "name": "Commissioning Requirements",
        "category": "Commissioning",
        "revision": "R02",
        "uploaded": "17 Jul 2026",
        "uploadedBy": "Vikram Singh",
        "status": "Approved",
        "aiIndex": "Processing",
        "discipline": "Commissioning"
    },
    {
        "id": "DOC-006",
        "name": "Generator Vendor Submittal",
        "category": "Vendor Submittal",
        "revision": "R02",
        "uploaded": "10 Jul 2026",
        "uploadedBy": "Rahul Verma",
        "status": "Approved",
        "aiIndex": "Indexed",
        "discipline": "Electrical"
    },
    {
        "id": "DOC-007",
        "name": "Fire & Life Safety Drawings",
        "category": "Drawing",
        "revision": "R01",
        "uploaded": "08 Jul 2026",
        "uploadedBy": "Neha Rao",
        "status": "Approved",
        "aiIndex": "Indexed",
        "discipline": "FLS"
    },
    {
        "id": "DOC-008",
        "name": "Quality Assurance Plan",
        "category": "Quality",
        "revision": "R03",
        "uploaded": "05 Jul 2026",
        "uploadedBy": "Neha Rao",
        "status": "Approved",
        "aiIndex": "Indexed",
        "discipline": "Quality"
    }
]

document_stats = {
    "total": 248,
    "indexed": 236,
    "processing": 7,
    "needsReview": 5
}

mock_compliance = [
    {
        "id": "CC-001",
        "equipment": "UPS-04",
        "parameter": "Efficiency",
        "requirement": "≥96%",
        "vendorValue": "94.8%",
        "status": "NON-COMPLIANT",
        "severity": "HIGH",
        "deviation": "-1.2%",
        "analysis": "Vendor efficiency falls below project requirement and may increase operational energy losses over the facility lifecycle.",
        "impact": ["Energy efficiency target", "Operating expenditure", "Specification acceptance"],
        "action": "Request revised equipment selection or obtain formal engineering deviation approval.",
        "sources": ["Electrical Design Specification §7.4.3", "UPS Vendor Submittal §3.2"]
    },
    {
        "id": "CC-002",
        "equipment": "UPS-04",
        "parameter": "Battery Autonomy",
        "requirement": "≥15 min",
        "vendorValue": "12 min",
        "status": "NON-COMPLIANT",
        "severity": "HIGH",
        "deviation": "-3 min",
        "analysis": "Battery autonomy below minimum requirement may impact ride-through capability.",
        "impact": ["Ride-through capability", "Tier III compliance"],
        "action": "Require vendor to upsize battery string or provide equivalent extended runtime module.",
        "sources": ["Electrical Design Specification §7.5.1", "UPS Vendor Submittal §4.1"]
    },
    {
        "id": "CC-003",
        "equipment": "UPS-04",
        "parameter": "Redundancy",
        "requirement": "N+1",
        "vendorValue": "N+1",
        "status": "COMPLIANT",
        "severity": "LOW"
    },
    {
        "id": "CC-004",
        "equipment": "CH-02",
        "parameter": "Cooling Redundancy",
        "requirement": "N+1",
        "vendorValue": "N",
        "status": "NON-COMPLIANT",
        "severity": "HIGH",
        "analysis": "Chiller redundancy configuration does not meet Tier III requirement.",
        "impact": ["Cooling availability", "Tier III certification"],
        "action": "Add redundant chiller unit or reconfigure existing plant to achieve N+1.",
        "sources": ["Cooling System Specification §5.2"]
    },
    {
        "id": "CC-005",
        "equipment": "GEN-03",
        "parameter": "Runtime",
        "requirement": "≥48 hours",
        "vendorValue": "52 hours",
        "status": "COMPLIANT",
        "severity": "LOW"
    },
    {
        "id": "CC-006",
        "equipment": "SWGR-02",
        "parameter": "Short-circuit Rating",
        "requirement": "65 kA",
        "vendorValue": "65 kA",
        "status": "COMPLIANT",
        "severity": "LOW"
    },
    {
        "id": "CC-007",
        "equipment": "CH-02",
        "parameter": "IPLV Efficiency",
        "requirement": "≥0.45 kW/TR",
        "vendorValue": "0.47 kW/TR",
        "status": "WARNING",
        "severity": "MEDIUM",
        "analysis": "Slight deviation from target IPLV; within tolerance but should be monitored.",
        "action": "Confirm test conditions and validate factory acceptance test data."
    }
]

compliance_stats = {
    "total": 47,
    "compliant": 38,
    "warnings": 3,
    "nonCompliant": 6,
    "highSeverity": 2
}

mock_rfis = [
    {
        "id": "RFI-042",
        "subject": "UPS Room Cable Routing Conflict",
        "discipline": "Electrical",
        "priority": "HIGH",
        "status": "Open",
        "aiMatch": 91,
        "created": "20 Jul 2026",
        "raisedBy": "Electrical Contractor",
        "question": "Can UPS room cable routing be shifted 300mm due to structural beam interference identified during installation?",
        "similar": {
            "id": "RFI-017",
            "subject": "Cable Tray Routing Adjustment",
            "match": 91,
            "question": "Cable tray conflicts with structural beam.",
            "resolution": "Routing may be shifted up to 400mm subject to minimum cable bend-radius requirements and consultant approval."
        },
        "suggested": "Approve the proposed 300mm cable routing adjustment subject to cable bend-radius verification and submission of updated coordinated shop drawings for consultant approval."
    },
    {
        "id": "RFI-041",
        "subject": "Cooling Pipe Clearance",
        "discipline": "Mechanical",
        "priority": "MEDIUM",
        "status": "Awaiting Response",
        "aiMatch": 84,
        "created": "18 Jul 2026"
    },
    {
        "id": "RFI-040",
        "subject": "Generator Exhaust Routing",
        "discipline": "Mechanical",
        "priority": "HIGH",
        "status": "Resolved",
        "aiMatch": 76,
        "created": "14 Jul 2026"
    },
    {
        "id": "RFI-039",
        "subject": "Fire Suppression Zoning",
        "discipline": "FLS",
        "priority": "MEDIUM",
        "status": "Open",
        "aiMatch": 68,
        "created": "12 Jul 2026"
    },
    {
        "id": "RFI-038",
        "subject": "Data Hall Floor Loading",
        "discipline": "Civil",
        "priority": "LOW",
        "status": "Resolved",
        "aiMatch": 55,
        "created": "09 Jul 2026"
    },
    {
        "id": "RFI-037",
        "subject": "PDU Metering Requirements",
        "discipline": "Electrical",
        "priority": "MEDIUM",
        "status": "Awaiting Response",
        "aiMatch": 72,
        "created": "07 Jul 2026"
    }
]

rfi_stats = {
    "open": 14,
    "critical": 3,
    "awaiting": 8,
    "closed": 63,
    "avgResolution": "2.8 days",
    "aiMatches": 21
}

mock_risks = [
    {
        "id": "RSK-001",
        "title": "UPS-04 Delivery Delay",
        "category": "Procurement",
        "probability": 85,
        "impact": "8 Days",
        "severity": "CRITICAL",
        "milestone": "Integrated Systems Testing",
        "status": "Open",
        "detail": {
            "equipment": "UPS-04",
            "plannedDelivery": "12 July 2026",
            "currentEstimate": "24 July 2026",
            "delay": "12 Days",
            "float": "4 Days",
            "criticalImpact": "8 Days",
            "analysis": "The current equipment delivery forecast exceeds available activity float and creates direct exposure to the integrated testing milestone.",
            "mitigations": [
                "Expedite vendor shipment.",
                "Evaluate partial shipment strategy.",
                "Resequence downstream electrical installation.",
                "Allocate dedicated installation crew upon arrival.",
                "Review commissioning sequence."
            ]
        }
    },
    {
        "id": "RSK-002",
        "title": "Cooling System Installation Delay",
        "category": "Schedule",
        "probability": 72,
        "impact": "5 Days",
        "severity": "HIGH",
        "milestone": "Cooling Completion",
        "status": "Monitoring",
        "detail": {
            "analysis": "Piping installation crew productivity trending below plan due to coordination clashes.",
            "mitigations": [
                "Add additional piping crew.",
                "Fast-track MEP coordination sign-off."
            ]
        }
    },
    {
        "id": "RSK-003",
        "title": "UPS Efficiency Deviation",
        "category": "Quality",
        "probability": 88,
        "impact": "High",
        "severity": "HIGH",
        "milestone": "Equipment Approval",
        "status": "Open",
        "detail": {
            "analysis": "Vendor submitted 94.8% efficiency versus 96% required.",
            "mitigations": [
                "Request revised equipment revision.",
                "Initiate engineering deviation approval process."
            ]
        }
    },
    {
        "id": "RSK-004",
        "title": "Battery Autonomy Deviation",
        "category": "Engineering",
        "probability": 82,
        "impact": "Medium",
        "severity": "HIGH",
        "milestone": "Equipment Approval",
        "status": "Open"
    },
    {
        "id": "RSK-005",
        "title": "Commissioning Resource Availability",
        "category": "Commissioning",
        "probability": 55,
        "impact": "3 Days",
        "severity": "MEDIUM",
        "milestone": "Final Commissioning",
        "status": "Monitoring"
    },
    {
        "id": "RSK-006",
        "title": "Cable Tray Coordination Clashes",
        "category": "Engineering",
        "probability": 60,
        "impact": "2 Days",
        "severity": "MEDIUM",
        "milestone": "Electrical Integration",
        "status": "Open"
    },
    {
        "id": "RSK-007",
        "title": "Switchgear FAT Slippage",
        "category": "Procurement",
        "probability": 48,
        "impact": "4 Days",
        "severity": "MEDIUM",
        "milestone": "Electrical Integration",
        "status": "Monitoring"
    },
    {
        "id": "RSK-008",
        "title": "Generator Exhaust Permit",
        "category": "Compliance",
        "probability": 40,
        "impact": "Medium",
        "severity": "MEDIUM",
        "milestone": "Commissioning",
        "status": "Open"
    },
    {
        "id": "RSK-009",
        "title": "IT White Space Cleanliness",
        "category": "Quality",
        "probability": 30,
        "impact": "Low",
        "severity": "LOW",
        "milestone": "Handover",
        "status": "Monitoring"
    },
    {
        "id": "RSK-010",
        "title": "Weather Impact on Rooftop Works",
        "category": "Schedule",
        "probability": 25,
        "impact": "Low",
        "severity": "LOW",
        "milestone": "Cooling Completion",
        "status": "Monitoring"
    },
    {
        "id": "RSK-011",
        "title": "Documentation Handover Readiness",
        "category": "Quality",
        "probability": 35,
        "impact": "Low",
        "severity": "LOW",
        "milestone": "Handover",
        "status": "Open"
    }
]

risk_stats = {
    "total": 11,
    "critical": 3,
    "high": 4,
    "medium": 4,
    "low": 8,
    "exposureDays": 18,
    "highestArea": "Procurement"
}

risk_distribution = [
    {"name": "Critical", "value": 3, "color": "#EF4444"},
    {"name": "High", "value": 4, "color": "#F59E0B"},
    {"name": "Medium", "value": 4, "color": "#3B82F6"},
    {"name": "Low", "value": 8, "color": "#22C55E"}
]

schedule_activities = [
    {"id": "A1", "name": "Civil Works", "start": "Jan 2026", "finish": "May 2026", "progress": 100, "critical": False, "status": "On Track"},
    {"id": "A2", "name": "Electrical Installation", "start": "Mar 2026", "finish": "Aug 2026", "progress": 76, "critical": True, "status": "At Risk"},
    {"id": "A3", "name": "UPS Installation", "start": "Jun 2026", "finish": "Jul 2026", "progress": 45, "critical": True, "status": "At Risk"},
    {"id": "A4", "name": "Cooling Installation", "start": "Apr 2026", "finish": "Aug 2026", "progress": 64, "critical": False, "status": "Monitor"},
    {"id": "A5", "name": "Generator Installation", "start": "May 2026", "finish": "Jul 2026", "progress": 88, "critical": False, "status": "On Track"},
    {"id": "A6", "name": "Integrated Systems Testing", "start": "Aug 2026", "finish": "Aug 2026", "progress": 0, "critical": True, "status": "At Risk"},
    {"id": "A7", "name": "Commissioning", "start": "Aug 2026", "finish": "Sep 2026", "progress": 12, "critical": True, "status": "Planned"}
]

milestones = [
    {"name": "UPS Installation Complete", "planned": "20 Jul 2026", "forecast": "28 Jul 2026", "variance": "+8 Days", "status": "At Risk"},
    {"name": "Cooling Completion", "planned": "02 Aug 2026", "forecast": "04 Aug 2026", "variance": "+2 Days", "status": "Monitor"},
    {"name": "Integrated Systems Testing", "planned": "12 Aug 2026", "forecast": "20 Aug 2026", "variance": "+8 Days", "status": "At Risk"},
    {"name": "Final Commissioning", "planned": "28 Aug 2026", "forecast": "05 Sep 2026", "variance": "+8 Days", "status": "At Risk"}
]

upcoming_milestones = [
    {"name": "UPS Installation", "planned": "26 Jul 2026", "forecast": "28 Jul 2026", "variance": "+2 Days", "status": "At Risk"},
    {"name": "Cooling System Completion", "planned": "02 Aug 2026", "forecast": "04 Aug 2026", "variance": "+2 Days", "status": "On Track"},
    {"name": "Integrated Systems Testing", "planned": "12 Aug 2026", "forecast": "20 Aug 2026", "variance": "+8 Days", "status": "At Risk"},
    {"name": "Commissioning Completion", "planned": "28 Aug 2026", "forecast": "05 Sep 2026", "variance": "+8 Days", "status": "Planned"}
]

schedule_stats = {
    "progress": 72,
    "activities": 184,
    "completed": 112,
    "inProgress": 48,
    "delayed": 9,
    "critical": 15
}

critical_path = [
    {"name": "UPS Delivery", "status": "12 Days Delayed", "severity": "CRITICAL"},
    {"name": "UPS Installation", "status": "Pending", "severity": "HIGH"},
    {"name": "Electrical Integration", "status": "Not Started", "severity": "MEDIUM"},
    {"name": "Integrated Systems Testing", "status": "Not Started", "severity": "HIGH"},
    {"name": "Commissioning", "status": "Not Started", "severity": "MEDIUM"}
]

mock_notifications = [
    {
        "id": "N1",
        "severity": "CRITICAL",
        "title": "UPS-04 Delivery Delay",
        "message": "Delivery delay may affect Integrated Systems Testing milestone.",
        "time": "10 min ago",
        "read": False
    },
    {
        "id": "N2",
        "severity": "HIGH",
        "title": "Cooling System Deviation",
        "message": "Vendor submission contains specification deviation.",
        "time": "42 min ago",
        "read": False
    },
    {
        "id": "N3",
        "severity": "MEDIUM",
        "title": "Similar RFI Detected",
        "message": "RFI-042 matches previously resolved RFI-017.",
        "time": "1 h ago",
        "read": False
    },
    {
        "id": "N4",
        "severity": "INFO",
        "title": "Document Indexed",
        "message": "Electrical specification successfully indexed.",
        "time": "2 h ago",
        "read": True
    }
]

recent_activity = [
    {"time": "10:42 AM", "text": "AI Compliance Agent identified UPS efficiency deviation."},
    {"time": "10:18 AM", "text": "RFI-042 similarity analysis completed."},
    {"time": "09:45 AM", "text": "UPS vendor submittal uploaded."},
    {"time": "Yesterday", "text": "Schedule Risk Engine identified procurement delay."},
    {"time": "Yesterday", "text": "Cooling system commissioning plan reviewed."}
]
