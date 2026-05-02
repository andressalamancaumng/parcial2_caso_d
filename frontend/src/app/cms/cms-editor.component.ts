import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../shared/services/auth.service';
import { environment } from '../../environments/environment';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser'; // Importante para [innerHTML]
import * as DOMPurify from 'dompurify';

@Component({
  selector: 'app-cms-editor',
  template: `
    <div class="cms-editor">
      <h2>Editor CMS — Noticias 360</h2>
      <input [(ngModel)]="titulo" name="titulo" placeholder="Titulo" />

      <!-- Uso de SafeHtml para el preview -->
      <div class="preview" [innerHTML]="previewHtml"></div>

      <textarea [(ngModel)]="contenidoHtml" name="contenido"
                (ngModelChange)="actualizarPreview()" rows="15"
                placeholder="Contenido HTML..."></textarea>

      <button (click)="guardarArticulo()">Guardar Borrador</button>
      
      <!-- Alineación de roles con el Backend (editor, admin) -->
      <button *ngIf="auth.tieneRol(['editor', 'admin'])" 
              (click)="publicarArticulo()">Publicar</button>

      <div>
        <h3>Fuentes Confidenciales</h3>
        <ul>
          <li *ngFor="let f of fuentes">{{ f.nombre }} — {{ f.contacto }}</li>
        </ul>
        <button (click)="cargarMisFuentes()">Cargar Mis Fuentes</button>
      </div>
    </div>
  `
})
export class CmsEditorComponent implements OnInit {
  
  titulo = '';
  contenidoHtml = '';
  previewHtml: SafeHtml = ''; // Cambiado a SafeHtml
  fuentes: any[] = [];
  articuloId: number | null = null;

  constructor(
    private http: HttpClient,
    private route: ActivatedRoute,
    public auth: AuthService,
    private sanitizer: DomSanitizer // Inyectado para bypass de seguridad post-sanitización
  ) {}

  ngOnInit() {
    // AQUÍ ESTÁ LA LÍNEA 57 CORREGIDA
    this.route.queryParams.subscribe((params: any) => {
      if (params['id']) {
        this.articuloId = +params['id'];
        
        this.http.get<any>(`${environment.apiUrl}/cms/articulo/${this.articuloId}`)
          // AQUÍ ESTÁ LA LÍNEA 62 CORREGIDA
          .subscribe((r: any) => {
            this.titulo = r.titulo;
            this.contenidoHtml = r.contenido;
            this.actualizarPreview();
          });
      }
    });
  }

  actualizarPreview() {
    // 1. Sanitización con DOMPurify (Punto 3.2.c)
    const cleanHtml = DOMPurify.sanitize(this.contenidoHtml, {
      ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'h1', 'h2'],
      ALLOWED_ATTR: ['href']
    });
    
    // 2. Avisar a Angular que el HTML ya es seguro
    this.previewHtml = this.sanitizer.bypassSecurityTrustHtml(cleanHtml);
  }

  guardarArticulo() {
    // Sanitización antes de enviar al servidor (Defensa en profundidad)
    const contenidoSeguro = DOMPurify.sanitize(this.contenidoHtml);

    this.http.post(`${environment.apiUrl}/cms/articulo`, {
      titulo: this.titulo,
      contenido: contenidoSeguro
      // AQUÍ ESTÁ LA LÍNEA 88 CORREGIDA
    }).subscribe((r: any) => alert('Articulo guardado correctamente'));
  }

  publicarArticulo() {
    if (!this.articuloId) return;
    
    if(confirm('¿Estás seguro de que deseas publicar este artículo?')) {
      this.http.post(`${environment.apiUrl}/cms/articulo/${this.articuloId}/publicar`, {})
        .subscribe(() => alert('Articulo publicado'));
    }
  }

  cargarMisFuentes() {
    this.http.get<any>(`${environment.apiUrl}/fuentes`)
      // AQUÍ ESTÁ LA LÍNEA 105 CORREGIDA
      .subscribe((data: any) => this.fuentes = data);
  }
}