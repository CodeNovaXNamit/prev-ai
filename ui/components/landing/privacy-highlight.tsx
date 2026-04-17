import { Card } from "@/components/ui/card";
import { ShieldIcon } from "@/components/ui/icons";

const assurances = [
  "Runs 100% on your device",
  "No cloud usage",
  "No external APIs in demo mode",
];

export function PrivacyHighlight() {
  return (
    <section id="privacy" className="section-shell pt-24">
      <Card className="relative overflow-hidden p-8 sm:p-10">
        <div className="absolute inset-0 bg-gradient-to-r from-[var(--info)]/10 via-transparent to-[var(--accent)]/10" />
        <div className="relative grid gap-8 lg:grid-cols-[0.95fr_1.05fr]">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full bg-[var(--accent-soft)] px-4 py-2 text-sm text-[var(--accent)]">
              <ShieldIcon className="h-4 w-4" />
              Privacy highlight
            </div>
            <h2
              className="mt-5 text-3xl font-semibold sm:text-4xl"
              style={{ fontFamily: "var(--font-heading)" }}
            >
              Built to prove that powerful AI can stay personal
            </h2>
            <p className="mt-4 text-lg leading-8 muted">
              PrivAI's interface tells a clear story: the assistant is useful,
              fast, and visually rich, but the user still owns the device, the
              data, and the decisions.
            </p>
          </div>

          <div className="grid gap-4 sm:grid-cols-3">
            {assurances.map((item, index) => (
              <div
                key={item}
                className="rounded-[24px] border border-white/10 bg-white/5 p-5"
              >
                <div className="text-sm uppercase tracking-[0.24em] text-[var(--info)]">
                  0{index + 1}
                </div>
                <div className="mt-5 text-xl font-semibold">{item}</div>
                <div className="mt-3 h-1 w-full rounded-full bg-white/10">
                  <div
                    className="h-1 rounded-full bg-gradient-to-r from-[var(--info)] to-[var(--accent)]"
                    style={{ width: `${82 + index * 6}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </section>
  );
}
