import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { toast } from "sonner";

export const Route = createFileRoute("/settings")({
  head: () => ({ meta: [{ title: "Settings — EPCMind AI" }, { name: "description", content: "Manage profile, appearance, notifications and AI preferences." }] }),
  component: SettingsPage,
});

function SettingsPage() {
  const [theme, setTheme] = useState<"dark" | "light" | "system">("dark");

  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove("dark", "light");
    if (theme === "light") root.classList.add("light");
    else root.classList.add("dark");
  }, [theme]);

  return (
    <div className="mx-auto max-w-4xl px-6 py-6 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">Manage your profile, appearance and AI preferences.</p>
      </div>

      <Card className="border-border bg-elevated">
        <CardHeader><CardTitle className="text-sm">Profile</CardTitle></CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div><Label className="text-xs">Name</Label><Input defaultValue="Arjun Mehta" /></div>
          <div><Label className="text-xs">Email</Label><Input defaultValue="arjun.mehta@epcmind.ai" /></div>
          <div><Label className="text-xs">Role</Label><Input defaultValue="Project Manager" /></div>
          <div><Label className="text-xs">Company</Label><Input defaultValue="EPCMind EPC Services" /></div>
          <div className="md:col-span-2"><Button onClick={() => toast.success("Settings saved")}>Save Changes</Button></div>
        </CardContent>
      </Card>

      <Card className="border-border bg-elevated">
        <CardHeader><CardTitle className="text-sm">Appearance</CardTitle></CardHeader>
        <CardContent>
          <RadioGroup value={theme} onValueChange={(v) => setTheme(v as typeof theme)} className="grid grid-cols-3 gap-3">
            {(["dark", "light", "system"] as const).map((t) => (
              <label key={t} className="flex cursor-pointer items-center gap-2 rounded-md border border-border bg-surface p-3">
                <RadioGroupItem value={t} />
                <span className="text-sm capitalize">{t}</span>
              </label>
            ))}
          </RadioGroup>
        </CardContent>
      </Card>

      <Card className="border-border bg-elevated">
        <CardHeader><CardTitle className="text-sm">Notifications</CardTitle></CardHeader>
        <CardContent className="space-y-3">
          {["Critical Risk Alerts", "Compliance Deviations", "RFI Matches", "Schedule Alerts", "Document Processing", "Email Notifications"].map((n) => (
            <div key={n} className="flex items-center justify-between rounded-md border border-border bg-surface px-3 py-2.5">
              <span className="text-sm">{n}</span>
              <Switch defaultChecked />
            </div>
          ))}
        </CardContent>
      </Card>

      <Card className="border-border bg-elevated">
        <CardHeader><CardTitle className="text-sm">AI Preferences</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-xs">Response Detail</Label>
            <RadioGroup defaultValue="balanced" className="mt-2 grid grid-cols-3 gap-3">
              {[["concise", "Concise"], ["balanced", "Balanced"], ["detailed", "Detailed"]].map(([v, l]) => (
                <label key={v} className="flex cursor-pointer items-center gap-2 rounded-md border border-border bg-surface p-3">
                  <RadioGroupItem value={v} /><span className="text-sm">{l}</span>
                </label>
              ))}
            </RadioGroup>
          </div>
          <div className="flex items-center justify-between rounded-md border border-border bg-surface px-3 py-2.5">
            <span className="text-sm">Always Show Sources</span><Switch defaultChecked />
          </div>
          <div className="flex items-center justify-between rounded-md border border-border bg-surface px-3 py-2.5">
            <span className="text-sm">Show Confidence Scores</span><Switch defaultChecked />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
