import { useQuery } from "@tanstack/react-query";
import { mlApi } from "../api/ml";
import "./MLHealthCard.css";

function formatTrainedAt(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function formatNumber(n: number): string {
  return new Intl.NumberFormat("en-GB").format(n);
}

export function MLHealthCard() {
  const { data: logs, isLoading } = useQuery({
    queryKey: ["ml", "training-log"],
    queryFn: () => mlApi.trainingLog(),
    staleTime: 5 * 60_000, // 5 minutes — training log doesn't change often
  });

  const latest = logs?.[0];

  if (isLoading || !latest) return null;

  return (
    <div className="ml-health-card">
      <div className="ml-health-card__header">
        <span className="ml-health-card__label font-display">
          Categorisation model
        </span>
        <span className="ml-health-card__indicator" aria-hidden="true" />
      </div>
      <p className="ml-health-card__summary">
        Last trained{" "}
        <strong>{formatTrainedAt(latest.trained_at)}</strong> on{" "}
        <strong>{formatNumber(latest.sample_count)}</strong> transactions
        across {Object.keys(latest.category_distribution).length} categories.
      </p>
    </div>
  );
}
