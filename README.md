# Combinatoria de Sumandos — Versión corregida

## 📘 Descripción General

Este programa encuentra **combinaciones de sumandos** que sumen un valor objetivo, con soporte explícito para el **formato numérico argentino** (coma decimal y sin puntos como separador de miles).

Cambios y correcciones en esta versión:
- Se verifica explícitamente el **formato** del archivo `sumandos.txt` (se informa por línea si contiene puntos, comas, etc.).
- Se verifica el formato ingresado para **objetivo** y **margen** y se registra el resultado del control. Si contienen puntos como separador de miles se intentará conversión automática, pero se informará. 
- El **header** y textos han sido actualizados: *"Combinador de Sumandos"* → **"Combinatoria de Sumandos"**.
- La leyenda por defecto cuando **no** se detectan combinaciones equivalentes ahora es:  
  **"No se detectaron combinaciones equivalentes generadas por sumandos que estén repetidos."**
- Al mostrar la **Suma total** de cada solución se indica si la suma fue *EXACTA* o *HALLADA APLICANDO MARGEN*.
- Se muestra el **tiempo total** tanto en segundos como en formato `hh:mm:ss`.
- En la versión web (Pyodide) se eliminó la visualización inicial de secciones superpuestas y se incorporó un control de formato y observaciones en la salida.

## 📦 Archivos incluidos

- `combinación_de_sumandos.py` → código principal actualizado (Python + OR-Tools).
- `index.html` → interfaz web para ejecutar con Pyodide (actualizada).
- `README.md` → este documento.
- `sumandos.txt` → archivo de ejemplo (mantener en formato argentino).

## 🧾 Control de formato (qué se verifica)

- No usar punto (`.`) como separador de miles en `sumandos.txt` ni en los campos ingresados. Si se detecta, se informa y se intentará conversión automática para no interrumpir la ejecución.
- Usar coma (`,`) como separador decimal cuando corresponda (por ejemplo `3,50`). Los enteros sin separadores también son aceptados.

## 🚀 Cómo ejecutar (localmente)

1. Tener Python 3.9+ e instalar OR-Tools:
   ```bash
   pip install ortools
   ```
2. Colocar `combinación_de_sumandos.py` y `sumandos.txt` en la misma carpeta.
3. Ejecutar:
   ```bash
   python "combinación_de_sumandos.py"
   ```
4. Responder las solicitudes: nombre del archivo, objetivo (ej. `19,35`) y margen (ej. `0,02`).

## 📄 Ejemplo de salida relevante

En los resultados la sección de **Detalles del cálculo** incluirá el control de formato aplicado y el **Tiempo total** en segundos y `hh:mm:ss`. Cada solución mostrará la suma total acompañada por `(EXACTO)` o `(HALLADA APLICANDO MARGEN)` según corresponda.

## 🧑‍💻 Créditos

**Código realizado por Vincenzo Natale – vnatale52@gmail.com**  
© 2025 Vincenzo Natale. Todos los derechos reservados.

## 📈 Complejidad Computacional: Crecimiento Exponencial

El algoritmo de Google OR-Tools utilizado en este programa debe evaluar **todas las combinaciones posibles** de sumandos para encontrar las que cumplan con el objetivo. Este problema tiene una complejidad computacional **exponencial** de O(2^n), donde n es la cantidad de sumandos.

### Cantidad de combinaciones a evaluar según número de sumandos:

| Sumandos | Combinaciones Posibles | Notación Científica | Tiempo Estimado* |
|----------|------------------------|---------------------|------------------|
| 10       | 1.024                  | 10³                 | Instantáneo      |
| 20       | 1.048.576              | ~10⁶                | < 1 segundo      |
| 30       | 1.073.741.824          | ~10⁹                | Segundos         |
| 40       | 1.099.511.627.776      | ~10¹²               | Minutos          |
| 50       | 1.125.899.906.842.624  | ~10¹⁵               | Horas/Días       |
| 80       | 1,21 × 10²⁴            | ~10²⁴               | Años             |
| 100      | 1,27 × 10³⁰            | ~10³⁰               | Inviable         |

\* *Los tiempos son aproximados y dependen del hardware, optimizaciones del solver y características específicas del problema.*

