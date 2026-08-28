import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgIf } from '@angular/common';
import { ApiService } from '../../core/api.service';
import { MetricGridComponent, Metrica } from '../../shared/metric-grid.component';

type Modo = 'calcular' | 'verificar';

interface LeyLittleSalida {
  modelo: string;
  lam: number;
  w: number;
  l: number;
  variable_calculada: string;
}

interface VerificacionSalida {
  modelo: string;
  l_esperado_segun_little: number;
  l_observado: number;
  diferencia_relativa: number;
  es_consistente: boolean;
  tolerancia_usada: number;
}

const NOMBRE_VARIABLE: Record<string, string> = {
  lam: 'λ (tasa de llegada)',
  w: 'W (tiempo en el sistema)',
  l: 'L (clientes en el sistema)',
};

@Component({
  selector: 'app-ley-little',
  standalone: true,
  imports: [FormsModule, NgIf, MetricGridComponent],
  template: `
    <h2>Ley de Little</h2>
    <p>
      Relaciona el número promedio de clientes en el sistema (L), la tasa de llegada (λ) y el
      tiempo promedio en el sistema (W): <strong>L = λ · W</strong>. Válida para cualquier sistema
      en estado estable, sin importar la distribución de llegadas o servicio.
    </p>

    <div class="layout">
      <form class="panel" (ngSubmit)="ejecutar()">
        <div class="field">
          <label for="modo">Qué quieres hacer</label>
          <select id="modo" [(ngModel)]="modo" name="modo">
            <option value="calcular">Calcular la variable faltante (L, λ o W)</option>
            <option value="verificar">Verificar consistencia con un L observado</option>
          </select>
        </div>

        <ng-container *ngIf="modo === 'calcular'">
          <p class="hint modo-hint">Deja vacía exactamente 1 de las 3 variables; esa se calcula.</p>

          <div class="field">
            <label for="lam">λ — tasa de llegada (clientes/minuto)</label>
            <input id="lam" type="number" step="0.01" min="0" [(ngModel)]="lam" name="lam" />
          </div>

          <div class="field">
            <label for="w">W — tiempo promedio en el sistema (minutos)</label>
            <input id="w" type="number" step="0.01" min="0" [(ngModel)]="w" name="w" />
          </div>

          <div class="field">
            <label for="l">L — clientes promedio en el sistema</label>
            <input id="l" type="number" step="0.01" min="0" [(ngModel)]="l" name="l" />
          </div>
        </ng-container>

        <ng-container *ngIf="modo === 'verificar'">
          <p class="hint modo-hint">
            Compara el L observado (ej. en una simulación DES) contra el L esperado por λ · W.
          </p>

          <div class="field">
            <label for="lamV">λ observado (clientes/minuto)</label>
            <input id="lamV" type="number" step="0.01" min="0.01" [(ngModel)]="lamVerificar" name="lamV" required />
          </div>

          <div class="field">
            <label for="wV">W observado (minutos)</label>
            <input id="wV" type="number" step="0.01" min="0.01" [(ngModel)]="wVerificar" name="wV" required />
          </div>

          <div class="field">
            <label for="lObs">L observado (clientes en el sistema)</label>
            <input id="lObs" type="number" step="0.01" min="0.01" [(ngModel)]="lObservado" name="lObs" required />
          </div>

          <div class="field">
            <label for="tolerancia">Tolerancia relativa aceptada</label>
            <input id="tolerancia" type="number" step="0.01" min="0.01" max="0.99" [(ngModel)]="tolerancia" name="tolerancia" required />
            <span class="hint">Ej. 0.05 = 5% de diferencia aceptada entre L observado y L esperado.</span>
          </div>
        </ng-container>

        <button class="btn-primary" type="submit" [disabled]="cargando()">
          {{ cargando() ? 'Calculando…' : (modo === 'calcular' ? 'Calcular' : 'Verificar consistencia') }}
        </button>
      </form>

      <div class="panel resultados">
        <div class="error-banner" *ngIf="error()">{{ error() }}</div>

        <ng-container *ngIf="resultadoCalculo() as r">
          <app-metric-grid [metricas]="metricasCalculo(r)"></app-metric-grid>
          <p class="veredicto">
            Variable calculada: <strong>{{ nombreVariable(r.variable_calculada) }}</strong>
          </p>
        </ng-container>

        <ng-container *ngIf="resultadoVerificacion() as r">
          <app-metric-grid [metricas]="metricasVerificacion(r)"></app-metric-grid>
          <p class="veredicto" [class.ok]="r.es_consistente" [class.alerta]="!r.es_consistente">
            {{ r.es_consistente
              ? '✓ Consistente: el L observado coincide con λ · W dentro de la tolerancia.'
              : '✗ Inconsistente: el L observado se aleja de λ · W más de lo tolerado — revisa la simulación o los supuestos.' }}
          </p>
        </ng-container>

        <p *ngIf="!resultadoCalculo() && !resultadoVerificacion() && !error()">
          Los resultados aparecerán aquí.
        </p>
      </div>
    </div>
  `,
  styleUrl: '../page-shared.css',
})
export class LeyLittleComponent {
  private api = inject(ApiService);

