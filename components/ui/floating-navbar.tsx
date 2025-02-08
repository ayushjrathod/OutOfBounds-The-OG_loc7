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
    //@ts-expect-error : NextJs
    icon?: JSX.Element;
  }[];
  className?: string;
}) => {
  const { data: session } = useSession();
  return (
    <AnimatePresence mode="wait">
      <motion.div
        initial={{
          opacity: 1,
          y: -100,
        }}
        animate={{
          y: 0,
          opacity: 1,
        }}
        transition={{
          duration: 0.2,
        }}
        className={cn(
          "flex max-w-fit  fixed top-10 inset-x-0 mx-auto border border-transparent dark:border-white/[0.2] rounded-full dark:bg-white bg-black shadow-[0px_2px_3px_-1px_rgba(0,0,0,0.1),0px_1px_0px_0px_rgba(25,28,33,0.02),0px_0px_0px_1px_rgba(25,28,33,0.08)] z-[5000] pr-2 pl-8 py-2  items-center justify-center space-x-4",
          className
        )}
      >
        {/* @ts-expect-error : NextJs */}
        {navItems.map((navItem: { name: string; link: string; icon?: JSX.Element }, idx: number) => (
          <Link
            key={`link=${idx}`}
            href={navItem.link}
            className={cn(
              "relative dark:text-neutral-50 items-center flex space-x-1 text-white dark:hover:text-neutral-300 hover:text-neutral-500"
            )}
          >
            <span className="block sm:hidden">{navItem.icon}</span>
            <span className="hidden sm:block text-sm">{navItem.name}</span>
          </Link>
        ))}
        {session ? (
          <>
            <button
              onClick={() => signOut()}
              className="border text-sm font-medium relative border-neutral-200 dark:border-white/[0.2] text-white dark:text-white px-4 py-2 rounded-full"
            >
              <span>Logout</span>
              <span className="absolute inset-x-0 w-1/2 mx-auto -bottom-px bg-gradient-to-r from-transparent via-red-500 to-transparent  h-px" />
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => (window.location.href = "/sign-in")}
              className="border text-sm font-medium relative border-neutral-200 dark:border-white/[0.2] text-white dark:text-white px-4 py-2 rounded-full"
            >
              <span>Login</span>
              <span className="absolute inset-x-0 w-1/2 mx-auto -bottom-px bg-gradient-to-r from-transparent via-blue-500 to-transparent  h-px" />
            </button>
          </>
        )}
      </motion.div>
    </AnimatePresence>
  );
};
