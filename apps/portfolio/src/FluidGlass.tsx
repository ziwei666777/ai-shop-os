/* eslint-disable react/no-unknown-property */
import * as THREE from "three";
import { memo, useEffect, useRef, useState } from "react";
import type { ReactNode } from "react";
import { Canvas, createPortal, useFrame, useThree } from "@react-three/fiber";
import { Image as DreiImage, MeshTransmissionMaterial, Preload, Text, useFBO, useGLTF } from "@react-three/drei";
import { easing } from "maath";
import "./FluidGlass.css";

type FluidGlassProps = {
  className?: string;
  variant?: "card" | "nav" | "soft";
};

type ReactBitsMode = "lens" | "bar" | "cube";

type ReactBitsGlassMaterialProps = {
  scale?: number;
  ior?: number;
  thickness?: number;
  chromaticAberration?: number;
  anisotropy?: number;
  roughness?: number;
  transmission?: number;
  color?: string;
  attenuationColor?: string;
  attenuationDistance?: number;
};

type ReactBitsFluidGlassProps = {
  className?: string;
  mode?: ReactBitsMode;
  lensProps?: ReactBitsGlassMaterialProps;
  barProps?: ReactBitsGlassMaterialProps;
  cubeProps?: ReactBitsGlassMaterialProps;
};

export function FluidGlass({ className = "", variant = "card" }: FluidGlassProps) {
  return (
    <span className={`fluidGlass fluidGlass--${variant} ${className}`} aria-hidden="true">
      <span className="fluidGlass__caustic" />
      <span className="fluidGlass__sheen" />
    </span>
  );
}

export function ReactBitsFluidGlass({
  className = "",
  mode = "lens",
  lensProps = {},
  barProps = {},
  cubeProps = {}
}: ReactBitsFluidGlassProps) {
  const Wrapper = mode === "bar" ? Bar : mode === "cube" ? Cube : Lens;
  const modeProps = mode === "bar" ? barProps : mode === "cube" ? cubeProps : lensProps;

  return (
    <div className={`reactBitsFluidGlass reactBitsFluidGlass--${mode} ${className}`} aria-hidden="true">
      <Canvas camera={{ position: [0, 0, 20], fov: 15 }} dpr={[1, 1.75]} gl={{ alpha: true, antialias: true }}>
        <Wrapper modeProps={modeProps}>
          <PortfolioGlassScene />
          <Preload />
        </Wrapper>
      </Canvas>
    </div>
  );
}

const ModeWrapper = memo(function ModeWrapper({
  children,
  mode,
  modeProps = {},
  glb,
  geometryKey,
  lockToBottom = false
}: {
  children: ReactNode;
  mode: ReactBitsMode;
  modeProps?: ReactBitsGlassMaterialProps;
  glb: string;
  geometryKey: string;
  lockToBottom?: boolean;
}) {
  const ref = useRef<THREE.Mesh>(null);
  const { nodes } = useGLTF(glb) as unknown as { nodes: Record<string, THREE.Mesh> };
  const geometry = nodes[geometryKey]?.geometry;
  const buffer = useFBO({ samples: 8 });
  const { viewport: vp } = useThree();
  const [scene] = useState(() => new THREE.Scene());
  const pointerRef = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const handlePointerMove = (event: PointerEvent) => {
      pointerRef.current = {
        x: (event.clientX / window.innerWidth) * 2 - 1,
        y: -(event.clientY / window.innerHeight) * 2 + 1
      };
    };

    window.addEventListener("pointermove", handlePointerMove, { passive: true });
    return () => window.removeEventListener("pointermove", handlePointerMove);
  }, []);

  useFrame((state, delta) => {
    if (!ref.current) return;

    const { gl, viewport, camera } = state;
    const pointer = pointerRef.current;
    const v = viewport.getCurrentViewport(camera, [0, 0, 15]);
    const destX = mode === "bar" ? 0 : (pointer.x * v.width) / 2;
    const destY = lockToBottom ? -v.height / 2 + 0.24 : (pointer.y * v.height) / 2;

    easing.damp3(ref.current.position, [destX, destY, 15], 0.15, delta);
    easing.dampE(ref.current.rotation, [Math.PI / 2 + pointer.y * 0.08, pointer.x * 0.1, pointer.x * 0.08], 0.18, delta);

    gl.setRenderTarget(buffer);
    gl.setClearColor(0x030614, 0);
    gl.clear(true, true, true);
    gl.render(scene, camera);
    gl.setRenderTarget(null);
  });

  const { scale, ior, thickness, anisotropy, chromaticAberration, ...extraMat } = modeProps;
  const resolvedScale = scale ?? (mode === "bar" ? 0.32 : mode === "cube" ? 0.42 : 0.34);

  return (
    <>
      {createPortal(children, scene)}
      <mesh scale={[vp.width, vp.height, 1]} position={[0, 0, 0]}>
        <planeGeometry />
        <meshBasicMaterial map={buffer.texture} transparent opacity={0.12} />
      </mesh>
      <mesh ref={ref} geometry={geometry} scale={resolvedScale}>
        <MeshTransmissionMaterial
          buffer={buffer.texture}
          ior={ior ?? 1.15}
          thickness={thickness ?? 5}
          anisotropy={anisotropy ?? 0.01}
          chromaticAberration={chromaticAberration ?? 0.1}
          roughness={0}
          transmission={1}
          color="#ffffff"
          attenuationColor="#ffffff"
          attenuationDistance={0.32}
          {...extraMat}
        />
      </mesh>
    </>
  );
});