  modo: Modo = 'calcular';

  // Modo "calcular": exactamente 2 de las 3 deben tener valor.
  lam: number | null = 2.0;
  w: number | null = 1.2;
  l: number | null = null;

  // Modo "verificar".
  lamVerificar = 2.0;
  wVerificar = 0.5333;
  lObservado = 1.0932;
  tolerancia = 0.05;

  cargando = signal(false);
  resultadoCalculo = signal<LeyLittleSalida | null>(null);
  resultadoVerificacion = signal<VerificacionSalida | null>(null);
  error = signal<string | null>(null);

  ejecutar() {
    this.error.set(null);
    this.resultadoCalculo.set(null);
    this.resultadoVerificacion.set(null);

    if (this.modo === 'calcular') {
      const valores = [this.lam, this.w, this.l].filter((v) => v !== null && v !== undefined);
      if (valores.length !== 2) {
        this.error.set('Ingresa exactamente 2 de las 3 variables (λ, W, L); la tercera se calcula.');
        return;
      }

      this.cargando.set(true);
      this.api
        .post<LeyLittleSalida>('/modelos/ley-little/', {
          lam: this.lam,
          w: this.w,
          l: this.l,
        })
        .subscribe({
          next: (r) => {
            this.resultadoCalculo.set(r);
            this.cargando.set(false);
          },
          error: (err) => {
            this.error.set(err?.error?.detail ?? 'Ocurrió un error al calcular.');
            this.cargando.set(false);
          },
        });
    } else {
      this.cargando.set(true);
      this.api
        .post<VerificacionSalida>('/modelos/ley-little/verificar', {
          lam: this.lamVerificar,
          w: this.wVerificar,
          l_observado: this.lObservado,
          tolerancia: this.tolerancia,
        })
        .subscribe({
          next: (r) => {
            this.resultadoVerificacion.set(r);
            this.cargando.set(false);
          },
          error: (err) => {
            this.error.set(err?.error?.detail ?? 'Ocurrió un error al verificar la consistencia.');
            this.cargando.set(false);
          },
        });
    }
  }

  nombreVariable(clave: string): string {
    return NOMBRE_VARIABLE[clave] ?? clave;
  }

  metricasCalculo(r: LeyLittleSalida): Metrica[] {
    return [
      { label: 'λ (clientes/min)', value: r.lam },
      { label: 'W (min)', value: r.w },
      { label: 'L (clientes)', value: r.l },
    ];
  }

  metricasVerificacion(r: VerificacionSalida): Metrica[] {
    return [
      { label: 'L esperado (λ·W)', value: r.l_esperado_segun_little },
      { label: 'L observado', value: r.l_observado },
      { label: 'Diferencia relativa', value: (r.diferencia_relativa * 100).toFixed(2) + '%' },
      { label: 'Tolerancia usada', value: (r.tolerancia_usada * 100).toFixed(0) + '%' },
    ];
  }
}
