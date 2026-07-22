import { cn } from "@/lib/utils";
import type { Severity, ComplianceStatus, RiskStatus, RFIStatus, MilestoneStatus } from "@/types";

const severityStyles: Record<string, string> = {
  CRITICAL: "bg-critical/15 text-critical border-critical/30",
  HIGH: "bg-warning/15 text-warning border-warning/30",
  MEDIUM: "bg-info/15 text-info border-info/30",
  LOW: "bg-success/15 text-success border-success/30",
  INFO: "bg-info/15 text-info border-info/30",
  NORMAL: "bg-success/15 text-success border-success/30",
  MONITOR: "bg-info/15 text-info border-info/30",
};

const statusStyles: Record<string, string> = {
  COMPLIANT: "bg-success/15 text-success border-success/30",
  WARNING: "bg-warning/15 text-warning border-warning/30",
  "NON-COMPLIANT": "bg-critical/15 text-critical border-critical/30",
  NOT_VERIFIABLE: "bg-muted-foreground/15 text-muted-foreground border-border",
  "On Track": "bg-success/15 text-success border-success/30",
  "At Risk": "bg-warning/15 text-warning border-warning/30",
  Delayed: "bg-critical/15 text-critical border-critical/30",
  Planned: "bg-muted-foreground/15 text-muted-foreground border-border",
  Monitor: "bg-info/15 text-info border-info/30",
  Open: "bg-warning/15 text-warning border-warning/30",
  "Awaiting Response": "bg-info/15 text-info border-info/30",
  Resolved: "bg-success/15 text-success border-success/30",
  Closed: "bg-muted-foreground/15 text-muted-foreground border-border",
  Monitoring: "bg-info/15 text-info border-info/30",
  Mitigated: "bg-success/15 text-success border-success/30",
  Approved: "bg-success/15 text-success border-success/30",
  "Under Review": "bg-warning/15 text-warning border-warning/30",
  Draft: "bg-muted-foreground/15 text-muted-foreground border-border",
  Indexed: "bg-success/15 text-success border-success/30",
  Processing: "bg-info/15 text-info border-info/30",
  "Needs Review": "bg-warning/15 text-warning border-warning/30",
};

export function SeverityBadge({ severity, className }: { severity: Severity | "INFO" | "NORMAL" | "MONITOR"; className?: string }) {
  return (
    <span className={cn("inline-flex items-center rounded border px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider", severityStyles[severity], className)}>
      {severity}
    </span>
  );
}

export function StatusBadge({ status, className }: { status: ComplianceStatus | RiskStatus | RFIStatus | MilestoneStatus | string; className?: string }) {
  return (
    <span className={cn("inline-flex items-center rounded border px-2 py-0.5 text-[11px] font-medium", statusStyles[status] ?? "bg-muted text-muted-foreground border-border", className)}>
      {status}
    </span>
  );
}
