import { createFileRoute } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { SeverityBadge, StatusBadge } from "@/components/shared/Badges";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export const Route = createFileRoute("/project")({
  head: () => ({ meta: [{ title: "Project Overview — EPCMind AI" }, { name: "description", content: "Comprehensive overview of the Bengaluru Hyperscale Data Centre EPC project." }] }),
  component: ProjectPage,
});

function ProjectPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    api.getProject().then(setData).catch(setError);
  }, []);

  if (error) return <div className="p-6 text-critical">Error loading project: {error.message}</div>;
  if (!data) return <div className="p-6 text-muted-foreground animate-pulse">Loading project data...</div>;

  const mockProject = data;
  const projectTeam = data.team;
  const disciplines = data.disciplines;
  const equipmentList = data.equipment;

  return (
    <div className="mx-auto max-w-[1600px] px-6 py-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Project Overview</h1>
        <p className="mt-1 text-sm text-muted-foreground">Comprehensive information across scope, team, disciplines and equipment.</p>
      </div>

      <Card className="border-border bg-elevated">
        <CardContent className="grid grid-cols-2 gap-6 p-6 md:grid-cols-4 lg:grid-cols-8">
          <Detail label="Project" value={mockProject.name} />
          <Detail label="Code" value={mockProject.code} />
          <Detail label="Location" value={mockProject.location} />
          <Detail label="Capacity" value={mockProject.capacity} />
          <Detail label="Tier" value={mockProject.tier} />
          <Detail label="Phase" value={mockProject.phase} />
          <Detail label="Progress" value={`${mockProject.progress}%`} />
          <Detail label="Health" value={<span className="text-warning font-semibold">{mockProject.health} / 100</span>} />
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="border-border bg-elevated">
          <CardHeader><CardTitle className="text-sm">Project Team</CardTitle></CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {projectTeam.map((p) => (
                <li key={p.name} className="flex items-center gap-3">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-primary to-cyan text-xs font-semibold text-primary-foreground">
                    {p.name.split(" ").map((s) => s[0]).slice(0,2).join("")}
                  </div>
                  <div>
                    <div className="text-sm font-medium">{p.name}</div>
                    <div className="text-xs text-muted-foreground">{p.role}</div>
                  </div>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card className="border-border bg-elevated lg:col-span-2">
          <CardHeader><CardTitle className="text-sm">Disciplines</CardTitle></CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {disciplines.map((d) => (
                <div key={d.name} className="rounded-md border border-border bg-surface p-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{d.name}</span>
                    <span className="text-[11px] text-muted-foreground">Health {d.health}</span>
                  </div>
                  <div className="mt-2"><Progress value={d.progress} className="h-1.5" /></div>
                  <div className="mt-1 text-[11px] text-muted-foreground">{d.progress}% complete</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="border-border bg-elevated">
        <CardHeader><CardTitle className="text-sm">Critical Equipment</CardTitle></CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent">
                <TableHead>Equipment</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Severity</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {equipmentList.map((e) => (
                <TableRow key={e.id}>
                  <TableCell className="font-medium">{e.id}</TableCell>
                  <TableCell className="text-muted-foreground">{e.type}</TableCell>
                  <TableCell><StatusBadge status={e.status} /></TableCell>
                  <TableCell><SeverityBadge severity={e.severity} /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-widest text-muted-foreground">{label}</div>
      <div className="mt-1 text-sm font-medium text-foreground">{value}</div>
    </div>
  );
}
