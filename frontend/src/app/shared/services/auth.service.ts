import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private token = localStorage.getItem('jwt_noticias');
  constructor(private http: HttpClient, private router: Router) {}
  login(email: string, password: string) {
    return this.http.post<any>(`${environment.apiUrl}/auth/login`, { email, password });
  }
  saveToken(t: string) { this.token = t; localStorage.setItem('jwt_noticias', t); }
  getToken() { return this.token; }
  logout() { this.token = null; localStorage.removeItem('jwt_noticias'); this.router.navigate(['/']); }
  isAuthenticated() { return !!this.token; }
  getRole(): string {
    if (!this.token) return '';
    try { return JSON.parse(atob(this.token.split('.')[1])).role || ''; } catch { return ''; }
  }
  getUserId(): number {
    if (!this.token) return 0;
    try { return JSON.parse(atob(this.token.split('.')[1])).user_id || 0; } catch { return 0; }
  }
}
