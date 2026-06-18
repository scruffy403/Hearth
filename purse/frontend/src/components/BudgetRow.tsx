import { useState } from "react";
import type { BudgetRowData } from "../pages/useBudgetsData";
import { formatCurrency } from "../lib/format";
import "./BudgetRow.css";

interface BudgetRowProps {
  row: BudgetRowData;
  onSave: (monthlyAmount: number) => void;
  isSaving: boolean;
}

export function BudgetRow({ row, onSave, isSaving }: BudgetRowProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [draftAmount, setDraftAmount] = useState(
    row.hasBudget ? String(row.budgeted) : ""
  );

  const isOverBudget = row.hasBudget && row.actual > row.budgeted;

  // Percentage of the bar that represents "within budget" vs "over budget".
  // Capped visually at 100% within-budget fill; overage renders as its
  // own ember segment past that point rather than stretching the bar.
  const withinBudgetPct = row.hasBudget
    ? Math.min((row.actual / row.budgeted) * 100, 100)
    : 0;
  const overagePct = isOverBudget
    ? Math.min(((row.actual - row.budgeted) / row.budgeted) * 100, 100)
    : 0;

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const parsed = parseFloat(draftAmount);
    if (!isNaN(parsed) && parsed > 0) {
      onSave(parsed);
      setIsEditing(false);
    }
  }

  function handleBlur(e: React.FocusEvent<HTMLInputElement>) {
    // Only close on blur if focus is moving outside the form entirely.
    // Without this check, clicking the Save button blurs the input first,
    // which closed the editor (and unmounted the form) before the click's
    // own submit event could fire — so Save silently did nothing.
    const form = e.currentTarget.closest("form");
    if (form && e.relatedTarget && form.contains(e.relatedTarget as Node)) {
      return;
    }
    setIsEditing(false);
  }

  return (
    <div className="budget-row">
      <div className="budget-row__top">
        <span className="budget-row__label font-display">{row.category}</span>

        {isEditing ? (
          <form className="budget-row__edit-form" onSubmit={handleSubmit}>
            <span className="budget-row__currency-prefix">£</span>
            <input
              type="number"
              step="0.01"
              min="0"
              autoFocus
              value={draftAmount}
              onChange={(e) => setDraftAmount(e.target.value)}
              onBlur={handleBlur}
              disabled={isSaving}
              className="budget-row__input"
            />
            <button type="submit" className="budget-row__save">
              Save
            </button>
          </form>
        ) : row.hasBudget ? (
          <button
            type="button"
            className="budget-row__amount-button"
            onClick={() => setIsEditing(true)}
          >
            <span className="numeral">{formatCurrency(row.actual)}</span>
            <span className="budget-row__of"> of {formatCurrency(row.budgeted)}</span>
          </button>
        ) : (
          <button
            type="button"
            className="budget-row__add-budget"
            onClick={() => setIsEditing(true)}
          >
            Add a budget
          </button>
        )}
      </div>

      {row.hasBudget ? (
        <div className="budget-row__track" role="presentation">
          <div
            className="budget-row__fill budget-row__fill--within"
            style={{ width: `${withinBudgetPct}%` }}
          />
          {isOverBudget && (
            <div
              className="budget-row__fill budget-row__fill--over"
              style={{ width: `${overagePct}%` }}
            />
          )}
        </div>
      ) : row.actual > 0 ? (
        <p className="budget-row__unbudgeted-note">
          {formatCurrency(row.actual)} spent this month with no budget set.
        </p>
      ) : null}
    </div>
  );
}