function Lens({ modeProps, children }: { modeProps: ReactBitsGlassMaterialProps; children: ReactNode }) {
  return (
    <ModeWrapper glb="/assets/3d/lens.glb" geometryKey="Cylinder" mode="lens" modeProps={modeProps}>
      {children}
    </ModeWrapper>
  );
}

function Cube({ modeProps, children }: { modeProps: ReactBitsGlassMaterialProps; children: ReactNode }) {
  return (
    <ModeWrapper glb="/assets/3d/cube.glb" geometryKey="Cube" mode="cube" modeProps={modeProps}>
      {children}
    </ModeWrapper>
  );
}

function Bar({ modeProps, children }: { modeProps: ReactBitsGlassMaterialProps; children: ReactNode }) {
  return (
    <ModeWrapper glb="/assets/3d/bar.glb" geometryKey="Cube" lockToBottom mode="bar" modeProps={modeProps}>
      {children}
    </ModeWrapper>
  );
}

function PortfolioGlassScene() {
  const group = useRef<THREE.Group>(null);
  const { viewport, camera } = useThree();

  useFrame(() => {
    if (!group.current) return;
    const v = viewport.getCurrentViewport(camera, [0, 0, 15]);
    const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
    const scrollProgress = window.scrollY / maxScroll;
    group.current.position.y = scrollProgress * v.height * 2.4;
  });

  return (
    <group ref={group} position={[0, 0, 12]}>
      <TextBlock text="MIN" position={[-1.42, 0.82, 0]} size={0.92} />
      <TextBlock text="PROJECTS" position={[0.55, 0.12, 0]} size={0.52} />
      <TextBlock text="AI CREATOR" position={[-1.12, -0.72, 0]} size={0.2} />
      <TextBlock text="PRODUCT / WEB / AGENT" position={[1.12, -1.1, 0]} size={0.16} />
      <TextBlock text="ABOUT  TEAM  SERVICES  PROJECT" position={[0, -2.18, 0]} size={0.14} />
      <TextBlock text="AI COMMERCE OS" position={[-1.55, -3.15, 0]} size={0.24} />
      <TextBlock text="EMOTION APP" position={[1.24, -3.7, 0]} size={0.22} />
      <TextBlock text="CONTACT  WUHAN  MVP" position={[0, -4.52, 0]} size={0.16} />
      <DreiImage position={[-2.08, -1.44, -0.2]} scale={[0.72, 0.48]} url="/emotion-mark-transparent.png" />
      <DreiImage position={[2.06, -2.62, -0.2]} scale={[0.92, 0.56]} url="/ai-commerce-console.png" />
    </group>
  );
}

function TextBlock({ text, position, size }: { text: string; position: [number, number, number]; size: number }) {
  return (
    <Text
      position={position}
      fontSize={size}
      letterSpacing={0}
      color="#f3f7ff"
      anchorX="center"
      anchorY="middle"
      outlineWidth={0}
      outlineBlur="18%"
      outlineColor="#02040f"
      outlineOpacity={0.45}
    >
      {text}
    </Text>
  );
}