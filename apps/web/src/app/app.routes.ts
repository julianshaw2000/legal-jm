import { Route } from '@angular/router';

export const appRoutes: Route[] = [
  { path: '', loadComponent: () => import('./features/home/home.component').then(m => m.HomeComponent) },
  { path: 'browse', loadComponent: () => import('./features/browse/browse.component').then(m => m.BrowseComponent) },
  { path: 'document/:id', loadComponent: () => import('./features/document/document.component').then(m => m.DocumentComponent) },
  { path: 'ask', loadComponent: () => import('./features/ask/ask.component').then(m => m.AskComponent) },
  { path: 'ingest', loadComponent: () => import('./features/ingest/ingest.component').then(m => m.IngestComponent) },
  { path: 'admin/users', loadComponent: () => import('./features/admin-users/admin-users.component').then(m => m.AdminUsersComponent) },
  { path: '**', redirectTo: '' }
];
