import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgFor, NgIf } from '@angular/common';
import { ApiService } from '../../core/api.service';
import { MetricGridComponent, Metrica } from '../../shared/metric-grid.component';

type MetodoPronostico = 'promedio_movil' | 'suavizacion_exponencial' | 'regresion_lineal';

interface PronosticoSalida {
  modelo: string;
  metodo: string;
  valores_ajustados: (number | null)[];
  pronostico: number[];
  error_medio_absoluto: number;
  pendiente?: number;
  intercepto?: number;
}

@Component({
  selector: 'app-pronostico',
  standalone: true,
  imports: [FormsModule, NgFor, NgIf, MetricGridComponent],
  template: `
    <h2>Pronóstico de afluencia</h2>
    <p>
      Predice cuántos clientes llegarán en los próximos periodos a partir de un histórico,
      usando promedio móvil, suavización exponencial o regresión lineal.
    </p>

    <div class="layout">
      <form class="panel" (ngSubmit)="ejecutar()">
        <div class="field">
          <label for="historico">Histórico (clientes por periodo, separados por coma)</label>
          <input id="historico" type="text" [(ngModel)]="historicoTexto" name="historico" required />
          <span class="hint">Ej: 120, 135, 128, 150, 145, 160, 158</span>
        </div>

        <div class="field">
          <label for="metodo">Método</label>
          <select id="metodo" [(ngModel)]="metodo" name="metodo" required>
            <option value="promedio_movil">Promedio móvil</option>
            <option value="suavizacion_exponencial">Suavización exponencial</option>
            <option value="regresion_lineal">Regresión lineal</option>
          </select>
        </div>

        <div class="field" *ngIf="metodo === 'promedio_movil'">
          <label for="ventana">Tamaño de ventana</label>
          <input id="ventana" type="number" step="1" min="1" [(ngModel)]="ventana" name="ventana" />
        </div>

        <div class="field" *ngIf="metodo === 'suavizacion_exponencial'">
          <label for="alpha">Factor de suavizado (alpha, entre 0 y 1)</label>
          <input id="alpha" type="number" step="0.05" min="0.01" max="0.99" [(ngModel)]="alpha" name="alpha" />
        </div>

        <div class="field">
          <label for="periodos">Periodos futuros a pronosticar</label>
          <input id="periodos" type="number" step="1" min="1" [(ngModel)]="nPeriodosPred" name="periodos" required />
        </div>

        <button class="btn-primary" type="submit" [disabled]="cargando()">
          {{ cargando() ? 'Calculando…' : 'Calcular pronóstico' }}
        </button>
      </form>

      <div class="panel resultados">
        <div class="error-banner" *ngIf="error()">{{ error() }}</div>

        <ng-container *ngIf="resultado() as r">
          <app-metric-grid [metricas]="metricas(r)"></app-metric-grid>

          <h3 class="subtitulo">Histórico vs. ajustado</h3>
          <div class="barras dos-series">
            <div class="par" *ngFor="let real of historico; let i = index">
              <div
                class="barra real"
                [style.height.%]="alturaBarra(real, todosLosValores(r))"
                [title]="'Real: ' + real"
              ></div>
              <div
                class="barra ajustado"
                *ngIf="r.valores_ajustados[i] !== null"
                [style.height.%]="alturaBarra(r.valores_ajustados[i]!, todosLosValores(r))"
                [title]="'Ajustado: ' + r.valores_ajustados[i]"
              ></div>
            </div>
          </div>
          <div class="leyenda">
            <span><i class="cuadro real"></i> Real</span>
            <span><i class="cuadro ajustado"></i> Ajustado</span>
          </div>

          <h3 class="subtitulo">Pronóstico ({{ r.pronostico.length }} periodos)</h3>
          <p class="lista-llegadas">{{ r.pronostico.join(', ') }}</p>
        </ng-container>

        <p *ngIf="!resultado() && !error()">Los resultados aparecerán aquí.</p>
      </div>
    </div>
  `,
  styleUrl: '../page-shared.css',
})
export class PronosticoComponent {
  private api = inject(ApiService);

  historicoTexto = '120, 135, 128, 150, 145, 160, 158';
  metodo: MetodoPronostico = 'suavizacion_exponencial';
  ventana = 3;
  alpha = 0.3;
  nPeriodosPred = 3;

  cargando = signal(false);
  resultado = signal<PronosticoSalida | null>(null);
  error = signal<string | null>(null);

  get historico(): number[] {
    return this.historicoTexto
      .split(',')
      .map((v) => Number(v.trim()))
      .filter((v) => !Number.isNaN(v));
  }

  ejecutar() {
    this.cargando.set(true);
    this.error.set(null);
    this.resultado.set(null);

    this.api.post<PronosticoSalida>('/modelos/pronostico/', {
      historico: this.historico,
      metodo: this.metodo,
      n_periodos_pred: this.nPeriodosPred,
      ventana: this.ventana,
      alpha: this.alpha,
    }).subscribe({
      next: (r) => {
        this.resultado.set(r);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set(err?.error?.detail ?? 'Ocurrió un error al calcular el pronóstico.');
        this.cargando.set(false);
      },
    });
  }

  metricas(r: PronosticoSalida): Metrica[] {
    const base: Metrica[] = [
      { label: 'Método', value: this.nombreMetodo(r.metodo) },
      { label: 'Error medio absoluto (MAE)', value: r.error_medio_absoluto },
    ];
    if (r.pendiente !== undefined) base.push({ label: 'Pendiente', value: r.pendiente });
    if (r.intercepto !== undefined) base.push({ label: 'Intercepto', value: r.intercepto });
    return base;
  }

  nombreMetodo(m: string): string {
    const nombres: Record<string, string> = {
      promedio_movil: 'Promedio móvil',
      suavizacion_exponencial: 'Suavización exponencial',
      regresion_lineal: 'Regresión lineal',
    };
    return nombres[m] ?? m;
  }

  todosLosValores(r: PronosticoSalida): number[] {
    const ajustados = r.valores_ajustados.filter((v): v is number => v !== null);
    return [...this.historico, ...ajustados];
  }

  alturaBarra(valor: number, serie: number[]): number {
    const max = Math.max(...serie, 1);
    return Math.max((valor / max) * 100, 4);
  }
}
