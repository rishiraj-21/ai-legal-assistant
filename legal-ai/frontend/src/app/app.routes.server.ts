import { RenderMode, ServerRoute } from '@angular/ssr';

export const serverRoutes: ServerRoute[] = [
  {
    path: '',
    renderMode: RenderMode.Prerender,
  },
  {
    path: 'signup',
    renderMode: RenderMode.Client,
  },
  {
    path: 'dashboard',
    renderMode: RenderMode.Client,
  },
  {
    path: 'analysis',
    renderMode: RenderMode.Client,
  },
  {
    path: 'consult',
    renderMode: RenderMode.Client,
  },
  {
    path: '**',
    renderMode: RenderMode.Client,
  },
];
