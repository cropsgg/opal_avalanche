import { Scale, FileText, Phone, Users, MessageSquare } from "lucide-react";
import Image from "next/image";
import { Baskervville, Montserrat } from "next/font/google";
import CountUp from "@/app/components/CountUp/CountUp";

const baskervville = Baskervville({
  subsets: ["latin"],
  weight: ["400"],
  style: ["italic", "normal"],
  variable: "--font-baskervville",
});
const montserrat = Montserrat({
  subsets: ["latin"],
  weight: ["400"],
  style: ["italic", "normal"],
  variable: "--font-montserrat",
});
export default function HowItWorksSection() {
  const consultationSteps = [
    {
      icon: Phone,
      title: "Initial Consultation",
      description:
        "Schedule a confidential consultation with our experienced legal and accounting team",
    },
    {
      icon: FileText,
      title: "Case & Requirement Evaluation",
      description:
        "Our experts thoroughly analyze your legal, tax, and compliance requirements",
    },
    {
      icon: Scale,
      title: "Strategy & Planning",
      description:
        "We develop a comprehensive legal and accounting strategy tailored to your needs",
    },
    {
      icon: Users,
      title: "Expert Representation & Filing",
      description:
        "Our skilled team represents your interests and handles all filings with dedication",
    },
    {
      icon: MessageSquare,
      title: "Regular Updates",
      description:
        "Stay informed with regular updates on your legal and accounting matters",
    },
  ];

  return (
    <section className="py-16 bg-[#F8F3EE]">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h2
            className={`text-3xl md:text-4xl lg:text-5xl font-light text-[#2A2A2A] mb-8 tracking-wide leading-tight ${baskervville.className}`}
          >
            YOUR TRUSTED LEGAL & ACCOUNTING PARTNERS
          </h2>
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {/* Left Side - Attorney Info */}
          <div className="lg:col-span-1">
            <div className="mb-6">
              <h3
                className={`text-xl font-semibold text-[#2A2A2A] mb-4 ${baskervville.className}`}
              >
                VERIFIED ATTORNEYS & CHARTERED ACCOUNTANTS
              </h3>
              <p
                className={`text-[#8B7355] leading-relaxed mb-6 ${montserrat.className}`}
              >
                When looking for legal or accounting help, you want
                professionals with experience in cases and filings like yours,
                who maintain the highest ethical and customer service standards.
              </p>
              <button
                className={`${montserrat.className} bg-[#8B7355] hover:bg-[#7A6449] text-white px-6 py-2  text-sm font-medium transition-colors duration-300`}
              >
                Learn More
              </button>
            </div>

            {/* Attorney Image */}
            <div className="bg-[#E8DDD1]  p-1">
              <div className="relative w-full h-80  overflow-hidden">
                <Image
                  src="/images/img1.png"
                  alt="Professional Attorney"
                  fill
                  className="object-cover"
                />
              </div>
            </div>
          </div>

          {/* Center - Stats */}
          <div className="lg:col-span-1 flex flex-col justify-center items-center">
            <div className="text-center space-y-8">
              <div>
                <div className="text-5xl font-light text-[#2A2A2A] mb-2">
                  <CountUp
                    from={0}
                    to={90}
                    separator=","
                    direction="up"
                    duration={1}
                    className="count-up-text"
                  />
                </div>
                <div className="text-[#8B7355] text-sm">
                  Legal
                  <br />
                  Execution
                </div>
              </div>
              <div>
                <div className="text-5xl font-light text-[#2A2A2A] mb-2">
                  <CountUp
                    from={0}
                    to={98}
                    separator=""
                    direction="up"
                    duration={1}
                    className="count-up-text"
                  />%
                </div>
                <div className="text-[#8B7355] text-sm">
                  Project
                  <br />
                  Success
                </div>
              </div>
            </div>
          </div>

          {/* Right Side - Benefits Card */}
          <div className="lg:col-span-1">
            <div className="bg-[#8B4513] text-white p-8 -2xl h-full">
              <h3
                className={`text-2xl font-bold mb-6 ${baskervville.className}`}
              >
                WHY CHOOSE LEGALEASE?
              </h3>

              <p
                className={`text-white/90 mb-8 leading-relaxed ${montserrat.className}`}
              >
                We provide high quality legal and accounting services for you,
                your business, and your family. Get the best people for all your
                compliance and advisory needs.
              </p>

              <div className="space-y-6">
                <div>
                  <h4 className={`font-semibold mb-2 ${montserrat.className}`}>
                    Legal & Accounting Representation
                  </h4>
                  <p
                    className={`text-white/80 text-sm leading-relaxed ${montserrat.className}`}
                  >
                    We provide efficient client service and ensure your legal,
                    tax, and compliance needs are met.
                  </p>
                </div>

                <div>
                  <h4 className={`font-semibold mb-2 ${montserrat.className}`}>
                    Compliance & Filings
                  </h4>
                  <p
                    className={`text-white/80 text-sm leading-relaxed ${montserrat.className}`}
                  >
                    We ensure your business stays compliant with GST, tax, and
                    regulatory filings.
                  </p>
                </div>

                <div>
                  <h4 className={`font-semibold mb-2 ${montserrat.className}`}>
                    Support
                  </h4>
                  <p
                    className={`text-white/80 text-sm leading-relaxed ${montserrat.className}`}
                  >
                    Our team is available 24/7 to provide legal and accounting
                    support whenever you need it.
                  </p>
                </div>
              </div>

              {/* Bottom Button and Image */}
              <div className="mt-8 flex justify-between items-end">
                <button className="bg-white text-[#8B4513] px-6 py-2  font-medium text-sm hover:bg-gray-100 transition-colors duration-300">
                  Contact Us
                </button>

                <div className="w-16 h-20 relative">
                  <Image
                    src="/images/img1.png"
                    alt="Attorney"
                    fill
                    className="object-cover "
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
