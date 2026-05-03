import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule, Scale, ArrowRight, Mail, Lock, User } from 'lucide-angular';

@Component({
  selector: 'app-signup',
  imports: [RouterLink, FormsModule, LucideAngularModule],
  templateUrl: './signup.html',
  styleUrl: './signup.css'
})
export default class Signup {
  private router = inject(Router);

  readonly ScaleIcon = Scale;
  readonly ArrowRightIcon = ArrowRight;
  readonly MailIcon = Mail;
  readonly LockIcon = Lock;
  readonly UserIcon = User;

  form = signal({ name: '', email: '', password: '' });
  loading = signal(false);
  readonly currentYear = new Date().getFullYear();

  onSubmit(): void {
    this.loading.set(true);
    setTimeout(() => {
      try {
        localStorage.setItem('lex_user', JSON.stringify({
          name: this.form().name,
          email: this.form().email
        }));
      } catch {}
      this.router.navigate(['/dashboard']);
    }, 700);
  }

  updateField(field: 'name' | 'email' | 'password', value: string): void {
    this.form.update(f => ({ ...f, [field]: value }));
  }
}
