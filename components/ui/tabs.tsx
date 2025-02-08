"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { useState } from "react";

type Tab = {
  title: string;
  value: string;
  content?: string | React.ReactNode | any;
};

export const Tabs = ({
  tabs: propTabs,
  containerClassName,
  activeTabClassName,
  tabClassName,
  contentClassName,
}: {
  tabs: Tab[];
  containerClassName?: string;
  activeTabClassName?: string;
  tabClassName?: string;
  contentClassName?: string;
}) => {
  const [active, setActive] = useState<Tab>(propTabs[0]);

  return (
    <>
      <div
        className={cn(
          "flex flex-row items-center justify-start relative overflow-auto sm:overflow-visible no-visible-scrollbar max-w-full w-full",
          containerClassName
        )}
      >
        {propTabs.map((tab) => (
          <button
            key={tab.title}
            onClick={() => setActive(tab)}
            className={cn("relative px-4 py-2 rounded-full", tabClassName)}
          >
            {active.value === tab.value && (
              <motion.div
                layoutId="activeTab"
                className={cn("absolute inset-0 bg-zinc-700 rounded-full", activeTabClassName)}
                transition={{ type: "spring", bounce: 0.3, duration: 0.6 }}
              />
            )}
            <span className="relative block text-white">{tab.title}</span>
          </button>
        ))}
      </div>
      <div className={cn("mt-8 relative w-full", contentClassName)}>
        {propTabs.map((tab) => (
          <div key={tab.value} className={cn("w-full", { hidden: tab.value !== active.value })}>
            {tab.content}
          </div>
        ))}
      </div>
    </>
  );
};
