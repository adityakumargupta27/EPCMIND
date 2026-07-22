import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Upload, FolderPlus, Filter, Search, MoreVertical, FileText, Sparkles, ShieldCheck, Download, Archive } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { StatusBadge } from "@/components/shared/Badges";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from "@/components/ui/dropdown-menu";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from "@/components/ui/alert-dialog";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { useEffect } from "react";
import { api } from "@/lib/api";
import type { Document } from "@/types";
import { toast } from "sonner";
import { EmptyState } from "@/components/shared/EmptyState";

export const Route = createFileRoute("/documents")({
  head: () => ({ meta: [{ title: "Project Documents — EPCMind AI" }, { name: "description", content: "Manage engineering specifications, vendor submittals and commissioning documentation." }] }),
  component: DocumentsPage,
});

function DocumentsPage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState<string>("all");
  const [status, setStatus] = useState<string>("all");
  const [uploadOpen, setUploadOpen] = useState(false);
  const [detail, setDetail] = useState<Document | null>(null);
  const [archiveTarget, setArchiveTarget] = useState<Document | null>(null);

  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    api.getDocuments().then(setData).catch(setError);
  }, []);

  const filtered = useMemo(() => {
    if (!data) return [];
    return data.docs.filter((d: Document) => {
      if (query && !d.name.toLowerCase().includes(query.toLowerCase())) return false;
      if (category !== "all" && d.category !== category) return false;
      if (status !== "all" && d.status !== status) return false;
      return true;
    });
  }, [data, query, category, status]);

  if (error) return <div className="p-6 text-critical">Error loading documents: {error.message}</div>;
  if (!data) return <div className="p-6 text-muted-foreground animate-pulse">Loading documents...</div>;

  const documentStats = data.stats;


  return (
    <div className="mx-auto max-w-[1600px] px-6 py-6 space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">Project Documents</h1>
          <p className="mt-1 text-sm text-muted-foreground">Manage engineering specifications, vendor submittals and commissioning documentation.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Button onClick={() => setUploadOpen(true)}><Upload className="mr-2 h-4 w-4" />Upload Document</Button>
          <Button variant="outline"><FolderPlus className="mr-2 h-4 w-4" />Import Folder</Button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard label="Total Documents" value={documentStats.total.toString()} />
        <StatCard label="Indexed" value={documentStats.indexed.toString()} tone="success" />
        <StatCard label="Processing" value={documentStats.processing.toString()} tone="info" />
        <StatCard label="Needs Review" value={documentStats.needsReview.toString()} tone="warning" />
      </div>

      <Card className="border-border bg-elevated">
        <CardContent className="p-4">
          <div className="mb-4 flex flex-wrap items-center gap-2">
            <div className="relative flex-1 min-w-[220px]">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search documents..." value={query} onChange={(e) => setQuery(e.target.value)} className="pl-8" />
            </div>
            <Select value={category} onValueChange={setCategory}>
              <SelectTrigger className="w-[200px]"><SelectValue placeholder="Category" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="Engineering Specification">Engineering Specification</SelectItem>
                <SelectItem value="Equipment Specification">Equipment Specification</SelectItem>
                <SelectItem value="Vendor Submittal">Vendor Submittal</SelectItem>
                <SelectItem value="Drawing">Drawing</SelectItem>
                <SelectItem value="Commissioning">Commissioning</SelectItem>
                <SelectItem value="Quality">Quality</SelectItem>
              </SelectContent>
            </Select>
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger className="w-[160px]"><SelectValue placeholder="Status" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="Approved">Approved</SelectItem>
                <SelectItem value="Under Review">Under Review</SelectItem>
                <SelectItem value="Draft">Draft</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline"><Filter className="mr-2 h-4 w-4" />More</Button>
          </div>

          {filtered.length === 0 ? (
            <EmptyState title="No documents match your search." description="Try adjusting your filters or search query." icon={FileText} />
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow className="hover:bg-transparent">
                    <TableHead>Document</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Revision</TableHead>
                    <TableHead>Uploaded</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>AI Index</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filtered.map((d) => (
                    <TableRow key={d.id} className="cursor-pointer" onClick={() => setDetail(d)}>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <FileText className="h-4 w-4 text-muted-foreground" />
                          <span className="font-medium">{d.name}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-muted-foreground">{d.category}</TableCell>
                      <TableCell className="text-muted-foreground">{d.revision}</TableCell>
                      <TableCell className="text-muted-foreground">{d.uploaded}</TableCell>
                      <TableCell><StatusBadge status={d.status} /></TableCell>
                      <TableCell><StatusBadge status={d.aiIndex} /></TableCell>
                      <TableCell className="text-right" onClick={(e) => e.stopPropagation()}>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-8 w-8"><MoreVertical className="h-4 w-4" /></Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => setDetail(d)}><FileText className="mr-2 h-3.5 w-3.5" />View</DropdownMenuItem>
                            <DropdownMenuItem onClick={() => navigate({ to: "/copilot" })}><Sparkles className="mr-2 h-3.5 w-3.5" />Ask AI</DropdownMenuItem>
                            <DropdownMenuItem onClick={() => navigate({ to: "/compliance" })}><ShieldCheck className="mr-2 h-3.5 w-3.5" />Run Compliance Check</DropdownMenuItem>
                            <DropdownMenuItem onClick={() => toast.success(`${d.name} downloaded`)}><Download className="mr-2 h-3.5 w-3.5" />Download</DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem className="text-critical" onClick={() => setArchiveTarget(d)}><Archive className="mr-2 h-3.5 w-3.5" />Archive</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <UploadDialog open={uploadOpen} onOpenChange={setUploadOpen} />
      <DocumentDetail doc={detail} onClose={() => setDetail(null)} />
      <AlertDialog open={!!archiveTarget} onOpenChange={(o) => !o && setArchiveTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Archive document?</AlertDialogTitle>
            <AlertDialogDescription>
              "{archiveTarget?.name}" will be moved to archive. This action can be reversed by an administrator.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={() => { toast.success("Document archived"); setArchiveTarget(null); }}>Archive</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

function StatCard({ label, value, tone }: { label: string; value: string; tone?: "success" | "warning" | "info" }) {
  const toneClass = tone === "success" ? "text-success" : tone === "warning" ? "text-warning" : tone === "info" ? "text-info" : "text-foreground";
  return (
    <Card className="border-border bg-elevated">
      <CardContent className="p-5">
        <div className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">{label}</div>
        <div className={`mt-2 text-2xl font-semibold ${toneClass}`}>{value}</div>
      </CardContent>
    </Card>
  );
}

function UploadDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (v: boolean) => void }) {
  const [stage, setStage] = useState<"idle" | "uploading" | "processing" | "indexed">("idle");
  const [progress, setProgress] = useState(0);

  const start = () => {
    setStage("uploading");
    setProgress(0);
    let p = 0;
    const iv = setInterval(() => {
      p += 12;
      setProgress(Math.min(p, 100));
      if (p >= 100) {
        clearInterval(iv);
        setStage("processing");
        setTimeout(() => {
          setStage("indexed");
          toast.success("Document uploaded and indexed");
          setTimeout(() => { onOpenChange(false); setStage("idle"); setProgress(0); }, 800);
        }, 900);
      }
    }, 120);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Upload Document</DialogTitle>
          <DialogDescription>Supported: PDF, DOCX, XLSX, CSV. Max size 50 MB.</DialogDescription>
        </DialogHeader>
        {stage === "idle" && (
          <div className="space-y-3">
            <div className="rounded-lg border-2 border-dashed border-border bg-surface p-8 text-center">
              <Upload className="mx-auto mb-2 h-8 w-8 text-muted-foreground" />
              <p className="text-sm font-medium">Drop file here or click to browse</p>
              <p className="mt-1 text-xs text-muted-foreground">PDF · DOCX · XLSX · CSV</p>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div><Label className="text-xs">Document Name</Label><Input placeholder="Electrical Spec R05" /></div>
              <div>
                <Label className="text-xs">Category</Label>
                <Select><SelectTrigger><SelectValue placeholder="Select..." /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="es">Engineering Specification</SelectItem>
                    <SelectItem value="vs">Vendor Submittal</SelectItem>
                    <SelectItem value="dr">Drawing</SelectItem>
                    <SelectItem value="rf">RFI</SelectItem>
                    <SelectItem value="cm">Commissioning</SelectItem>
                    <SelectItem value="ql">Quality</SelectItem>
                    <SelectItem value="sc">Schedule</SelectItem>
                    <SelectItem value="ot">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div><Label className="text-xs">Revision</Label><Input placeholder="R01" /></div>
              <div><Label className="text-xs">Discipline</Label><Input placeholder="Electrical" /></div>
            </div>
          </div>
        )}
        {stage !== "idle" && (
          <div className="space-y-3 py-4">
            <div className="text-sm font-medium">
              {stage === "uploading" && "Uploading document..."}
              {stage === "processing" && "Processing with AI intelligence..."}
              {stage === "indexed" && "Indexed successfully ✓"}
            </div>
            <Progress value={stage === "indexed" ? 100 : progress} />
            <ul className="text-xs text-muted-foreground space-y-1">
              <li className="text-success">• Upload complete</li>
              <li className={stage === "processing" || stage === "indexed" ? "text-success" : ""}>• Extracting document content</li>
              <li className={stage === "indexed" ? "text-success" : ""}>• Indexed into project knowledge base</li>
            </ul>
          </div>
        )}
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={start} disabled={stage !== "idle"}>Upload</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function DocumentDetail({ doc, onClose }: { doc: Document | null; onClose: () => void }) {
  const navigate = useNavigate();
  return (
    <Dialog open={!!doc} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-w-2xl">
        {doc && (
          <>
            <DialogHeader>
              <DialogTitle>{doc.name}</DialogTitle>
              <DialogDescription>{doc.category} · Revision {doc.revision}</DialogDescription>
            </DialogHeader>
            <div className="grid grid-cols-2 gap-3 text-xs">
              <Meta label="Discipline" value={doc.discipline} />
              <Meta label="Upload Date" value={doc.uploaded} />
              <Meta label="Uploaded By" value={doc.uploadedBy} />
              <Meta label="Status" value={<StatusBadge status={doc.status} />} />
              <Meta label="AI Index" value={<StatusBadge status={doc.aiIndex} />} />
            </div>
            {doc.summary && (
              <div className="rounded-md border border-border bg-surface p-3 text-xs text-muted-foreground">
                <div className="mb-1 text-[10px] font-semibold uppercase tracking-widest text-cyan">AI Summary</div>
                {doc.summary}
              </div>
            )}
            <div className="grid grid-cols-2 gap-4 text-xs">
              <div>
                <div className="mb-1 font-semibold text-foreground">Related RFIs</div>
                <ul className="space-y-1 text-muted-foreground">
                  <li>RFI-042 · UPS Room Cable Routing</li>
                  <li>RFI-037 · PDU Metering</li>
                </ul>
              </div>
              <div>
                <div className="mb-1 font-semibold text-foreground">Related Equipment</div>
                <ul className="space-y-1 text-muted-foreground">
                  <li>UPS-04</li>
                  <li>SWGR-02</li>
                </ul>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={onClose}>Close</Button>
              <Button variant="outline" onClick={() => navigate({ to: "/compliance" })}><ShieldCheck className="mr-2 h-3.5 w-3.5" />Run Compliance</Button>
              <Button onClick={() => navigate({ to: "/copilot" })}><Sparkles className="mr-2 h-3.5 w-3.5" />Ask AI</Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}

function Meta({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-widest text-muted-foreground">{label}</div>
      <div className="mt-0.5 font-medium text-foreground">{value}</div>
    </div>
  );
}
