"use client";

import { useMemo } from "react";
import { SmokeScene } from "react-smoke";
import * as THREE from "three";

export default function SmokeSceneComponent() {
  const smokeColor = useMemo(() => new THREE.Color("lightblue"), []);

  return (
    <div
      className="fixed inset-0"
      style={{
        zIndex: 0,
      }}
    >
      <SmokeScene
        smoke={{
          color: smokeColor,
          opacity: 0.1,
          density: 15,
          enableRotation: true,
          enableWind: true,
          enableTurbulence: true,
        }}
      />
    </div>
  );
}