### Consideraciones importantes:

- **10-20 sumandos**: Ejecución prácticamente instantánea, ideal para pruebas.
- **30 sumandos**: Procesamiento rápido, apto para uso regular.
- **40 sumandos**: Puede tomar varios minutos dependiendo del hardware.
- **50+ sumandos**: El tiempo de cálculo crece exponencialmente. Para conjuntos grandes, considere filtrar o reducir el espacio de búsqueda.
- **80-100 sumandos**: Computacionalmente inviable con este enfoque exhaustivo. Se requeriría usar heurísticas o algoritmos de aproximación.

### Optimizaciones del algoritmo:

Google OR-Tools implementa varias optimizaciones internas:
- **Poda de búsqueda**: Descarta ramas que no pueden conducir a soluciones.
- **Propagación de restricciones**: Reduce el espacio de búsqueda mediante inferencias lógicas.
- **Búsqueda inteligente**: Prioriza exploración de combinaciones más prometedoras.

Estas optimizaciones permiten que el algoritmo sea más eficiente que una búsqueda de fuerza bruta pura, pero la complejidad exponencial subyacente permanece.

## ✨ Actualización reciente:
- **Validación estricta de formato argentino**: El programa ahora solicita al usuario que reingrese datos si detecta formato incorrecto (uso de punto como separador de miles).
- **Tiempo total mejorado**: Se muestra tanto en segundos como en formato hh:mm:ss adaptado a la configuración regional argentina.
- **Documentación sobre complejidad**: Nueva sección que explica el crecimiento exponencial del algoritmo y las combinaciones para diferentes cantidades de sumandos (10, 20, 30, 40, 50, 80, 100).



#  English version 
## Overview

Combinatoria de Sumandos is a mathematical optimization application that finds combinations of numbers (sumandos) that add up to a target value within a specified margin of error. The application is designed specifically to handle Argentine number formatting (comma as decimal separator, no dots as thousand separators).

The system uses Google OR-Tools' CP-SAT solver to efficiently find all possible combinations and provides both a command-line Python interface and a web-based interface powered by Pyodide for in-browser execution.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (November 2025)

### Validation Strict Format
- **Strict Argentine format validation**: The Python CLI now validates input format strictly and requests users to re-enter data if incorrect format is detected
- **Error messages**: Clear error messages when point (.) is used as thousand separator or invalid formats are detected
- **Input loops**: While loops ensure users provide correct format before proceeding with calculations

### Time Display Enhancement
- **Dual format display**: Time is now shown in both seconds (with Argentine decimal format using comma) and hh:mm:ss format
- **Python CLI**: Shows time as "X,XXX segundos | HH:MM:SS (hh:mm:ss)"
- **Web version**: Shows time as "X.XXX segundos | HH:MM:SS (hh:mm:ss)"
- **Time formatting**: Custom calculation ensures proper HH:MM:SS format regardless of execution duration

### Documentation Updates
- **Computational complexity section**: New comprehensive section in README.md explaining exponential growth O(2^n)
- **Combination tables**: Detailed table showing number of combinations for 10, 20, 30, 40, 50, 80, and 100 sumandos
- **Performance estimates**: Time estimates for different quantities of sumandos
- **Algorithm optimizations**: Explanation of Google OR-Tools internal optimizations (pruning, constraint propagation, intelligent search)

### Bug Fixes
- **Web version JavaScript**: Fixed critical ReferenceError in margin assignment that prevented calculations
- **Format control consolidation**: Improved control_formatos handling across Python codebase

### User Experience Enhancements (November 2025)
- **Use Cases Section**: Added collapsible section in web interface showing 10 practical use cases (accounting reconciliation, audit, duplicate detection, cash reconciliation, etc.)
- **Example Files**: Created downloadable example files:
  - `sumandos_ejemplo.txt`: 20 sample invoices for testing
  - `ejemplo_instrucciones.txt`: Complete instructions for using the example
- **Download Functionality**: Added JavaScript functions to download example files directly from the browser without requiring server access
- **Interactive UI**: Implemented expandable/collapsible use cases section with smooth CSS transitions

## System Architecture

### Application Structure

