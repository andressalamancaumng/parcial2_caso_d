"""Tests de fuentes confidenciales — Parcial 2 Parte 1"""
import pytest

def test_cifrado_real_vs_base64():
    from src.auth.service import cifrar_fuente, descifrar_fuente
    texto = "Juan Perez, Fiscal"
    cifrado = cifrar_fuente(texto)
    # DOCUMENTA LA VULNERABILIDAD: base64 es reversible sin clave
    import base64
    # Si esto pasa, el "cifrado" es solo base64 — no es cifrado real
    assert base64.b64decode(cifrado).decode() == texto, "base64 es reversible — NO es cifrado seguro"

def test_admin_no_puede_ver_fuentes_en_claro():
    """TODO: verificar que un admin no puede descifrar fuentes de otros periodistas"""
    pass

def test_idor_fuentes():
    """TODO: verificar que periodista_id en query param no puede sobrepasar el del JWT"""
    pass
