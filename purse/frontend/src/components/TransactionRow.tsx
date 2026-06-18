import { useState } from "react";
import type { Transaction } from "../types/transaction";
import { formatCurrencySigned, formatDateShort } from "../lib/format";
import "./TransactionRow.css";

interface TransactionRowProps {
  transaction: Transaction;
  categories: string[];
  onUpdateCategory: (category: string, saveAsMerchantRule: boolean) => void;
  isUpdating: boolean;
}

export function TransactionRow({
  transaction,
  categories,
  onUpdateCategory,
  isUpdating,
}: TransactionRowProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [saveAsRule, setSaveAsRule] = useState(true);

  const isIncome = transaction.amount > 0;
  const amountClass = isIncome
    ? "transaction-row__amount--income"
    : "transaction-row__amount--expense";

  const isLowConfidence =
    transaction.category_source === "ml" &&
    transaction.ml_confidence !== null &&
    transaction.ml_confidence < 0.6;

  function handleSelect(category: string) {
    onUpdateCategory(category, saveAsRule);
    setIsEditing(false);
  }

  return (
    <div className="transaction-row">
      <div className="transaction-row__main">
        <span className="transaction-row__label font-display">
          {transaction.merchant_clean ?? transaction.merchant_raw}
        </span>
        <span className="transaction-row__meta">
          {formatDateShort(transaction.date)}
          {transaction.notes && ` · ${transaction.notes}`}
        </span>
      </div>

      <div className="transaction-row__category">
        {isEditing ? (
          <div className="transaction-row__editor">
            <select
              className="transaction-row__select"
              autoFocus
              defaultValue=""
              onChange={(e) => {
                if (e.target.value) handleSelect(e.target.value);
              }}
              onBlur={() => setIsEditing(false)}
              disabled={isUpdating}
            >
              <option value="" disabled>
                Choose category&hellip;
              </option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
            <label className="transaction-row__rule-toggle">
              <input
                type="checkbox"
                checked={saveAsRule}
                onChange={(e) => setSaveAsRule(e.target.checked)}
              />
              Remember for this merchant
            </label>
          </div>
        ) : (
          <button
            type="button"
            className={
              isLowConfidence
                ? "transaction-row__category-button transaction-row__category-button--low-confidence"
                : "transaction-row__category-button"
            }
            onClick={() => setIsEditing(true)}
            title="Click to change category"
          >
            {transaction.category_dashboard ?? "Uncategorised"}
            {isLowConfidence && <span className="transaction-row__flag">needs review</span>}
          </button>
        )}
      </div>

      <span className={`transaction-row__amount numeral ${amountClass}`}>
        {formatCurrencySigned(transaction.amount)}
      </span>
    </div>
  );
}
