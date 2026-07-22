import { Search } from "lucide-react";

export function EmptyState({ title, description, icon: Icon = Search }: { title: string; description?: string; icon?: React.ComponentType<{ className?: string }> }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface/40 px-6 py-16 text-center">
      <Icon className="mb-3 h-8 w-8 text-muted-foreground" />
      <h3 className="text-sm font-semibold text-foreground">{title}</h3>
      {description && <p className="mt-1 max-w-sm text-xs text-muted-foreground">{description}</p>}
    </div>
  );
}
