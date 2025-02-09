import { GlowingEffectDemo } from "@/components/about";
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
    <div className="relative bg-[#F8F2E6] min-h-screen overflow-hidden">
      {/* Animated background gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(at_top_left,_#fde68a_0%,_transparent_60%)] opacity-30" />

      <FloatingNav className="backdrop-blur-lg bg-white/50" navItems={navItems} />

      <main className="relative flex items-center justify-center pt-32 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-4xl space-y-8">
          {/* Animated heading */}
          <h1 className="text-5xl sm:text-6xl md:text-7xl font-bold text-gray-900 mb-4 animate-fade-in-up">
            <span className="bg-gradient-to-r from-amber-600 to-amber-400 bg-clip-text text-transparent">
              Welcome to AuditIQ
            </span>
          </h1>

          {/* Enhanced paragraph styling */}
          <p
            className="text-lg sm:text-xl text-amber-900/80 leading-relaxed max-w-3xl mx-auto 
                        transition-all duration-300 hover:tracking-wide"
          >
            The solution is an AI-powered expense report generator that leverages VLM and LLMs to automate receipt data
            extraction, report creation, and fraud detection, insights, and recommendations.
          </p>

          {/* Enhanced button container */}
          <div className="flex justify-center pt-8">
            <Link href="/upload">
              <HoverBorderGradient
                containerClassName="rounded-full transition-transform duration-300 hover:scale-105"
                as="button"
                className="bg-gradient-to-r from-amber-500 to-amber-600 text-white text-xl 
                          font-semibold px-8 py-3 flex items-center space-x-2 shadow-lg 
                          hover:shadow-amber-200/40"
              >
                <span>Get Started</span>
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-5 w-5 ml-2"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z"
                    clipRule="evenodd"
                  />
                </svg>
              </HoverBorderGradient>
            </Link>
          </div>
        </div>
      </main>

      {/* About section with responsive spacing */}
      <div id="about" className="py-24 px-4 sm:px-6 lg:px-8 bg-white/30 backdrop-blur-lg">
        <GlowingEffectDemo />
      </div>
    </div>
  );
}
