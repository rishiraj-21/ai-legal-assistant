import { Component, computed, inject } from '@angular/core';
import { LucideAngularModule, FileText, ShieldCheck, Scale, Handshake, Gavel } from 'lucide-angular';
import { AnalysisService } from '../../../../core/services/analysis.service';

@Component({
  selector: 'app-legal-pathway',
  imports: [LucideAngularModule],
  templateUrl: './legal-pathway.html',
  styleUrl: './legal-pathway.css'
})
export class LegalPathway {
  private analysisService = inject(AnalysisService);

  readonly FileTextIcon = FileText;
  readonly documents = computed(() => this.analysisService.result()?.documents ?? []);

  readonly iconMap: Record<string, any> = {
    'file-text': FileText,
    'shield-check': ShieldCheck,
    'scale': Scale,
    'handshake': Handshake,
    'gavel': Gavel,
  };

  private readonly defaultIcons = ['file-text', 'shield-check', 'scale', 'handshake', 'gavel', 'file-text'];

  steps = computed(() => {
    const result = this.analysisService.result();
    if (result?.steps?.length) {
      return result.steps.map((s, i) => ({
        icon: this.defaultIcons[i % this.defaultIcons.length],
        title: s.title,
        detail: s.detail,
      }));
    }
    return [];
  });

  getIcon(name: string) {
    return this.iconMap[name] || FileText;
  }
}
