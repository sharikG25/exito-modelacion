import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgFor, NgIf } from '@angular/common';
import { ApiService } from '../../core/api.service';
import { MetricGridComponent, Metrica } from '../../shared/metric-grid.component';

interface ClienteSimulado {
  cliente_id: number;
  hora_llegada: number;
  hora_inicio_servicio: number;
  hora_fin_servicio: number;
  tiempo_espera: number;
  tiempo_servicio: number;
  tiempo_en_sistema: number;
  caja_asignada: number;
}

interface SimulacionDESSalida {
  modelo: string;
  n_clientes: number;
  clientes: ClienteSimulado[];
  eventos: { tipo: string; cliente_id: number; tiempo: number }[];
  metricas: Record<string, number>;
}

@Component({
  selector: 'app-simulacion-des',
  standalone: true,
  imports: [FormsModule, NgFor, NgIf, MetricGridComponent],
  template: `
    <h2>Simulación de eventos discretos</h2>
    <p>
      Simula el flujo completo del cliente (llegada, inicio y fin de servicio) uno por uno,
      permitiendo observar la evolución real del sistema, no solo sus promedios.
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
        </div>

        <div class="field">
          <label for="duracion">Duración de la simulación (minutos)</label>
          <input id="duracion" type="number" step="10" min="1" [(ngModel)]="duracionMin" name="duracion" required />
        </div>

        <div class="field">
          <label for="semilla">Semilla aleatoria — opcional</label>
          <input id="semilla" type="number" step="1" [(ngModel)]="semilla" name="semilla" />
        </div>

        <button class="btn-primary" type="submit" [disabled]="cargando()">
          {{ cargando() ? 'Simulando…' : 'Ejecutar simulación' }}
        </button>
      </form>

      <div class="panel resultados">
        <div class="error-banner" *ngIf="error()">{{ error() }}</div>

        <ng-container *ngIf="resultado() as r">
          <app-metric-grid [metricas]="metricas(r)"></app-metric-grid>

          <h3 class="subtitulo">
            Detalle por cliente (primeros 20 de {{ r.n_clientes }})
          </h3>
          <div class="tabla-scroll">
            <table class="tabla-resultado">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Llegada</th>
                  <th>Inicio</th>
                  <th>Fin</th>
                  <th>Espera</th>
                  <th>Servicio</th>
                  <th>En sistema</th>
                  <th>Caja</th>
                </tr>
              </thead>
              <tbody>
                <tr *ngFor="let cli of r.clientes.slice(0, 20)">
                  <td>{{ cli.cliente_id }}</td>
                  <td class="num">{{ cli.hora_llegada }}</td>
                  <td class="num">{{ cli.hora_inicio_servicio }}</td>
                  <td class="num">{{ cli.hora_fin_servicio }}</td>
                  <td class="num">{{ cli.tiempo_espera }}</td>
                  <td class="num">{{ cli.tiempo_servicio }}</td>
                  <td class="num">{{ cli.tiempo_en_sistema }}</td>
                  <td>{{ cli.caja_asignada }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </ng-container>

        <p *ngIf="!resultado() && !error()">Los resultados aparecerán aquí.</p>
      </div>
    </div>
  `,
  styleUrl: '../page-shared.css',
})
export class SimulacionDesComponent {
  private api = inject(ApiService);

  lam = 2.0;
  mu = 1.5;
  c = 2;
  duracionMin = 120;
  semilla: number | null = 42;

  cargando = signal(false);
  resultado = signal<SimulacionDESSalida | null>(null);
  error = signal<string | null>(null);

  ejecutar() {
    this.cargando.set(true);
    this.error.set(null);
    this.resultado.set(null);

    this.api.post<SimulacionDESSalida>('/modelos/simulacion-des/', {
      lam: this.lam,
      mu: this.mu,
      c: this.c,
      duracion_min: this.duracionMin,
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

  metricas(r: SimulacionDESSalida): Metrica[] {
    return [
      { label: 'Clientes simulados', value: r.n_clientes },
      { label: 'Espera promedio (min)', value: r.metricas['espera_promedio'] },
      { label: 'Tiempo en sistema prom. (min)', value: r.metricas['tiempo_en_sistema_promedio'] },
      { label: 'Longitud fila promedio', value: r.metricas['longitud_fila_promedio'] },
      { label: 'Utilización de cajas', value: r.metricas['utilizacion_promedio_cajas'] },
      { label: 'Prob. de esperar', value: r.metricas['probabilidad_esperar'] },
    ];
  }
}
