import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgFor, NgIf } from '@angular/common';
import { ApiService } from '../../core/api.service';
import { MetricGridComponent, Metrica } from '../../shared/metric-grid.component';

interface MontecarloSalida {
  modelo: string;
  numero_clientes: number;
  tiempos_llegada: number[];
  tiempos_entre_llegadas: number[];
  promedio_entre_llegadas: number;
  tasa_llegada_observada: number;
  clientes_por_hora: number[];
  tiempos_servicio_simulados?: number[];
}

@Component({
  selector: 'app-montecarlo',
  standalone: true,
  imports: [FormsModule, NgIf, NgFor, MetricGridComponent],
  template: `
    <h2>Simulación de Montecarlo</h2>
    <p>
      Genera las llegadas de clientes a lo largo de una jornada usando un proceso de Poisson
      (intervalos entre llegadas ~ Exponencial), para alimentar los demás modelos con datos sintéticos.
    </p>

    <div class="layout">
      <form class="panel" (ngSubmit)="ejecutar()">
        <div class="field">
          <label for="lam">Tasa de llegada (λ) — clientes/minuto</label>
          <input id="lam" type="number" step="0.1" min="0.01" [(ngModel)]="lam" name="lam" required />
        </div>

        <div class="field">
          <label for="duracion">Duración de la jornada (minutos)</label>
          <input id="duracion" type="number" step="10" min="1" [(ngModel)]="duracionMin" name="duracion" required />
          <span class="hint">Ej. 480 = jornada de 8 horas</span>
        </div>

        <div class="field">
          <label for="servicio">Tiempo promedio de servicio (min) — opcional</label>
          <input id="servicio" type="number" step="0.1" min="0" [(ngModel)]="tiempoServicioProm" name="servicio" />
        </div>

        <div class="field">
          <label for="semilla">Semilla aleatoria — opcional</label>
          <input id="semilla" type="number" step="1" [(ngModel)]="semilla" name="semilla" />
          <span class="hint">Fija un número para obtener siempre el mismo resultado.</span>
        </div>

        <button class="btn-primary" type="submit" [disabled]="cargando()">
          {{ cargando() ? 'Simulando…' : 'Simular llegadas' }}
        </button>
      </form>

      <div class="panel resultados">
        <div class="error-banner" *ngIf="error()">{{ error() }}</div>

        <ng-container *ngIf="resultado() as r">
          <app-metric-grid [metricas]="metricas(r)"></app-metric-grid>

          <h3 class="subtitulo">Clientes por hora</h3>
          <div class="barras">
            <div
              class="barra"
              *ngFor="let cantidad of r.clientes_por_hora; let i = index"
              [style.height.%]="alturaBarra(cantidad, r.clientes_por_hora)"
              [title]="'Hora ' + (i + 1) + ': ' + cantidad + ' clientes'"
            >
              <span class="barra-valor">{{ cantidad }}</span>
            </div>
          </div>

          <h3 class="subtitulo">Primeras llegadas (minuto)</h3>
          <p class="lista-llegadas">{{ primerasLlegadas(r) }}</p>
        </ng-container>

        <p *ngIf="!resultado() && !error()">Los resultados aparecerán aquí.</p>
      </div>
    </div>
  `,
  styleUrl: '../page-shared.css',
})
export class MontecarloComponent {
  private api = inject(ApiService);

  lam = 2.0;
  duracionMin = 480;
  tiempoServicioProm: number | null = 3.0;
  semilla: number | null = 42;

  cargando = signal(false);
  resultado = signal<MontecarloSalida | null>(null);
  error = signal<string | null>(null);

  ejecutar() {
    this.cargando.set(true);
    this.error.set(null);
    this.resultado.set(null);

    this.api.post<MontecarloSalida>('/modelos/montecarlo/', {
      lam: this.lam,
      duracion_min: this.duracionMin,
      tiempo_servicio_prom: this.tiempoServicioProm ?? null,
      semilla: this.semilla ?? null,
    }).subscribe({
      next: (r) => {
        this.resultado.set(r);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set(err?.error?.detail ?? 'Ocurrió un error al ejecutar la simulación.');
        this.cargando.set(false);
      },
    });
  }

  metricas(r: MontecarloSalida): Metrica[] {
    return [
      { label: 'Clientes generados', value: r.numero_clientes },
      { label: 'Tasa observada (clientes/min)', value: r.tasa_llegada_observada },
      { label: 'Promedio entre llegadas (min)', value: r.promedio_entre_llegadas },
    ];
  }

  alturaBarra(valor: number, serie: number[]): number {
    const max = Math.max(...serie, 1);
    return Math.max((valor / max) * 100, 4);
  }

  primerasLlegadas(r: MontecarloSalida): string {
    return r.tiempos_llegada.slice(0, 15).join(', ') + (r.tiempos_llegada.length > 15 ? '…' : '');
  }
}
