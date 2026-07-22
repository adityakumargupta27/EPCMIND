import { useEffect, useState } from "react";
import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import {
  LayoutDashboard, Sparkles, ShieldCheck, MessagesSquare, AlertTriangle,
  FileText, CalendarClock, FolderKanban, Settings, Search, Bell, HelpCircle,
  ChevronLeft, ChevronRight, PanelLeft, Cpu, Circle,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import {
  CommandDialog, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList, CommandSeparator,
} from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { SeverityBadge } from "@/components/shared/Badges";
import { mockNotifications } from "@/data/mockNotifications";
import { mockProject } from "@/data/mockProject";
import { toast } from "sonner";

const navSections = [
  {
    label: "OVERVIEW",
    items: [{ to: "/dashboard", label: "Dashboard", icon: LayoutDashboard }],
  },
  {
    label: "AI INTELLIGENCE",
    items: [
      { to: "/copilot", label: "AI Copilot", icon: Sparkles },
      { to: "/compliance", label: "Compliance", icon: ShieldCheck },
      { to: "/rfis", label: "RFI Intelligence", icon: MessagesSquare },
      { to: "/risks", label: "Risk Intelligence", icon: AlertTriangle },
    ],
  },
  {
    label: "PROJECT",
    items: [
      { to: "/documents", label: "Documents", icon: FileText },
      { to: "/schedule", label: "Schedule", icon: CalendarClock },
      { to: "/project", label: "Project Overview", icon: FolderKanban },
    ],
  },
  { label: "SYSTEM", items: [{ to: "/settings", label: "Settings", icon: Settings }] },
];

const searchIndex = [
  { type: "Page", name: "Dashboard", to: "/dashboard" },
  { type: "Page", name: "AI Copilot", to: "/copilot" },
  { type: "Page", name: "Compliance", to: "/compliance" },
  { type: "Page", name: "RFI Intelligence", to: "/rfis" },
  { type: "Page", name: "Risk Intelligence", to: "/risks" },
  { type: "Page", name: "Documents", to: "/documents" },
  { type: "Page", name: "Schedule", to: "/schedule" },
  { type: "Document", name: "UPS Technical Specification", to: "/documents" },
  { type: "Document", name: "Electrical Design Specification", to: "/documents" },
  { type: "RFI", name: "RFI-042 Cable Routing Conflict", to: "/rfis" },
  { type: "RFI", name: "RFI-041 Cooling Pipe Clearance", to: "/rfis" },
  { type: "Equipment", name: "UPS-04", to: "/project" },
  { type: "Equipment", name: "CH-02", to: "/project" },
  { type: "Risk", name: "UPS Delivery Delay", to: "/risks" },
  { type: "Risk", name: "UPS Efficiency Deviation", to: "/risks" },
];

function Logo() {
  return (
    <div className="flex items-center gap-2">
      <div className="flex h-8 w-8 items-center justify-center rounded-md bg-gradient-to-br from-primary to-cyan text-primary-foreground">
        <Cpu className="h-4 w-4" />
      </div>
      <div className="flex flex-col leading-tight">
        <span className="text-sm font-semibold tracking-tight text-foreground">EPCMind AI</span>
        <span className="text-[10px] uppercase tracking-widest text-muted-foreground">Intelligence Platform</span>
      </div>
    </div>
  );
}

function Sidebar({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  return (
    <aside className={cn("hidden md:flex shrink-0 flex-col border-r border-sidebar-border bg-sidebar transition-all", collapsed ? "w-16" : "w-64")}>
      <div className={cn("flex h-14 items-center border-b border-sidebar-border px-3", collapsed && "justify-center px-0")}>
        {collapsed ? (
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-gradient-to-br from-primary to-cyan text-primary-foreground">
            <Cpu className="h-4 w-4" />
          </div>
        ) : <Logo />}
      </div>
      <nav className="flex-1 overflow-y-auto scrollbar-thin px-2 py-4">
        <TooltipProvider delayDuration={100}>
          {navSections.map((section) => (
            <div key={section.label} className="mb-4">
              {!collapsed && (
                <div className="mb-1 px-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">
                  {section.label}
                </div>
              )}
              <ul className="space-y-0.5">
                {section.items.map((item) => {
                  const active = pathname === item.to || pathname.startsWith(item.to + "/");
                  const link = (
                    <Link
                      to={item.to}
                      className={cn(
                        "flex items-center gap-3 rounded-md px-2 py-2 text-sm transition-colors",
                        active ? "bg-primary/15 text-primary" : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-foreground",
                        collapsed && "justify-center"
                      )}
                    >
                      <item.icon className="h-4 w-4 shrink-0" />
                      {!collapsed && <span className="truncate">{item.label}</span>}
                      {!collapsed && active && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-primary" />}
                    </Link>
                  );
                  return (
                    <li key={item.to}>
                      {collapsed ? (
                        <Tooltip>
                          <TooltipTrigger asChild>{link}</TooltipTrigger>
                          <TooltipContent side="right">{item.label}</TooltipContent>
                        </Tooltip>
                      ) : link}
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </TooltipProvider>
      </nav>
      <div className="border-t border-sidebar-border p-2">
        {!collapsed ? (
          <div className="rounded-md border border-sidebar-border bg-elevated p-3">
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Active Project</span>
              <span className="flex items-center gap-1 text-[10px] font-semibold text-warning">
                <Circle className="h-2 w-2 fill-warning text-warning" />
                {mockProject.status}
              </span>
            </div>
            <div className="mt-1 text-sm font-semibold text-foreground">{mockProject.code}</div>
            <div className="text-xs text-muted-foreground">Bengaluru Hyperscale</div>
            <div className="text-xs text-muted-foreground">Data Centre</div>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="h-2 w-2 rounded-full bg-warning" />
          </div>
        )}
        <button
          onClick={onToggle}
          className="mt-2 flex w-full items-center justify-center rounded-md border border-sidebar-border bg-transparent px-2 py-1.5 text-xs text-muted-foreground hover:bg-sidebar-accent hover:text-foreground"
        >
          {collapsed ? <ChevronRight className="h-3.5 w-3.5" /> : (<><ChevronLeft className="h-3.5 w-3.5 mr-1" />Collapse</>)}
        </button>
      </div>
    </aside>
  );
}

const routeTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/copilot": "AI Copilot",
  "/compliance": "Compliance",
  "/rfis": "RFI Intelligence",
  "/risks": "Risk Intelligence",
  "/documents": "Documents",
  "/schedule": "Schedule",
  "/project": "Project Overview",
  "/settings": "Settings",
};

function Header({ onToggleSidebar }: { onToggleSidebar: () => void }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const [cmdOpen, setCmdOpen] = useState(false);
  const navigate = useNavigate();
  const title = routeTitles[pathname] ?? "Dashboard";

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setCmdOpen((v) => !v);
      }
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  const unread = mockNotifications.filter((n) => !n.read).length;

  const grouped = searchIndex.reduce<Record<string, typeof searchIndex>>((acc, item) => {
    (acc[item.type] ||= []).push(item);
    return acc;
  }, {});

  return (
    <header className="sticky top-0 z-20 flex h-14 items-center justify-between border-b border-border bg-background/80 px-4 backdrop-blur">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={onToggleSidebar} className="md:hidden">
          <PanelLeft className="h-4 w-4" />
        </Button>
        <nav className="flex items-center gap-1.5 text-xs">
          <span className="text-muted-foreground">EPCMind AI</span>
          <span className="text-muted-foreground">/</span>
          <span className="font-medium text-foreground">{title}</span>
        </nav>
      </div>

      <div className="hidden lg:flex items-center gap-3 rounded-md border border-border bg-surface px-3 py-1.5">
        <div className="h-2 w-2 rounded-full bg-warning" />
        <div className="flex flex-col leading-tight">
          <span className="text-[10px] uppercase tracking-widest text-muted-foreground">Current Project</span>
          <span className="text-xs font-semibold text-foreground">{mockProject.code} · {mockProject.name}</span>
        </div>
      </div>

      <div className="flex items-center gap-1.5">
        <Button variant="ghost" size="sm" onClick={() => setCmdOpen(true)} className="gap-2 text-muted-foreground">
          <Search className="h-4 w-4" />
          <span className="hidden md:inline text-xs">Search</span>
          <kbd className="hidden md:inline rounded border border-border bg-elevated px-1.5 py-0.5 text-[10px]">⌘K</kbd>
        </Button>
        <Popover>
          <PopoverTrigger asChild>
            <Button variant="ghost" size="icon" className="relative">
              <Bell className="h-4 w-4" />
              {unread > 0 && <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-critical" />}
            </Button>
          </PopoverTrigger>
          <PopoverContent align="end" className="w-96 p-0">
            <div className="flex items-center justify-between border-b border-border px-4 py-3">
              <span className="text-sm font-semibold">Notifications</span>
              <button className="text-xs text-primary hover:underline" onClick={() => toast.success("All notifications marked as read")}>Mark all read</button>
            </div>
            <ul className="max-h-96 overflow-y-auto scrollbar-thin divide-y divide-border">
              {mockNotifications.map((n) => (
                <li key={n.id} className="px-4 py-3 hover:bg-accent/50">
                  <div className="flex items-start gap-3">
                    <SeverityBadge severity={n.severity} />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-foreground">{n.title}</div>
                      <div className="text-xs text-muted-foreground">{n.message}</div>
                      <div className="mt-1 text-[10px] text-muted-foreground">{n.time}</div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
            <button
              className="block w-full border-t border-border px-4 py-2 text-xs font-medium text-primary hover:bg-accent"
              onClick={() => navigate({ to: "/risks" })}
            >
              View all alerts
            </button>
          </PopoverContent>
        </Popover>
        <Button variant="ghost" size="icon"><HelpCircle className="h-4 w-4" /></Button>
        <div className="ml-2 flex items-center gap-2 border-l border-border pl-3">
          <div className="hidden md:flex flex-col text-right leading-tight">
            <span className="text-xs font-medium text-foreground">Arjun Mehta</span>
            <span className="text-[10px] text-muted-foreground">Project Manager</span>
          </div>
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-gradient-to-br from-primary to-cyan text-xs font-semibold text-primary-foreground">AM</div>
        </div>
      </div>

      <CommandDialog open={cmdOpen} onOpenChange={setCmdOpen}>
        <CommandInput placeholder="Search documents, RFIs, equipment, risks, pages..." />
        <CommandList>
          <CommandEmpty>No results found.</CommandEmpty>
          {Object.entries(grouped).map(([group, items], i) => (
            <div key={group}>
              {i > 0 && <CommandSeparator />}
              <CommandGroup heading={group}>
                {items.map((item) => (
                  <CommandItem key={item.name} onSelect={() => { setCmdOpen(false); navigate({ to: item.to }); }}>
                    {item.name}
                  </CommandItem>
                ))}
              </CommandGroup>
            </div>
          ))}
        </CommandList>
      </CommandDialog>
    </header>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const [collapsed, setCollapsed] = useState(false);
  return (
    <div className="flex min-h-screen w-full bg-background text-foreground">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed((v) => !v)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header onToggleSidebar={() => setCollapsed((v) => !v)} />
        <main className="flex-1 overflow-x-hidden">{children}</main>
      </div>
    </div>
  );
}
