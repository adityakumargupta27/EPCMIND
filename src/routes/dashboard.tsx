import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import {
  Activity, TrendingUp, MessagesSquare, ShieldCheck, AlertTriangle, FileText,
  RefreshCw, ArrowRight, Sparkles, ChevronRight,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { SeverityBadge, StatusBadge } from "@/components/shared/Badges";
import { useEffect } from "react";
import { api } from "@/lib/api";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RTooltip } from "recharts";
import { toast } from "sonner";

export const Route = createFileRoute("/dashboard")({
  head: () => ({
    meta: [
      { title: "Project Intelligence Dashboard — EPCMind AI" },
      { name: "description", content: "Real-time intelligence across engineering, procurement, quality and commissioning." },
    ],
  }),
  component: DashboardPage,
});

function KpiCard({ label, value, subtitle, subtitleTone, to, icon: Icon }: {
  label: string; value: string; subtitle: string; subtitleTone?: "warning" | "critical" | "success" | "muted";
  to: string; icon: React.ComponentType<{ className?: string }>;
}) {
  const toneClass = subtitleTone === "critical" ? "text-critical" : subtitleTone === "warning" ? "text-warning" : subtitleTone === "success" ? "text-success" : "text-muted-foreground";
  return (
    <Link to={to} className="group">
      <Card className="border-border bg-elevated transition-all hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5">
        <CardContent className="p-5">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">{label}</span>
            <Icon className="h-4 w-4 text-muted-foreground group-hover:text-primary" />
          </div>
          <div className="mt-3 text-3xl font-semibold tracking-tight text-foreground">{value}</div>
          <div className={`mt-1 text-xs ${toneClass}`}>{subtitle}</div>
        </CardContent>
      </Card>
    </Link>
  );
}

