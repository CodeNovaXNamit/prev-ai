export function Card({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`glass-panel rounded-[28px] ${className}`}>{children}</div>
  );
}
