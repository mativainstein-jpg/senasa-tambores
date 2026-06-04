# SENASA Trazabilidad Apicola - Consulta de Tambores

Proyecto de consola para automatizar consultas de tambores en SENASA Trazabilidad Apicola.

El programa no automatiza AFIP. Abre Chromium visible, conserva la sesion entre ejecuciones y espera a que el usuario inicie sesion y navegue manualmente hasta la consulta.

## Flujo de uso

1. El programa abre Chromium visible con un perfil persistente local.
2. El usuario inicia sesion manualmente en AFIP.
3. El usuario navega manualmente hasta:

   `https://trazabilidadapicola.senasa.gob.ar/Sur/Tambores/Consulta`

4. El usuario vuelve a la consola y presiona `ENTER`.
5. El programa procesa automaticamente los tambores de `Tambores.xlsx`.
6. El resultado queda en `RESULTADO.xlsx`.

## Archivos principales

- `main.py`: punto de entrada.
- `senasa_tambores/app.py`: orquestacion del flujo.
- `senasa_tambores/browser.py`: automatizacion Playwright con contexto persistente.
- `senasa_tambores/excel_io.py`: lectura y escritura incremental de Excel.
- `senasa_tambores/parser.py`: parsing de mensajes conocidos.
- `requirements.txt`: dependencias Python.
- `instalar_dependencias.bat`: instalacion para ejecutar desde codigo fuente en Windows.
- `ejecutar.bat`: ejecucion desde codigo fuente en Windows.
- `build_exe.bat`: generacion del EXE con PyInstaller.
- `crear_plantilla_tambores.py`: crea una plantilla simple de entrada.

## Requisitos

- Windows 10/11.
- Python 3.12 instalado y disponible como `py -3.12`.
- Acceso manual a AFIP/SENASA desde el equipo.

## Instalacion para ejecutar desde fuente

En una consola de Windows, dentro de la carpeta del proyecto:

```bat
instalar_dependencias.bat
```

Esto crea `.venv`, instala:

- Playwright
- pandas
- openpyxl
- PyInstaller

y descarga Chromium para Playwright.

## Entrada

El archivo de entrada debe llamarse:

```text
Tambores.xlsx
```

Debe estar en la misma carpeta que `main.py` si se ejecuta desde fuente, o en la misma carpeta que `SENASA_Tambores.exe` si se ejecuta el EXE.

La primera columna debe contener los numeros de tambor. Si existe una columna llamada `NumeroTambor`, se usa esa columna.

Formato esperado:

| NumeroTambor |
| --- |
| 123456 |
| 789012 |

Para crear una plantilla:

```bat
.venv\Scripts\python crear_plantilla_tambores.py
```

## Ejecucion desde fuente

```bat
ejecutar.bat
```

## Salida

El programa crea o actualiza:

```text
RESULTADO.xlsx
```

Columnas:

- `NumeroTambor`
- `Resultado`
- `Estado`
- `Mensaje`
- `FechaHora`

El progreso se guarda despues de cada consulta. Si el proceso se corta, al volver a ejecutar se omiten los tambores que ya tengan resultado en `RESULTADO.xlsx`.

## Parsing implementado

Si el texto detectado contiene:

```text
El tambor no le pertenece
```

el resultado sera:

- `Resultado`: `NO_PERTENECE`
- `Estado`: texto dentro de corchetes
- `Mensaje`: mensaje completo detectado

Casos contemplados:

- `Error: [En uso] El tambor no le pertenece.`
- `Error: [Pendiente de Aceptación] El tambor no le pertenece.`
- `Error: [Esperando Certificado de Exportación] El tambor no le pertenece.`

Si el texto no se reconoce:

- `Resultado`: `NO_RECONOCIDO`
- `Estado`: vacio
- `Mensaje`: texto detectado en pantalla

Si ocurre un error operativo o timeout:

- `Resultado`: `ERROR`
- `Estado`: vacio
- `Mensaje`: detalle del error

## Perfil persistente

Playwright usa contexto persistente en:

```text
playwright_profile
```

Esa carpeta queda junto al programa y permite conservar cookies/sesion entre ejecuciones cuando el sitio lo permite.

Si necesita reiniciar la sesion desde cero, cierre el programa y borre la carpeta `playwright_profile`.

## Generar EXE

En Windows:

```bat
build_exe.bat
```

El ejecutable queda en:

```text
dist\SENASA_Tambores.exe
```

Para usarlo:

1. Coloque `Tambores.xlsx` en la misma carpeta que `SENASA_Tambores.exe`.
2. Ejecute `SENASA_Tambores.exe`.
3. Inicie sesion manualmente en AFIP en el Chromium abierto.
4. Navegue a la URL de consulta de SENASA.
5. Presione `ENTER` en la consola.

Decision tecnica: el EXE incluye el codigo Python y el driver de Playwright, pero Chromium se instala con `python -m playwright install chromium` durante la construccion. Para ejecutar en otra PC, instale dependencias o ejecute una instalacion de Playwright/Chromium equivalente en esa maquina.

## Decisiones razonables tomadas

- No se automatiza AFIP ni el ingreso de credenciales.
- Se usa Chromium visible para que el usuario tenga control del login y la navegacion.
- Se usa `launch_persistent_context` para conservar sesion.
- El resultado se guarda despues de cada tambor para poder reanudar.
- Si `RESULTADO.xlsx` ya existe, los tambores ya procesados se saltean.
- Si hay numeros duplicados en `Tambores.xlsx`, se conserva un unico resultado por numero.
- Los selectores de la pagina se buscan por nombres y textos probables (`NumeroTambor`, `tambor`, `Consultar`) para tolerar pequenas variaciones del HTML.
- Si SENASA cambia los nombres de campos o botones, el error se registra como `ERROR` y se puede ajustar `senasa_tambores/browser.py`.

## Problemas frecuentes

### `RESULTADO.xlsx` no se puede guardar

Cierre el archivo en Excel y vuelva a ejecutar. Excel bloquea archivos abiertos para escritura.

### Chromium no abre

Ejecute:

```bat
python -m playwright install chromium
```

dentro del entorno donde se instalo Playwright.

### El programa no encuentra el campo o boton

Confirme que la pagina abierta sea exactamente:

```text
https://trazabilidadapicola.senasa.gob.ar/Sur/Tambores/Consulta
```

Si la pagina fue modificada por SENASA, ajuste los selectores en `senasa_tambores/browser.py`.