function DashboardPage() {
  const navigate = useNavigate();
  const [refreshing, setRefreshing] = useState(false);
  const [ts, setTs] = useState("Just now");
  
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<Error | null>(null);

  const loadData = async () => {
    try {
      const [project, risks, schedule, activity] = await Promise.all([
        api.getProject(),
        api.getRisks(),
        api.getSchedule(),
        api.getRecentActivity(),
      ]);
      setData({ project, risks, schedule, activity });
    } catch (e) {
      setError(e instanceof Error ? e : new Error("Unknown error"));
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const refresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
    setTs("Just now");
    toast.success("Dashboard refreshed");
  };

  if (error) return <div className="p-6 text-critical">Error loading dashboard: {error.message}</div>;
  if (!data) return <div className="p-6 text-muted-foreground animate-pulse">Loading dashboard...</div>;

  const mockProject = data.project;
  const healthBreakdown = data.project.healthBreakdown;
  const progressBreakdown = data.project.progressBreakdown;
  const riskDistribution = data.risks.distribution;
  const upcomingMilestones = data.schedule.upcoming;
  const recentActivity = data.activity;

  return (
    <div className="mx-auto max-w-[1600px] px-6 py-6 space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Project Intelligence Dashboard</h1>
          <p className="mt-1 text-sm text-muted-foreground">Real-time intelligence across engineering, procurement, quality and commissioning.</p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-muted-foreground">Last updated: {ts}</span>
          <Button variant="outline" size="sm" onClick={refresh} disabled={refreshing}>
            <RefreshCw className={`mr-2 h-3.5 w-3.5 ${refreshing ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Project status bar */}
      <Card className="border-border bg-gradient-to-r from-elevated to-surface">
        <CardContent className="flex flex-wrap items-center justify-between gap-6 p-5">
          <div className="flex items-center gap-4">
            <div className="h-10 w-1 rounded-full bg-warning" />
            <div>
              <div className="text-lg font-semibold text-foreground">{mockProject.name}</div>
              <div className="text-xs text-muted-foreground">{mockProject.code} · {mockProject.location}</div>
            </div>
          </div>
          <div className="flex flex-wrap gap-6 text-xs">
            <Stat label="Capacity" value={mockProject.capacity} />
            <Stat label="Tier" value={mockProject.tier} />
            <Stat label="Phase" value={mockProject.phase} />
            <Stat label="Progress" value={`${mockProject.progress}%`} />
            <Stat label="Status" value={<StatusBadge status="At Risk" />} />
          </div>
        </CardContent>
      </Card>

      {/* KPI grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
        <KpiCard label="Project Health" value="78 / 100" subtitle="At Risk" subtitleTone="warning" to="/project" icon={Activity} />
        <KpiCard label="Project Progress" value="72%" subtitle="+4% this month" subtitleTone="success" to="/schedule" icon={TrendingUp} />
        <KpiCard label="Open RFIs" value="14" subtitle="3 Critical" subtitleTone="critical" to="/rfis" icon={MessagesSquare} />
        <KpiCard label="Compliance Issues" value="6" subtitle="2 High Severity" subtitleTone="warning" to="/compliance" icon={ShieldCheck} />
        <KpiCard label="Active Risks" value="11" subtitle="3 Critical" subtitleTone="critical" to="/risks" icon={AlertTriangle} />
        <KpiCard label="Documents" value="248" subtitle="236 Indexed" subtitleTone="muted" to="/documents" icon={FileText} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Project Health */}
        <Card className="border-border bg-elevated lg:col-span-1">
          <CardHeader>
            <CardTitle className="text-sm">Project Health Score</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-5xl font-semibold text-foreground">78</span>
              <span className="text-sm text-muted-foreground">/ 100</span>
              <StatusBadge status="At Risk" className="ml-auto" />
            </div>
            <div className="mt-5 space-y-3">
              {healthBreakdown.map((h) => {
                const tone = h.value < 65 ? "bg-critical" : h.value < 80 ? "bg-warning" : "bg-success";
                return (
                  <div key={h.name}>
                    <div className="mb-1 flex justify-between text-xs">
                      <span className="text-muted-foreground">{h.name}</span>
                      <span className="font-medium text-foreground">{h.value}</span>
                    </div>
                    <div className="h-1.5 w-full rounded-full bg-secondary">
                      <div className={`h-full rounded-full ${tone}`} style={{ width: `${h.value}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Progress */}
        <Card className="border-border bg-elevated lg:col-span-1">
          <CardHeader><CardTitle className="text-sm">Construction Progress</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <span className="text-5xl font-semibold text-foreground">72%</span>
              <span className="text-xs text-success">+4% this month</span>
            </div>
            <div className="mt-5 space-y-3">
              {progressBreakdown.map((p) => (
                <div key={p.name}>
                  <div className="mb-1 flex justify-between text-xs">
                    <span className="text-muted-foreground">{p.name}</span>
                    <span className="font-medium text-foreground">{p.value}%</span>
                  </div>
                  <Progress value={p.value} className="h-1.5" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Risk Distribution */}
        <Card className="border-border bg-elevated lg:col-span-1">
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm">Risk Distribution</CardTitle>
            <Button variant="ghost" size="sm" onClick={() => navigate({ to: "/risks" })}>View <ChevronRight className="ml-1 h-3 w-3" /></Button>
          </CardHeader>
          <CardContent>
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={riskDistribution} dataKey="value" innerRadius={55} outerRadius={80} paddingAngle={2}>
                    {riskDistribution.map((entry) => (<Cell key={entry.name} fill={entry.color} />))}
                  </Pie>
                  <RTooltip contentStyle={{ background: "#151D2B", border: "1px solid #253044", borderRadius: 8, fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {riskDistribution.map((r) => (
                <div key={r.name} className="flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full" style={{ background: r.color }} />
                  <span className="text-muted-foreground">{r.name}</span>
                  <span className="ml-auto font-medium text-foreground">{r.value}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* AI Alerts */}
      <div>
        <div className="mb-3 flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-cyan" />
          <h2 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground">AI Intelligence Alerts</h2>
        </div>
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
          <AlertCard
            severity="CRITICAL" title="UPS-04 Delivery Delay"
            body="Shipment is currently 12 days behind schedule and exceeds available activity float by 8 days."
            impact="Integrated Systems Testing"
            cta="View Risk" onCta={() => navigate({ to: "/risks" })}
          />
          <AlertCard
            severity="HIGH" title="UPS Efficiency Specification Deviation"
            body="Required ≥96%. Vendor submitted 94.8%. Deviation of −1.2% requires resolution."
            impact="Equipment approval"
            cta="Review Compliance" onCta={() => navigate({ to: "/compliance" })}
          />
          <AlertCard
            severity="MEDIUM" title="Similar RFI Identified"
            body="RFI-042 shows 91% similarity with resolved RFI-017 on cable tray routing adjustment."
            impact="RFI resolution acceleration"
            cta="Review RFI" onCta={() => navigate({ to: "/rfis" })}
          />
        </div>
      </div>

      {/* Milestones + activity */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="border-border bg-elevated lg:col-span-2">
          <CardHeader className="flex-row items-center justify-between space-y-0">
            <CardTitle className="text-sm">Upcoming Milestones</CardTitle>
            <Button variant="ghost" size="sm" onClick={() => navigate({ to: "/schedule" })}>
              View Full Schedule <ArrowRight className="ml-1 h-3 w-3" />
            </Button>
          </CardHeader>
          <CardContent>
            <ul className="divide-y divide-border">
              {upcomingMilestones.map((m) => (
                <li key={m.name} className="flex items-center justify-between py-3">
                  <div>
                    <div className="text-sm font-medium text-foreground">{m.name}</div>
                    <div className="text-xs text-muted-foreground">Due: {m.planned}</div>
                  </div>
                  <StatusBadge status={m.status} />
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card className="border-border bg-elevated">
          <CardHeader><CardTitle className="text-sm">Recent Activity</CardTitle></CardHeader>
          <CardContent>
            <ol className="relative space-y-4 border-l border-border pl-4">
              {recentActivity.map((a, i) => (
                <li key={i} className="relative">
                  <span className="absolute -left-[21px] top-1 h-2 w-2 rounded-full bg-primary" />
                  <div className="text-[11px] text-muted-foreground">{a.time}</div>
                  <div className="text-xs text-foreground">{a.text}</div>
                </li>
              ))}
            </ol>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <div className="text-[10px] uppercase tracking-widest text-muted-foreground">{label}</div>
      <div className="mt-0.5 text-sm font-medium text-foreground">{value}</div>
    </div>
  );
}

function AlertCard({ severity, title, body, impact, cta, onCta }: {
  severity: "CRITICAL" | "HIGH" | "MEDIUM"; title: string; body: string; impact: string; cta: string; onCta: () => void;
}) {
  const borderTone = severity === "CRITICAL" ? "border-l-critical" : severity === "HIGH" ? "border-l-warning" : "border-l-info";
  return (
    <Card className={`border-border bg-elevated border-l-4 ${borderTone}`}>
      <CardContent className="p-5">
        <div className="flex items-center justify-between">
          <SeverityBadge severity={severity} />
          <Sparkles className="h-3.5 w-3.5 text-cyan" />
        </div>
        <h3 className="mt-3 text-sm font-semibold text-foreground">{title}</h3>
        <p className="mt-1 text-xs text-muted-foreground">{body}</p>
        <div className="mt-3 rounded-md border border-border bg-surface px-2 py-1.5 text-[11px]">
          <span className="text-muted-foreground">Potential Impact: </span>
          <span className="font-medium text-foreground">{impact}</span>
        </div>
        <Button variant="outline" size="sm" className="mt-4 w-full" onClick={onCta}>
          {cta} <ArrowRight className="ml-1 h-3 w-3" />
        </Button>
      </CardContent>
    </Card>
  );
}
