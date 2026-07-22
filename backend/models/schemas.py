from pydantic import BaseModel
from typing import List, Optional, Literal, Dict, Any

Severity = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]
ComplianceStatus = Literal["COMPLIANT", "WARNING", "NON-COMPLIANT", "NOT_VERIFIABLE"]
RiskStatus = Literal["Open", "Monitoring", "Mitigated", "Closed"]
RFIStatus = Literal["Open", "Awaiting Response", "Resolved", "Closed"]
MilestoneStatus = Literal["On Track", "At Risk", "Planned", "Monitor", "Delayed"]

class Project(BaseModel):
    name: str
    code: str
    location: str
    facilityType: str
    capacity: str
    tier: str
    phase: str
    progress: int
    health: int
    status: str
    completion: str

class Document(BaseModel):
    id: str
    name: str
    category: str
    revision: str
    uploaded: str
    uploadedBy: str
    status: Literal["Approved", "Under Review", "Draft"]
    aiIndex: Literal["Indexed", "Processing", "Needs Review"]
    discipline: str
    summary: Optional[str] = None

class SourceDetail(BaseModel):
    document: str
    page: int
    section: Optional[str] = None

class ComplianceCheck(BaseModel):
    id: str
    equipment: str
    parameter: str
    requirement: str
    vendorValue: str
    status: ComplianceStatus
    severity: Severity
    deviation: Optional[str] = None
    analysis: Optional[str] = None
    impact: Optional[List[str]] = None
    action: Optional[str] = None
    sources: Optional[List[str]] = None
    requirementSource: Optional[SourceDetail] = None
    vendorSource: Optional[SourceDetail] = None


class RFISimilar(BaseModel):
    id: str
    subject: str
    match: int
    question: Optional[str] = None
    resolution: Optional[str] = None
    discipline: Optional[str] = None

class RFI(BaseModel):
    id: str
    subject: str
    discipline: str
    priority: Severity
    status: RFIStatus
    aiMatch: int
    created: str
    question: Optional[str] = None
    equipment: Optional[str] = None
    location: Optional[str] = None
    raisedBy: Optional[str] = None
    similar: Optional[RFISimilar] = None
    suggested: Optional[str] = None
    reasoning: Optional[str] = None
    recommendedActions: Optional[List[str]] = None
    confidence: Optional[float] = None
    sources: Optional[List[SourceDetail]] = None
    finalResolution: Optional[str] = None


class RiskDetail(BaseModel):
    equipment: Optional[str] = None
    plannedDelivery: Optional[str] = None
    currentEstimate: Optional[str] = None
    delay: Optional[str] = None
    float: Optional[str] = None
    criticalImpact: Optional[str] = None
    analysis: str
    mitigations: List[str]

class Risk(BaseModel):
    id: str
    title: str
    category: str
    probability: int
    impact: str
    severity: Severity
    milestone: str
    status: RiskStatus
    detail: Optional[RiskDetail] = None

class ScheduleActivity(BaseModel):
    id: str
    name: str
    start: str
    finish: str
    progress: int
    critical: bool
    status: MilestoneStatus

class Milestone(BaseModel):
    name: str
    planned: str
    forecast: str
    variance: str
    status: MilestoneStatus

class Notification(BaseModel):
    id: str
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    title: str
    message: str
    time: str
    read: bool

class SourceCitation(BaseModel):
    document: str
    section: str
    page: int

class AIMeta(BaseModel):
    risk: Optional[Severity] = None
    action: Optional[str] = None

class AIMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    sources: Optional[List[SourceCitation]] = None
    meta: Optional[AIMeta] = None

class Equipment(BaseModel):
    id: str
    type: str
    status: str
    severity: Literal["CRITICAL", "NORMAL", "MONITOR"]

class ProjectDataResponse(BaseModel):
    name: str
    code: str
    location: str
    facilityType: str
    capacity: str
    tier: str
    phase: str
    progress: int
    health: int
    status: str
    completion: str
    healthBreakdown: Dict[str, Any]
    progressBreakdown: Dict[str, Any]
    team: List[Dict[str, Any]]
    disciplines: List[Dict[str, Any]]
    equipment: List[Equipment]

class DocumentDataResponse(BaseModel):
    docs: List[Document]
    stats: Dict[str, Any]

class ComplianceDataResponse(BaseModel):
    checks: List[ComplianceCheck]
    stats: Dict[str, Any]

class RFIDataResponse(BaseModel):
    rfis: List[RFI]
    stats: Dict[str, Any]

class RiskDataResponse(BaseModel):
    risks: List[Risk]
    stats: Dict[str, Any]
    distribution: List[Dict[str, Any]]

class ScheduleDataResponse(BaseModel):
    activities: List[ScheduleActivity]
    milestones: List[Milestone]
    upcoming: List[Milestone]
    stats: Dict[str, Any]
    criticalPath: Dict[str, Any]
