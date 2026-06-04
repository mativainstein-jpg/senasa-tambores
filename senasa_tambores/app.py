from __future__ import annotations

import sys
import traceback
from pathlib import Path

from playwright.sync_api import TimeoutError

from .browser import BrowserSession, profile_location
from .config import AppConfig, TARGET_URL
from .excel_io import load_existing_results, load_tambores, save_results
from .parser import build_error_result, parse_query_text


def resolve_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def run() -> None:
    config = AppConfig(base_dir=resolve_base_dir())

    print("=" * 72)
    print("SENASA Trazabilidad Apicola - Consulta automatica de tambores")
    print("=" * 72)
    print(f"Carpeta de trabajo: {config.base_dir}")
    print(f"Entrada esperada:   {config.input_path}")
    print(f"Salida:             {config.output_path}")
    print(f"Perfil Chromium:    {profile_location(config)}")
    print()

    try:
        tambores = load_tambores(config.input_path)
        results = load_existing_results(config.output_path)
    except Exception as exc:
        print(f"[ERROR] {exc}")
        input("Presione ENTER para cerrar...")
        raise SystemExit(1) from exc

    unique_tambores = list(dict.fromkeys(tambores))
    pending = [
        numero
        for numero in unique_tambores
        if not results.get(numero) or not results[numero].resultado.strip()
    ]
    print(f"Tambores en entrada: {len(tambores)}")
    print(f"Numeros unicos:      {len(unique_tambores)}")
    print(f"Ya procesados:       {len(unique_tambores) - len(pending)}")
    print(f"Pendientes:          {len(pending)}")
    print()

    try:
        save_results(config.output_path, tambores, results)
    except Exception as exc:
        print(f"[ERROR] No se pudo inicializar RESULTADO.xlsx: {exc}")
        print("Verifique que el archivo no este abierto en Excel.")
        input("Presione ENTER para cerrar...")
        raise SystemExit(1) from exc

    with BrowserSession(config) as browser:
        print("[NAVEGADOR] Abriendo Chromium visible...")
        print("[NAVEGADOR] Si no aparece la pantalla correcta, inicie sesion en AFIP manualmente.")
        print(f"[NAVEGADOR] Luego navegue manualmente hasta: {TARGET_URL}")
        browser.open_login_start()
        print()
        input("Cuando este en la pagina de Consulta de Tambores, presione ENTER para comenzar...")
        print()

        if not pending:
            print("[OK] No hay tambores pendientes. RESULTADO.xlsx ya tiene progreso guardado.")
            return

        for index, numero_tambor in enumerate(pending, start=1):
            print(f"[{index}/{len(pending)}] Consultando tambor {numero_tambor}...")

            try:
                detected_text = browser.consultar_tambor(numero_tambor)
                result = parse_query_text(numero_tambor, detected_text)
                print(f"    Resultado: {result.resultado} | Estado: {result.estado or '-'}")
                if result.mensaje:
                    print(f"    Mensaje: {result.mensaje[:250]}")
            except TimeoutError as exc:
                result = build_error_result(numero_tambor, f"Timeout durante la consulta: {exc}")
                print(f"    [TIMEOUT] {result.mensaje}")
            except KeyboardInterrupt:
                print()
                print("[INTERRUMPIDO] Se detuvo el proceso por teclado. Guardando progreso...")
                break
            except Exception as exc:
                result = build_error_result(numero_tambor, f"Error durante la consulta: {exc}")
                print(f"    [ERROR] {result.mensaje}")
                print("    Detalle tecnico:")
                print("    " + traceback.format_exc().replace("\n", "\n    ").strip())

            results[numero_tambor] = result
            try:
                save_results(config.output_path, tambores, results)
                print("    Progreso guardado en RESULTADO.xlsx")
            except Exception as exc:
                print(f"    [ERROR] No se pudo guardar RESULTADO.xlsx: {exc}")
                print("    Cierre RESULTADO.xlsx si esta abierto en Excel y vuelva a ejecutar.")
                break

        print()
        print("[FIN] Procesamiento finalizado.")
        print(f"[FIN] Revise el archivo: {config.output_path}")
