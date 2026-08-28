import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgFor, NgIf, KeyValuePipe } from '@angular/common';
import { ApiService } from '../../core/api.service';

interface MarkovSalida {
  modelo: string;
  estados: string[];
  estado_inicial: string;
  distribucion_por_paso: Record<string, number>[];
  recorrido_simulado: string[];
  pasos_hasta_absorcion: Record<string, number> | null;
}

@Component({
  selector: 'app-markov',
  standalone: true,
  imports: [FormsModule, NgFor, NgIf, KeyValuePipe],
  template: `
    <h2>Cadenas de Markov</h2>
    <p>
      Modela el recorrido del cliente entre zonas del almacén: en cada paso, se mueve a otra zona
      según las probabilidades de transición definidas.
    </p>

    <div class="layout">
      <form class="panel" (ngSubmit)="ejecutar()">
        <div class="field">
          <label for="estados">Zonas (separadas por coma)</label>
          <input id="estados" type="text" [(ngModel)]="estadosTexto" name="estados" (ngModelChange)="regenerarMatriz()" required />
          <span class="hint">Ej: Entrada, Pasillos, Cajas, Salida</span>
        </div>

        <div class="field">
          <label>Matriz de transición (cada fila debe sumar 1.0)</label>
          <table class="matriz">
            <thead>
              <tr>
                <th></th>
                <th *ngFor="let e of estados">{{ e }}</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let fila of matriz; let i = index">
                <th>{{ estados[i] }}</th>
                <td *ngFor="let _ of fila; let j = index">
                  <input type="number" step="0.05" min="0" max="1" [(ngModel)]="matriz[i][j]" [name]="'m' + i + '-' + j" />
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="field">
          <label for="inicial">Zona inicial</label>
          <select id="inicial" [(ngModel)]="estadoInicial" name="inicial" required>
            <option *ngFor="let e of estados" [value]="e">{{ e }}</option>
          </select>
        </div>

        <div class="field">
          <label for="absorbentes">Zonas de salida (absorbentes) — separadas por coma</label>
          <input id="absorbentes" type="text" [(ngModel)]="absorbentesTexto" name="absorbentes" />
          <span class="hint">Ej: Salida</span>
        </div>

        <div class="field">
          <label for="pasos">Número de pasos a simular</label>
          <input id="pasos" type="number" step="1" min="1" [(ngModel)]="nPasos" name="pasos" required />
        </div>

        <div class="field">
          <label for="semilla">Semilla aleatoria — opcional</label>
          <input id="semilla" type="number" step="1" [(ngModel)]="semilla" name="semilla" />
        </div>

        <button class="btn-primary" type="submit" [disabled]="cargando()">
          {{ cargando() ? 'Calculando…' : 'Calcular' }}
        </button>
      </form>

      <div class="panel resultados">
        <div class="error-banner" *ngIf="error()">{{ error() }}</div>

        <ng-container *ngIf="resultado() as r">
          <h3 class="subtitulo">Recorrido simulado</h3>
          <div class="recorrido">
            <span class="chip" *ngFor="let zona of r.recorrido_simulado; let last = last">
              {{ zona }}<span class="flecha" *ngIf="!last"> → </span>
            </span>
          </div>

          <h3 class="subtitulo">Distribución de probabilidad en el último paso</h3>
          <div class="metric-grid">
            <div class="metric-card" *ngFor="let kv of ultimaDistribucion(r) | keyvalue">
              <div class="value">{{ kv.value }}</div>
              <div class="label">{{ kv.key }}</div>
            </div>
          </div>

          <ng-container *ngIf="r.pasos_hasta_absorcion as pasos">
            <h3 class="subtitulo">Pasos esperados hasta salir del almacén</h3>
            <div class="metric-grid">
              <div class="metric-card" *ngFor="let kv of pasos | keyvalue">
                <div class="value">{{ kv.value }}</div>
                <div class="label">{{ kv.key }}</div>
              </div>
            </div>
          </ng-container>
        </ng-container>

        <p *ngIf="!resultado() && !error()">Los resultados aparecerán aquí.</p>
      </div>
    </div>
  `,
  styleUrl: '../page-shared.css',
})
export class MarkovComponent {
  private api = inject(ApiService);

  estadosTexto = 'Entrada, Pasillos, Cajas, Salida';
  estados: string[] = ['Entrada', 'Pasillos', 'Cajas', 'Salida'];
  matriz: number[][] = [
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.7, 0.3, 0.0],
    [0.0, 0.1, 0.2, 0.7],
    [0.0, 0.0, 0.0, 1.0],
  ];
  estadoInicial = 'Entrada';
  absorbentesTexto = 'Salida';
  nPasos = 8;
  semilla: number | null = 42;

  cargando = signal(false);
  resultado = signal<MarkovSalida | null>(null);
  error = signal<string | null>(null);

  regenerarMatriz() {
    const nuevosEstados = this.estadosTexto
      .split(',')
      .map((e) => e.trim())
      .filter((e) => e.length > 0);

    this.estados = nuevosEstados;

    // Reconstruye la matriz preservando los valores existentes donde sea posible.
    const n = nuevosEstados.length;
    const nuevaMatriz: number[][] = [];
    for (let i = 0; i < n; i++) {
      const fila: number[] = [];
      for (let j = 0; j < n; j++) {
        fila.push(this.matriz[i]?.[j] ?? (i === j ? 1 : 0));
      }
      nuevaMatriz.push(fila);
    }
    this.matriz = nuevaMatriz;

    if (!this.estados.includes(this.estadoInicial)) {
      this.estadoInicial = this.estados[0] ?? '';
    }
  }

  ejecutar() {
    this.cargando.set(true);
    this.error.set(null);
    this.resultado.set(null);

    const estadosAbsorbentes = this.absorbentesTexto
      .split(',')
      .map((e) => e.trim())
      .filter((e) => e.length > 0);

    this.api.post<MarkovSalida>('/modelos/markov/', {
      estados: this.estados,
      matriz_transicion: this.matriz,
      estado_inicial: this.estadoInicial,
      n_pasos: this.nPasos,
      estados_absorbentes: estadosAbsorbentes.length > 0 ? estadosAbsorbentes : null,
      semilla: this.semilla ?? null,
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

  ultimaDistribucion(r: MarkovSalida): Record<string, number> {
    return r.distribucion_por_paso[r.distribucion_por_paso.length - 1];
  }
}