**Dual-Interface Design**
- **Python CLI (`combinación_de_sumandos.py`)**: Standalone command-line tool for local execution
- **Web Interface (`index.html`)**: Browser-based interface using Pyodide to run Python code client-side without a backend server

The application follows a single-file architecture for the CLI version, containing all logic within one Python script for simplicity and portability.

### Core Solver Architecture

**Constraint Programming Approach**
- Uses Google OR-Tools CP-SAT solver for combinatorial optimization
- Custom solution collector (`ColectorDeSoluciones`) that extends `cp_model.CpSolverSolutionCallback`
- Implements binary decision variables (0 or 1) for each number to indicate inclusion/exclusion in combinations
- Converts floating-point decimal numbers to integers (multiplied by 100) to work with CP-SAT's integer-only constraint system

**Number Format Validation**
- Custom validation function (`verificar_formato_linea`) to ensure Argentine number format compliance
- Automatic detection and attempted conversion of incorrect formats (e.g., dots as thousand separators)
- Format validation applied to both input file and user-entered target/margin values

### Processing Pipeline

1. **Input Loading**: Read numbers from `sumandos.txt` file with format validation per line
2. **Conversion**: Transform decimal numbers to integers (×100) for solver compatibility
3. **Model Building**: Create CP-SAT model with binary variables and sum constraint
4. **Solution Search**: Enumerate all valid combinations using the constraint solver
5. **Duplicate Detection**: Identify equivalent solutions caused by repeated input values
6. **Output Formatting**: Present results with timing information and exact/margin-based match indicators

### Web Architecture (Pyodide)

**Client-Side Python Execution**
- Pyodide loads the full Python interpreter in WebAssembly
- OR-Tools library loaded dynamically in the browser
- No backend server required - all computation happens client-side
- File upload handled through browser File API
- Results downloadable as text files directly from browser

**UI Components**
- Sticky navigation bar for quick access to downloads
- Animated gradient header
- File upload input for `sumandos.txt`
- Text inputs for target value and margin
- Results display area with monospace formatting
- Animated download button for saving results

### Internationalization & Localization

**Argentine Locale Support**
- Explicit locale configuration attempts (`es_AR.UTF-8`, `es_ES.UTF-8`)
- Comma (,) as decimal separator
- No dots as thousand separators
- Validation and automatic correction with user notification

### Output Features

**Comprehensive Reporting**
- Format validation details for each input line
- Total execution time in both seconds and `hh:mm:ss` format
- Solution counter with sum totals
- Indicator for exact matches vs. margin-based matches
- Detection and reporting of equivalent combinations from duplicate inputs

### Performance Considerations

**Integer Arithmetic**
- Floating-point numbers converted to integers to avoid precision issues
- All calculations performed in integer space (cents instead of currency units)
- Results converted back to decimal format for display

**Solution Enumeration**
- Callback-based solution collection allows handling large solution sets
- All solutions stored in memory for post-processing (duplicate detection)

## External Dependencies

### Python Libraries

**Google OR-Tools (`ortools`)**
- Core dependency for constraint programming
- Specifically uses `ortools.sat.python.cp_model` module
- CP-SAT solver provides efficient combinatorial optimization
- Version requirement: Compatible with Python 3.9+

**Standard Library Modules**
- `locale`: Number format localization (Argentine format)
- `os`: File system operations
- `time`: Performance timing measurements
- `datetime`/`timedelta`: Time formatting for results
- `collections.Counter`/`defaultdict`: Duplicate detection logic

### Web Technologies

**Pyodide**
- WebAssembly-based Python runtime for browsers
- Enables client-side Python execution without server
- Loads OR-Tools package dynamically

**Frontend Stack**
- Pure HTML5/CSS3/JavaScript (no frameworks)
- Vanilla JavaScript for file handling and DOM manipulation
- CSS animations for visual feedback (gradient header, glowing download button)

### File System

**Input File**
- `sumandos.txt`: Plain text file with one number per line
- Argentine number format required (comma decimal separator)
- Supports positive and negative numbers
- Example file included with 20 sample values

**No Database**
- Application is stateless
- All data loaded from text files
- Results exported as downloadable text files
- No persistent storage required