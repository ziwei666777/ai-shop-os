"use client";

import { useEffect, useState } from "react";
import type { CSSProperties } from "react";
import {
  ArrowUpRight,
  CornerUpLeft,
  Droplets,
  FlaskConical,
  Leaf,
  Menu,
  Search,
  ShoppingBag,
  Sun,
  X
} from "lucide-react";

const backgroundImage =
  "https://images.higgs.ai/?default=1&output=webp&url=https%3A%2F%2Fd8j0ntlcm91z4.cloudfront.net%2Fuser_38xzZboKViGWJOttwIXH07lWA1P%2Fhf_20260624_110248_b62f758d-f68c-4045-a7b4-91771d6d0a0f.png&w=1280&q=85";
const avatarImage =
  "https://polo-pecan-73837341.figma.site/_assets/v11/ca8093996e970200cbcf8bde8744175e52da5a79.png";
const inlineCapsuleImage =
  "https://polo-pecan-73837341.figma.site/_assets/v11/6a7de4fbe9c9e2315040607320a9ff5e93117bf4.png";
const heroProductImage =
  "https://polo-pecan-73837341.figma.site/_assets/v11/50ad042b3cd48a2e120ea3ba17c8cfeaf3cc334c.png";
const panelLeafImage =
  "https://polo-pecan-73837341.figma.site/_assets/v11/6736cbe6e26afa2cd7c04a91892a79f7640785b5.png";
const smallProductImage =
  "https://polo-pecan-73837341.figma.site/_assets/v11/30e8f38d1f993c357a3be2721557fc899d5640fc.png";

const navLinks = ["About", "Products", "Promotions", "Contact"];

const headlineLines = [
  [
    { text: "The", dimmed: false, delay: "delay-300" },
    { text: "Power", dimmed: false, delay: "delay-400" },
    { text: "of", dimmed: true, delay: "delay-500" }
  ],
  [
    { text: "Nature", dimmed: true, delay: "delay-600" },
    { text: "in", dimmed: true, delay: "delay-700" },
    { text: "Every", dimmed: false, delay: "delay-800" }
  ]
];

const carouselCards = [
  {
    text: "Experience our newly enhanced natural formula",
    Icon: FlaskConical,
    tone: "black"
  },
  {
    text: "Pure organic ingredients sourced sustainably",
    Icon: Leaf,
    tone: "emerald"
  },
  {
    text: "Advanced bioavailability for maximum absorption",
    Icon: Droplets,
    tone: "cyan"
  },
  {
    text: "Clinically tested for daily energy & vitality",
    Icon: Sun,
    tone: "amber"
  }
];

export default function Page() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeCard, setActiveCard] = useState(0);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setActiveCard((current) => (current + 1) % carouselCards.length);
    }, 3500);

    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  return (
    <main
      className="terra-page"
      style={{ "--hero-bg": `url("${backgroundImage}")` } as CSSProperties}
    >
      <nav className="terra-nav animate-fade-in" aria-label="Primary navigation">
        <a className="terra-brand animate-slide-left delay-200" href="#top">
          TerraElix
        </a>

        <div className="terra-nav-links animate-fade-in delay-400">
          {navLinks.map((link) => (
            <a href={`#${link.toLowerCase()}`} key={link}>
              {link}
            </a>
          ))}
        </div>

        <div className="terra-actions animate-slide-right delay-300">
          <button type="button" aria-label="Search">
            <Search size={20} strokeWidth={1.5} />
          </button>
          <button type="button" aria-label="Shopping bag">
            <ShoppingBag size={20} strokeWidth={1.5} />
          </button>
          <button type="button" aria-label="Return">
            <CornerUpLeft size={20} strokeWidth={1.5} />
          </button>
          <img src={avatarImage} alt="TerraElix member avatar" />
          <button
            className="menu-toggle"
            type="button"
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((open) => !open)}
          >
            {menuOpen ? <X size={22} strokeWidth={1.6} /> : <Menu size={22} strokeWidth={1.6} />}
          </button>
        </div>
      </nav>

      {menuOpen ? (
        <div className="mobile-menu" role="dialog" aria-modal="true" aria-label="Mobile navigation">
          {navLinks.map((link) => (
            <a href={`#${link.toLowerCase()}`} key={link} onClick={() => setMenuOpen(false)}>
              {link}
            </a>
          ))}
        </div>
      ) : null}

      <section className="terra-hero" id="top">
        <div className="hero-copy">
          <h1 aria-label="The Power of Nature in Every Capsule">
            {headlineLines.map((line, lineIndex) => (
              <span className="headline-line" key={lineIndex}>
                {line.map((word) => (
                  <span
                    className={`word-mask animate-word-reveal ${word.dimmed ? "dimmed" : ""} ${word.delay}`}
                    key={word.text}
                    aria-hidden="true"
                  >
                    <span>{word.text}</span>
                  </span>
                ))}
              </span>
            ))}
            <span className="headline-line">
              <span className="word-mask animate-word-reveal delay-900" aria-hidden="true">
                <span>Capsule</span>
              </span>
              <img
                className="inline-capsule animate-scale-in delay-1000"
                src={inlineCapsuleImage}
                alt=""
                aria-hidden="true"
              />
            </span>
          </h1>

          <div className="cta-row animate-fade-up delay-600">
            <a className="primary-cta" href="#products">
              Explore Now
              <ArrowUpRight size={24} strokeWidth={1.6} />
            </a>
            <p>Discover our new plant-based supplements for daily balance and clean energy.</p>
          </div>
        </div>
      </section>

      <div className="mobile-product-wrap animate-scale-in delay-800">
        <img src={heroProductImage} alt="TerraElix plant-based supplement capsules" />
      </div>

      <section className="panel-grid" id="products" aria-label="TerraElix product highlights">
        <article className="panel panel-assessment animate-fade-up delay-900">
          <div>
            <h2>Start your personalized path to natural balance</h2>
            <a href="#about">Personal Assessment</a>
          </div>
          <img src={panelLeafImage} alt="" aria-hidden="true" />
        </article>

        <article className="panel panel-carousel animate-fade-up delay-1000">
          <div className="carousel-stage" aria-live="polite">
            {carouselCards.map(({ text, Icon, tone }, index) => (
              <div
                className={`carousel-card ${activeCard === index ? "active" : ""}`}
                key={text}
                aria-hidden={activeCard !== index}
              >
                <span className={`icon-bubble ${tone}`}>
                  <Icon size={22} strokeWidth={1.7} />
                </span>
                <p>{text}</p>
              </div>
            ))}
          </div>
          <div className="carousel-dots" aria-label="Formula highlights">
            {carouselCards.map((card, index) => (
              <button
                className={activeCard === index ? "active" : ""}
                type="button"
                aria-label={`Show highlight ${index + 1}`}
                onClick={() => setActiveCard(index)}
                key={card.text}
              />
            ))}
          </div>
        </article>

        <article className="panel panel-community animate-fade-up delay-1100">
          <img src={smallProductImage} alt="TerraElix daily wellness pack" />
          <div>
            <strong>+14K</strong>
            <p>People have already optimized their wellness</p>
          </div>
        </article>
      </section>

      <img
        className="desktop-product animate-scale-in delay-700"
        src={heroProductImage}
        alt="TerraElix plant-based supplement capsules"
      />
    </main>
  );
}
