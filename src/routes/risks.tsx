import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Play, Download, Filter, Sparkles, AlertTriangle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { SeverityBadge, StatusBadge } from "@/components/shared/Badges";
import { useEffect } from "react";
import { api } from "@/lib/api";
import type { Risk } from "@/types";
import { toast } from "sonner";

export const Route = createFileRoute("/risks")({
  head: () => ({ meta: [{ title: "Risk Intelligence — EPCMind AI" }, { name: "description", content: "AI-assisted detection of schedule, procurement, engineering and commissioning risks." }] }),
  component: RiskPage,
});

const stages = [
  "Analyzing schedule dependencies...",
  "Checking procurement status...",
  "Evaluating activity float...",
  "Mapping milestone exposure...",
  "Generating mitigation strategies...",
];

function RiskPage() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState<Risk | null>(null);
  const [runOpen, setRunOpen] = useState(false);

  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    api.getRisks().then(setData).catch(setError);
  }, []);

  if (error) return <div className="p-6 text-critical">Error loading risks: {error.message}</div>;
  if (!data) return <div className="p-6 text-muted-foreground animate-pulse">Loading risks...</div>;

  const mockRisks = data.risks;
  const riskStats = data.stats;

  return (
    <div className="mx-auto max-w-[1600px] px-6 py-6 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Project Risk Intelligence</h1>
          <p className="mt-1 text-sm text-muted-foreground">AI-assisted detection of schedule, procurement, engineering and commissioning risks.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={() => setRunOpen(true)}><Play className="mr-2 h-4 w-4" />Run Risk Analysis</Button>
          <Button variant="outline" onClick={() => toast.success("Risk register exported")}><Download className="mr-2 h-4 w-4" />Export Risk Register</Button>
          <Button variant="outline"><Filter className="mr-2 h-4 w-4" />Filters</Button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-6">
        <Stat label="Total Active Risks" value={riskStats.total} />
        <Stat label="Critical" value={riskStats.critical} tone="critical" />
        <Stat label="High" value={riskStats.high} tone="warning" />
        <Stat label="Medium" value={riskStats.medium} tone="info" />
        <Stat label="Schedule Exposure" value={`${riskStats.exposureDays} Days`} tone="critical" />
        <Stat label="Highest Risk Area" value={riskStats.highestArea} tone="warning" />
      </div>

      <Card className="border-border bg-elevated">
        <CardContent className="p-4">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Risk</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Probability</TableHead>
                  <TableHead>Impact</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Affected Milestone</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockRisks.map((r) => (
                  <TableRow key={r.id} className="cursor-pointer" onClick={() => setSelected(r)}>
                    <TableCell className="font-medium">{r.title}</TableCell>
                    <TableCell className="text-muted-foreground">{r.category}</TableCell>
                    <TableCell><div className="flex items-center gap-2"><Progress value={r.probability} className="h-1.5 w-16" /><span className="text-xs">{r.probability}%</span></div></TableCell>
                    <TableCell className="text-muted-foreground">{r.impact}</TableCell>
                    <TableCell><SeverityBadge severity={r.severity} /></TableCell>
                    <TableCell className="text-muted-foreground">{r.milestone}</TableCell>
                    <TableCell><StatusBadge status={r.status} /></TableCell>
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
              <SheetHeader><SheetTitle>{selected.title}</SheetTitle></SheetHeader>
              <div className="mt-6 space-y-4 text-sm">
                <div className="flex flex-wrap gap-2">
                  <SeverityBadge severity={selected.severity} />
                  <StatusBadge status={selected.status} />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <Kv label="Category" value={selected.category} />
                  <Kv label="Probability" value={`${selected.probability}%`} />
                  <Kv label="Impact" value={selected.impact} />
                  <Kv label="Affected Milestone" value={selected.milestone} />
                  {selected.detail?.equipment && <Kv label="Equipment" value={selected.detail.equipment} />}
                  {selected.detail?.plannedDelivery && <Kv label="Planned Delivery" value={selected.detail.plannedDelivery} />}
                  {selected.detail?.currentEstimate && <Kv label="Current Estimate" value={selected.detail.currentEstimate} />}
                  {selected.detail?.delay && <Kv label="Delay" value={<span className="text-critical font-semibold">{selected.detail.delay}</span>} />}
                  {selected.detail?.float && <Kv label="Available Float" value={selected.detail.float} />}
                  {selected.detail?.criticalImpact && <Kv label="Critical Path Impact" value={<span className="text-critical font-semibold">{selected.detail.criticalImpact}</span>} />}
                </div>
                {selected.detail?.analysis && (
                  <div className="rounded-md border border-border bg-surface p-3">
                    <div className="mb-1 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest text-cyan"><Sparkles className="h-3 w-3" />AI Analysis</div>
                    <p className="text-xs text-muted-foreground">{selected.detail.analysis}</p>
                  </div>
                )}
                {selected.detail?.mitigations && (
                  <div>
                    <div className="mb-1 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Recommended Mitigation</div>
                    <ul className="list-disc list-inside space-y-1 text-xs">
                      {selected.detail.mitigations.map((m) => <li key={m}>{m}</li>)}
                    </ul>
                  </div>
                )}
                <div className="flex flex-wrap gap-2 pt-2">
                  <Button size="sm" onClick={() => toast.success("Owner assigned")}>Assign Owner</Button>
                  <Button size="sm" variant="outline" onClick={() => toast.success("Mitigation action created")}>Create Action</Button>
                  <Button size="sm" variant="outline" onClick={() => navigate({ to: "/copilot" })}><Sparkles className="mr-1.5 h-3 w-3" />Ask Copilot</Button>
                  <Button size="sm" variant="outline" onClick={() => { toast.success("Risk marked as mitigated"); setSelected(null); }}>Mark Mitigated</Button>
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>

      <RunDialog open={runOpen} onOpenChange={setRunOpen} />
    </div>
  );
}

function RunDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const [step, setStep] = useState(-1);
  const start = () => {
    setStep(0);
    let i = 0;
    const iv = setInterval(() => {
      i++;
      setStep(i);
      if (i >= stages.length) {
        clearInterval(iv);
        setTimeout(() => { setStep(-1); onOpenChange(false); toast.success("3 critical risks identified"); }, 700);
      }
    }, 550);
  };
  return (
    <Dialog open={open} onOpenChange={(v) => { if (!v) setStep(-1); onOpenChange(v); }}>
      <DialogContent>
        <DialogHeader><DialogTitle>Run Risk Analysis</DialogTitle></DialogHeader>
        {step === -1 ? (
          <div className="py-4 text-sm text-muted-foreground">Runs schedule, procurement, quality and commissioning risk detection across the current project state.</div>
        ) : (
          <div className="space-y-3 py-2">
            <Progress value={(step) * (100 / stages.length)} />
            <ul className="text-xs space-y-1">
              {stages.map((s, i) => <li key={s} className={i < step ? "text-foreground" : "text-muted-foreground/50"}>{i < step ? "✓" : "○"} {s}</li>)}
            </ul>
          </div>
        )}
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={start} disabled={step !== -1}><AlertTriangle className="mr-2 h-4 w-4" />Analyze</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}

function Stat({ label, value, tone }: { label: string; value: number | string; tone?: "critical" | "warning" | "info" }) {
  const t = tone === "critical" ? "text-critical" : tone === "warning" ? "text-warning" : tone === "info" ? "text-info" : "text-foreground";
  return (<Card className="border-border bg-elevated"><CardContent className="p-5"><div className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">{label}</div><div className={`mt-2 text-xl font-semibold ${t}`}>{value}</div></CardContent></Card>);
}
function Kv({ label, value }: { label: string; value: React.ReactNode }) {
  return (<div><div className="text-[10px] uppercase tracking-widest text-muted-foreground">{label}</div><div className="mt-0.5 text-sm font-medium text-foreground">{value}</div></div>);
}
