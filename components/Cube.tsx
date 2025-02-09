"use client";

import Script from "next/script";

export default function Cube() {
  return (
    <div
      style={{
        backgroundColor: "black",
        backgroundImage: "url(https://resend.com/_next/image?url=%2Fstatic%2Flanding-page%2Fbghero.png&w=1080&q=75)",
        backgroundRepeat: "no-repeat",
        backgroundSize: "cover",
        backgroundPosition: "center",
        width: "100%",
        height: "100%",
      }}
      className="h-screen w-1/2"
    >
      <Script type="module" src="https://unpkg.com/@splinetool/viewer@1.9.56/build/spline-viewer.js" />
      <spline-viewer url="https://prod.spline.design/DlnNMurvV4Ugn-k6/scene.splinecode"></spline-viewer>
    </div>
  );
}
