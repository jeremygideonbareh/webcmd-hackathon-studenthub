import * as React from "react";
import { Check, Copy, ExternalLink, Percent } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { fetchDiscounts } from "@/lib/api";
import type { StudentDiscount } from "@/lib/types";

export function DiscountsTab({
  initialDiscounts = [],
}: {
  initialDiscounts?: StudentDiscount[];
}) {
  const [discounts, setDiscounts] = React.useState<StudentDiscount[]>(initialDiscounts);
  const [copiedId, setCopiedId] = React.useState<string | null>(null);

  React.useEffect(() => {
    fetchDiscounts()
      .then((data) => {
        if (data && data.length > 0) setDiscounts(data);
        else if (initialDiscounts.length > 0) setDiscounts(initialDiscounts);
      })
      .catch((err) => {
        console.error("Error loading discounts:", err);
        if (initialDiscounts.length > 0) setDiscounts(initialDiscounts);
      });
  }, [initialDiscounts]);

  const handleCopyCode = (id: string, code?: string) => {
    if (!code) return;
    void navigator.clipboard.writeText(code);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <Card id="discounts" className="shadow-sm border">
      <CardHeader className="pb-3">
        <CardTitle className="text-xl sm:text-2xl flex items-center gap-2">
          <Percent className="h-5 w-5 text-primary" aria-hidden="true" />
          Student Deals & Discounts
        </CardTitle>
        <CardDescription className="text-sm mt-1">
          Exclusive student pricing, free software licenses, and hardware perks verified with your student identity.
        </CardDescription>
      </CardHeader>

      <CardContent className="pt-2 space-y-4">
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {discounts.map((d) => (
            <article key={d.id} className="flex flex-col justify-between rounded-xl border p-4 sm:p-5 bg-card hover:shadow-sm transition-shadow">
              <div>
                <div className="flex items-start justify-between gap-2">
                  <Badge variant="outline" className="text-[10px] uppercase tracking-wider font-semibold">
                    {d.category}
                  </Badge>
                  <span className="shrink-0 rounded-full border border-green-200 bg-green-50 dark:bg-green-950/40 px-2.5 py-0.5 text-xs font-bold text-green-700 dark:text-green-300">
                    {d.discount}
                  </span>
                </div>
                <h4 className="mt-2.5 font-semibold text-base leading-snug text-foreground">{d.title}</h4>
                <p className="mt-1 text-xs font-medium text-muted-foreground">{d.provider}</p>
                <p className="mt-2 text-xs text-muted-foreground leading-relaxed">{d.description}</p>
              </div>

              <div className="mt-4 border-t pt-3 flex items-center justify-between gap-2">
                {d.code ? (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopyCode(d.id, d.code)}
                    className="h-8 gap-1.5 text-xs font-mono"
                    aria-label={`Copy code for ${d.title}`}
                  >
                    {copiedId === d.id ? (
                      <>
                        <Check className="h-3.5 w-3.5 text-green-600" aria-hidden="true" /> Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="h-3.5 w-3.5" aria-hidden="true" /> {d.code}
                      </>
                    )}
                  </Button>
                ) : (
                  <span className="text-[10px] text-muted-foreground">EDU Verification Required</span>
                )}

                {d.url && (
                  <a
                    href={d.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex min-h-[44px] items-center gap-1 text-xs font-semibold text-primary hover:underline"
                  >
                    Claim Perk <ExternalLink className="h-3 w-3" aria-hidden="true" />
                  </a>
                )}
              </div>
            </article>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
