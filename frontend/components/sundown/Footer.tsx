'use client';

import { motion } from 'framer-motion';
import { ArrowRight } from 'lucide-react';

export default function Footer() {
  return (
    <div className="fixed bottom-0 w-full h-full z-10 text-white flex flex-col justify-end bg-black">
      {/* Animated background blobs */}
      <motion.div
        animate={{
          filter: ['blur(50px)', 'blur(30px)'],
          transform: [
            'translate(10%, -10%) skew(0deg)',
            'translate(-10%, 10%) skew(-12deg)'
          ]
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          repeatType: 'reverse',
          ease: 'easeInOut'
        }}
        className="absolute -top-[10%] left-0 w-[150vw] h-[50vh] rounded-b-full bg-gradient-to-br from-[#FE320A] to-[#fe6c0a] rotate-12 blur-[50px]"
      />

      <motion.div
        animate={{
          filter: ['blur(50px)', 'blur(30px)'],
          transform: [
            'translate(-10%, -10%) skew(0deg)',
            'translate(10%, 10%) skew(12deg)'
          ]
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          repeatType: 'reverse',
          ease: 'easeInOut',
          delay: 1
        }}
        className="absolute -top-[20%] right-0 w-[75vw] h-[25vh] rounded-b-full bg-[#FE320A] -rotate-12 blur-[30px]"
      />

      {/* Footer Content */}
      <div className="relative z-20 flex flex-col justify-between h-full">
        {/* Top section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-end px-6 md:px-24 py-8 mt-auto">
          <div className="flex flex-col md:flex-row gap-4 md:gap-12">
            {['Work', 'Studio', 'Contact'].map((item) => (
              <motion.h1
                key={item}
                whileHover={{ opacity: 0.5 }}
                transition={{ duration: 0.5, ease: 'easeInOut' }}
                className="text-4xl md:text-6xl font-light cursor-pointer"
              >
                {item}
              </motion.h1>
            ))}
          </div>

          <div className="flex flex-col items-end gap-4 mt-8 md:mt-0">
            <p className="text-lg md:text-xl font-light text-right">
              Get industry insights and creative <br /> inspiration straight to your inbox.
            </p>
            <div className="flex items-center justify-between border-b border-[#EFEAE3] pb-3 min-w-[300px]">
              <input
                type="email"
                placeholder="Email Address"
                className="bg-transparent border-none text-lg md:text-xl font-light placeholder:text-[#EFEAE3] flex-1 outline-none"
              />
              <button className="p-2 text-[#EFEAE3] hover:text-white transition-colors">
                <ArrowRight size={24} />
              </button>
            </div>
          </div>
        </div>

        {/* Large text */}
        <div className="px-6 md:px-10 py-8">
          <h1 className="text-[15vw] md:text-[23vw] font-light leading-none">
            Sundown
          </h1>
        </div>

        {/* Bottom section */}
        <div className="border-t border-gray-600 px-6 md:px-10 py-6 flex flex-col md:flex-row justify-between items-center gap-4 text-base md:text-xl font-light">
          <p>Copyright © Sundown Studio</p>
          <p>Brooklyn, NY</p>
          <div className="flex gap-6">
            <a href="#" className="text-white hover:text-gray-300 transition-colors">Instagram</a>
            <a href="#" className="text-white hover:text-gray-300 transition-colors">LinkedIn</a>
          </div>
        </div>
      </div>
    </div>
  );
}
