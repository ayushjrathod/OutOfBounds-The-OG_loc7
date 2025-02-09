"use client";

import { motion } from "framer-motion";

const RetroLoader = (): JSX.Element => {
  return (
    <div className="flex items-center justify-center h-screen bg-black">
      <div className="relative w-36 h-36">
        <motion.div
          className="absolute inset-0 w-full h-full border-8 border-dashed border-[#ffcc00] rounded-full shadow-[0_0_20px_#ffcc00]"
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 1.2, ease: "linear" }}
        />
        <motion.div
          className="absolute inset-0 flex items-center justify-center text-[#ffcc00] font-mono text-lg tracking-widest drop-shadow-md"
          animate={{ scale: [1, 1.3, 1], opacity: [0.8, 1, 0.8] }}
          transition={{ repeat: Infinity, duration: 0.8, ease: "easeInOut" }}
        >
          <motion.span
            className="text-[20px]"
            animate={{ y: [0, -5, 0] }}
            transition={{ repeat: Infinity, duration: 0.6, ease: "easeInOut" }}
          >
            ⌛
          </motion.span>
          LOADING...
        </motion.div>
      </div>
    </div>
  );
};

export default RetroLoader;
