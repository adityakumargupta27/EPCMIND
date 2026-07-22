import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { SeverityBadge, StatusBadge } from "@/components/shared/Badges";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export const Route = createFileRoute("/schedule")({
  head: () => ({ meta: [{ title: "Schedule Intelligence — EPCMind AI" }, { name: "description", content: "Monitor critical milestones, activity progress and schedule exposure." }] }),
  component: SchedulePage,
});

const MONTHS = ["Jan 2026", "Feb 2026", "Mar 2026", "Apr 2026", "May 2026", "Jun 2026", "Jul 2026", "Aug 2026", "Sep 2026"];

function monthIndex(s: string) { const i = MONTHS.indexOf(s); return i < 0 ? 0 : i; }

function SchedulePage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    api.getSchedule().then(setData).catch(setError);
  }, []);

  if (error) return <div className="p-6 text-critical">Error loading schedule: {error.message}</div>;
  if (!data) return <div className="p-6 text-muted-foreground animate-pulse">Loading schedule...</div>;

  const scheduleActivities = data.activities;
  const milestones = data.milestones;
  const scheduleStats = data.stats;
  const criticalPath = data.criticalPath;

  return (
    <div className="mx-auto max-w-[1600px] px-6 py-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Project Schedule Intelligence</h1>
        <p className="mt-1 text-sm text-muted-foreground">Monitor critical milestones, activity progress and schedule exposure.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-6">
        <Stat label="Overall Progress" value={`${scheduleStats.progress}%`} />
        <Stat label="Activities" value={scheduleStats.activities} />
        <Stat label="Completed" value={scheduleStats.completed} tone="success" />
        <Stat label="In Progress" value={scheduleStats.inProgress} tone="info" />
        <Stat label="Delayed" value={scheduleStats.delayed} tone="critical" />
        <Stat label="Critical Activities" value={scheduleStats.critical} tone="warning" />
      </div>

      <Card className="border-border bg-elevated">
        <CardHeader><CardTitle className="text-sm">Timeline</CardTitle></CardHeader>
        <CardContent>
          <div className="min-w-[720px]">
            <div className="mb-2 grid grid-cols-9 gap-1 text-[10px] text-muted-foreground">
              {MONTHS.map((m) => <div key={m} className="text-center">{m.split(" ")[0]}</div>)}
            </div>
            <div className="space-y-2">
              {scheduleActivities.map((a) => {
                const start = monthIndex(a.start);
                const end = monthIndex(a.finish);
                const span = Math.max(end - start + 1, 1);
                return (
                  <div key={a.id} className="grid grid-cols-9 gap-1 items-center">
                    <div className="col-span-9 grid grid-cols-9 gap-1 relative">
                      <div className="col-span-9 absolute inset-0 flex items-center pl-1 text-[11px] text-foreground pointer-events-none z-10">
                        {a.name}
                      </div>
                      <div style={{ gridColumnStart: start + 1, gridColumnEnd: `span ${span}` }} className={`h-8 rounded ${a.critical ? "bg-critical/25 border border-critical/50" : "bg-primary/25 border border-primary/40"}`}>
                        <div className="h-full rounded" style={{ width: `${a.progress}%`, background: a.critical ? "rgba(239,68,68,0.55)" : "rgba(59,130,246,0.55)" }} />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            <div className="mt-4 flex items-center gap-4 text-[11px] text-muted-foreground">
              <span className="flex items-center gap-1.5"><span className="h-2 w-4 rounded-sm bg-primary/50" />Activity</span>
              <span className="flex items-center gap-1.5"><span className="h-2 w-4 rounded-sm bg-critical/60" />Critical Path</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="border-border bg-elevated lg:col-span-1">
          <CardHeader><CardTitle className="text-sm">Critical Path</CardTitle></CardHeader>
          <CardContent>
            <ol className="space-y-3">
              {criticalPath.map((cp, i) => (
                <li key={cp.name} className="flex items-start gap-3">
                  <div className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-secondary text-[11px] font-semibold text-foreground">{i + 1}</div>
                  <div className="flex-1">
                    <div className="text-sm font-medium">{cp.name}</div>
                    <div className={`text-xs ${cp.status.includes("Delayed") ? "text-critical font-semibold" : "text-muted-foreground"}`}>{cp.status}</div>
                  </div>
                  <SeverityBadge severity={cp.severity} />
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>

        <Card className="border-border bg-elevated lg:col-span-2">
          <CardHeader><CardTitle className="text-sm">Milestones</CardTitle></CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow className="hover:bg-transparent">
                  <TableHead>Milestone</TableHead>
                  <TableHead>Planned Date</TableHead>
                  <TableHead>Forecast Date</TableHead>
                  <TableHead>Variance</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {milestones.map((m) => (
                  <TableRow key={m.name}>
                    <TableCell className="font-medium">{m.name}</TableCell>
                    <TableCell className="text-muted-foreground">{m.planned}</TableCell>
                    <TableCell className="text-muted-foreground">{m.forecast}</TableCell>
                    <TableCell><span className={m.variance.startsWith("+") ? "text-critical font-semibold" : "text-muted-foreground"}>{m.variance}</span></TableCell>
                    <TableCell><StatusBadge status={m.status} /></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: number | string; tone?: "critical" | "warning" | "info" | "success" }) {
  const t = tone === "critical" ? "text-critical" : tone === "warning" ? "text-warning" : tone === "info" ? "text-info" : tone === "success" ? "text-success" : "text-foreground";
  return (<Card className="border-border bg-elevated"><CardContent className="p-5"><div className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">{label}</div><div className={`mt-2 text-2xl font-semibold ${t}`}>{value}</div></CardContent></Card>);
}
