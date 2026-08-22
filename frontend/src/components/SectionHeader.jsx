export default function SectionHeader({ overline, title, description, align = "left", as = "h2" }) {
  const alignClass = align === "center" ? "text-center mx-auto" : "text-left";
  const HeadingTag = as;

  return (
    <div className={`max-w-3xl ${alignClass}`}>
      {overline && <div className="tech-label mb-4" data-testid="section-overline">{overline}</div>}
      <HeadingTag className="font-display text-3xl sm:text-4xl lg:text-5xl text-white tracking-wider leading-[1.05] uppercase">
        {title}
      </HeadingTag>
      {description && (
        <p className="mt-4 sm:mt-6 text-sm sm:text-base text-white/60 leading-relaxed max-w-2xl">
          {description}
        </p>
      )}
    </div>
  );
}
