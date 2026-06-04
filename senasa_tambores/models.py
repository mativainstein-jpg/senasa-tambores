from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TamborResult:
    numero_tambor: str
    resultado: str
    estado: str
    mensaje: str
    fecha_hora: str

    def to_row(self) -> dict[str, str]:
        return {
            "NumeroTambor": self.numero_tambor,
            "Resultado": self.resultado,
            "Estado": self.estado,
            "Mensaje": self.mensaje,
            "FechaHora": self.fecha_hora,
        }
