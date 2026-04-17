import { Card } from "@/components/ui/card";
import { NotesIcon, ShieldIcon, SummaryIcon, TaskIcon } from "@/components/ui/icons";

const features = [
  {
    title: "Local Processing",
    description: "Keep prompts, context, and assistant actions running on-device with no cloud dependency.",
    icon: ShieldIcon,
  },
  {
    title: "Secure Notes",
    description: "Capture thoughts in sleek note cards backed by browser storage for a local-first demo flow.",
    icon: NotesIcon,
  },
  {
    title: "Smart Tasks",
    description: "Track priorities, completion rates, and daily momentum with productivity-focused interactions.",
    icon: TaskIcon,
  },
  {
    title: "AI Summarization",
    description: "Simulate concise summaries with a premium prompt-to-output panel designed for speed and clarity.",
    icon: SummaryIcon,
  },
];

export function FeaturesSection() {
  return (
    <section id="features" className="section-shell pt-24">
      <div className="mb-10 max-w-2xl">
        <div className="mb-3 text-sm uppercase tracking-[0.28em] text-[var(--accent)]">
          Core capabilities
        </div>
        <h2 className="section-title" style={{ fontFamily: "var(--font-heading)" }}>
          Privacy-first features with product-grade polish
        </h2>
        <p className="mt-4 text-lg muted">
          Every section is built to feel like a real premium AI product while
          reinforcing user control, transparency, and responsive interaction.
        </p>
      </div>

      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {features.map((feature) => {
          const Icon = feature.icon;

          return (
            <Card
              key={feature.title}
              className="group overflow-hidden p-6 transition duration-300 hover:-translate-y-1 hover:border-white/20"
            >
              <div className="mb-5 inline-flex rounded-2xl border border-white/10 bg-white/5 p-3 text-[var(--info)] transition group-hover:scale-105">
                <Icon className="h-6 w-6" />
              </div>
              <h3 className="text-xl font-semibold">{feature.title}</h3>
              <p className="mt-3 leading-7 muted">{feature.description}</p>
            </Card>
          );
        })}
      </div>
    </section>
  );
}
