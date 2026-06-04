from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


TARGET_URL = "https://trazabilidadapicola.senasa.gob.ar/Sur/Tambores/Consulta"


@dataclass(frozen=True)
class AppConfig:
    base_dir: Path
    input_filename: str = "Tambores.xlsx"
    output_filename: str = "RESULTADO.xlsx"
    profile_dirname: str = "playwright_profile"
    default_timeout_ms: int = 15_000
    post_submit_timeout_ms: int = 20_000

    @property
    def input_path(self) -> Path:
        return self.base_dir / self.input_filename

    @property
    def output_path(self) -> Path:
        return self.base_dir / self.output_filename

    @property
    def profile_dir(self) -> Path:
        return self.base_dir / self.profile_dirname
