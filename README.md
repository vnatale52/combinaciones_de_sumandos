## 📘 Descripción General

Este programa utiliza la librería **Google OR-Tools** (módulo `cp_model`) para encontrar **todas las combinaciones posibles de sumandos** que sumen un valor objetivo determinado.  
Está diseñado especialmente para el **formato regional argentino**, utilizando **coma (`,`) como separador decimal** y sin utilizar el punto (`.`) como separador de miles.

Ejemplo:  
✅ Correcto → `3,50`  
❌ Incorrecto → `3.50` o `12.345`  

---

🧮 Cantidad de combinaciones posibles

El número total de combinaciones que el solver debe evaluar crece exponencialmente con la cantidad de sumandos.
Dado que cada sumando puede estar incluido (1) o excluido (0) en una combinación, el total de combinaciones posibles se calcula como:

Combinaciones totales =  2 elevado a la n  ,    donde  n  es la cantidad de sumandos.

Cantidad de sumandos (n)	
10	 2¹⁰	   1.024            Total de combinaciones posibles
20	 2²⁰	   1.048.576        Total de combinaciones posibles
30	 2³⁰	   1.073.741.824    Total de combinaciones posibles
40	 2⁴⁰	   1.099.511.627.776   Total de combinaciones posibles
50	 2⁵⁰	   1.125.899.906.842.624    Total de combinaciones posibles
100	 2¹⁰⁰   ≈ 1,27 × 10³⁰     Total de combinaciones posibles

Esto significa que con apenas 30 o 40 sumandos, la cantidad de combinaciones posibles ya supera miles de millones, por lo que el tiempo de ejecución puede aumentar considerablemente.
OR-Tools maneja eficientemente este crecimiento gracias a su motor de búsqueda de restricciones, pero se recomienda filtrar o limitar el conjunto de sumandos siempre que sea posible.

## 📦 Archivos incluidos

- `combinador_sumandos.py` → código principal del programa.  
- `README.md` → este documento.  
- `sumandos.txt` → archivo de ejemplo con sumandos.

---

## 📄 Ejemplo de archivo `sumandos.txt`

```
1,100
2,950
3,300
4,000
5,000
6,000
7,000
8,100
8,100
9,000
10,234
```

---

## 🚀 Cómo ejecutar

1. Instalar Python 3.9 o superior.  
2. Instalar OR-Tools (una sola vez):
   ```bash
   pip install ortools
   ```
3. Colocar `combinador_sumandos.py` y `sumandos.txt` en la misma carpeta.
4. Ejecutar:
   ```bash
   python combinador_sumandos.py
   ```

El programa te pedirá:  
- El nombre del archivo de sumandos (por ejemplo, `sumandos.txt`)  
- El valor objetivo (por ejemplo, `19,35`)  
- El margen de error permitido (por ejemplo, `0,02`)

---

## ⚙️ Funcionalidades destacadas

✅ **Admite margen de error configurable (0 o positivo)**  
   - Si el margen es `0`, solo se aceptan coincidencias exactas.  
   - Si es positivo (ejemplo: `0,05`), se aceptan resultados entre `(objetivo - 0,05)` y `(objetivo + 0,05)`.

✅ **Detecta y advierte valores duplicados**  
   - Ejemplo de aviso:  
     ```
     ⚠️  Atención: Se detectaron valores duplicados en el archivo:
        - 8,100 aparece 2 veces
        Estos duplicados pueden generar combinaciones equivalentes.
     ```

✅ **Informa combinaciones equivalentes**  
   - Si los duplicados generan combinaciones diferentes pero equivalentes, se indica explícitamente:  
     ```
     ⚠️  Se detectaron combinaciones equivalentes:
        - Solución 1, Solución 2
     ```

✅ **Colores en consola (ANSI)**  
   - 🟢 Verde → Solución exacta  
   - 🟡 Amarillo → Solución dentro del margen permitido  
   - 🔴 Rojo → Solución fuera del rango permitido

