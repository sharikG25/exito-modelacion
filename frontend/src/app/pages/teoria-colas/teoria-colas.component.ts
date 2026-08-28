import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';
import { ApiService } from '../../core/api.service';
import { MetricGridComponent, Metrica } from '../../shared/metric-grid.component';

interface TeoriaColasSalida {
  modelo: string;
  c?: number;
  rho: number;
  p0: number;
  l: number;
  lq: number;
  w: number;
  wq: number;
  prob_esperar: number;
}

@Component({
  selector: 'app-teoria-colas',
  standalone: true,
  imports: [FormsModule, NgIf, MetricGridComponent],
  template: `
    <h2>Teoría de colas</h2>
    <p>
      Estima el tiempo de espera y la utilización de las cajas a partir de la tasa de llegada
      de clientes y la tasa de servicio, usando los modelos M/M/1 (una caja) o M/M/c (varias cajas).
    </p>

    <div class="layout">
      <form class="panel" (ngSubmit)="ejecutar()">
        <div class="field">
          <label for="lam">Tasa de llegada (λ) — clientes/minuto</label>
          <input id="lam" type="number" step="0.1" min="0.01" [(ngModel)]="lam" name="lam" required />
        </div>

        <div class="field">
          <label for="mu">Tasa de servicio por caja (μ) — clientes/minuto</label>
          <input id="mu" type="number" step="0.1" min="0.01" [(ngModel)]="mu" name="mu" required />
        </div>

        <div class="field">
          <label for="c">Número de cajas abiertas</label>
          <input id="c" type="number" step="1" min="1" [(ngModel)]="c" name="c" required />
          <span class="hint">Si es 1, se usa M/M/1. Si es mayor, M/M/c (fórmula de Erlang C).</span>
        </div>

        <button class="btn-primary" type="submit" [disabled]="cargando()">
          {{ cargando() ? 'Calculando…' : 'Calcular' }}
        </button>
      </form>

      <div class="panel resultados">
        <div class="error-banner" *ngIf="error()">{{ error() }}</div>

        <ng-container *ngIf="resultado() as r">
          <p class="modelo-usado"><strong>Modelo aplicado:</strong> {{ r.c && r.c > 1 ? 'M/M/c' : 'M/M/1' }}</p>
          <app-metric-grid [metricas]="metricas(r)"></app-metric-grid>
        </ng-container>

        <p *ngIf="!resultado() && !error()">Los resultados aparecerán aquí.</p>
      </div>
    </div>
  `,
  styleUrl: '../page-shared.css',
})
export class TeoriaColasComponent {
  private api = inject(ApiService);

  lam = 2.5;
  mu = 3.0;
  c = 2;

  cargando = signal(false);
  resultado = signal<TeoriaColasSalida | null>(null);
  error = signal<string | null>(null);

  ejecutar() {
    this.cargando.set(true);
    this.error.set(null);
    this.resultado.set(null);

    this.api.post<TeoriaColasSalida>('/modelos/teoria-colas/', {
      lam: this.lam,
      mu: this.mu,
      c: this.c,
    }).subscribe({
      next: (r) => {
        this.resultado.set(r);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set(err?.error?.detail ?? 'Ocurrió un error al calcular el modelo.');
        this.cargando.set(false);
      },
    });
  }

  metricas(r: TeoriaColasSalida): Metrica[] {
    return [
      { label: 'Utilización (ρ)', value: r.rho },
      { label: 'P(sistema vacío)', value: r.p0 },
      { label: 'Clientes en sistema (L)', value: r.l },
      { label: 'Clientes en fila (Lq)', value: r.lq },
      { label: 'Tiempo en sistema (W) min', value: r.w },
      { label: 'Tiempo en fila (Wq) min', value: r.wq },
      { label: 'Prob. de esperar', value: r.prob_esperar },
    ];
  }
}
