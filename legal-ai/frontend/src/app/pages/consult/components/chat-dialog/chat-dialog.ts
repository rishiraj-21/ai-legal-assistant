import { Component, input, output, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule, Phone, X, Send } from 'lucide-angular';
import { Lawyer, ChatMessage } from '../../../../core/models/analysis.model';

@Component({
  selector: 'app-chat-dialog',
  imports: [FormsModule, LucideAngularModule],
  templateUrl: './chat-dialog.html',
  styleUrl: './chat-dialog.css'
})
export class ChatDialog {
  lawyer = input.required<Lawyer>();
  closed = output<void>();
  videoRequested = output<void>();

  readonly PhoneIcon = Phone;
  readonly XIcon = X;
  readonly SendIcon = Send;

  messages = signal<ChatMessage[]>([]);
  draft = signal('');

  ngOnInit(): void {
    this.messages.set([
      { from: 'them', text: `Hi, I'm ${this.lawyer().name.split(' ')[0]}. How can I help you today?` }
    ]);
  }

  send(): void {
    if (!this.draft().trim()) return;
    const text = this.draft().trim();
    this.messages.update(m => [...m, { from: 'me', text }]);
    this.draft.set('');
    setTimeout(() => {
      this.messages.update(m => [
        ...m,
        { from: 'them', text: 'Thanks for sharing — could you also send any related documents you have?' }
      ]);
    }, 900);
  }

  onKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Enter') this.send();
  }
}
