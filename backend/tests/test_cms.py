"""Tests del CMS — Parcial 2 Parte 1"""
import pytest

def test_publicar_sin_rol_editor():
    """TODO: verificar que un PERIODISTA no puede publicar directamente"""
    pass

def test_autor_id_viene_del_jwt():
    """TODO: verificar que el autor_id del body es ignorado y se usa el del JWT"""
    pass

def test_contenido_html_sanitizado():
    """TODO: verificar que <script>alert(1)</script> en contenido es sanitizado"""
    pass
