import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./pages/landing/landing'),
  },
  {
    path: 'signup',
    loadComponent: () => import('./pages/signup/signup'),
  },
  {
    path: 'dashboard',
    loadComponent: () => import('./pages/dashboard/dashboard'),
  },
  {
    path: 'analysis',
    loadComponent: () => import('./pages/analysis/analysis'),
  },
  {
    path: 'consult',
    loadComponent: () => import('./pages/consult/consult'),
  },
  {
    path: '**',
    loadComponent: () => import('./pages/not-found/not-found'),
  },
];
