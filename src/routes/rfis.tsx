import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { Plus, Sparkles, Download, Copy, MessagesSquare, CheckCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { SeverityBadge, StatusBadge } from "@/components/shared/Badges";
import { api } from "@/lib/api";
import type { RFI } from "@/types";
import { toast } from "sonner";

export const Route = createFileRoute("/rfis")({
  head: () => ({ meta: [{ title: "RFI Intelligence — EPCMind AI" }, { name: "description", content: "Identify recurring issues and accelerate technical query resolution using project knowledge." }] }),
  component: RFIPage,
});

function RFIPage() {
  const navigate = useNavigate();
  const [selected, setSelected] = useState<RFI | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [draft, setDraft] = useState("");

  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);

  const refreshData = () => {
    api.getRFIs().then(setData).catch(setError);
  };

  useEffect(() => {
    refreshData();
  }, []);

  if (error) return <div className="p-6 text-critical">Error loading RFIs: {error.message}</div>;
  if (!data) return <div className="p-6 text-muted-foreground animate-pulse">Loading RFIs...</div>;

  const rfisList: RFI[] = data.rfis;
  const rfiStats = data.stats;

  return (
    <div className="mx-auto max-w-[1600px] px-6 py-6 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">RFI Intelligence</h1>
          <p className="mt-1 text-sm text-muted-foreground">Identify recurring issues and accelerate technical query resolution using project knowledge.</p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={() => setCreateOpen(true)}><Plus className="mr-2 h-4 w-4" />Create RFI</Button>
          <Button variant="outline" onClick={() => { refreshData(); toast.success("RFI list refreshed"); }}><Sparkles className="mr-2 h-4 w-4" />Analyze RFIs</Button>
          <Button variant="outline" onClick={() => toast.success("RFI list exported")}><Download className="mr-2 h-4 w-4" />Export</Button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-6">
        <Stat label="Open" value={rfiStats.open} />
        <Stat label="Critical" value={rfiStats.critical} tone="critical" />
        <Stat label="Awaiting Response" value={rfiStats.awaiting} tone="warning" />
        <Stat label="Closed" value={rfiStats.closed} tone="success" />
        <Stat label="Avg Resolution" value={rfiStats.avgResolution} />
        <Stat label="AI Matches Found" value={rfiStats.aiMatches} tone="info" />
      </div>

      <Card className="border-border bg-elevated">
        <CardContent className="p-4">
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>RFI ID</TableHead>
                  <TableHead>Subject</TableHead>
                  <TableHead>Discipline</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>AI Match</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="text-right">Action</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rfisList.map((r) => (
                  <TableRow key={r.id} className="cursor-pointer" onClick={() => { setSelected(r); setDraft(r.suggested ?? ""); }}>
                    <TableCell className="font-medium">{r.id}</TableCell>
                    <TableCell>{r.subject}</TableCell>
                    <TableCell className="text-muted-foreground">{r.discipline}</TableCell>
                    <TableCell><SeverityBadge severity={r.priority} /></TableCell>
                    <TableCell><StatusBadge status={r.status} /></TableCell>
                    <TableCell>
                      <span className={`font-semibold ${r.aiMatch >= 65 ? "text-cyan" : "text-muted-foreground"}`}>{r.aiMatch > 0 ? `${r.aiMatch}%` : "—"}</span>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{r.created}</TableCell>
                    <TableCell className="text-right"><Button variant="ghost" size="sm">View</Button></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <Sheet open={!!selected} onOpenChange={(o) => !o && setSelected(null)}>
        <SheetContent className="w-full sm:max-w-xl overflow-y-auto scrollbar-thin">
          {selected && (
            <>
              <SheetHeader>
                <SheetTitle>{selected.id} · {selected.subject}</SheetTitle>
              </SheetHeader>
              <div className="mt-6 space-y-4 text-sm">
                <div className="flex flex-wrap items-center gap-2">
                  <SeverityBadge severity={selected.priority} />
                  <StatusBadge status={selected.status} />
                  {selected.confidence && (
                    <span className="inline-flex items-center rounded border border-cyan/30 bg-cyan/10 px-2 py-0.5 text-[10px] font-semibold text-cyan">
                      {Math.round(selected.confidence * 100)}% Confidence
                    </span>
                  )}
                </div>
                
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <Meta label="Discipline" value={selected.discipline} />
                  <Meta label="Created" value={selected.created} />
                  <Meta label="Raised By" value={selected.raisedBy ?? "Contractor"} />
                  {selected.equipment && <Meta label="Equipment" value={selected.equipment} />}
                  {selected.location && <Meta label="Location" value={selected.location} />}
                </div>

                {selected.question && <Block label="Description / Question" value={selected.question} />}

                {selected.similar && (
                  <Card className="border-cyan/30 bg-cyan/5">
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 text-cyan">
                          <Sparkles className="h-3.5 w-3.5" />
                          <span className="text-[10px] font-semibold uppercase tracking-widest">Similar Historical RFI Match</span>
                        </div>
                        <span className="text-xl font-semibold text-cyan">{selected.similar.match}%</span>
                      </div>
                      <div className="mt-2 text-sm font-semibold">{selected.similar.id} · {selected.similar.subject}</div>
                      {selected.similar.question && (
                        <div className="mt-1 text-xs text-muted-foreground"><span className="font-medium text-foreground">Previous Question:</span> {selected.similar.question}</div>
                      )}
                      {selected.similar.resolution && (
                        <div className="mt-1 text-xs text-muted-foreground"><span className="font-medium text-foreground">Previous Resolution:</span> {selected.similar.resolution}</div>
                      )}
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="mt-3"
                        onClick={() => {
                          const matchItem = rfisList.find(r => r.id === selected.similar?.id);
                          if (matchItem) {
                            setSelected(matchItem);
                            setDraft(matchItem.suggested ?? matchItem.finalResolution ?? "");
                          } else {
                            toast.info(`Historical RFI ${selected.similar?.id} resolution: ${selected.similar?.resolution}`);
                          }
                        }}
                      >
                        View Previous RFI
                      </Button>
                    </CardContent>
                  </Card>
                )}

                {selected.suggested && (
                  <div className="space-y-3">
                    <div>
                      <div className="mb-1 flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-widest text-cyan">
                        <Sparkles className="h-3 w-3" />AI-Assisted Suggested Resolution
                      </div>
                      <Textarea value={draft} onChange={(e) => setDraft(e.target.value)} className="min-h-[120px] text-xs" />
                    </div>

                    {selected.reasoning && (
                      <div className="rounded-md border border-border bg-surface p-3 text-xs">
                        <div className="mb-1 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Engineering Rationale</div>
                        <p className="text-muted-foreground">{selected.reasoning}</p>
                      </div>
                    )}

                    {selected.recommendedActions && selected.recommendedActions.length > 0 && (
                      <div>
                        <div className="mb-1 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Recommended Actions</div>
                        <ul className="list-disc list-inside space-y-0.5 text-xs text-foreground">
                          {selected.recommendedActions.map((act, idx) => <li key={idx}>{act}</li>)}
                        </ul>
                      </div>
                    )}

                    <div className="mt-2 flex flex-wrap gap-2">
                      <Button size="sm" variant="outline" onClick={() => { navigator.clipboard.writeText(draft); toast.success("Response copied"); }}><Copy className="mr-1.5 h-3 w-3" />Copy Response</Button>
                      <Button size="sm" onClick={() => toast.success("Used as draft response")}>Use as Draft</Button>
                      <Button size="sm" variant="outline" onClick={() => navigate({ to: "/copilot" })}><Sparkles className="mr-1.5 h-3 w-3" />Ask Copilot</Button>
                    </div>
                  </div>
                )}

                {selected.sources && selected.sources.length > 0 && (
                  <div className="rounded-md border border-border bg-surface p-3 space-y-1">
                    <div className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Supporting Project Sources</div>
                    <ul className="space-y-1 text-xs text-muted-foreground">
                      {selected.sources.map((s, idx) => (
                        <li key={idx}>• {s.document} (Page {s.page}{s.section ? `, ${s.section}` : ''})</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>

      <CreateRFIDialog open={createOpen} onOpenChange={setCreateOpen} onComplete={refreshData} onSelectCreated={(newRfi) => { setSelected(newRfi); setDraft(newRfi.suggested ?? ""); }} />
    </div>
  );
}

function CreateRFIDialog({ open, onOpenChange, onComplete, onSelectCreated }: { open: boolean; onOpenChange: (v: boolean) => void; onComplete: () => void; onSelectCreated: (rfi: RFI) => void }) {
  const [stage, setStage] = useState<"form" | "searching" | "done">("form");
  const [subject, setSubject] = useState("");
  const [discipline, setDiscipline] = useState("Electrical");
  const [priority, setPriority] = useState("HIGH");
  const [equipment, setEquipment] = useState("");
  const [location, setLocation] = useState("");
  const [question, setQuestion] = useState("");
  const [createdRFI, setCreatedRFI] = useState<RFI | null>(null);

  const submit = async () => {
    if (!subject || !question) {
      toast.error("Please provide both a Subject and Description for the RFI.");
      return;
    }

    setStage("searching");
    try {
      const result = await api.createRFI({
        subject,
        question,
        discipline,
        priority,
        equipment,
        location,
        raisedBy: "Electrical Contractor"
      });

      setCreatedRFI(result);
      setStage("done");
      onComplete();
    } catch (err: any) {
      setStage("form");
      toast.error(err.message || "Failed to create RFI");
    }
  };

  const reset = () => {
    setStage("form");
    setSubject("");
    setQuestion("");
    setEquipment("");
    setLocation("");
    setCreatedRFI(null);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader><DialogTitle>Create New RFI</DialogTitle></DialogHeader>
        {stage === "form" && (
          <div className="space-y-3">
            <div>
              <Label className="text-xs">Subject / Title</Label>
              <Input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="UPS Room Cable Routing Conflict" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-xs">Discipline</Label>
                <Select value={discipline} onValueChange={setDiscipline}>
                  <SelectTrigger><SelectValue placeholder="Electrical" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Electrical">Electrical</SelectItem>
                    <SelectItem value="Mechanical">Mechanical</SelectItem>
                    <SelectItem value="Civil">Civil</SelectItem>
                    <SelectItem value="FLS">FLS</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label className="text-xs">Priority</Label>
                <Select value={priority} onValueChange={setPriority}>
                  <SelectTrigger><SelectValue placeholder="HIGH" /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="CRITICAL">Critical</SelectItem>
                    <SelectItem value="HIGH">High</SelectItem>
                    <SelectItem value="MEDIUM">Medium</SelectItem>
                    <SelectItem value="LOW">Low</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-xs">Related Equipment</Label>
                <Input value={equipment} onChange={(e) => setEquipment(e.target.value)} placeholder="UPS-04" />
              </div>
              <div>
                <Label className="text-xs">Location</Label>
                <Input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="UPS Room" />
              </div>
            </div>
            <div>
              <Label className="text-xs">Description / Technical Question</Label>
              <Textarea value={question} onChange={(e) => setQuestion(e.target.value)} placeholder="Describe the technical query and site conflict..." className="min-h-[90px]" />
            </div>
          </div>
        )}

        {stage === "searching" && (
          <div className="py-6 text-center">
            <Sparkles className="mx-auto mb-2 h-6 w-6 animate-pulse text-cyan" />
            <div className="text-sm font-medium">Searching historical project knowledge & vector store...</div>
            <p className="mt-1 text-xs text-muted-foreground">Evaluating historical precedents and generating AI resolution...</p>
          </div>
        )}

        {stage === "done" && createdRFI && (
          <div className="space-y-3 py-2">
            {createdRFI.similar ? (
              <div className="rounded-md border border-cyan/30 bg-cyan/5 p-4 text-sm">
                <div className="flex items-center justify-between text-cyan">
                  <span className="flex items-center gap-2 font-semibold">
                    <Sparkles className="h-4 w-4" />Similar RFI Precedent Match: {createdRFI.similar.match}%
                  </span>
                </div>
                <div className="mt-2 text-xs font-semibold text-foreground">Matches {createdRFI.similar.id} · {createdRFI.similar.subject}</div>
                {createdRFI.similar.resolution && (
                  <div className="mt-1 text-xs text-muted-foreground"><span className="font-medium text-foreground">Previous Resolution:</span> {createdRFI.similar.resolution}</div>
                )}
              </div>
            ) : (
              <div className="rounded-md border border-border bg-surface p-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-2 text-foreground font-semibold mb-1">
                  <CheckCircle className="h-4 w-4 text-success" />RFI Created Successfully
                </div>
                No strong historical precedents above threshold. AI resolution generated using project document context.
              </div>
            )}

            {createdRFI.suggested && (
              <div className="rounded-md border border-border bg-surface p-3 text-xs">
                <div className="font-semibold text-cyan mb-1">AI-Assisted Suggested Resolution</div>
                <p className="text-muted-foreground line-clamp-3">{createdRFI.suggested}</p>
              </div>
            )}
          </div>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={reset}>{stage === "done" ? "Close" : "Cancel"}</Button>
          {stage === "form" && <Button onClick={submit}>Submit RFI & Run AI Analysis</Button>}
          {stage === "done" && createdRFI && (
            <Button onClick={() => { onSelectCreated(createdRFI); reset(); }}>
              <MessagesSquare className="mr-2 h-3.5 w-3.5" />Open RFI Details
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function Stat({ label, value, tone }: { label: string; value: number | string; tone?: "critical" | "warning" | "success" | "info" }) {
  const t = tone === "critical" ? "text-critical" : tone === "warning" ? "text-warning" : tone === "success" ? "text-success" : tone === "info" ? "text-cyan" : "text-foreground";
  return (
    <Card className="border-border bg-elevated"><CardContent className="p-5">
      <div className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">{label}</div>
      <div className={`mt-2 text-2xl font-semibold ${t}`}>{value}</div>
    </CardContent></Card>
  );
}

function Meta({ label, value }: { label: string; value: React.ReactNode }) {
  return (<div><span className="text-[10px] uppercase tracking-widest text-muted-foreground">{label}: </span><span className="text-xs font-medium">{value}</span></div>);
}

function Block({ label, value }: { label: string; value: React.ReactNode }) {
  return (<div><div className="mb-1 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">{label}</div><div className="text-sm">{value}</div></div>);
}
