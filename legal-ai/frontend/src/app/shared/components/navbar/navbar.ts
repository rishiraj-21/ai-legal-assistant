import { Component, inject } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { LucideAngularModule, Scale } from 'lucide-angular';

@Component({
  selector: 'app-navbar',
  imports: [RouterLink, LucideAngularModule],
  templateUrl: './navbar.html',
  styleUrl: './navbar.css'
})
export class Navbar {
  private router = inject(Router);
  readonly ScaleIcon = Scale;

  get isLanding(): boolean {
    return this.router.url === '/' || this.router.url === '';
  }
}
