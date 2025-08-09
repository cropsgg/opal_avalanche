'use client';

import { motion } from 'framer-motion';

export default function MovingText() {
  const textItems = ['EXPERIENCES', 'CONTENT', 'ENVIRONMENTS'];

  return (
    <div className="bg-[#EFEAE3] py-16 md:py-32">
      <div className="overflow-hidden whitespace-nowrap">
        <motion.div
          animate={{ x: ['0%', '-100%'] }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: 'linear'
          }}
          className="flex items-center whitespace-nowrap"
        >
          {[...Array(3)].map((_, containerIndex) => (
            <div key={containerIndex} className="flex items-center shrink-0">
              {textItems.map((text, index) => (
                <div key={`${containerIndex}-${index}`} className="flex items-center">
                  <h1 className="text-6xl md:text-[9vw] font-light mx-8">
                    {text}
                  </h1>
                  <div className="w-12 h-12 md:w-[70px] md:h-[70px] bg-[#FE320A] rounded-full mx-8" />
                </div>
              ))}
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}
