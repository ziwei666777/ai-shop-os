import { type CSSProperties, type ReactNode, useCallback, useEffect, useRef } from "react";
import "./BorderGlow.css";

const GRADIENT_POSITIONS = ["80% 55%", "69% 34%", "8% 6%", "41% 38%", "86% 85%", "82% 18%", "51% 4%"];
const GRADIENT_KEYS = [
  "--gradient-one",
  "--gradient-two",
  "--gradient-three",
  "--gradient-four",
  "--gradient-five",
  "--gradient-six",
  "--gradient-seven"
];
const COLOR_MAP = [0, 1, 2, 0, 1, 2, 1];

interface BorderGlowProps {
  animated?: boolean;
  backgroundColor?: string;
  borderRadius?: number;
  children: ReactNode;
  className?: string;
  colors?: string[];
  coneSpread?: number;
  edgeSensitivity?: number;
  fillOpacity?: number;
  glowColor?: string;
  glowIntensity?: number;
  glowRadius?: number;
}

type GlowStyle = CSSProperties & Record<string, string | number>;

function parseHSL(hslStr: string) {
  const match = hslStr.match(/([\d.]+)\s*([\d.]+)%?\s*([\d.]+)%?/);
  if (!match) return { h: 225, s: 80, l: 68 };
  return { h: Number.parseFloat(match[1]), s: Number.parseFloat(match[2]), l: Number.parseFloat(match[3]) };
}

function buildGlowVars(glowColor: string, intensity: number) {
  const { h, s, l } = parseHSL(glowColor);
  const base = `${h}deg ${s}% ${l}%`;
  const opacities = [100, 60, 50, 40, 30, 20, 10];
  const keys = ["", "-60", "-50", "-40", "-30", "-20", "-10"];
  const vars: Record<string, string> = {};

  opacities.forEach((opacity, index) => {
    vars[`--glow-color${keys[index]}`] = `hsl(${base} / ${Math.min(opacity * intensity, 100)}%)`;
  });

  return vars;
}

function buildGradientVars(colors: string[]) {
  const vars: Record<string, string> = {};

  for (let index = 0; index < 7; index += 1) {
    const color = colors[Math.min(COLOR_MAP[index], colors.length - 1)];
    vars[GRADIENT_KEYS[index]] = `radial-gradient(at ${GRADIENT_POSITIONS[index]}, ${color} 0px, transparent 50%)`;
  }

  vars["--gradient-base"] = `linear-gradient(${colors[0]} 0 100%)`;
  return vars;
}

function easeOutCubic(x: number) {
  return 1 - (1 - x) ** 3;
}

function easeInCubic(x: number) {
  return x * x * x;
}

function animateValue({
  delay = 0,
  duration = 1000,
  ease = easeOutCubic,
  end = 100,
  onEnd,
  onUpdate,
  start = 0
}: {
  delay?: number;
  duration?: number;
  ease?: (value: number) => number;
  end?: number;
  onEnd?: () => void;
  onUpdate: (value: number) => void;
  start?: number;
}) {
  const t0 = performance.now() + delay;

  const tick = () => {
    const elapsed = performance.now() - t0;
    const t = Math.min(elapsed / duration, 1);
    onUpdate(start + (end - start) * ease(t));
    if (t < 1) requestAnimationFrame(tick);
    else onEnd?.();
  };

  window.setTimeout(() => requestAnimationFrame(tick), delay);
}

export function BorderGlow({
  animated = false,
  backgroundColor = "#071026",
  borderRadius = 8,
  children,
  className = "",
  colors = ["#2037d6", "#5f7cff", "#f3f7ff"],
  coneSpread = 24,
  edgeSensitivity = 28,
  fillOpacity = 0.32,
  glowColor = "225 85 66",
  glowIntensity = 1,
  glowRadius = 34
}: BorderGlowProps) {
  const cardRef = useRef<HTMLDivElement>(null);

  const getCenterOfElement = useCallback((el: HTMLElement) => {
    const { width, height } = el.getBoundingClientRect();
    return [width / 2, height / 2];
  }, []);

  const getEdgeProximity = useCallback(
    (el: HTMLElement, x: number, y: number) => {
      const [cx, cy] = getCenterOfElement(el);
      const dx = x - cx;
      const dy = y - cy;
      let kx = Infinity;
      let ky = Infinity;
      if (dx !== 0) kx = cx / Math.abs(dx);
      if (dy !== 0) ky = cy / Math.abs(dy);
      return Math.min(Math.max(1 / Math.min(kx, ky), 0), 1);
    },
    [getCenterOfElement]
  );

  const getCursorAngle = useCallback(
    (el: HTMLElement, x: number, y: number) => {
      const [cx, cy] = getCenterOfElement(el);
      const dx = x - cx;
      const dy = y - cy;
      if (dx === 0 && dy === 0) return 0;
      const radians = Math.atan2(dy, dx);
      const degrees = radians * (180 / Math.PI) + 90;
      return degrees < 0 ? degrees + 360 : degrees;
    },
    [getCenterOfElement]
  );

  const handlePointerMove = useCallback(
    (event: React.PointerEvent<HTMLDivElement>) => {
      const card = cardRef.current;
      if (!card) return;

      const rect = card.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;

      card.style.setProperty("--edge-proximity", `${(getEdgeProximity(card, x, y) * 100).toFixed(3)}`);
      card.style.setProperty("--cursor-angle", `${getCursorAngle(card, x, y).toFixed(3)}deg`);
    },
    [getCursorAngle, getEdgeProximity]
  );

  useEffect(() => {
    if (!animated || !cardRef.current) return undefined;
    const card = cardRef.current;
    const angleStart = 110;
    const angleEnd = 465;
    card.classList.add("sweep-active");
    card.style.setProperty("--cursor-angle", `${angleStart}deg`);

    animateValue({ duration: 500, onUpdate: (value) => card.style.setProperty("--edge-proximity", `${value}`) });
    animateValue({
      duration: 1500,
      ease: easeInCubic,
      end: 50,
      onUpdate: (value) => card.style.setProperty("--cursor-angle", `${(angleEnd - angleStart) * (value / 100) + angleStart}deg`)
    });
    animateValue({
      delay: 1500,
      duration: 2250,
      ease: easeOutCubic,
      end: 100,
      onUpdate: (value) => card.style.setProperty("--cursor-angle", `${(angleEnd - angleStart) * (value / 100) + angleStart}deg`),
      start: 50
    });
    animateValue({
      delay: 2500,
      duration: 1500,
      ease: easeInCubic,
      end: 0,
      onEnd: () => card.classList.remove("sweep-active"),
      onUpdate: (value) => card.style.setProperty("--edge-proximity", `${value}`),
      start: 100
    });

    return undefined;
  }, [animated]);

  const style: GlowStyle = {
    "--border-radius": `${borderRadius}px`,
    "--card-bg": backgroundColor,
    "--cone-spread": coneSpread,
    "--edge-sensitivity": edgeSensitivity,
    "--fill-opacity": fillOpacity,
    "--glow-padding": `${glowRadius}px`,
    ...buildGlowVars(glowColor, glowIntensity),
    ...buildGradientVars(colors)
  };

  return (
    <div className={`border-glow-card ${className}`} onPointerMove={handlePointerMove} ref={cardRef} style={style}>
      <span className="edge-light" />
      <div className="border-glow-inner">{children}</div>
    </div>
  );
}

export default BorderGlow;
