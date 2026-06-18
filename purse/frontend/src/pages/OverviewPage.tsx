import { useCurrentMonthSummary, useRecentTransactions, useBudgetsVsActual } from "./useOverviewData";
import { formatCurrency, formatDateShort, formatMonthName } from "../lib/format";
import { LedgerRow } from "../components/LedgerRow";
import "./OverviewPage.css";

function buildSummarySentence(
  total: number,
  topCategories: { category: string; total: number }[]
): string {
  if (total === 0) {
    return "Nothing recorded yet this month.";
  }

  const month = formatMonthName();
  const top = topCategories.slice(0, 2).map((c) => c.category);

  if (top.length === 0) {
    return `You've spent ${formatCurrency(total)} so far in ${month}.`;
  }

  if (top.length === 1) {
    return `You've spent ${formatCurrency(total)} so far in ${month}, mostly on ${top[0]}.`;
  }

  return `You've spent ${formatCurrency(total)} so far in ${month}, mostly on ${top[0]} and ${top[1]}.`;
}

export function OverviewPage() {
  const { data: summary, isLoading: summaryLoading } = useCurrentMonthSummary();
  const { data: recentTransactions, isLoading: transactionsLoading } = useRecentTransactions();
  const { data: budgetsVsActual } = useBudgetsVsActual();

  const totalSpend = summary?.reduce((sum, c) => sum + c.total, 0) ?? 0;
  const sortedByTotal = [...(summary ?? [])].sort((a, b) => b.total - a.total);

  return (
    <div className="overview-page">
      <section className="overview-hero">
        {summaryLoading ? (
          <p className="overview-hero__sentence overview-hero__sentence--loading">
            Tallying the month&hellip;
          </p>
        ) : (
          <p className="overview-hero__sentence">
            {buildSummarySentence(totalSpend, sortedByTotal)}
          </p>
        )}
      </section>

      <section className="overview-section">
        <h2 className="overview-section__heading">This month, by category</h2>
        <div className="ledger">
          {sortedByTotal.length === 0 && !summaryLoading && (
            <p className="overview-empty">
              No spending recorded for this month yet — it'll appear here as
              transactions sync in.
            </p>
          )}
          {sortedByTotal.map((category) => {
            const budget = budgetsVsActual?.find(
              (b) => b.category === category.category
            );
            return (
              <LedgerRow
                key={category.category}
                label={category.category}
                amount={category.total}
                meta={`${category.transaction_count} transaction${
                  category.transaction_count === 1 ? "" : "s"
                }`}
                budgetTotal={budget?.budgeted}
              />
            );
          })}
        </div>
      </section>

      <section className="overview-section">
        <h2 className="overview-section__heading">Recent transactions</h2>
        <div className="ledger">
          {transactionsLoading && <p>Loading recent transactions&hellip;</p>}
          {recentTransactions?.map((tx) => (
            <LedgerRow
              key={tx.id}
              label={tx.merchant_clean ?? tx.merchant_raw}
              amount={tx.amount}
              meta={`${formatDateShort(tx.date)} · ${tx.category_dashboard ?? "Uncategorised"}`}
              isIncome={tx.amount > 0}
            />
          ))}
          {recentTransactions?.length === 0 && (
            <p className="overview-empty">
              No transactions yet. Once your YNAB sync runs, they'll show up
              here.
            </p>
          )}
        </div>
      </section>
    </div>
  );
}
