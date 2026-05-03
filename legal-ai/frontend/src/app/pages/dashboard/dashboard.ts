import { Component, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Navbar } from '../../shared/components/navbar/navbar';
import { HeroInput } from '../../shared/components/hero-input/hero-input';
import { AnalysisService } from '../../core/services/analysis.service';

@Component({
  selector: 'app-dashboard',
  imports: [Navbar, HeroInput],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export default class Dashboard {
  private router = inject(Router);
  private analysisService = inject(AnalysisService);

  analyzing = signal(false);
  readonly currentYear = new Date().getFullYear();

  handleAnalyze(event: { issue: string; caseType: string }): void {
    this.analyzing.set(true);
    this.analysisService.setAnalysis(event.issue, event.caseType);
    setTimeout(() => {
      this.router.navigate(['/analysis']);
    }, 250);
  }
}
