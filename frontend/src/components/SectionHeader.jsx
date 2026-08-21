export default function SectionHeader({ overline, title, description, align = "left" }) {
  const alignClass = align === "center" ? "text-center mx-auto" : "text-left";
  return (
    <div className={`max-w-3xl ${alignClass}`}>
      {overline && <div className="tech-label mb-4" data-testid="section-overline">{overline}</div>}
      <h2 className="font-display text-4xl sm:text-5xl lg:text-6xl text-white tracking-wider leading-[1.05] uppercase">
        {title}
      </h2>
      {description && (
        <p className="mt-6 text-base sm:text-lg text-white/60 leading-relaxed max-w-2xl">
          {description}
        </p>
      )}
    </div>
  );
}
