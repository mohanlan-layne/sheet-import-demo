export interface Suggestion {
  id: string;
  label: string;
  value: string;
  description?: string;
}

export interface SubmitResult {
  success: boolean;
  message?: string;
}
