import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppLayout } from "./layouts/AppLayout";
import { OverviewPage } from "./pages/OverviewPage";
import { TransactionsPage } from "./pages/TransactionsPage";
import { CategoriesListPage } from "./pages/CategoriesListPage";
import { CategoryDetailPage } from "./pages/CategoryDetailPage";
import { BudgetsPage } from "./pages/BudgetsPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<OverviewPage />} />
          <Route path="/transactions" element={<TransactionsPage />} />
          <Route path="/categories" element={<CategoriesListPage />} />
          <Route path="/categories/:categoryName" element={<CategoryDetailPage />} />
          <Route path="/budgets" element={<BudgetsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
