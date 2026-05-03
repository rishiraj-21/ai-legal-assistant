import { Component, computed, inject } from '@angular/core';
import { LucideAngularModule, Check } from 'lucide-angular';
import { AnalysisService } from '../../../../core/services/analysis.service';

@Component({
  selector: 'app-negotiation',
  imports: [LucideAngularModule],
  templateUrl: './negotiation.html',
  styleUrl: './negotiation.css'
})
export class Negotiation {
  private analysisService = inject(AnalysisService);

  readonly CheckIcon = Check;

  readonly yourPos = computed(() => {
    const points = this.analysisService.result()?.advocatePoints;
    return points?.slice(0, 3) ?? [];
  });

  readonly oppPos = computed(() => {
    const points = this.analysisService.result()?.opponentPoints;
    return points?.slice(0, 3) ?? [];
  });

  readonly settlementProbability = computed(() =>
    this.analysisService.result()?.settlementProbability ?? 0
  );

  readonly recommendation = computed(() =>
    this.analysisService.result()?.settlementRecommendation ?? null
  );

  readonly reasoning = computed(() =>
    this.analysisService.result()?.settlementReasoning ?? null
  );
}
