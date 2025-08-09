'use client';

import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';

export default function Loader() {
  const [isLoading, setIsLoading] = useState(true);

  const words = ['ENVIRONMENTS', 'EXPERIENCES', 'CONTENT'];

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 4200);

    return () => clearTimeout(timer);
  }, []);

  return (
    <AnimatePresence>
      {isLoading && (
        <motion.div
          initial={{ y: 0 }}
          exit={{ y: '-100%' }}
          transition={{ duration: 0.7, ease: 'easeInOut' }}
          className="fixed inset-0 z-[999] bg-black flex items-center justify-center"
        >
          {words.map((word, index) => (
            <motion.h1
              key={word}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{
                duration: 1,
                delay: (index + 1) * 1,
                ease: 'linear'
              }}
              className="absolute text-4xl md:text-6xl font-medium bg-gradient-to-r from-orange-400 to-red-500 bg-clip-text text-transparent"
            >
              {word}
            </motion.h1>
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
