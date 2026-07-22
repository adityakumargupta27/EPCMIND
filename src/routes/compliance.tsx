import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMemo, useState, useEffect } from "react";
import { Play, Download, Filter, Sparkles, ShieldCheck } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { SeverityBadge, StatusBadge } from "@/components/shared/Badges";
import { api } from "@/lib/api";
import type { ComplianceCheck, Document } from "@/types";
import { toast } from "sonner";

export const Route = createFileRoute("/compliance")({
  head: () => ({ meta: [{ title: "Compliance Intelligence — EPCMind AI" }, { name: "description", content: "AI-assisted comparison of project requirements against vendor submissions." }] }),
  component: CompliancePage,
});

const stages = [
  "Retrieving project requirements...",
  "Reading vendor submission...",
  "Matching technical parameters...",
  "Evaluating compliance...",
  "Generating engineering recommendations...",
];

function CompliancePage() {
  const navigate = useNavigate();
  const [filter, setFilter] = useState<string>("all");
  const [selected, setSelected] = useState<ComplianceCheck | null>(null);
  const [analysisOpen, setAnalysisOpen] = useState(false);

  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);

  const refreshData = () => {
    api.getComplianceChecks().then(setData).catch(setError);
  };

  useEffect(() => {
    refreshData();
  }, []);

  const filtered = useMemo(() => {
    if (!data) return [];
    return data.checks.filter((c: ComplianceCheck) => filter === "all" || c.status === filter);
  }, [data, filter]);

  if (error) return <div className="p-6 text-critical">Error loading compliance data: {error.message}</div>;
  if (!data) return <div className="p-6 text-muted-foreground animate-pulse">Loading compliance data...</div>;

  const complianceStats = data.stats;

  return (
    <div className="mx-auto max-w-[1600px] px-6 py-6 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Specification Compliance Intelligence</h1>
          <p className="mt-1 text-sm text-muted-foreground">AI-assisted comparison of project requirements against vendor submissions.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={() => setAnalysisOpen(true)}><Play className="mr-2 h-4 w-4" />Run New Analysis</Button>
          <Button variant="outline" onClick={() => toast.success("Compliance report exported")}><Download className="mr-2 h-4 w-4" />Export Report</Button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
        <StatCard label="Total Checks" value={complianceStats.total} />
        <StatCard label="Compliant" value={complianceStats.compliant} tone="success" />
        <StatCard label="Warnings" value={complianceStats.warnings || 0} tone="warning" />
        <StatCard label="Non-Compliant" value={complianceStats.nonCompliant} tone="critical" />
        <StatCard label="High Severity" value={complianceStats.highSeverity} tone="critical" />
      </div>

      <Card className="border-border bg-elevated">
        <CardContent className="p-4">
          <div className="mb-4 flex flex-wrap items-center gap-2">
            <Select value={filter} onValueChange={setFilter}>
              <SelectTrigger className="w-[180px]"><SelectValue placeholder="Status" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="COMPLIANT">Compliant</SelectItem>
                <SelectItem value="WARNING">Warning</SelectItem>
                <SelectItem value="NON-COMPLIANT">Non-Compliant</SelectItem>
                <SelectItem value="NOT_VERIFIABLE">Not Verifiable</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline"><Filter className="mr-2 h-4 w-4" />More Filters</Button>
          </div>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Equipment</TableHead>
                  <TableHead>Parameter</TableHead>
                  <TableHead>Requirement</TableHead>
                  <TableHead>Vendor Value</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((c: ComplianceCheck) => (
                  <TableRow key={c.id} className="cursor-pointer" onClick={() => setSelected(c)}>
                    <TableCell className="font-medium">{c.equipment}</TableCell>
                    <TableCell>{c.parameter}</TableCell>
                    <TableCell className="text-muted-foreground">{c.requirement}</TableCell>
                    <TableCell className="text-muted-foreground">{c.vendorValue}</TableCell>
                    <TableCell><StatusBadge status={c.status} /></TableCell>
                    <TableCell><SeverityBadge severity={c.severity} /></TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setSelected(c); }}>View</Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <Sheet open={!!selected} onOpenChange={(o) => !o && setSelected(null)}>
        <SheetContent className="w-full sm:max-w-lg overflow-y-auto scrollbar-thin">
          {selected && (
            <>
              <SheetHeader>
                <SheetTitle>{selected.equipment} · {selected.parameter}</SheetTitle>
                <SheetDescription>
                  <span className="flex items-center gap-2 pt-2"><StatusBadge status={selected.status} /><SeverityBadge severity={selected.severity} /></span>
                </SheetDescription>
              </SheetHeader>
              <div className="mt-6 space-y-4 text-sm">
                <Block label="Project Requirement" value={selected.requirement} />
                <Block label="Vendor Submission" value={selected.vendorValue} />
                {selected.deviation && <Block label="Deviation" value={<span className="text-critical font-semibold">{selected.deviation}</span>} />}
                {selected.analysis && (
                  <div className="rounded-md border border-border bg-surface p-3">
                    <div className="mb-1 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest text-cyan"><Sparkles className="h-3 w-3" />AI Analysis</div>
                    <p className="text-xs text-muted-foreground">{selected.analysis}</p>
                  </div>
                )}
                {selected.impact && selected.impact.length > 0 && (
                  <div>
                    <div className="mb-1 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Potential Impact</div>
                    <ul className="list-disc list-inside space-y-0.5 text-xs text-foreground">
                      {selected.impact.map((i) => <li key={i}>{i}</li>)}
                    </ul>
                  </div>
                )}
                {selected.action && <Block label="Recommended Action" value={<span className="text-xs">{selected.action}</span>} />}
                
                {/* Genuine Source Citations */}
                <div className="rounded-md border border-border bg-surface p-3 space-y-2">
                  <div className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Source Documents</div>
                  {selected.requirementSource && (
                    <div className="text-xs">
                      <span className="font-semibold text-foreground">Requirement Source: </span>
                      <span className="text-muted-foreground">{selected.requirementSource.document} (Page {selected.requirementSource.page}{selected.requirementSource.section ? `, ${selected.requirementSource.section}` : ''})</span>
                    </div>
                  )}
                  {selected.vendorSource ? (
                    <div className="text-xs">
                      <span className="font-semibold text-foreground">Vendor Source: </span>
                      <span className="text-muted-foreground">{selected.vendorSource.document} (Page {selected.vendorSource.page}{selected.vendorSource.section ? `, ${selected.vendorSource.section}` : ''})</span>
                    </div>
                  ) : (
                    <div className="text-xs text-muted-foreground italic">
                      Vendor Source: Not specified / missing from vendor submittal.
                    </div>
                  )}
                </div>

                <div className="flex flex-wrap gap-2 pt-4">
                  <Button size="sm" onClick={() => navigate({ to: "/copilot" })}><Sparkles className="mr-1.5 h-3 w-3" />Ask Copilot</Button>
                  <Button size="sm" variant="outline" onClick={() => navigate({ to: "/rfis" })}>Create RFI</Button>
                  <Button size="sm" variant="outline" onClick={() => { toast.success("Marked as reviewed"); setSelected(null); }}>Mark Reviewed</Button>
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>

      <AnalysisDialog open={analysisOpen} onOpenChange={setAnalysisOpen} onComplete={refreshData} />
    </div>
  );
}

function AnalysisDialog({ open, onOpenChange, onComplete }: { open: boolean; onOpenChange: (v: boolean) => void; onComplete: () => void }) {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [reqDocId, setReqDocId] = useState<string>("");
  const [vendorDocId, setVendorDocId] = useState<string>("");
  const [equipment, setEquipment] = useState<string>("UPS-04");
  const [discipline, setDiscipline] = useState<string>("Electrical");
  const [running, setRunning] = useState(false);
  const [step, setStep] = useState(0);

  useEffect(() => {
    if (open) {
      api.getDocuments().then((res) => {
        setDocuments(res.docs || []);
        if (res.docs && res.docs.length > 0) {
          setReqDocId(res.docs[0].id);
          if (res.docs.length > 1) {
            setVendorDocId(res.docs[1].id);
          } else {
            setVendorDocId(res.docs[0].id);
          }
        }
      }).catch(() => {});
    }
  }, [open]);

  const run = async () => {
    if (!reqDocId || !vendorDocId) {
      toast.error("Please select both a Requirement Document and a Vendor Submission Document.");
      return;
    }
    if (reqDocId === vendorDocId) {
      toast.error("Requirement Document and Vendor Submission Document must be different.");
      return;
    }

    setRunning(true);
    setStep(0);

    const iv = setInterval(() => {
      setStep((s) => Math.min(s + 1, stages.length - 1));
    }, 800);

    try {
      await api.runComplianceAnalysis({
        requirement_document_id: reqDocId,
        vendor_document_id: vendorDocId,
        equipment,
        discipline
      });
      clearInterval(iv);
      setRunning(false);
      onOpenChange(false);
      toast.success("Compliance analysis complete!");
      onComplete();
    } catch (err: any) {
      clearInterval(iv);
      setRunning(false);
      toast.error(err.message || "Failed to execute compliance analysis.");
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader><DialogTitle>Run Specification Compliance Analysis</DialogTitle></DialogHeader>
        {!running ? (
          <div className="grid grid-cols-2 gap-3">
            <div className="col-span-2">
              <Label className="text-xs">Requirement Document (Specification)</Label>
              <Select value={reqDocId} onValueChange={setReqDocId}>
                <SelectTrigger><SelectValue placeholder="Select Requirement Document..." /></SelectTrigger>
                <SelectContent>
                  {documents.map((d) => (
                    <SelectItem key={d.id} value={d.id}>{d.name} ({d.category})</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="col-span-2">
              <Label className="text-xs">Vendor Submission Document</Label>
              <Select value={vendorDocId} onValueChange={setVendorDocId}>
                <SelectTrigger><SelectValue placeholder="Select Vendor Submittal..." /></SelectTrigger>
                <SelectContent>
                  {documents.map((d) => (
                    <SelectItem key={d.id} value={d.id}>{d.name} ({d.category})</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs">Equipment ID</Label>
              <Input value={equipment} onChange={(e) => setEquipment(e.target.value)} placeholder="UPS-04" />
            </div>
            <div>
              <Label className="text-xs">Discipline</Label>
              <Select value={discipline} onValueChange={setDiscipline}>
                <SelectTrigger><SelectValue placeholder="Electrical" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="Electrical">Electrical</SelectItem>
                  <SelectItem value="Mechanical">Mechanical</SelectItem>
                  <SelectItem value="Commissioning">Commissioning</SelectItem>
                  <SelectItem value="Quality">Quality</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        ) : (
          <div className="space-y-3 py-2">
            <Progress value={(step + 1) * (100 / stages.length)} />
            <ul className="text-xs space-y-1">
              {stages.map((s, i) => (
                <li key={s} className={i <= step ? "text-foreground" : "text-muted-foreground/50"}>
                  {i <= step ? "✓" : "○"} {s}
                </li>
              ))}
            </ul>
          </div>
        )}
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={running}>Cancel</Button>
          <Button onClick={run} disabled={running}><ShieldCheck className="mr-2 h-4 w-4" />Run AI Analysis</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function StatCard({ label, value, tone }: { label: string; value: number | string; tone?: "success" | "warning" | "critical" }) {
  const t = tone === "success" ? "text-success" : tone === "warning" ? "text-warning" : tone === "critical" ? "text-critical" : "text-foreground";
  return (
    <Card className="border-border bg-elevated"><CardContent className="p-5">
      <div className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">{label}</div>
      <div className={`mt-2 text-2xl font-semibold ${t}`}>{value}</div>
    </CardContent></Card>
  );
}

function Block({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <div className="mb-1 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">{label}</div>
      <div className="text-sm text-foreground">{value}</div>
    </div>
  );
}
