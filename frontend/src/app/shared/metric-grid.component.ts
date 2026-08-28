import { Component, Input } from '@angular/core';
import { NgFor } from '@angular/common';

export interface Metrica {
  label: string;
  value: string | number;
}

@Component({
  selector: 'app-metric-grid',
  standalone: true,
  imports: [NgFor],
  template: `
    <div class="metric-grid">
      <div class="metric-card" *ngFor="let m of metricas">
        <div class="value">{{ m.value }}</div>
        <div class="label">{{ m.label }}</div>
      </div>
    </div>
  `,
})
export class MetricGridComponent {
  @Input({ required: true }) metricas: Metrica[] = [];
}
