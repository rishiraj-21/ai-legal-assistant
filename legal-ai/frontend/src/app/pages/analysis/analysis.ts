import { Component, inject, signal, computed, OnInit, OnDestroy, AfterViewInit, ElementRef, viewChild, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';
import { Router, RouterLink } from '@angular/router';
import { LucideAngularModule, ArrowLeft, Download, UserPlus } from 'lucide-angular';
import { Navbar } from '../../shared/components/navbar/navbar';
import { AnalysisLoader } from '../../shared/components/analysis-loader/analysis-loader';
import { LegalPathway } from './sections/legal-pathway/legal-pathway';
import { RiskScore } from './sections/risk-score/risk-score';
import { Adversarial } from './sections/adversarial/adversarial';
import { Negotiation } from './sections/negotiation/negotiation';
import { AnalysisService } from '../../core/services/analysis.service';
import { AnalysisApiService } from '../../core/services/analysis-api.service';
import { ToastService } from '../../core/services/toast.service';
import { Section, SectionTab } from '../../core/models/analysis.model';

@Component({
  selector: 'app-analysis',
  imports: [RouterLink, LucideAngularModule, Navbar, AnalysisLoader, LegalPathway, RiskScore, Adversarial, Negotiation],
  templateUrl: './analysis.html',
  styleUrl: './analysis.css'
})
export default class Analysis implements OnInit, OnDestroy, AfterViewInit {
  private router = inject(Router);
  private analysisService = inject(AnalysisService);
  private analysisApiService = inject(AnalysisApiService);
  private toastService = inject(ToastService);
  private platformId = inject(PLATFORM_ID);

  readonly ArrowLeftIcon = ArrowLeft;
  readonly DownloadIcon = Download;
  readonly UserPlusIcon = UserPlus;

  readonly sections: SectionTab[] = [
    { id: 'pathway', label: 'Legal Pathway' },
    { id: 'risk', label: 'Risk Score' },
    { id: 'adversarial', label: 'Adversarial' },
    { id: 'settlement', label: 'Settlement' },
  ];

  loading = signal(true);
  active = signal<Section>('pathway');

  pathwayRef = viewChild<ElementRef>('pathwaySection');
  riskRef = viewChild<ElementRef>('riskSection');
  adversarialRef = viewChild<ElementRef>('adversarialSection');
  settlementRef = viewChild<ElementRef>('settlementSection');

  private observer?: IntersectionObserver;
  private apiSub?: { unsubscribe(): void };

  riskScore = computed(() => this.analysisService.result()?.riskScore ?? 72);

  riskSummary = computed(() => this.analysisService.result()?.riskSummary ?? null);

  riskFactors = computed<[string, number, string?][]>(() => {
    const result = this.analysisService.result();
    // Prefer detailed factors from AI (includes explanation)
    if (result?.detailedFactors?.length) {
      return result.detailedFactors.map(f => [f.label, f.value, f.explanation] as [string, number, string?]);
    }
    // Fallback to legacy riskFactors format
    if (result?.riskFactors?.length) {
      return result.riskFactors.map(f => {
        const [label, value] = f.split(':');
        return [label, parseInt(value, 10), undefined] as [string, number, string?];
      });
    }
    return [];
  });

  riskLabel = computed(() => this.analysisService.result()?.riskLabel ?? null);

  get issue(): string {
    return this.analysisService.state()?.issue ?? 'Untitled case';
  }

  get caseType(): string {
    return this.analysisService.state()?.type ?? 'Civil';
  }

  get dateString(): string {
    return new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
  }

  readonly currentYear = new Date().getFullYear();

  ngOnInit(): void {
    const state = this.analysisService.state();
    if (!state) {
      this.router.navigate(['/dashboard']);
      return;
    }

    const startTime = Date.now();

    this.apiSub = this.analysisApiService.submitAnalysis(state.issue, state.type).subscribe({
      next: (res) => {
        this.analysisService.setResult(res.analysis);
        const elapsed = Date.now() - startTime;
        const remaining = Math.max(1500 - elapsed, 0);
        setTimeout(() => this.loading.set(false), remaining);
      },
      error: () => {
        this.toastService.error('Analysis failed', 'Using default analysis data.');
        const elapsed = Date.now() - startTime;
        const remaining = Math.max(1500 - elapsed, 0);
        setTimeout(() => this.loading.set(false), remaining);
      },
    });
  }

  ngAfterViewInit(): void {
    if (!isPlatformBrowser(this.platformId)) return;
    const check = setInterval(() => {
      if (!this.loading()) {
        clearInterval(check);
        setTimeout(() => this.setupScrollSpy(), 100);
      }
    }, 200);
  }

  ngOnDestroy(): void {
    this.apiSub?.unsubscribe();
    this.observer?.disconnect();
  }

  private setupScrollSpy(): void {
    this.observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter(e => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) {
          const section = visible.target.getAttribute('data-section') as Section;
          if (section) this.active.set(section);
        }
      },
      { rootMargin: '-30% 0px -55% 0px', threshold: [0.1, 0.5, 1] }
    );

    const refs = [this.pathwayRef(), this.riskRef(), this.adversarialRef(), this.settlementRef()];
    refs.forEach(ref => {
      if (ref?.nativeElement) this.observer!.observe(ref.nativeElement);
    });
  }

  scrollTo(id: Section): void {
    const refMap: Record<Section, ReturnType<typeof this.pathwayRef>> = {
      pathway: this.pathwayRef(),
      risk: this.riskRef(),
      adversarial: this.adversarialRef(),
      settlement: this.settlementRef(),
    };
    refMap[id]?.nativeElement?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  goBack(): void {
    this.router.navigate(['/dashboard']);
  }
}
