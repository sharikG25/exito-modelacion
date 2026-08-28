export interface Estacion {
  path: string;
  nombre: string;
  descripcion: string;
}

/** Las 8 "estaciones" (modelos matemáticos) que aparecen en la barra lateral. */
export const ESTACIONES: Estacion[] = [
  { path: 'teoria-colas', nombre: 'Teoría de colas', descripcion: 'M/M/1 y M/M/c' },
  { path: 'montecarlo', nombre: 'Montecarlo', descripcion: 'Llegadas de clientes' },
  { path: 'markov', nombre: 'Cadenas de Markov', descripcion: 'Recorrido por zonas' },
  { path: 'pronostico', nombre: 'Pronóstico', descripcion: 'Afluencia futura' },
  { path: 'asignacion', nombre: 'Asignación de personal', descripcion: 'Algoritmo húngaro' },
  { path: 'distribucion-servicio', nombre: 'Distribución de servicio', descripcion: 'Ajuste Exp/Normal' },
  { path: 'simulacion-des', nombre: 'Simulación DES', descripcion: 'Eventos discretos' },
  { path: 'ley-little', nombre: 'Ley de Little', descripcion: 'L = λW' },
];
