import { Component, OnInit, OnDestroy, signal } from '@angular/core';
import { LucideAngularModule, Scale } from 'lucide-angular';
import { ANALYSIS_STEPS } from '../../../core/services/mock-data';

@Component({
  selector: 'app-analysis-loader',
  imports: [LucideAngularModule],
  templateUrl: './analysis-loader.html',
  styleUrl: './analysis-loader.css'
})
export class AnalysisLoader implements OnInit, OnDestroy {
  readonly ScaleIcon = Scale;
  readonly steps = ANALYSIS_STEPS;
  visible = signal(0);
  private timers: ReturnType<typeof setTimeout>[] = [];

  ngOnInit(): void {
    this.timers = this.steps.map((_, i) =>
      setTimeout(() => this.visible.update(v => Math.max(v, i + 1)), i * 600)
    );
  }

  ngOnDestroy(): void {
    this.timers.forEach(clearTimeout);
  }

  isActive(i: number): boolean {
    return i < this.visible();
  }

  isCurrent(i: number): boolean {
    return i === this.visible() - 1;
  }
}
