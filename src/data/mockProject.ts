import type { Project } from "@/types";

export const mockProject: Project = {
  name: "Bengaluru Hyperscale Data Centre",
  code: "BLR-DC-01",
  location: "Bengaluru, Karnataka, India",
  facilityType: "Hyperscale Data Centre",
  capacity: "48 MW",
  tier: "Tier III",
  phase: "MEP Installation & Commissioning",
  progress: 72,
  health: 78,
  status: "At Risk",
  completion: "September 2026",
};

export const healthBreakdown = [
  { name: "Schedule Health", value: 74 },
  { name: "Quality Health", value: 88 },
  { name: "Procurement Health", value: 61 },
  { name: "Engineering Health", value: 84 },
  { name: "Commissioning Readiness", value: 69 },
];

export const progressBreakdown = [
  { name: "Civil Works", value: 100 },
  { name: "Electrical", value: 76 },
  { name: "Mechanical", value: 69 },
  { name: "Cooling Systems", value: 64 },
  { name: "IT Infrastructure", value: 58 },
  { name: "Commissioning", value: 34 },
];

export const projectTeam = [
  { name: "Arjun Mehta", role: "Project Manager" },
  { name: "Priya Sharma", role: "Engineering Lead" },
  { name: "Rahul Verma", role: "Electrical Lead" },
  { name: "Neha Rao", role: "Quality Manager" },
  { name: "Vikram Singh", role: "Commissioning Manager" },
];

export const disciplines = [
  { name: "Civil", progress: 100, health: 95 },
  { name: "Electrical", progress: 76, health: 82 },
  { name: "Mechanical", progress: 69, health: 78 },
  { name: "Cooling", progress: 64, health: 71 },
  { name: "Fire & Life Safety", progress: 58, health: 84 },
  { name: "ICT", progress: 48, health: 80 },
  { name: "Commissioning", progress: 34, health: 69 },
];

export const equipmentList = [
  { id: "UPS-04", type: "UPS", status: "Delayed", severity: "CRITICAL" as const },
  { id: "CH-02", type: "Chiller", status: "On Track", severity: "NORMAL" as const },
  { id: "GEN-03", type: "Generator", status: "Delivered", severity: "NORMAL" as const },
  { id: "SWGR-02", type: "Switchgear", status: "Installation", severity: "MONITOR" as const },
];
