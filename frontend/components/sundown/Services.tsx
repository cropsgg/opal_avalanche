'use client';

import { Swiper, SwiperSlide } from 'swiper/react';
import 'swiper/css';

interface Service {
  title: string;
  description: string;
  image: string;
}

const services: Service[] = [
  {
    title: 'Nike',
    description: 'Retained Production support across retail and events in NY, CHI, LA. Creative Design, Design Management, Production/Project Management, and execution of work from concept to installation across the Country.',
    image: '/sundown-assets/swip1.svg'
  },
  {
    title: 'Arc\'teryx',
    description: 'Creative Concepting, Design, Design Management, Project Management, and execution of work from concept to installation across the Country. Cross functional communication and management of third party partners.',
    image: '/sundown-assets/swip2.svg'
  },
  {
    title: 'Converse',
    description: 'Production and design along with install oversight and execution support for the SoHo store opening on Broadway St, New York. Also working on creative and production work for a new store opening in Glendale, California.',
    image: '/sundown-assets/swip3.svg'
  },
  {
    title: 'Hunter',
    description: 'Design and Production partner for Hunter Holiday 2022 Pop-in at Nordstrom 57th St, New York, including activations in Women\'s, Men\'s and Kid\'s zones. Thirty-five (35) additional smaller take-downs in Nordstrom stores across the US. Concept design for Holiday boot customization events in stores across winter 2022.',
    image: '/sundown-assets/swip4.svg'
  },
  {
    title: 'CES',
    description: 'Creative, Design, and Production Partner for 2023 CES. Scope Included creation of Branding Identity, Assets, and Digital Content, Design, Production design, Production oversight and Installation of client activations for IBM, Delta, Instacart, and more.',
    image: '/sundown-assets/swip5.svg'
  },
  {
    title: 'Afterpay',
    description: 'Creative, Design, and Production Partner for 2022 NY Fashion Week Pop-Up space. In Partnership with B-Reel scope including creation of Final Design, Design Assets, 3D Renders, Production design, Production/Partner oversight and creation of a two (2) story pop-up for Afterpay\'s clients such as Crocs, JD Sports, Container Store, & Revolve.',
    image: '/sundown-assets/swip6.svg'
  }
];

export default function Services() {
  return (
    <div className="w-full h-[70vh] py-20 px-4 md:px-8 bg-[#EFEAE3]">
      <Swiper
        slidesPerView="auto"
        centeredSlides={true}
        spaceBetween={100}
        className="w-full h-full"
      >
        {services.map((service, index) => (
          <SwiperSlide key={index} className="w-auto max-w-md">
            <div className="flex flex-col items-start justify-start pl-8 gap-8 border-l border-gray-400 h-full">
              <img
                src={service.image}
                alt={service.title}
                className="w-32 h-32 object-contain"
              />
              <p className="text-lg font-light leading-relaxed">
                {service.description}
              </p>
            </div>
          </SwiperSlide>
        ))}
      </Swiper>
    </div>
  );
}
