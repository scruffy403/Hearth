interface PlaceholderPageProps {
  title: string;
}

export function PlaceholderPage({ title }: PlaceholderPageProps) {
  return (
    <div>
      <h2>{title}</h2>
      <p style={{ fontFamily: "var(--font-body)", color: "var(--color-text-soft)" }}>
        This page hasn't been built yet.
      </p>
    </div>
  );
}
