import { Component, inject, signal, computed } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule, MessageCircle, Video, Star, BadgeCheck, Clock, Search, Sparkles } from 'lucide-angular';
import { Navbar } from '../../shared/components/navbar/navbar';
import { ChatDialog } from './components/chat-dialog/chat-dialog';
import { ToastService } from '../../core/services/toast.service';
import { LAWYERS, CONSULT_FILTERS } from '../../core/services/mock-data';
import { Lawyer, ConsultMode } from '../../core/models/analysis.model';

@Component({
  selector: 'app-consult',
  imports: [FormsModule, LucideAngularModule, Navbar, ChatDialog],
  templateUrl: './consult.html',
  styleUrl: './consult.css'
})
export default class Consult {
  private toastService = inject(ToastService);

  readonly MessageCircleIcon = MessageCircle;
  readonly VideoIcon = Video;
  readonly StarIcon = Star;
  readonly BadgeCheckIcon = BadgeCheck;
  readonly ClockIcon = Clock;
  readonly SearchIcon = Search;
  readonly SparklesIcon = Sparkles;

  readonly filters = CONSULT_FILTERS;

  mode = signal<ConsultMode>('chat');
  query = signal('');
  filter = signal('All');
  chatWith = signal<Lawyer | null>(null);

  filtered = computed(() => {
    return LAWYERS.filter(l => {
      const matchesFilter = this.filter() === 'All' || l.spec.toLowerCase().includes(this.filter().toLowerCase());
      const q = this.query().trim().toLowerCase();
      const matchesQuery = !q || l.name.toLowerCase().includes(q) || l.spec.toLowerCase().includes(q);
      return matchesFilter && matchesQuery;
    });
  });

  openChat(l: Lawyer): void {
    this.chatWith.set(l);
  }

  startVideo(name: string): void {
    this.toastService.success(`Video call request sent to ${name}`, 'Connecting shortly\u2026');
  }

  onAction(l: Lawyer): void {
    if (this.mode() === 'chat') {
      this.openChat(l);
    } else {
      this.startVideo(l.name);
    }
  }

  closeChat(): void {
    this.chatWith.set(null);
  }

  onVideoFromChat(): void {
    this.toastService.info('Switching to video\u2026');
  }
}
