export interface MLTrainingLog {
  id: string;
  trained_at: string; // ISO datetime string
  sample_count: number;
  category_distribution: Record<string, number>;
  metrics: Record<string, number>;
}
