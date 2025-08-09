"use client";

import React, { useState } from "react";
import {
  Phone,
  Mail,
  MapPin,
  Clock,
  User,
  MessageSquare,
  Send,
  CheckCircle,
} from "lucide-react";
import Link from "next/link";

export default function ContactSection() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    service: "",
    message: "",
  });
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = () => {
    // Handle form submission logic here
    setIsSubmitted(true);
    setTimeout(() => setIsSubmitted(false), 3000);
  };

  return (
    <>
      <div className="bg-stone-50 py-20 px-6">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-baskervville text-amber-900 mb-4 tracking-wide">
              NEED EXPERTISE?
            </h2>
            <div className="flex items-center justify-center gap-8 mb-6">
              <div className="h-px bg-amber-800 w-20"></div>
              <span className="text-amber-700 font-medium text-lg">
                LET'S CONNECT
              </span>
              <div className="h-px bg-amber-800 w-20"></div>
            </div>
            <p className="text-amber-800 text-lg max-w-2xl mx-auto leading-relaxed">
              Whether you need legal assistance, tax consultation, or business
              compliance support, our expert team is here to provide
              comprehensive solutions tailored to your needs.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-16">
            {/* Contact Information */}
            <div className="space-y-8">
              <div className="bg-white p-8 -lg shadow-lg font-baskervville">
                <h3 className="text-2xl font-baskervville text-amber-900 mb-6 text-center">
                  Get In Touch
                </h3>

                <div className="space-y-6 font-montserrat">
                  <div className="flex items-center gap-4 p-4 bg-stone-50 -lg">
                    <div className="bg-amber-800 p-3 -full">
                      <Mail className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold text-amber-900 font-baskervville">
                        Email Us
                      </p>
                      <p className="text-amber-700 text-sm">
                        connect@legalegalease.in
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 p-4 bg-stone-50 -lg">
                    <div className="bg-amber-800 p-3 -full">
                      <Phone className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold text-amber-900 font-baskervville">
                        Call Us
                      </p>
                      <p className="text-amber-700 text-sm">+91 98765 43210</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 p-4 bg-stone-50 -lg">
                    <div className="bg-amber-800 p-3 -full">
                      <MapPin className="w-5 h-5 text-white" />
                    </div>
                    <div>
                      <p className="font-semibold text-amber-900 font-baskervville">
                        Visit Us
                      </p>
                      <p className="text-amber-700 text-sm">
                        Legal District, Business Hub
                        <br />
                        Mumbai, Maharashtra
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Services Overview */}
            </div>

            {/* Contact Form */}
            <div className="bg-white p-8 -lg shadow-lg font-baskervville">
              <h3 className="text-2xl font-baskervville text-amber-900 mb-6 text-center">
                Send Us A Message
              </h3>

              {isSubmitted ? (
                <div className="text-center py-8">
                  <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
                  <h4 className="text-xl font-semibold text-amber-900 mb-2">
                    Thank You!
                  </h4>
                  <p className="text-amber-700">
                    We'll get back to you within 24 hours.
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-amber-900 font-semibold mb-2">
                        Full Name
                      </label>
                      <div className="relative">
                        <User className="absolute left-3 top-3 w-5 h-5 text-amber-600" />
                        <input
                          type="text"
                          name="name"
                          value={formData.name}
                          onChange={handleInputChange}
                          className="w-full pl-10 pr-4 py-3 border border-amber-200 -lg focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                          placeholder="Enter your full name"
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-amber-900 font-semibold mb-2">
                        Email Address
                      </label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-3 w-5 h-5 text-amber-600" />
                        <input
                          type="email"
                          name="email"
                          value={formData.email}
                          onChange={handleInputChange}
                          className="w-full pl-10 pr-4 py-3 border border-amber-200 -lg focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                          placeholder="Enter your email"
                          required
                        />
                      </div>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-amber-900 font-semibold mb-2">
                        Phone Number
                      </label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-3 w-5 h-5 text-amber-600" />
                        <input
                          type="tel"
                          name="phone"
                          value={formData.phone}
                          onChange={handleInputChange}
                          className="w-full pl-10 pr-4 py-3 border border-amber-200 -lg focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                          placeholder="Enter your phone number"
                          required
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-amber-900 font-semibold mb-2">
                        Service Required
                      </label>
                      <select
                        name="service"
                        value={formData.service}
                        onChange={handleInputChange}
                        className="w-full px-4 py-3 border border-amber-200 -lg focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        required
                      >
                        <option value="">Select a service</option>
                        <option value="legal-consultation">
                          Legal Consultation
                        </option>
                        <option value="tax-filing">Tax Return Filing</option>
                        <option value="gst-compliance">GST Compliance</option>
                        <option value="business-registration">
                          Business Registration
                        </option>
                        <option value="contract-drafting">
                          Contract Drafting
                        </option>
                        <option value="audit-services">Audit Services</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-amber-900 font-semibold mb-2">
                      Message
                    </label>
                    <div className="relative">
                      <MessageSquare className="absolute left-3 top-3 w-5 h-5 text-amber-600" />
                      <textarea
                        name="message"
                        value={formData.message}
                        onChange={handleInputChange}
                        rows={4}
                        className="w-full pl-10 pr-4 py-3 border border-amber-200 -lg focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent resize-none"
                        placeholder="Tell us about your requirements..."
                        required
                      />
                    </div>
                  </div>

                  <button
                    onClick={handleSubmit}
                    className="w-full bg-amber-800 text-white py-3 px-6 -lg font-semibold hover:bg-amber-900 transition-colors duration-200 flex items-center justify-center gap-2"
                  >
                    <Send className="w-5 h-5" />
                    Send Message
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Bottom Section */}
          <div className="flex p-12 justify-center space-x-8 md:space-x-12 ">
            <Link
              href="/"
              className="text-[#8B7355] hover:text-[#2A2A2A] transition-colors duration-300"
            >
              Compliance
            </Link>
            <Link
              href="/"
              className="text-[#8B7355] hover:text-[#2A2A2A] transition-colors duration-300"
            >
              Home
            </Link>
            <Link
              href="/features"
              className="text-[#8B7355] hover:text-[#2A2A2A] transition-colors duration-300"
            >
              Projects
            </Link>
            <Link
              href="/blog"
              className="text-[#8B7355] hover:text-[#2A2A2A] transition-colors duration-300"
            >
              Blog
            </Link>
            <Link
              href="/contact"
              className="text-[#8B7355] hover:text-[#2A2A2A] transition-colors duration-300"
            >
              Contacts
            </Link>
          </div>

        </div>
      </div>
    </>
  );
}
