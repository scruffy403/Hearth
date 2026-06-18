import { Link, useParams } from "react-router-dom";
import { useCategoryTrends, useCategoryMerchants } from "./useCategoriesData";
import { CategoryTrendBars } from "../components/CategoryTrendBars";
import { formatCurrency } from "../lib/format";
import "./CategoryDetailPage.css";

export function CategoryDetailPage() {
  const { categoryName } = useParams<{ categoryName: string }>();
  const category = categoryName ? decodeURIComponent(categoryName) : "";

  const { data: trends, isLoading: trendsLoading } = useCategoryTrends(category);
  const { data: merchants, isLoading: merchantsLoading } = useCategoryMerchants(category);

  return (
    <div className="category-detail-page">
      <Link to="/categories" className="category-detail-page__back">
        &larr; All categories
      </Link>

      <h2 className="font-display">{category}</h2>

      <section className="category-detail-section">
        <h3>Last six months</h3>
        <div className="ledger">
          {trendsLoading && <p className="category-detail-empty">Loading trend&hellip;</p>}
          {!trendsLoading && trends?.length === 0 && (
            <p className="category-detail-empty">No history yet for this category.</p>
          )}
          {trends && trends.length > 0 && <CategoryTrendBars data={trends} />}
        </div>
      </section>

      <section className="category-detail-section">
        <h3>Where it goes</h3>
        <p className="category-detail-section__caption">Last six months</p>
        <div className="ledger">
          {merchantsLoading && <p className="category-detail-empty">Loading merchants&hellip;</p>}
          {!merchantsLoading && merchants?.length === 0 && (
            <p className="category-detail-empty">No merchants recorded yet.</p>
          )}
          {merchants?.map((merchant) => (
            <Link
              key={merchant.merchant}
              to={`/transactions?range=last_6_months&category=${encodeURIComponent(
                category
              )}&merchant=${encodeURIComponent(merchant.merchant)}`}
              className="category-merchant-row"
            >
              <div className="category-merchant-row__main">
                <span className="category-merchant-row__label font-display">
                  {merchant.merchant}
                </span>
                <span className="category-merchant-row__meta">
                  {merchant.transaction_count} transaction
                  {merchant.transaction_count === 1 ? "" : "s"}
                </span>
              </div>
              <span className="category-merchant-row__amount numeral">
                {formatCurrency(merchant.total)}
              </span>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
