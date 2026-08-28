import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgFor, NgIf } from '@angular/common';
import { ApiService } from '../../core/api.service';
import { MetricGridComponent, Metrica } from '../../shared/metric-grid.component';

interface AjusteExponencial {
  lambda: number;
  ks_estadistico: number;
  ks_p_valor: number;
  prob_superar_objetivo?: number | null;
}

interface AjusteNormal {
  media: number;
  desviacion: number;
  ks_estadistico: number;
  ks_p_valor: number;
  prob_superar_objetivo?: number | null;
}

interface DistribucionServicioSalida {
  modelo: string;
  n: number;
  media: number;
  desviacion: number;
  varianza: number;
  ajuste_exponencial: AjusteExponencial;
  ajuste_normal: AjusteNormal;
  mejor_ajuste: string;
  tiempo_objetivo?: number | null;
}

@Component({
  selector: 'app-distribucion-servicio',
  standalone: true,
  imports: [FormsModule, NgIf, NgFor, MetricGridComponent],
  template: `
    <h2>Distribución de tiempo de servicio</h2>
    <p>
      Ajusta una muestra de tiempos de atención a las distribuciones Exponencial y Normal, y usa
      la prueba de bondad de ajuste de Kolmogorov-Smirnov para decidir cuál describe mejor los
      datos — un insumo clave para elegir el supuesto correcto en el modelo de teoría de colas.
    </p>

    <div class="layout">
      <form class="panel" (ngSubmit)="ejecutar()">
        <div class="field">
          <label for="tiempos">Tiempos de servicio observados (min, separados por coma)</label>
          <textarea
            id="tiempos"
            rows="4"
            [(ngModel)]="tiemposTexto"
            name="tiempos"
            required
          ></textarea>
          <span class="hint">Ej. 2.1, 3.4, 1.8, 2.9, 4.2, 2.5, 3.0, 2.2, 3.8, 2.6</span>
        </div>

        <div class="field">
          <label for="objetivo">Tiempo objetivo (min) — opcional</label>
          <input
            id="objetivo"
            type="number"
            step="0.1"
            min="0"
            [(ngModel)]="tiempoObjetivo"
            name="objetivo"
          />
          <span class="hint">Calcula la probabilidad de que un cliente tarde más de este tiempo.</span>
        </div>

        <button class="btn-primary" type="submit" [disabled]="cargando()">
          {{ cargando() ? 'Ajustando…' : 'Ajustar distribuciones' }}
        </button>
      </form>

      <div class="panel resultados">
        <div class="error-banner" *ngIf="error()">{{ error() }}</div>

        <ng-container *ngIf="resultado() as r">
          <app-metric-grid [metricas]="metricas(r)"></app-metric-grid>

          <h3 class="subtitulo">Ajuste de distribuciones</h3>
          <div class="tabla-scroll">
            <table class="tabla-resultado">
              <thead>
                <tr>
                  <th>Distribución</th>
                  <th>Parámetros</th>
                  <th>KS estadístico</th>
                  <th>KS p-valor</th>
                  <th *ngIf="tieneObjetivo(r)">P(servicio &gt; objetivo)</th>
                </tr>
              </thead>
              <tbody>
                <tr [class.mejor]="r.mejor_ajuste === 'Exponencial'">
                  <td>Exponencial</td>
                  <td>λ = {{ r.ajuste_exponencial.lambda }}</td>
                  <td class="num">{{ r.ajuste_exponencial.ks_estadistico }}</td>
                  <td class="num">{{ r.ajuste_exponencial.ks_p_valor }}</td>
                  <td class="num" *ngIf="tieneObjetivo(r)">
                    {{ r.ajuste_exponencial.prob_superar_objetivo }}
                  </td>
                </tr>
                <tr [class.mejor]="r.mejor_ajuste === 'Normal'">
                  <td>Normal</td>
                  <td>μ = {{ r.ajuste_normal.media }}, σ = {{ r.ajuste_normal.desviacion }}</td>
                  <td class="num">{{ r.ajuste_normal.ks_estadistico }}</td>
                  <td class="num">{{ r.ajuste_normal.ks_p_valor }}</td>
                  <td class="num" *ngIf="tieneObjetivo(r)">
                    {{ r.ajuste_normal.prob_superar_objetivo }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <p class="veredicto">
            Mejor ajuste según Kolmogorov-Smirnov: <strong>{{ r.mejor_ajuste }}</strong>
            (mayor p-valor, menor estadístico KS).
          </p>
        </ng-container>

        <p *ngIf="!resultado() && !error()">Los resultados aparecerán aquí.</p>
      </div>
    </div>
  `,
  styleUrl: '../page-shared.css',
})
export class DistribucionServicioComponent {
  private api = inject(ApiService);

  tiemposTexto = '2.1, 3.4, 1.8, 2.9, 4.2, 2.5, 3.0, 2.2, 3.8, 2.6';
  tiempoObjetivo: number | null = 4.0;

  cargando = signal(false);
  resultado = signal<DistribucionServicioSalida | null>(null);
  error = signal<string | null>(null);

  ejecutar() {
    const tiemposServicio = this.tiemposTexto
      .split(',')
      .map((v) => Number(v.trim()))
      .filter((v) => !Number.isNaN(v) && v > 0);

    if (tiemposServicio.length < 2) {
      this.error.set('Ingresa al menos 2 tiempos de servicio válidos, separados por coma.');
      this.resultado.set(null);
      return;
    }

    this.cargando.set(true);
    this.error.set(null);
    this.resultado.set(null);

    this.api
      .post<DistribucionServicioSalida>('/modelos/distribucion-servicio/', {
        tiempos_servicio: tiemposServicio,
        tiempo_objetivo: this.tiempoObjetivo ?? null,
      })
      .subscribe({
        next: (r) => {
          this.resultado.set(r);
          this.cargando.set(false);
        },
        error: (err) => {
          this.error.set(err?.error?.detail ?? 'Ocurrió un error al ajustar las distribuciones.');
          this.cargando.set(false);
        },
      });
  }

  tieneObjetivo(r: DistribucionServicioSalida): boolean {
    return r.tiempo_objetivo !== null && r.tiempo_objetivo !== undefined;
  }

  metricas(r: DistribucionServicioSalida): Metrica[] {
    return [
      { label: 'Muestras (n)', value: r.n },
      { label: 'Media (min)', value: r.media },
      { label: 'Desviación estándar', value: r.desviacion },
      { label: 'Varianza', value: r.varianza },
    ];
  }
}
