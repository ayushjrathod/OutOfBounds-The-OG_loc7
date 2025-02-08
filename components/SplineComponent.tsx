"use client";

import Spline from "@splinetool/react-spline/next";

export default function SplineComponent() {
  return (
    <div className="lg:w-1/2 h-[400px] lg:h-[800px] w-full">
      <Spline scene="https://prod.spline.design/T4icAyrJcvTFCCah/scene.splinecode" />
    </div>
  );
}
