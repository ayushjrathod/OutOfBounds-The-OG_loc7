import { GlowingEffectDemo } from "@/components/about";
import Cube from "@/components/Cube";
import SmokeSceneComponent from "@/components/SmokeSceneComponent";
import { FloatingNav } from "@/components/ui/floating-navbar";
import { HoverBorderGradient } from "@/components/ui/hover-border-gradient";
import { HomeIcon } from "lucide-react";
import Link from "next/link";

export default function Home() {
  const navItems = [
    { name: "Home", link: "/", icon: <HomeIcon /> },
    { name: "About", link: "#about" },
    { name: "Upload", link: "/upload" },
    { name: "ChatBot", link: "/chat" },
  ];
  return (
    <div className="relative bg-black z-50">
      <FloatingNav className="" navItems={navItems} />
      <SmokeSceneComponent />
      <main className="relative flex items-center bg-transparent mt-16">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 flex flex-col lg:flex-row items-center justify-between">
          <div className="text-left lg:w-1/2 mb-8 lg:mb-0">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white mb-4">Welcome to OutOfBounds</h1>
            <p className="text-xl sm:text-2xl md:text-xl text-gray-400 mb-8 mx-2 text-justify">
              This is the hero section of team OutOfBounds. Current project is being developed for lines of code v7.0
              hackathon. lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut
              labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut
            </p>
            <div className="flex flex-col">
              <Link href="/upload">
                <HoverBorderGradient
                  containerClassName="rounded-full"
                  as="button"
                  className="bg-gray-100 text-black text-xl tracking-wide font-bold px-4 py-2 flex items-center space-x-2"
                >
                  <span>Get Started</span>
                </HoverBorderGradient>
              </Link>
            </div>
          </div>
          {/* <SplineComponent /> */}
          <Cube />
        </div>
      </main>
      <div id="about" className="m-24">
        <GlowingEffectDemo />
      </div>
    </div>
  );
}
