import { Injectable, signal } from '@angular/core';

export interface Toast {
  id: number;
  message: string;
  description?: string;
  type: 'success' | 'info' | 'error';
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  private nextId = 0;
  readonly toasts = signal<Toast[]>([]);

  success(message: string, description?: string): void {
    this.add({ message, description, type: 'success' });
  }

  info(message: string, description?: string): void {
    this.add({ message, description, type: 'info' });
  }

  error(message: string, description?: string): void {
    this.add({ message, description, type: 'error' });
  }

  private add(t: Omit<Toast, 'id'>): void {
    const id = this.nextId++;
    this.toasts.update(list => [...list, { ...t, id }]);
    setTimeout(() => this.dismiss(id), 4000);
  }

  dismiss(id: number): void {
    this.toasts.update(list => list.filter(t => t.id !== id));
  }
}
