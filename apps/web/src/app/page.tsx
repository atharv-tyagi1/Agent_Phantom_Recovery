"use client";

import { useEffect } from "react";
import { LandingNav } from "@/components/landing/LandingNav";
import { LandingHero } from "@/components/landing/LandingHero";
import { ValueBar } from "@/components/landing/ValueBar";
import { DashboardShowcase } from "@/components/landing/DashboardShowcase";
import { BentoGrid } from "@/components/landing/BentoGrid";
import { LandingCTA } from "@/components/landing/LandingCTA";
import { LandingFooter } from "@/components/landing/LandingFooter";

export default function LandingPage() {
  useEffect(() => {
    const reveals = document.querySelectorAll(".reveal");
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("active");
          }
        });
      },
      { threshold: 0.1 }
    );

    reveals.forEach((r) => observer.observe(r));
    return () => observer.disconnect();
  }, []);

  return (
    <div className="min-h-screen bg-[#0E0E0E] text-[#e5e2e1] overflow-x-hidden">
      <LandingNav />
      <main className="relative z-10 pt-16">
        <LandingHero />
        <ValueBar />
        <DashboardShowcase />
        <BentoGrid />
        <LandingCTA />
      </main>
      <LandingFooter />
    </div>
  );
}
