'use client'

import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'

const AuthPage = () => {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const buttonVariants = {
    hidden: (direction: number) => ({
      y: direction * 500,
      opacity: 0,
    }),
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring' as const,
        stiffness: 80,
        damping: 8,
        mass: 1.5,
        bounce: 0.6,
      },
    },
  }

  const circleVariants = {
    animate: {
      rotate: 360,
      transition: {
        duration: 20,
        ease: 'linear' as const,
        repeat: Infinity,
      },
    },
  }

  if (!mounted) return null

  return (
    <div className="relative h-screen w-full bg-cream-100 flex items-center justify-center overflow-hidden">
      {/* Background circles */}
      {[...Array(20)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full bg-gradient-to-r from-brown-500 to-brown-900"
          style={{
            width: `${Math.random() * 300 + 150}px`,
            height: `${Math.random() * 300 + 150}px`,
            top: `${Math.random() * 100}%`,
            left: `${Math.random() * 100}%`,
            zIndex: 0,
          }}
          animate="animate"
          variants={circleVariants}
          custom={Math.random() > 0.5 ? 1 : -1}
        />
      ))}

      <div className="z-10 flex flex-col md:flex-row gap-6 items-center">
        <motion.button
          className="px-8 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-lg shadow-lg hover:shadow-cyan-500/30 transition-shadow"
          custom={-1}
          initial="hidden"
          animate="visible"
          variants={buttonVariants}
        >
          Sign In
        </motion.button>

        <motion.button
          className="px-8 py-3 bg-gradient-to-r from-purple-500 to-pink-600 text-white font-semibold rounded-lg shadow-lg hover:shadow-purple-500/30 transition-shadow"
          custom={1}
          initial="hidden"
          animate="visible"
          variants={buttonVariants}
        >
          Sign Up
        </motion.button>
      </div>
    </div>
  )
}

export default AuthPage
