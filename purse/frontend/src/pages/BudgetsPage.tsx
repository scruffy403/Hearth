import { useBudgetRows, useUpsertBudget } from "./useBudgetsData";
import { BudgetRow } from "../components/BudgetRow";
import "./BudgetsPage.css";

export function BudgetsPage() {
  const { rows, isLoading } = useBudgetRows();
  const upsertBudget = useUpsertBudget();

  return (
    <div className="budgets-page">
      <h2>Budgets</h2>
      <p className="budgets-page__subtitle">
        This month's spend against what you've budgeted. Categories without
        a budget yet still show what's been spent.
      </p>

      <div className="ledger">
        {isLoading && <p className="budgets-empty">Loading budgets&hellip;</p>}

        {!isLoading && rows.length === 0 && (
          <p className="budgets-empty">No categories found.</p>
        )}

        {rows.map((row) => (
          <BudgetRow
            key={row.category}
            row={row}
            isSaving={upsertBudget.isPending}
            onSave={(monthlyAmount) =>
              upsertBudget.mutate({ category: row.category, monthlyAmount })
            }
          />
        ))}
      </div>
    </div>
  );
}
