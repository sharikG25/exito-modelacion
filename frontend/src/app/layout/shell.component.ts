import { Component } from '@angular/core';
import { NgFor } from '@angular/common';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { ESTACIONES } from '../core/estaciones';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [NgFor, RouterLink, RouterLinkActive, RouterOutlet],
  template: `
    <div class="shell">
      <aside class="sidebar">
        <div class="brand">
          <span class="brand-mark"></span>
          <div>
            <h1>Éxito<span class="dim">Sim</span></h1>
            <p class="tagline">Modelación de flujo de clientes</p>
          </div>
        </div>

        <nav>
          <a
            *ngFor="let e of estaciones"
            [routerLink]="e.path"
            routerLinkActive="active"
            class="station-link"
          >
            <span class="dot"></span>
            <span>
              <strong>{{ e.nombre }}</strong>
              <small>{{ e.descripcion }}</small>
            </span>
          </a>
        </nav>
      </aside>

      <div class="main">
        <header class="topbar">
          <!-- Carril de flujo: puntos que representan clientes moviéndose por el sistema -->
          <div class="flow-lane" aria-hidden="true">
            <span class="flow-dot" style="animation-delay: 0s"></span>
            <span class="flow-dot" style="animation-delay: 0.6s"></span>
            <span class="flow-dot" style="animation-delay: 1.2s"></span>
            <span class="flow-dot" style="animation-delay: 1.8s"></span>
          </div>
          <span class="topbar-label">Panel analítico</span>
        </header>

        <main class="content">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styleUrl: './shell.component.css',
})
export class ShellComponent {
  estaciones = ESTACIONES;
}
