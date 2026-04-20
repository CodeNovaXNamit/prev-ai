"use client";

import { useEffect, useRef } from "react";

export function ParallaxStage({ children }: { children: React.ReactNode }) {
  const stageRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const stage = stageRef.current;
    if (!stage || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      return;
    }

    const nodes = Array.from(stage.querySelectorAll<HTMLElement>("[data-depth]"));

    const handleMove = (event: PointerEvent) => {
      const rect = stage.getBoundingClientRect();
      const x = (event.clientX - rect.left) / rect.width - 0.5;
      const y = (event.clientY - rect.top) / rect.height - 0.5;

      stage.style.transform = `rotateX(${(-y * 4).toFixed(2)}deg) rotateY(${(x * 5).toFixed(2)}deg)`;

      nodes.forEach((node) => {
        const depth = Number(node.dataset.depth ?? 0);
        const tx = x * depth * 24;
        const ty = y * depth * 18;
        const tz = depth * 18;
        node.style.transform = `translate3d(${tx}px, ${ty}px, ${tz}px)`;
      });
    };

    const handleLeave = () => {
      stage.style.transform = "";
      nodes.forEach((node) => {
        node.style.transform = "";
      });
    };

    stage.addEventListener("pointermove", handleMove);
    stage.addEventListener("pointerleave", handleLeave);

    return () => {
      stage.removeEventListener("pointermove", handleMove);
      stage.removeEventListener("pointerleave", handleLeave);
    };
  }, []);

  return (
    <div ref={stageRef} className="hero-visual reveal stagger-1">
      <div className="hero-aurora" aria-hidden="true" />
      {children}
    </div>
  );
}
