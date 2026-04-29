import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private auth: AuthService) {}
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = this.auth.getToken();
    const authReq = token
  ? req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    })
  : req;
    return next.handle(req).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status === 401) {
        localStorage.removeItem('jwt_noticias');
        window.location.href = '/login';
      }

      if (err.status === 403) {
        alert('No tienes permiso para realizar esta acción.');
      }

      return throwError(() => err);
    })
  );
  }
}
