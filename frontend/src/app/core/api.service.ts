import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

/**
 * Servicio único para llamar a cualquiera de los 8 modelos matemáticos
 * del backend. Cada página de modelo usa `post<TSalida>(ruta, body)`
 * con su propia interfaz de entrada/salida.
 */
@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private base = environment.apiUrl;

  post<TSalida>(ruta: string, body: unknown): Observable<TSalida> {
    return this.http.post<TSalida>(`${this.base}${ruta}`, body);
  }
}