✅ **Informe completo en archivo de salida**  
   El archivo de resultados (`soluciones_sumandos.txt`) incluye:  
   - Fecha y hora de inicio y fin  
   - Tiempo total de ejecución  
   - Margen utilizado y rango de aceptación  
   - Contenido original del archivo `sumandos.txt`  
   - Detección de duplicados  
   - Todas las combinaciones halladas (en columna, con etiqueta `[EXACTA]` o `[MARGEN]`)  
   - Combinaciones equivalentes (si existen)

✅ **Mensaje informativo en caso sin solución**  
   Si el solver no encuentra ninguna combinación válida:
   ```
   Solver determinó que el problema no tiene solución, dado que no pudo encontrar una solución exacta al centavo.
   (Solo un centavo de diferencia en el objetivo pudo haber generado dicho resultado vacío.)
   ```

---

## 💬 Ejemplo de salida en consola

```
--- Solución 1 [EXACTA] ---
   2,95
   3,30
   5,00
   8,10
Suma total: 19,35
✅ Coincide exactamente con el objetivo (sin margen aplicado).

--- Solución 2 [MARGEN] ---
   1,10
   2,95
   3,30
   5,00
   7,00
Suma total: 19,34
✔️ Se utilizó el margen de error (dentro del rango permitido).
```

---

## 🧮 Rango del margen de error

El margen de error puede ser **cero o un número positivo**.  
Por ejemplo, si el **objetivo es 100** y el **margen es 5**, se consideran válidas todas las combinaciones cuya suma sea **mayor o igual a 95** y **menor o igual a 105**.

Si el usuario ingresa un margen negativo, el programa:  
- Muestra una advertencia.  
- Permite decidir si usar el valor absoluto o establecer margen cero.

En todos los casos, se deja constancia de la decisión del usuario tanto en consola como en el archivo de salida.

---

## 🧾 Archivo de salida (`soluciones_sumandos.txt`)

Ejemplo del encabezado:

```
🔢 RESULTADOS DE COMBINACIONES GOOGLE OR-TOOLS (Argentina)
================================================================================
🗓️ Inicio: 2025-11-10 20:33:21
🕕 Fin: 2025-11-10 20:33:24
🎯 Objetivo: 19,35
💰 Margen ingresado originalmente: 0,02
💰 Margen final utilizado: ±0,02 pesos (±2 centavos)
📈 Rango válido: desde 19,33 hasta 19,37
⚙️ Condición aplicada: objetivo - margen ≤ suma_total ≤ objetivo + margen
🕒 Tiempo total: 2,731 segundos
================================================================================
```

---

## 🧠 Lógica interna del solver

1. Se convierte cada valor a centavos para evitar errores de redondeo.  
2. Se crea una variable booleana para cada sumando (`1` = incluido, `0` = excluido).  
3. Se define la restricción de suma según el margen configurado.  
4. Se exploran **todas las combinaciones posibles** con `SearchForAllSolutions`.  
5. Se almacenan las soluciones y se detectan equivalentes mediante agrupación por conjunto.

---

## ⚠️ Advertencias importantes

- **No uses el punto como separador de miles.**
  - Ejemplo incorrecto: `12.345`  
  - Ejemplo correcto: `12345`
- **Usa coma decimal.**
  - Ejemplo correcto: `3,25`
- Un margen demasiado pequeño puede causar que no se encuentren soluciones debido a errores de redondeo.

---

## 📊 Colores en consola

| Estado | Color | Descripción |
|--------|--------|-------------|
| EXACTA | 🟢 Verde | Coincide exactamente con el objetivo |
| MARGEN | 🟡 Amarillo | Dentro del margen permitido |
| NO VÁLIDA | 🔴 Rojo | Fuera del rango de error permitido |

---

## 📁 Resultados generados

El programa genera automáticamente un archivo:

```
soluciones_<nombre_del_archivo>.txt
```

Ejemplo:
```
soluciones_sumandos.txt
```

El archivo incluye todas las soluciones, duplicados detectados, equivalencias y trazabilidad completa.

---

## 🧑‍💻 Créditos

**Código realizado por Vincenzo Natale – vnatale52@gmail.com**  
Basado en Google OR-Tools (`from ortools.sat.python import cp_model`).

© 2025 Vincenzo Natale. Todos los derechos reservados.
