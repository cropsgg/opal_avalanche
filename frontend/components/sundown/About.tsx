'use client';

import { motion } from 'framer-motion';
import { useInView } from 'react-intersection-observer';

export default function About() {
  const [ref, inView] = useInView({
    threshold: 0.3,
    triggerOnce: true
  });

  return (
    <div className="relative bg-[#EFEAE3] min-h-screen py-16 md:py-32">
      <div ref={ref} className="relative z-10 px-4 md:px-16 flex flex-col md:flex-row items-center justify-between h-[80vh]">
        <motion.h1
          initial={{ opacity: 0, x: -50 }}
          animate={inView ? { opacity: 1, x: 0 } : {}}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          className="w-full md:w-[60%] text-3xl md:text-[4vw] leading-tight md:leading-[4vw] font-light"
        >
          We are a group of design-driven, goal-focused creators, producers, and designers who believe that the details make all the difference.
        </motion.h1>

        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, delay: 0.3, ease: 'easeOut' }}
          className="w-full md:w-1/5 mt-8 md:mt-64 flex flex-col"
        >
          <img
            src="/sundown-assets/img1.webp"
            alt="Studio"
            className="w-full rounded-2xl mb-8"
          />
          <p className="text-sm md:text-base font-light leading-relaxed">
            We love to create, we love to solve, we love to collaborate, and we love to turn amazing ideas into reality. We're here to partner with you through every step of the process and know that relationships are the most important things we build.
          </p>
        </motion.div>
      </div>

      {/* Animated blob */}
      <motion.div
        animate={{
          filter: ['blur(20px)', 'blur(30px)'],
          transform: [
            'translate(10%, -10%) skew(0deg)',
            'translate(-10%, 10%) skew(-12deg)'
          ]
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          repeatType: 'reverse',
          ease: 'easeInOut'
        }}
        className="absolute top-[58%] left-[25%] w-[32vw] h-[32vw] rounded-full bg-gradient-to-br from-[#FE320A] to-[#fe6c0a] blur-[20px]"
      />
    </div>
  );
}
