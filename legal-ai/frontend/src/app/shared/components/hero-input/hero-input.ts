import { Component, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule, Sparkles, ArrowRight } from 'lucide-angular';
import { CASE_TYPES } from '../../../core/services/mock-data';

@Component({
  selector: 'app-hero-input',
  imports: [FormsModule, LucideAngularModule],
  templateUrl: './hero-input.html',
  styleUrl: './hero-input.css'
})
export class HeroInput {
  analyzing = input(false);
  analyze = output<{ issue: string; caseType: string }>();

  readonly SparklesIcon = Sparkles;
  readonly ArrowRightIcon = ArrowRight;
  readonly caseTypes = CASE_TYPES;
  readonly badges = ['Confidential', 'Not legal advice', 'Precedent-aware', 'Built with care'];

  issue = signal('');
  type = signal('Civil');

  onAnalyze(): void {
    if (this.issue().trim()) {
      this.analyze.emit({ issue: this.issue(), caseType: this.type() });
    }
  }
}
