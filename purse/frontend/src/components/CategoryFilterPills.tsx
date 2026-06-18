import "./CategoryFilterPills.css";

interface CategoryFilterPillsProps {
  categories: string[];
  selected: string[];
  onToggle: (category: string) => void;
  onClear: () => void;
}

export function CategoryFilterPills({
  categories,
  selected,
  onToggle,
  onClear,
}: CategoryFilterPillsProps) {
  return (
    <div className="category-pills" role="group" aria-label="Filter by category">
      {categories.map((category) => {
        const isActive = selected.includes(category);
        return (
          <button
            key={category}
            type="button"
            className={isActive ? "category-pill category-pill--active" : "category-pill"}
            onClick={() => onToggle(category)}
            aria-pressed={isActive}
          >
            {category}
          </button>
        );
      })}
      {selected.length > 0 && (
        <button type="button" className="category-pill category-pill--clear" onClick={onClear}>
          Clear filters
        </button>
      )}
    </div>
  );
}
