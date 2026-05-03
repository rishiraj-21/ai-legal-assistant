import { Injectable, signal } from '@angular/core';
import { AnalysisApiResponse, AnalysisState } from '../models/analysis.model';

@Injectable({ providedIn: 'root' })
export class AnalysisService {
  private readonly _state = signal<AnalysisState | null>(null);
  private readonly _result = signal<AnalysisApiResponse['analysis'] | null>(null);

  readonly state = this._state.asReadonly();
  readonly result = this._result.asReadonly();

  setAnalysis(issue: string, type: string): void {
    this._state.set({ issue, type });
  }

  setResult(data: AnalysisApiResponse['analysis']): void {
    this._result.set(data);
  }

  clear(): void {
    this._state.set(null);
    this._result.set(null);
  }
}
