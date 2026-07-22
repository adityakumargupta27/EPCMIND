import type { RFI } from "@/types";

export const mockRFIs: RFI[] = [
  {
    id: "RFI-042",
    subject: "UPS Room Cable Routing Conflict",
    discipline: "Electrical",
    priority: "HIGH",
    status: "Open",
    aiMatch: 91,
    created: "20 Jul 2026",
    raisedBy: "Electrical Contractor",
    question:
      "Can UPS room cable routing be shifted 300mm due to structural beam interference identified during installation?",
    similar: {
      id: "RFI-017",
      subject: "Cable Tray Routing Adjustment",
      match: 91,
      question: "Cable tray conflicts with structural beam.",
      resolution:
        "Routing may be shifted up to 400mm subject to minimum cable bend-radius requirements and consultant approval.",
    },
    suggested:
      "Approve the proposed 300mm cable routing adjustment subject to cable bend-radius verification and submission of updated coordinated shop drawings for consultant approval.",
  },
  {
    id: "RFI-041",
    subject: "Cooling Pipe Clearance",
    discipline: "Mechanical",
    priority: "MEDIUM",
    status: "Awaiting Response",
    aiMatch: 84,
    created: "18 Jul 2026",
  },
  {
    id: "RFI-040",
    subject: "Generator Exhaust Routing",
    discipline: "Mechanical",
    priority: "HIGH",
    status: "Resolved",
    aiMatch: 76,
    created: "14 Jul 2026",
  },
  {
    id: "RFI-039",
    subject: "Fire Suppression Zoning",
    discipline: "FLS",
    priority: "MEDIUM",
    status: "Open",
    aiMatch: 68,
    created: "12 Jul 2026",
  },
  {
    id: "RFI-038",
    subject: "Data Hall Floor Loading",
    discipline: "Civil",
    priority: "LOW",
    status: "Resolved",
    aiMatch: 55,
    created: "09 Jul 2026",
  },
  {
    id: "RFI-037",
    subject: "PDU Metering Requirements",
    discipline: "Electrical",
    priority: "MEDIUM",
    status: "Awaiting Response",
    aiMatch: 72,
    created: "07 Jul 2026",
  },
];

export const rfiStats = {
  open: 14,
  critical: 3,
  awaiting: 8,
  closed: 63,
  avgResolution: "2.8 days",
  aiMatches: 21,
};
