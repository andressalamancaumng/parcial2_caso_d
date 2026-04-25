import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
import { AuthService } from '../shared/services/auth.service';
import { environment } from '../../environments/environment';

@Component({
  selector: 'app-cms-editor',
  template: `
    <div class="cms-editor">
      <h2>Editor CMS — Noticias 360</h2>
      <input [(ngModel)]="titulo" name="titulo" placeholder="Titulo" />

      <!-- ← VULNERABLE: bypassSecurityTrustHtml sin DOMPurify -->
      <div class="preview" [innerHTML]="previewHtml"></div>

      <textarea [(ngModel)]="contenidoHtml" name="contenido"
                (ngModelChange)="actualizarPreview()" rows="15"
                placeholder="Contenido HTML..."></textarea>

      <!-- ← VULNERABLE: autorId editable — no viene del JWT -->
      <input [(ngModel)]="autorId" name="autorId" type="number" placeholder="ID del autor" />

      <button (click)="guardarArticulo()">Guardar Borrador</button>
      <!-- ← VULNERABLE: boton publicar visible para todos los roles -->
      <button (click)="publicarArticulo()">Publicar</button>

      <!-- ← VULNERABLE: boton carga todas las fuentes sin filtro -->
      <div>
        <h3>Fuentes Confidenciales</h3>
        <ul>
          <li *ngFor="let f of fuentes">{{ f.nombre }} — {{ f.contacto }}</li>
        </ul>
        <button (click)="cargarTodasFuentes()">Cargar Todas las Fuentes</button>
      </div>
    </div>
  `
})
export class CmsEditorComponent implements OnInit {
  titulo = '';
  contenidoHtml = '';
  previewHtml: SafeHtml = '';
  autorId: number | null = null;  // ← editable
  fuentes: any[] = [];
  articuloId: number | null = null;

  constructor(
    private http: HttpClient,
    private route: ActivatedRoute,
    private sanitizer: DomSanitizer,
    private auth: AuthService
  ) {}

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      if (params['id']) {
        this.articuloId = +params['id'];
        // ← VULNERABLE: sin prefijo Bearer (delegado al interceptor, pero el interceptor tampoco lo pone)
        this.http.get<any>(`${environment.apiUrl}/cms/articulo/${this.articuloId}`)
          .subscribe(r => {
            this.titulo = r.titulo;
            this.contenidoHtml = r.contenido;
            this.autorId = r.autor_id;
            this.actualizarPreview();
          });
      }
    });
  }

  actualizarPreview() {
    // ← VULNERABLE: bypassSecurityTrustHtml sin sanitizar con DOMPurify primero
    this.previewHtml = this.sanitizer.bypassSecurityTrustHtml(this.contenidoHtml);
  }

  guardarArticulo() {
    this.http.post(`${environment.apiUrl}/cms/articulo`, {
      titulo: this.titulo,
      contenido: this.contenidoHtml,
      autor_id: this.autorId        // ← editable — suplantacion de autoria
    }).subscribe(r => console.log('Guardado:', r));
  }

  publicarArticulo() {
    if (!this.articuloId) return;
    // ← VULNERABLE: sin confirmacion
    this.http.post(`${environment.apiUrl}/cms/articulo/${this.articuloId}/publicar`, {})
      .subscribe(() => alert('Articulo publicado'));
  }

  cargarTodasFuentes() {
    // ← VULNERABLE: periodista_id=0 carga todas las fuentes
    this.http.get<any>(`${environment.apiUrl}/fuentes?periodista_id=0`)
      .subscribe(data => this.fuentes = data);
  }
}
