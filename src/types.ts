export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
export type ComplianceStatus = "COMPLIANT" | "WARNING" | "NON-COMPLIANT" | "NOT_VERIFIABLE";
export type RiskStatus = "Open" | "Monitoring" | "Mitigated" | "Closed";
export type RFIStatus = "Open" | "Awaiting Response" | "Resolved" | "Closed";
export type MilestoneStatus = "On Track" | "At Risk" | "Planned" | "Monitor" | "Delayed";

export interface SourceDetail {
  document: string;
  page: number;
  section?: string;
}

export interface ComplianceCheck {
  id: string;
  equipment: string;
  parameter: string;
  requirement: string;
  vendorValue: string;
  status: ComplianceStatus;
  severity: Severity;
  deviation?: string;
  analysis?: string;
  impact?: string[];
  action?: string;
  sources?: string[];
  requirementSource?: SourceDetail;
  vendorSource?: SourceDetail;
}


export interface Project {
  name: string;
  code: string;
  location: string;
  facilityType: string;
  capacity: string;
  tier: string;
  phase: string;
  progress: number;
  health: number;
  status: string;
  completion: string;
}

export interface Document {
  id: string;
  name: string;
  category: string;
  revision: string;
  uploaded: string;
  uploadedBy: string;
  status: "Approved" | "Under Review" | "Draft";
  aiIndex: "Indexed" | "Processing" | "Needs Review";
  discipline: string;
  summary?: string;
}

export interface ComplianceCheck {
  id: string;
  equipment: string;
  parameter: string;
  requirement: string;
  vendorValue: string;
  status: ComplianceStatus;
  severity: Severity;
  deviation?: string;
  analysis?: string;
  impact?: string[];
  action?: string;
  sources?: string[];
}

export interface RFISimilar {
  id: string;
  subject: string;
  match: number;
  question?: string;
  resolution?: string;
  discipline?: string;
}

export interface RFI {
  id: string;
  subject: string;
  discipline: string;
  priority: Severity;
  status: RFIStatus;
  aiMatch: number;
  created: string;
  question?: string;
  equipment?: string;
  location?: string;
  raisedBy?: string;
  similar?: RFISimilar;
  suggested?: string;
  reasoning?: string;
  recommendedActions?: string[];
  confidence?: number;
  sources?: SourceDetail[];
  finalResolution?: string;
}


export interface Risk {
  id: string;
  title: string;
  category: string;
  probability: number;
  impact: string;
  severity: Severity;
  milestone: string;
  status: RiskStatus;
  detail?: {
    equipment?: string;
    plannedDelivery?: string;
    currentEstimate?: string;
    delay?: string;
    float?: string;
    criticalImpact?: string;
    analysis: string;
    mitigations: string[];
  };
}

export interface ScheduleActivity {
  id: string;
  name: string;
  start: string;
  finish: string;
  progress: number;
  critical: boolean;
  status: MilestoneStatus;
}

export interface Milestone {
  name: string;
  planned: string;
  forecast: string;
  variance: string;
  status: MilestoneStatus;
}

export interface Notification {
  id: string;
  severity: Severity | "INFO";
  title: string;
  message: string;
  time: string;
  read: boolean;
}

export interface AIMessage {
  role: "user" | "assistant";
  content: string;
  sources?: SourceCitation[];
  meta?: { risk?: Severity; action?: string };
}

export interface SourceCitation {
  document: string;
  section: string;
  page: number;
}

export interface Equipment {
  id: string;
  type: string;
  status: string;
  severity: "CRITICAL" | "NORMAL" | "MONITOR";
}
