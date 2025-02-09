// FloatingNav.tsx
"use client";
import { cn } from "@/lib/utils";
import { AnimatePresence, motion } from "framer-motion";
import { signOut, useSession } from "next-auth/react";
import Link from "next/link";

export const FloatingNav = ({
  navItems,
  className,
}: {
  navItems: {
    name: string;
    link: string;
    icon?: JSX.Element;
  }[];
  className?: string;
}) => {
  const { data: session } = useSession();
  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{ opacity: 1, y: -100 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.2 }}
        className={cn(
          "flex max-w-fit fixed top-6 inset-x-0 mx-auto border border-amber-200/50 bg-white/50 backdrop-blur-lg",
          "shadow-[0px_2px_3px_-1px_rgba(245,158,11,0.1),0px_1px_0px_0px_rgba(245,158,11,0.02)]",
          "z-[5000] px-6 py-2.5 items-center justify-center space-x-6 rounded-full",
          className
        )}
      >
        {navItems.map((navItem, idx) => (
          <Link
            key={`link=${idx}`}
            href={navItem.link}
            className={cn(
              "relative text-amber-900/90 items-center flex space-x-1",
              "hover:text-amber-600 transition-colors duration-200"
            )}
          >
            <span className="block sm:hidden">{navItem.icon}</span>
            <span className="hidden sm:block text-sm font-medium">{navItem.name}</span>
          </Link>
        ))}
        {session ? (
          <button
            onClick={() => signOut()}
            className="border border-amber-200 text-amber-800 px-4 py-1.5 rounded-full 
                      hover:bg-amber-50 transition-colors duration-200 relative"
          >
            <span>Logout</span>
            <span className="absolute inset-x-0 w-1/2 mx-auto -bottom-px bg-gradient-to-r from-transparent via-amber-500 to-transparent h-px" />
          </button>
        ) : (
          <button
            onClick={() => (window.location.href = "/sign-in")}
            className="border border-amber-200 text-amber-800 px-4 py-1.5 rounded-full 
                      hover:bg-amber-50 transition-colors duration-200 relative"
          >
            <span>Login</span>
            <span className="absolute inset-x-0 w-1/2 mx-auto -bottom-px bg-gradient-to-r from-transparent via-amber-500 to-transparent h-px" />
          </button>
        )}
      </motion.div>
    </AnimatePresence>
  );
};
