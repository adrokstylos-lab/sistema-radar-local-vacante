import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";

/** Neblina + scanlines permanentes, e intro "boot" que aparece una sola vez. */
export default function AnimatedOverlay() {
  const [booting, setBooting] = useState(true);
  useEffect(() => {
    const t = setTimeout(() => setBooting(false), 1700);
    return () => clearTimeout(t);
  }, []);

  return (
    <>
      <div className="fx-fog" />
      <div className="fx-scan" />

      <AnimatePresence>
        {booting && (
          <motion.div
            className="pointer-events-none absolute inset-0 z-40 grid place-items-center bg-void"
            initial={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="text-center">
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5 }}
                className="hud-title text-2xl font-bold tracking-[0.3em] text-bright"
              >
                RADAR LOCAL
              </motion.div>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: 220 }}
                transition={{ duration: 1, ease: "easeInOut" }}
                className="mx-auto mt-3 h-px bg-ice/60"
              />
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="hud-label mt-3"
              >
                Inicializando sistema de inteligencia…
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
