import "./LedgerRow.css";
import { formatCurrencySigned } from "../lib/format";

interface LedgerRowProps {
  label: string;
  amount: number;
  meta?: string;
  isIncome?: boolean;
  budgetTotal?: number;
}

export function LedgerRow({ label, amount, meta, isIncome, budgetTotal }: LedgerRowProps) {
  const signedAmount = isIncome ? Math.abs(amount) : -Math.abs(amount);
  const amountClass = signedAmount < 0 ? "ledger-row__amount--expense" : "ledger-row__amount--income";

  const overBudget = budgetTotal !== undefined && Math.abs(amount) > budgetTotal;

  return (
    <div className="ledger-row">
      <div className="ledger-row__main">
        <span className="ledger-row__label font-display">{label}</span>
        {meta && <span className="ledger-row__meta">{meta}</span>}
      </div>
      <div className="ledger-row__figures">
        {budgetTotal !== undefined && (
          <span
            className={
              overBudget
                ? "ledger-row__budget ledger-row__budget--over"
                : "ledger-row__budget"
            }
          >
            of {formatCurrencySigned(budgetTotal).replace("+", "")}
          </span>
        )}
        <span className={`ledger-row__amount numeral ${amountClass}`}>
          {formatCurrencySigned(signedAmount)}
        </span>
      </div>
    </div>
  );
}
