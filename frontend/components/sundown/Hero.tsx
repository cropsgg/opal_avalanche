'use client';

import { motion } from 'framer-motion';
import { Menu } from 'lucide-react';
import { useState } from 'react';

export default function Hero() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <div className="relative min-h-screen w-full px-4 md:px-8 bg-[#EFEAE3] overflow-hidden">
      {/* Navigation */}
      <nav className="relative z-100 flex items-center justify-between py-8 md:py-12">
        <img
          src="https://assets-global.website-files.com/64d3dd9edfb41666c35b15b7/64d3dd9edfb41666c35b15c2_Sundown%20logo.svg"
          alt="Sundown Logo"
          className="h-8 md:h-12"
        />

        <div className="hidden md:flex items-center gap-4">
          {['Work', 'Studio', 'Contact'].map((item) => (
            <motion.div
              key={item}
              whileHover={{ scale: 1.05 }}
              className="relative overflow-hidden"
            >
              <motion.div
                initial={{ bottom: '-100%' }}
                whileHover={{ bottom: 0 }}
                transition={{ duration: 0.4, ease: 'easeInOut' }}
                className="absolute inset-0 bg-black rounded-full"
              />
              <a
                href="#"
                className="relative z-10 block px-5 py-2.5 text-black hover:text-white font-medium text-lg border border-black/20 rounded-full transition-colors duration-400"
              >
                {item}
              </a>
            </motion.div>
          ))}
        </div>

        <button className="md:hidden text-2xl p-2 border border-gray-400 rounded-full">
          <Menu />
        </button>
      </nav>

      {/* Hero Content */}
      <div className="flex flex-col-reverse md:flex-row items-end justify-between mt-16 pb-10 border-b border-black/20">
        <div className="w-full md:w-1/4 mt-8 md:mt-0">
          <h3 className="text-lg md:text-xl leading-relaxed">
            Sundown is a multi-disciplinary studio focused on creating unique, end-to-end experiences and environments.
          </h3>
        </div>

        <div className="text-right">
          <motion.h1
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, ease: 'easeOut' }}
            className="text-6xl md:text-[10rem] leading-[0.8] font-light"
          >
            SPACES <br />
            THAT <br />
            INSPIRE
          </motion.h1>
        </div>
      </div>

      {/* Hero Shapes */}
      <div className="absolute right-0 top-[75vh] w-[46vw] h-[36vw] pointer-events-none">
        <div className="absolute inset-0 bg-gradient-to-br from-[#FE320A] to-[#fe6c0a] rounded-l-full blur-[20px]" />

        <motion.div
          animate={{
            x: ['55%', '0%'],
            y: ['-3%', '10%']
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            repeatType: 'reverse',
            ease: 'linear'
          }}
          className="absolute w-[30vw] h-[30vw] rounded-full bg-gradient-to-br from-[#FE320A] to-[#fe3f0a] blur-[25px]"
        />

        <motion.div
          animate={{
            x: ['5%', '-20%'],
            y: ['-5%', '30%']
          }}
          transition={{
            duration: 5,
            repeat: Infinity,
            repeatType: 'reverse',
            ease: 'linear'
          }}
          className="absolute w-[30vw] h-[30vw] rounded-full bg-gradient-to-br from-[#FE320A] to-[#FF9831] blur-[25px]"
        />
      </div>

      {/* Video */}
      <motion.video
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1, delay: 0.5 }}
        src="/sundown-assets/video.mp4"
        autoPlay
        muted
        loop
        className="relative w-full mt-16 rounded-3xl"
        style={{ aspectRatio: '16/9' }}
      />
    </div>
  );
}
