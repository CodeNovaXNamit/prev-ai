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
    let frame = 0;
    let active = true;
    let targetX = 0;
    let targetY = 0;
    let currentX = 0;
    let currentY = 0;

    const render = () => {
      currentX += (targetX - currentX) * 0.14;
      currentY += (targetY - currentY) * 0.14;

      stage.style.setProperty("--stage-rotate-x", `${(-currentY * 4).toFixed(2)}deg`);
      stage.style.setProperty("--stage-rotate-y", `${(currentX * 5).toFixed(2)}deg`);

      nodes.forEach((node) => {
        const depth = Number(node.dataset.depth ?? 0);
        node.style.setProperty("--parallax-x", `${(currentX * depth * 24).toFixed(2)}px`);
        node.style.setProperty("--parallax-y", `${(currentY * depth * 18).toFixed(2)}px`);
        node.style.setProperty("--parallax-z", `${(depth * 18).toFixed(2)}px`);
      });

      if (
        active ||
        Math.abs(targetX - currentX) > 0.001 ||
        Math.abs(targetY - currentY) > 0.001
      ) {
        frame = window.requestAnimationFrame(render);
      } else {
        frame = 0;
      }
    };

    const ensureFrame = () => {
      if (!frame) {
        frame = window.requestAnimationFrame(render);
      }
    };

    const handleMove = (event: PointerEvent) => {
      const rect = stage.getBoundingClientRect();
      targetX = (event.clientX - rect.left) / rect.width - 0.5;
      targetY = (event.clientY - rect.top) / rect.height - 0.5;
      active = true;
      ensureFrame();
    };

    const handleLeave = () => {
      targetX = 0;
      targetY = 0;
      active = false;
      ensureFrame();
    };

    stage.addEventListener("pointermove", handleMove);
    stage.addEventListener("pointerleave", handleLeave);
    ensureFrame();

    return () => {
      stage.removeEventListener("pointermove", handleMove);
      stage.removeEventListener("pointerleave", handleLeave);
      if (frame) {
        window.cancelAnimationFrame(frame);
      }
    };
  }, []);

  return (
    <div ref={stageRef} className="hero-visual reveal stagger-1">
      <div className="hero-aurora" aria-hidden="true" />
      {children}
    </div>
  );
}
