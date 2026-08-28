import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'teoria-colas', pathMatch: 'full' },
  {
    path: 'teoria-colas',
    loadComponent: () =>
      import('./pages/teoria-colas/teoria-colas.component').then((m) => m.TeoriaColasComponent),
  },
  {
    path: 'montecarlo',
    loadComponent: () =>
      import('./pages/montecarlo/montecarlo.component').then((m) => m.MontecarloComponent),
  },
  {
    path: 'markov',
    loadComponent: () => import('./pages/markov/markov.component').then((m) => m.MarkovComponent),
  },
  {
    path: 'pronostico',
    loadComponent: () =>
      import('./pages/pronostico/pronostico.component').then((m) => m.PronosticoComponent),
  },
  {
    path: 'asignacion',
    loadComponent: () =>
      import('./pages/asignacion/asignacion.component').then((m) => m.AsignacionComponent),
  },
  {
    path: 'distribucion-servicio',
    loadComponent: () =>
      import('./pages/distribucion-servicio/distribucion-servicio.component').then(
        (m) => m.DistribucionServicioComponent
      ),
  },
  {
    path: 'simulacion-des',
    loadComponent: () =>
      import('./pages/simulacion-des/simulacion-des.component').then(
        (m) => m.SimulacionDesComponent
      ),
  },
  {
    path: 'ley-little',
    loadComponent: () =>
      import('./pages/ley-little/ley-little.component').then((m) => m.LeyLittleComponent),
  },
];
