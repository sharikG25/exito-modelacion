import { Component, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgFor, NgIf } from '@angular/common';
import { ApiService } from '../../core/api.service';
import { MetricGridComponent, Metrica } from '../../shared/metric-grid.component';

interface AsignacionResultado {
  empleado: string;
  puesto: string;
  costo: number;
}

interface AsignacionSalida {
  modelo: string;
  asignaciones: AsignacionResultado[];
  costo_total: number;
  empleados_sin_asignar: string[];
  puestos_sin_cubrir: string[];
}

@Component({
  selector: 'app-asignacion',
  standalone: true,
  imports: [FormsModule, NgFor, NgIf, MetricGridComponent],
  template: `
    <h2>Asignación de personal</h2>
    <p>
      Asigna empleados a puestos/cajas minimizando el costo total (por ejemplo, tiempo de
      atención esperado), usando el algoritmo húngaro.
    </p>

    <div class="layout">
      <form class="panel" (ngSubmit)="ejecutar()">
        <div class="field">
          <label for="empleados">Empleados (separados por coma)</label>
          <input id="empleados" type="text" [(ngModel)]="empleadosTexto" name="empleados" (ngModelChange)="regenerarMatriz()" required />
        </div>

        <div class="field">
          <label for="puestos">Puestos/cajas (separados por coma)</label>
          <input id="puestos" type="text" [(ngModel)]="puestosTexto" name="puestos" (ngModelChange)="regenerarMatriz()" required />
        </div>

        <div class="field">
          <label>Matriz de costos (empleado × puesto)</label>
          <table class="matriz">
            <thead>
              <tr>
                <th></th>
                <th *ngFor="let p of puestos">{{ p }}</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let fila of matrizCostos; let i = index">
                <th>{{ empleados[i] }}</th>
                <td *ngFor="let _ of fila; let j = index">
                  <input type="number" step="0.5" min="0" [(ngModel)]="matrizCostos[i][j]" [name]="'c' + i + '-' + j" />
                </td>
              </tr>
            </tbody>
          </table>
          <span class="hint">Un costo más alto puede representar mayor tiempo de atención o menor habilidad en ese puesto.</span>
        </div>

        <button class="btn-primary" type="submit" [disabled]="cargando()">
          {{ cargando() ? 'Calculando…' : 'Calcular asignación óptima' }}
        </button>
      </form>

      <div class="panel resultados">
        <div class="error-banner" *ngIf="error()">{{ error() }}</div>

        <ng-container *ngIf="resultado() as r">
          <app-metric-grid [metricas]="metricas(r)"></app-metric-grid>

          <h3 class="subtitulo">Asignación óptima</h3>
          <table class="tabla-resultado">
            <thead>
              <tr>
                <th>Empleado</th>
                <th>Puesto</th>
                <th>Costo</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let a of r.asignaciones">
                <td>{{ a.empleado }}</td>
                <td>{{ a.puesto }}</td>
                <td class="num">{{ a.costo }}</td>
              </tr>
            </tbody>
          </table>

          <p class="nota-extra" *ngIf="r.empleados_sin_asignar.length > 0">
            Empleados sin asignar: {{ r.empleados_sin_asignar.join(', ') }}
          </p>
          <p class="nota-extra" *ngIf="r.puestos_sin_cubrir.length > 0">
            Puestos sin cubrir: {{ r.puestos_sin_cubrir.join(', ') }}
          </p>
        </ng-container>

        <p *ngIf="!resultado() && !error()">Los resultados aparecerán aquí.</p>
      </div>
    </div>
  `,
  styleUrl: '../page-shared.css',
})
export class AsignacionComponent {
  private api = inject(ApiService);

  empleadosTexto = 'Ana, Luis, Marta';
  puestosTexto = 'Caja 1, Caja 2, Caja 3';
  empleados: string[] = ['Ana', 'Luis', 'Marta'];
  puestos: string[] = ['Caja 1', 'Caja 2', 'Caja 3'];
  matrizCostos: number[][] = [
    [4, 2, 8],
    [3, 6, 5],
    [7, 4, 3],
  ];

  cargando = signal(false);
  resultado = signal<AsignacionSalida | null>(null);
  error = signal<string | null>(null);

  regenerarMatriz() {
    this.empleados = this.empleadosTexto.split(',').map((e) => e.trim()).filter((e) => e.length > 0);
    this.puestos = this.puestosTexto.split(',').map((p) => p.trim()).filter((p) => p.length > 0);

    const nuevaMatriz: number[][] = [];
    for (let i = 0; i < this.empleados.length; i++) {
      const fila: number[] = [];
      for (let j = 0; j < this.puestos.length; j++) {
        fila.push(this.matrizCostos[i]?.[j] ?? 1);
      }
      nuevaMatriz.push(fila);
    }
    this.matrizCostos = nuevaMatriz;
  }

  ejecutar() {
    this.cargando.set(true);
    this.error.set(null);
    this.resultado.set(null);

    this.api.post<AsignacionSalida>('/modelos/asignacion/', {
      empleados: this.empleados,
      puestos: this.puestos,
      matriz_costos: this.matrizCostos,
    }).subscribe({
      next: (r) => {
        this.resultado.set(r);
        this.cargando.set(false);
      },
      error: (err) => {
        this.error.set(err?.error?.detail ?? 'Ocurrió un error al calcular la asignación.');
        this.cargando.set(false);
      },
    });
  }

  metricas(r: AsignacionSalida): Metrica[] {
    return [
      { label: 'Costo total óptimo', value: r.costo_total },
      { label: 'Asignaciones realizadas', value: r.asignaciones.length },
    ];
  }
}
