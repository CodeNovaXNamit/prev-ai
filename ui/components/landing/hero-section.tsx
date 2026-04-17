import { LinkButton } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ShieldIcon, SparkIcon } from "@/components/ui/icons";

const heroMetrics = [
  { label: "Privacy score", value: "99.9%", tone: "from-[var(--info)] to-cyan-300" },
  { label: "Cloud dependency", value: "0%", tone: "from-[var(--accent)] to-amber-300" },
  { label: "On-device actions", value: "24/7", tone: "from-fuchsia-400 to-[var(--info)]" },
];

export function HeroSection() {
  return (
    <section className="section-shell relative pt-16 sm:pt-20">
      <div className="grid items-center gap-10 lg:grid-cols-[1.08fr_0.92fr]">
        <div>
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs uppercase tracking-[0.28em] text-[var(--info)]">
            <ShieldIcon className="h-4 w-4" />
            AI That Belongs To You, AI That Never Leaves Your Device.
          </div>
          <h1
            className="max-w-4xl text-5xl font-bold tracking-tight sm:text-6xl xl:text-7xl"
            style={{ fontFamily: "var(--font-heading)" }}
          >
            PrivAI
            <span className="gradient-text"> Your Data. Your AI. Your Control.</span>
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 muted">
            A high-end local-first AI assistant prototype with futuristic design,
            responsive workflows, and privacy guarantees built right into the
            interface.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <LinkButton href="#dashboard">Get Started</LinkButton>
            <LinkButton href="#dashboard" variant="secondary">
              Try Demo
            </LinkButton>
          </div>
          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            {heroMetrics.map((metric) => (
              <Card key={metric.label} className="p-4">
                <div className={`mb-3 h-1.5 rounded-full bg-gradient-to-r ${metric.tone}`} />
                <div className="text-2xl font-semibold">{metric.value}</div>
                <div className="mt-1 text-sm muted">{metric.label}</div>
              </Card>
            ))}
          </div>
        </div>

        <Card className="relative overflow-hidden p-6 shadow-warm">
          <div className="absolute inset-0 grid-overlay opacity-20" />
          <div className="relative flex items-center justify-between">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full bg-[var(--accent-soft)] px-3 py-1 text-xs text-[var(--accent)]">
                <SparkIcon className="h-4 w-4" />
                Local cognitive core
              </div>
              <h2
                className="mt-4 text-3xl font-semibold"
                style={{ fontFamily: "var(--font-heading)" }}
              >
                Premium offline intelligence
              </h2>
            </div>
            <div className="h-14 w-14 rounded-2xl bg-gradient-to-br from-[var(--info)]/30 to-[var(--accent)]/30 p-3 text-[var(--info)]">
              <ShieldIcon className="h-full w-full" />
            </div>
          </div>

          <div className="relative mt-8 rounded-[28px] border border-white/10 bg-black/20 p-5">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm muted">Neural workspace</div>
                <div className="mt-1 text-xl font-semibold">
                  Device-secure assistant runtime
                </div>
              </div>
              <div className="h-3 w-3 animate-pulse rounded-full bg-emerald-400" />
            </div>

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                <div className="text-sm muted">Inference lane</div>
                <div className="mt-4 flex h-32 items-end gap-2">
                  {[35, 64, 48, 74, 58, 88, 72].map((height, index) => (
                    <div
                      key={index}
                      className="flex-1 rounded-t-full bg-gradient-to-t from-[var(--accent)] to-[var(--info)]"
                      style={{ height: `${height}%` }}
                    />
                  ))}
                </div>
              </div>

              <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                <div className="text-sm muted">Protected context graph</div>
                <div className="mt-4 space-y-3">
                  {["Chat memory", "Private notes", "Tasks and summaries"].map(
                    (item) => (
                      <div
                        key={item}
                        className="flex items-center justify-between rounded-2xl bg-black/20 px-4 py-3"
                      >
                        <span>{item}</span>
                        <span className="text-sm text-emerald-400">Local only</span>
                      </div>
                    ),
                  )}
                </div>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </section>
  );
}
