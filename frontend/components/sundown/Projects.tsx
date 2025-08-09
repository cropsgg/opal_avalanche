'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';

interface Project {
  title: string;
  company: string;
  category: string;
  image: string;
}

const projects: Project[] = [
  {
    title: 'Makers Studio HOI',
    company: 'NIKE',
    category: 'Experiential',
    image: 'https://assets-global.website-files.com/64d3dd9edfb41666c35b15d4/64d3dd9edfb41666c35b1733_Nike_HOI_50th_SU22_FL1_5388.webp'
  },
  {
    title: 'SOHO 2023',
    company: 'ARC\'TERYX',
    category: 'Environment',
    image: 'https://assets-global.website-files.com/64d3dd9edfb41666c35b15d4/64d3dd9edfb41666c35b163b_Copy-of-IMG_1180.webp'
  },
  {
    title: 'Play New Kidvision',
    company: 'NIKE',
    category: 'Environment',
    image: 'https://assets-global.website-files.com/64d3dd9edfb41666c35b15d4/64d3dd9edfb41666c35b1698_Nike_Soho_Play-New-Kids_10-27-21_1950.webp'
  },
  {
    title: 'SOHO 2023',
    company: 'CONVERSE',
    category: 'Environment',
    image: 'https://assets-global.website-files.com/64d3dd9edfb41666c35b15d4/64d3dd9edfb41666c35b163d_Copy%20of%20DSC04086.webp'
  },
  {
    title: 'Air Force 1 2021',
    company: 'NIKE',
    category: 'Environment',
    image: 'https://assets-global.website-files.com/64d3dd9edfb41666c35b15d4/64d3dd9edfb41666c35b1733_Nike_HOI_50th_SU22_FL1_5388.webp'
  },
  {
    title: '50th Anniversary',
    company: 'NIKE',
    category: 'Environment',
    image: 'https://assets-global.website-files.com/64d3dd9edfb41666c35b15d4/64d3dd9edfb41666c35b16f4_Copy%20of%20Nike_Soho_50th_SU22_FL1_6176.webp'
  },
  {
    title: 'NYFW Popup',
    company: 'AFTERPAY',
    category: 'Environment',
    image: 'https://assets-global.website-files.com/64d3dd9edfb41666c35b15d4/64d3dd9edfb41666c35b170d_AM704059.webp'
  }
];

export default function Projects() {
  const [hoveredProject, setHoveredProject] = useState<number | null>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = (e: React.MouseEvent) => {
    setMousePosition({ x: e.clientX, y: e.clientY });
  };

  return (
    <div className="bg-[#EFEAE3] w-full py-16 min-h-screen" onMouseMove={handleMouseMove}>
      <div className="relative">
        {projects.map((project, index) => (
          <motion.div
            key={index}
            className="relative w-full h-32 px-4 md:px-8 flex items-center border-b border-gray-400/40 overflow-hidden cursor-pointer"
            onMouseEnter={() => setHoveredProject(index)}
            onMouseLeave={() => setHoveredProject(null)}
            whileHover={{ backgroundColor: 'rgba(0,0,0,0.02)' }}
          >
            <h2 className="relative z-10 text-3xl md:text-5xl font-light">
              {project.title}
            </h2>

            <motion.div
              initial={{ y: '-100%' }}
              animate={{ y: hoveredProject === index ? '0%' : '-100%' }}
              transition={{ duration: 0.25, ease: 'easeInOut' }}
              className="absolute inset-0 bg-[#FF9831] flex items-center justify-end px-4 md:px-8"
            >
              <div className="flex flex-col items-end">
                <p className="text-lg md:text-xl font-medium">{project.company}</p>
                <span className="text-sm md:text-base font-light">{project.category}</span>
              </div>
            </motion.div>
          </motion.div>
        ))}
      </div>

      {/* Fixed image that follows mouse */}
      {hoveredProject !== null && (
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          transition={{ duration: 0.2 }}
          className="fixed w-96 h-[30rem] rounded-2xl pointer-events-none z-50 bg-cover bg-center"
          style={{
            backgroundImage: `url(${projects[hoveredProject].image})`,
            left: mousePosition.x - 192, // Half of width (384/2)
            top: mousePosition.y - 240   // Half of height (480/2)
          }}
        />
      )}
    </div>
  );
}
