import type { Milestone, ScheduleActivity } from "@/types";

export const scheduleActivities: ScheduleActivity[] = [
  { id: "A1", name: "Civil Works", start: "Jan 2026", finish: "May 2026", progress: 100, critical: false, status: "On Track" },
  { id: "A2", name: "Electrical Installation", start: "Mar 2026", finish: "Aug 2026", progress: 76, critical: true, status: "At Risk" },
  { id: "A3", name: "UPS Installation", start: "Jun 2026", finish: "Jul 2026", progress: 45, critical: true, status: "At Risk" },
  { id: "A4", name: "Cooling Installation", start: "Apr 2026", finish: "Aug 2026", progress: 64, critical: false, status: "Monitor" },
  { id: "A5", name: "Generator Installation", start: "May 2026", finish: "Jul 2026", progress: 88, critical: false, status: "On Track" },
  { id: "A6", name: "Integrated Systems Testing", start: "Aug 2026", finish: "Aug 2026", progress: 0, critical: true, status: "At Risk" },
  { id: "A7", name: "Commissioning", start: "Aug 2026", finish: "Sep 2026", progress: 12, critical: true, status: "Planned" },
];

export const milestones: Milestone[] = [
  { name: "UPS Installation Complete", planned: "20 Jul 2026", forecast: "28 Jul 2026", variance: "+8 Days", status: "At Risk" },
  { name: "Cooling Completion", planned: "02 Aug 2026", forecast: "04 Aug 2026", variance: "+2 Days", status: "Monitor" },
  { name: "Integrated Systems Testing", planned: "12 Aug 2026", forecast: "20 Aug 2026", variance: "+8 Days", status: "At Risk" },
  { name: "Final Commissioning", planned: "28 Aug 2026", forecast: "05 Sep 2026", variance: "+8 Days", status: "At Risk" },
];

export const upcomingMilestones: Milestone[] = [
  { name: "UPS Installation", planned: "26 Jul 2026", forecast: "28 Jul 2026", variance: "+2 Days", status: "At Risk" },
  { name: "Cooling System Completion", planned: "02 Aug 2026", forecast: "04 Aug 2026", variance: "+2 Days", status: "On Track" },
  { name: "Integrated Systems Testing", planned: "12 Aug 2026", forecast: "20 Aug 2026", variance: "+8 Days", status: "At Risk" },
  { name: "Commissioning Completion", planned: "28 Aug 2026", forecast: "05 Sep 2026", variance: "+8 Days", status: "Planned" },
];

export const scheduleStats = {
  progress: 72,
  activities: 184,
  completed: 112,
  inProgress: 48,
  delayed: 9,
  critical: 15,
};

export const criticalPath = [
  { name: "UPS Delivery", status: "12 Days Delayed", severity: "CRITICAL" as const },
  { name: "UPS Installation", status: "Pending", severity: "HIGH" as const },
  { name: "Electrical Integration", status: "Not Started", severity: "MEDIUM" as const },
  { name: "Integrated Systems Testing", status: "Not Started", severity: "HIGH" as const },
  { name: "Commissioning", status: "Not Started", severity: "MEDIUM" as const },
];
