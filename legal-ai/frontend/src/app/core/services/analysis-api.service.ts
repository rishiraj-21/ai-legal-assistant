import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { AnalysisApiResponse } from '../models/analysis.model';

@Injectable({ providedIn: 'root' })
export class AnalysisApiService {
  private readonly http = inject(HttpClient);
  submitAnalysis(issue: string, caseType: string): Observable<AnalysisApiResponse> {
    return this.http.post<AnalysisApiResponse>('/api/analysis/submit', {
      issue,
      caseType,
    });
  }
}
