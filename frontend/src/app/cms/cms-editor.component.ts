import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import DOMPurify from 'dompurify';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-cms-editor',
  template: `
    <div class="cms-editor">
      <h2>Editor CMS — Noticias 360</h2>

      <input
        [(ngModel)]="titulo"
        name="titulo"
        placeholder="Título"
      />

      <div class="preview" [innerHTML]="previewHtml"></div>

      <textarea
        [(ngModel)]="contenidoHtml"
        name="contenido"
        (ngModelChange)="actualizarPreview()"
        rows="15"
        placeholder="Contenido HTML..."
      ></textarea>

      <button (click)="guardarArticulo()">Guardar Borrador</button>

      <button
        *ngIf="puedePublicar()"
        [disabled]="!articuloId"
        (click)="publicarArticulo()"
      >
        Publicar
      </button>

      <p *ngIf="!puedePublicar()">
        No tienes permiso para publicar artículos.
      </p>
    </div>
  `
})
export class CmsEditorComponent implements OnInit {
  titulo = '';
  contenidoHtml = '';
  previewHtml = '';
  articuloId: number | null = null;

  constructor(
    private http: HttpClient,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      if (params['id']) {
        this.articuloId = +params['id'];

        this.http.get<any>(`${environment.apiUrl}/cms/articulo/${this.articuloId}`)
          .subscribe(r => {
            this.titulo = r.titulo;
            this.contenidoHtml = r.contenido;
            this.actualizarPreview();
          });
      }
    });
  }

  actualizarPreview() {
    this.previewHtml = this.sanitizarHtml(this.contenidoHtml);
  }

  guardarArticulo() {
    const contenidoSanitizado = this.sanitizarHtml(this.contenidoHtml);

    this.http.post(`${environment.apiUrl}/cms/articulo`, {
      titulo: this.titulo,
      contenido: contenidoSanitizado
    }).subscribe(() => {
      alert('Artículo guardado correctamente.');
    });
  }

  publicarArticulo() {
    if (!this.articuloId) {
      return;
    }

    const confirmar = confirm('¿Confirmas que deseas publicar este artículo?');

    if (!confirmar) {
      return;
    }

    this.http.post(`${environment.apiUrl}/cms/articulo/${this.articuloId}/publicar`, {})
      .subscribe(() => {
        alert('Artículo publicado correctamente.');
      });
  }

  puedePublicar(): boolean {
    const role = this.obtenerRolDesdeToken();

    return role === 'ROLE_EDITOR' || role === 'ROLE_ADMIN';
  }

  private sanitizarHtml(html: string): string {
    return DOMPurify.sanitize(html, {
      ALLOWED_TAGS: [
        'p',
        'br',
        'strong',
        'b',
        'em',
        'i',
        'u',
        'ul',
        'ol',
        'li',
        'h2',
        'h3',
        'blockquote',
        'a'
      ],
      ALLOWED_ATTR: [
        'href',
        'title',
        'target',
        'rel'
      ],
      FORBID_TAGS: [
        'script',
        'style',
        'iframe',
        'object',
        'embed'
      ],
      FORBID_ATTR: [
        'onclick',
        'onerror',
        'onload',
        'style'
      ],
      ALLOW_DATA_ATTR: false
    });
  }

  private obtenerRolDesdeToken(): string | null {
    const token = localStorage.getItem('jwt_noticias');

    if (!token) {
      return null;
    }

    try {
      const jwt = token.replace(/^Bearer\s+/i, '');
      const payloadBase64 = jwt.split('.')[1];

      if (!payloadBase64) {
        return null;
      }

      const payloadJson = atob(
        payloadBase64.replace(/-/g, '+').replace(/_/g, '/')
      );

      const payload = JSON.parse(payloadJson);

      return payload.role || null;
    } catch {
      return null;
    }
  }
}