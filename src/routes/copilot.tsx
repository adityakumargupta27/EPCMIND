import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Send, Sparkles, Paperclip, Copy, ShieldCheck, ExternalLink, Plus, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { SeverityBadge } from "@/components/shared/Badges";
import { api } from "@/lib/api";
import type { AIMessage } from "@/types";
import { toast } from "sonner";
import { useNavigate } from "@tanstack/react-router";

export const Route = createFileRoute("/copilot")({
  head: () => ({ meta: [{ title: "AI Copilot — EPCMind AI" }, { name: "description", content: "Ask questions across your project specifications, RFIs, schedules and quality documentation." }] }),
  component: CopilotPage,
});

const suggested = [
  "What is the required UPS redundancy?",
  "Which equipment currently threatens the commissioning schedule?",
  "Show unresolved high-severity compliance deviations.",
  "What does the specification require for battery autonomy?",
  "Which RFIs relate to cable routing?",
];

const history = [
  "UPS Redundancy Requirements",
  "Cooling Specification Review",
  "Commissioning Requirements",
  "Cable Routing Question",
];

const loadingStages = [
  "Understanding your question...",
  "Searching project knowledge...",
  "Analyzing relevant specifications...",
  "Generating response...",
];

function CopilotPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<AIMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [stage, setStage] = useState(0);

  const send = async (text: string) => {
    if (!text.trim() || loading) return;
    setMessages((m) => [...m, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    setStage(0);
    const iv = setInterval(() => setStage((s) => Math.min(s + 1, loadingStages.length - 1)), 400);
    const resp = await api.askCopilot(text);
    clearInterval(iv);
    setMessages((m) => [...m, resp]);
    setLoading(false);
  };

  return (
    <div className="flex h-[calc(100vh-3.5rem)] w-full">
      {/* Left panel */}
      <aside className="hidden lg:flex w-64 shrink-0 flex-col border-r border-border bg-surface">
        <div className="border-b border-border p-3">
          <Button className="w-full" onClick={() => setMessages([])}><Plus className="mr-2 h-4 w-4" />New Conversation</Button>
        </div>
        <div className="p-3">
          <div className="mb-2 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">History</div>
          <ul className="space-y-1">
            {history.map((h) => (
              <li key={h}>
                <button className="flex w-full items-center gap-2 rounded-md px-2 py-2 text-left text-xs text-muted-foreground hover:bg-accent hover:text-foreground">
                  <MessageSquare className="h-3.5 w-3.5" />
                  <span className="truncate">{h}</span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      </aside>

      {/* Center */}
      <div className="flex min-w-0 flex-1 flex-col">
        <div className="border-b border-border px-6 py-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-cyan" />
            <h1 className="text-lg font-semibold">Project Intelligence Copilot</h1>
          </div>
          <p className="mt-0.5 text-xs text-muted-foreground">Ask questions across your project specifications, RFIs, schedules and quality documentation.</p>
        </div>

        <div className="flex-1 overflow-y-auto scrollbar-thin px-6 py-6">
          {messages.length === 0 && !loading && (
            <div className="mx-auto max-w-2xl">
              <div className="mb-6 text-center">
                <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-cyan">
                  <Sparkles className="h-6 w-6 text-primary-foreground" />
                </div>
                <h2 className="text-xl font-semibold">Ask EPCMind about your project</h2>
                <p className="mt-1 text-sm text-muted-foreground">Grounded in your specifications, RFIs, submittals and schedule.</p>
              </div>
              <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                {suggested.map((s) => (
                  <button key={s} onClick={() => send(s)} className="rounded-lg border border-border bg-elevated p-3 text-left text-xs transition-colors hover:border-primary/40 hover:bg-accent">
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="mx-auto max-w-3xl space-y-6">
            {messages.map((m, i) => (
              <div key={i} className={m.role === "user" ? "flex justify-end" : ""}>
                {m.role === "user" ? (
                  <div className="max-w-[80%] rounded-lg bg-primary/15 border border-primary/20 px-4 py-2.5 text-sm">{m.content}</div>
                ) : (
                  <Card className="border-border bg-elevated">
                    <CardContent className="space-y-3 p-5">
                      <div className="flex items-center gap-2">
                        <Sparkles className="h-4 w-4 text-cyan" />
                        <span className="text-xs font-semibold uppercase tracking-widest text-cyan">EPCMind Response</span>
                        {m.meta?.risk && <SeverityBadge severity={m.meta.risk} />}
                      </div>
                      <p className="whitespace-pre-line text-sm text-foreground">{m.content}</p>
                      {m.meta?.action && (
                        <div className="rounded-md border border-border bg-surface p-3">
                          <div className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Recommended Action</div>
                          <div className="mt-1 text-xs text-foreground">{m.meta.action}</div>
                        </div>
                      )}
                      {m.sources && (
                        <div>
                          <div className="mb-1.5 text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Sources</div>
                          <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                            {m.sources.map((s, j) => (
                              <div key={j} className="rounded-md border border-border bg-surface p-2.5">
                                <div className="flex items-center gap-1.5 text-xs font-medium">
                                  <ExternalLink className="h-3 w-3 text-muted-foreground" />
                                  {s.document}
                                </div>
                                <div className="mt-0.5 text-[11px] text-muted-foreground">{s.section} · Page {s.page}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      <div className="flex flex-wrap gap-2 pt-2">
                        <Button variant="outline" size="sm" onClick={() => { navigator.clipboard.writeText(m.content); toast.success("Response copied"); }}>
                          <Copy className="mr-1.5 h-3 w-3" />Copy Answer
                        </Button>
                        <Button variant="outline" size="sm" onClick={() => navigate({ to: "/compliance" })}>
                          <ShieldCheck className="mr-1.5 h-3 w-3" />Run Compliance Check
                        </Button>
                        <Button variant="outline" size="sm">View Sources</Button>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            ))}
            {loading && (
              <Card className="border-border bg-elevated">
                <CardContent className="p-5">
                  <div className="flex items-center gap-2 text-cyan">
                    <Sparkles className="h-4 w-4 animate-pulse" />
                    <span className="text-xs font-semibold uppercase tracking-widest">Analyzing project intelligence...</span>
                  </div>
                  <ul className="mt-3 space-y-1.5 text-xs">
                    {loadingStages.map((s, i) => (
                      <li key={s} className={i <= stage ? "text-foreground" : "text-muted-foreground/50"}>
                        {i <= stage ? "✓" : "○"} {s}
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>
        </div>

        <div className="border-t border-border bg-surface px-6 py-4">
          <div className="mx-auto max-w-3xl">
            <div className="relative">
              <Textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(input); } }}
                placeholder="Ask EPCMind anything about this project..."
                className="min-h-[60px] resize-none pr-24"
              />
              <div className="absolute bottom-2 right-2 flex items-center gap-1">
                <Button variant="ghost" size="icon" className="h-8 w-8"><Paperclip className="h-4 w-4" /></Button>
                <Button size="icon" className="h-8 w-8" onClick={() => send(input)} disabled={loading || !input.trim()}><Send className="h-4 w-4" /></Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right panel */}
      <aside className="hidden xl:flex w-72 shrink-0 flex-col border-l border-border bg-surface p-4">
        <div className="text-[10px] font-semibold uppercase tracking-widest text-muted-foreground">Sources & Context</div>
        <div className="mt-3 space-y-2">
          {["Electrical Design Specification", "UPS Vendor Submittal", "Cooling System Specification", "Commissioning Requirements"].map((s) => (
            <div key={s} className="rounded-md border border-border bg-elevated p-2.5 text-xs">
              <div className="font-medium">{s}</div>
              <div className="text-[10px] text-muted-foreground">Indexed · Retrieved for context</div>
            </div>
          ))}
        </div>
      </aside>
    </div>
  );
}
