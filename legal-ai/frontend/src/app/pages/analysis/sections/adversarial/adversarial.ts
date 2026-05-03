import { Component, computed, inject } from '@angular/core';
import { LucideAngularModule, Shield, Swords, AlertTriangle } from 'lucide-angular';
import { AnalysisService } from '../../../../core/services/analysis.service';

@Component({
  selector: 'app-adversarial',
  imports: [LucideAngularModule],
  templateUrl: './adversarial.html',
  styleUrl: './adversarial.css'
})
export class Adversarial {
  private analysisService = inject(AnalysisService);

  readonly ShieldIcon = Shield;
  readonly SwordsIcon = Swords;
  readonly AlertTriangleIcon = AlertTriangle;

  readonly advocatePoints = computed(() => this.analysisService.result()?.advocatePoints ?? []);
  readonly opponentPoints = computed(() => this.analysisService.result()?.opponentPoints ?? []);
  readonly vulnerabilities = computed(() => this.analysisService.result()?.vulnerabilities ?? []);
  readonly advocateConfidence = computed(() => this.analysisService.result()?.advocateConfidence ?? 50);
  readonly opponentConfidence = computed(() => this.analysisService.result()?.opponentConfidence ?? 50);

  readonly advocatePct = computed(() => {
    const a = this.advocateConfidence();
    const o = this.opponentConfidence();
    const total = a + o;
    return total > 0 ? Math.round((a / total) * 100) : 50;
  });

  readonly opponentPct = computed(() => 100 - this.advocatePct());
}
