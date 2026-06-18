import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import {
  useTransactionsList,
  useAllCategories,
  useUpdateTransactionCategory,
  type DateRangeFilter,
} from "./useTransactionsData";
import { CategoryFilterPills } from "../components/CategoryFilterPills";
import { DateRangeSelector } from "../components/DateRangeSelector";
import { TransactionRow } from "../components/TransactionRow";
import "./TransactionsPage.css";

const VALID_RANGES: DateRangeFilter[] = [
  "this_month",
  "last_month",
  "last_30_days",
  "last_6_months",
  "all",
];

export function TransactionsPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  // Initial state can be seeded via URL params, e.g. arriving from a
  // Categories merchant drill-down link:
  // /transactions?category=Eating+Out&merchant=Costa+Coffee&range=last_6_months
  const initialRange = searchParams.get("range");
  const initialCategory = searchParams.get("category");
  const initialMerchant = searchParams.get("merchant");

  const [dateRange, setDateRange] = useState<DateRangeFilter>(
    VALID_RANGES.includes(initialRange as DateRangeFilter)
      ? (initialRange as DateRangeFilter)
      : "this_month"
  );
  const [selectedCategories, setSelectedCategories] = useState<string[]>(
    initialCategory ? [initialCategory] : []
  );
  const [lowConfidenceOnly, setLowConfidenceOnly] = useState(false);
  const [merchantFilter, setMerchantFilter] = useState<string | undefined>(
    initialMerchant ?? undefined
  );

  const { data: categories } = useAllCategories();
  const { data: transactions, isLoading } = useTransactionsList({
    dateRange,
    categories: selectedCategories,
    lowConfidenceOnly,
    merchant: merchantFilter,
  });
  const updateCategory = useUpdateTransactionCategory();

  function toggleCategory(category: string) {
    setSelectedCategories((prev) =>
      prev.includes(category) ? prev.filter((c) => c !== category) : [...prev, category]
    );
  }

  function clearMerchantFilter() {
    setMerchantFilter(undefined);
    searchParams.delete("merchant");
    setSearchParams(searchParams);
  }

  return (
    <div className="transactions-page">
      <h2>Transactions</h2>

      {merchantFilter && (
        <div className="merchant-filter-banner">
          Showing only <strong>{merchantFilter}</strong>
          <button type="button" onClick={clearMerchantFilter}>
            Clear
          </button>
        </div>
      )}

      <div className="transactions-filters">
        <DateRangeSelector value={dateRange} onChange={setDateRange} />

        {categories && categories.length > 0 && (
          <CategoryFilterPills
            categories={categories}
            selected={selectedCategories}
            onToggle={toggleCategory}
            onClear={() => setSelectedCategories([])}
          />
        )}

        <button
          type="button"
          className={
            lowConfidenceOnly
              ? "transactions-review-toggle transactions-review-toggle--active"
              : "transactions-review-toggle"
          }
          onClick={() => setLowConfidenceOnly((prev) => !prev)}
        >
          {lowConfidenceOnly ? "Showing items needing review" : "Show items needing review"}
        </button>
      </div>

      <div className="ledger">
        {isLoading && <p className="transactions-empty">Loading transactions&hellip;</p>}

        {!isLoading && transactions?.length === 0 && (
          <p className="transactions-empty">
            {lowConfidenceOnly
              ? "Nothing needs review right now — every transaction has a confident category."
              : "No transactions match these filters."}
          </p>
        )}

        {transactions?.map((tx) => (
          <TransactionRow
            key={tx.id}
            transaction={tx}
            categories={categories ?? []}
            isUpdating={updateCategory.isPending}
            onUpdateCategory={(category, saveAsMerchantRule) =>
              updateCategory.mutate({
                id: tx.id,
                payload: { category, save_as_merchant_rule: saveAsMerchantRule },
              })
            }
          />
        ))}
      </div>
    </div>
  );
}
