import { AnimatePresence, motion } from "framer-motion";
import { useMemo, useState } from "react";

const COLORS = ["#7DE3FF", "#35E0A1", "#F5C36B", "#F5F8FF", "#E5556E"];

interface Spark {
  x: number;
  y: number;
  color: string;
  size: number;
  delay: number;
}

function makeSparks(n: number): Spark[] {
  return Array.from({ length: n }, () => {
    const angle = Math.random() * Math.PI * 2;
    const dist = 90 + Math.random() * 240;
    return {
      x: Math.cos(angle) * dist,
      y: Math.sin(angle) * dist,
      color: COLORS[Math.floor(Math.random() * COLORS.length)],
      size: 4 + Math.random() * 7,
      delay: Math.random() * 0.15,
    };
  });
}

export default function GiftEasterEgg() {
  const [open, setOpen] = useState(false);
  // Nuevas chispas cada vez que se abre.
  const sparks = useMemo(() => makeSparks(64), [open]);

  return (
    <>
      {/* Botón de regalo (frente) */}
      <motion.button
        onClick={() => setOpen(true)}
        initial={{ scale: 0, rotate: -30 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 260, damping: 18, delay: 1.9 }}
        whileHover={{ scale: 1.12, rotate: [0, -8, 8, 0] }}
        whileTap={{ scale: 0.92 }}
        className="glass pointer-events-auto absolute right-4 top-[84px] z-40 grid h-11 w-11 place-items-center rounded-xl text-xl md:top-[92px]"
        title="Sorpresa"
        aria-label="Sorpresa"
      >
        🎁
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            className="pointer-events-auto absolute inset-0 z-50 grid place-items-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setOpen(false)}
          >
            {/* Fondo oscuro con blur */}
            <div className="absolute inset-0 bg-void/70 backdrop-blur-sm" />

            {/* Chispas */}
            <div className="pointer-events-none absolute left-1/2 top-1/2">
              {sparks.map((s, i) => (
                <motion.span
                  key={i}
                  className="absolute rounded-full"
                  style={{ width: s.size, height: s.size, background: s.color, boxShadow: `0 0 10px ${s.color}` }}
                  initial={{ x: 0, y: 0, opacity: 0, scale: 0.4 }}
                  animate={{ x: s.x, y: s.y, opacity: [0, 1, 1, 0], scale: [0.4, 1.2, 1, 0.6] }}
                  transition={{ duration: 1.3, delay: s.delay, ease: "easeOut", repeat: Infinity, repeatDelay: 0.5 }}
                />
              ))}
            </div>

            {/* Mensaje central */}
            <motion.div
              className="relative z-10 px-6 text-center"
              initial={{ scale: 0.6, opacity: 0, y: 10 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ type: "spring", stiffness: 220, damping: 18, delay: 0.15 }}
            >
              <div className="mb-3 text-5xl">🎉</div>
              <h1
                className="hud-title text-3xl font-extrabold tracking-wide text-bright sm:text-5xl"
                style={{ textShadow: "0 0 24px rgba(125,227,255,0.55)" }}
              >
                el abuelo es viejo y manco
              </h1>
              <p className="hud-label mt-4">toca para cerrar</p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
