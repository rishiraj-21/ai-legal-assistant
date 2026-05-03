import { Component, input, signal, OnInit, OnDestroy } from '@angular/core';

@Component({
  selector: 'app-risk-score',
  templateUrl: './risk-score.html',
  styleUrl: './risk-score.css'
})
export class RiskScore implements OnInit, OnDestroy {
  score = input(72);
  value = signal(0);
  private timer?: ReturnType<typeof setTimeout>;

  factors = input<[string, number, string?][]>([]);
  riskLabel = input<string | null>(null);
  riskSummary = input<string | null>(null);
  readonly radius = 90;
  readonly circumference = 2 * Math.PI * 90;

  ngOnInit(): void {
    this.timer = setTimeout(() => this.value.set(this.score()), 200);
  }

  ngOnDestroy(): void {
    if (this.timer) clearTimeout(this.timer);
  }

  get offset(): number {
    return this.circumference - (this.value() / 100) * this.circumference;
  }

  get label(): string {
    const rl = this.riskLabel();
    if (rl) return rl.toUpperCase();
    const s = this.score();
    return s >= 70 ? 'HIGH' : s >= 40 ? 'MEDIUM' : 'LOW';
  }

  get labelColor(): string {
    const s = this.score();
    return s >= 70 ? 'text-destructive' : s >= 40 ? 'text-warning' : 'text-success';
  }
}
