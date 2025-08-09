'use client';

import { useEffect } from 'react';
import Loader from '@/components/sundown/Loader';
import Hero from '@/components/sundown/Hero';
import MovingText from '@/components/sundown/MovingText';
import About from '@/components/sundown/About';
import Projects from '@/components/sundown/Projects';
import Services from '@/components/sundown/Services';
import Footer from '@/components/sundown/Footer';

export default function SundownPage() {
  useEffect(() => {
    // Add any global effects here if needed
  }, []);

  return (
    <div className="relative">
      <Loader />
      <div className="relative z-10">
        <Hero />
        <MovingText />
        <About />
        <Projects />
        <Services />
        <div className="h-[70vh]" />
      </div>
      <Footer />
    </div>
  );
}
