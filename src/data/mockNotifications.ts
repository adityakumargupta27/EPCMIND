import type { Notification } from "@/types";

export const mockNotifications: Notification[] = [
  {
    id: "N1",
    severity: "CRITICAL",
    title: "UPS-04 Delivery Delay",
    message: "Delivery delay may affect Integrated Systems Testing milestone.",
    time: "10 min ago",
    read: false,
  },
  {
    id: "N2",
    severity: "HIGH",
    title: "Cooling System Deviation",
    message: "Vendor submission contains specification deviation.",
    time: "42 min ago",
    read: false,
  },
  {
    id: "N3",
    severity: "MEDIUM",
    title: "Similar RFI Detected",
    message: "RFI-042 matches previously resolved RFI-017.",
    time: "1 h ago",
    read: false,
  },
  {
    id: "N4",
    severity: "INFO",
    title: "Document Indexed",
    message: "Electrical specification successfully indexed.",
    time: "2 h ago",
    read: true,
  },
];

export const recentActivity = [
  { time: "10:42 AM", text: "AI Compliance Agent identified UPS efficiency deviation." },
  { time: "10:18 AM", text: "RFI-042 similarity analysis completed." },
  { time: "09:45 AM", text: "UPS vendor submittal uploaded." },
  { time: "Yesterday", text: "Schedule Risk Engine identified procurement delay." },
  { time: "Yesterday", text: "Cooling system commissioning plan reviewed." },
];
