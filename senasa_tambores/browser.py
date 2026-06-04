from __future__ import annotations

from pathlib import Path

from playwright.sync_api import BrowserContext, Error, Page, TimeoutError, sync_playwright

from .config import TARGET_URL, AppConfig


INPUT_SELECTORS = [
    "#NumeroTambor",
    "input[name='NumeroTambor']",
    "input[id*='NumeroTambor' i]",
    "input[name*='NumeroTambor' i]",
    "input[id*='tambor' i]",
    "input[name*='tambor' i]",
    "input[placeholder*='tambor' i]",
    "input[type='text']",
    "input:not([type])",
]

SUBMIT_SELECTORS = [
    "button:has-text('Consultar')",
    "input[type='submit'][value*='Consultar' i]",
    "button[type='submit']",
    "input[type='submit']",
    "a:has-text('Consultar')",
]

MESSAGE_SELECTORS = [
    ".alert",
    ".validation-summary-errors",
    ".field-validation-error",
    ".text-danger",
    "[role='alert']",
    ".error",
    ".mensaje",
    ".message",
    ".toast",
    "table",
]


class BrowserSession:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._playwright = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    def __enter__(self) -> "BrowserSession":
        self.config.profile_dir.mkdir(parents=True, exist_ok=True)
        self._playwright = sync_playwright().start()
        self.context = self._playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.config.profile_dir),
            headless=False,
            viewport={"width": 1366, "height": 768},
            accept_downloads=True,
            args=["--start-maximized"],
        )
        self.context.set_default_timeout(self.config.default_timeout_ms)
        self.page = self._get_or_create_page(self.context)
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        if self.context:
            self.context.close()
        if self._playwright:
            self._playwright.stop()

    def open_login_start(self) -> None:
        page = self.require_page()
        try:
            page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=30_000)
        except TimeoutError:
            pass

    def consultar_tambor(self, numero_tambor: str) -> str:
        page = self.require_page()
        self._fill_tambor_input(page, numero_tambor)
        self._click_submit(page)
        self._wait_after_submit(page)
        return self._extract_detected_text(page)

    def require_page(self) -> Page:
        if not self.page:
            raise RuntimeError("No hay una pagina activa de Chromium.")
        return self.page

    @staticmethod
    def _get_or_create_page(context: BrowserContext) -> Page:
        if context.pages:
            return context.pages[0]
        return context.new_page()

    def _fill_tambor_input(self, page: Page, numero_tambor: str) -> None:
        for selector in INPUT_SELECTORS:
            locator = page.locator(selector).first
            try:
                if locator.count() and locator.is_visible() and locator.is_enabled():
                    locator.fill("")
                    locator.fill(numero_tambor)
                    return
            except (Error, TimeoutError):
                continue

        label_patterns = ["Numero Tambor", "Numero de Tambor", "Número Tambor", "Número de Tambor", "Tambor"]
        for label in label_patterns:
            locator = page.get_by_label(label, exact=False).first
            try:
                if locator.count() and locator.is_visible() and locator.is_enabled():
                    locator.fill("")
                    locator.fill(numero_tambor)
                    return
            except (Error, TimeoutError):
                continue

        raise TimeoutError("No se encontro un campo visible para ingresar el NumeroTambor.")

    def _click_submit(self, page: Page) -> None:
        for selector in SUBMIT_SELECTORS:
            locator = page.locator(selector).first
            try:
                if locator.count() and locator.is_visible() and locator.is_enabled():
                    locator.click()
                    return
            except (Error, TimeoutError):
                continue

        raise TimeoutError("No se encontro un boton visible para consultar.")

    def _wait_after_submit(self, page: Page) -> None:
        try:
            page.wait_for_load_state("networkidle", timeout=self.config.post_submit_timeout_ms)
        except TimeoutError:
            pass

        try:
            page.wait_for_timeout(750)
        except Error:
            pass

    def _extract_detected_text(self, page: Page) -> str:
        chunks: list[str] = []

        for selector in MESSAGE_SELECTORS:
            locator = page.locator(selector)
            try:
                count = min(locator.count(), 8)
                for index in range(count):
                    item = locator.nth(index)
                    if item.is_visible():
                        text = item.inner_text(timeout=2_000).strip()
                        if text:
                            chunks.append(text)
            except (Error, TimeoutError):
                continue

        try:
            body_text = page.locator("body").inner_text(timeout=5_000).strip()
            if body_text:
                chunks.append(body_text)
        except (Error, TimeoutError):
            pass

        return "\n".join(dict.fromkeys(chunks))


def profile_location(config: AppConfig) -> Path:
    return config.profile_dir
