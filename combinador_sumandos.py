from ortools.sat.python import cp_model
import locale
import os
import time
from datetime import datetime
from collections import Counter, defaultdict

# Configuración regional Argentina (coma decimal)
try:
    locale.setlocale(locale.LC_NUMERIC, 'es_AR.UTF-8')
except Exception:
    try:
        locale.setlocale(locale.LC_NUMERIC, 'es_ES.UTF-8')
    except Exception:
        locale.setlocale(locale.LC_NUMERIC, '')

# Colores ANSI
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


class ColectorDeSoluciones(cp_model.CpSolverSolutionCallback):
    """Recolecta todas las soluciones halladas por el solver."""
    def __init__(self, variables_decision, sumandos_originales, sumandos_enteros):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__vars = variables_decision
        self.__sumandos_originales = sumandos_originales
        self.__sumandos_enteros = sumandos_enteros
        self.soluciones = []

    def on_solution_callback(self):
        combinacion = []
        suma = 0
        for i, var in enumerate(self.__vars):
            if self.Value(var) == 1:
                combinacion.append(self.__sumandos_originales[i])
                suma += self.__sumandos_enteros[i]
        self.soluciones.append((combinacion, suma / 100.0))


def resolver_con_margen(sumandos, objetivo, margen):
    """Resuelve el problema considerando un margen de error simétrico."""
    objetivo_entero = int(round(objetivo * 100))
    margen_entero = int(round(margen * 100))
    sumandos_enteros = [int(round(s * 100)) for s in sumandos]

    modelo = cp_model.CpModel()
    x = [modelo.NewBoolVar(f'x_{i}') for i in range(len(sumandos_enteros))]
    suma_total = sum(sumandos_enteros[i] * x[i] for i in range(len(sumandos_enteros)))

    if margen == 0:
        modelo.Add(suma_total == objetivo_entero)
        condicion_margen = "suma_total == objetivo"
    else:
        modelo.Add(suma_total >= objetivo_entero - margen_entero)
        modelo.Add(suma_total <= objetivo_entero + margen_entero)
        condicion_margen = "objetivo - margen ≤ suma_total ≤ objetivo + margen"

    solver = cp_model.CpSolver()
    colector = ColectorDeSoluciones(x, sumandos, sumandos_enteros)

    inicio = time.time()
    status = solver.SearchForAllSolutions(modelo, colector)
    fin = time.time()

    tiempo_total = fin - inicio
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        return colector.soluciones, tiempo_total, condicion_margen
    else:
        return None, tiempo_total, condicion_margen


def cargar_sumandos(nombre_archivo):
    """Carga los sumandos desde un archivo en formato argentino (coma decimal)."""
    if not os.path.exists(nombre_archivo):
        print(f"❌ El archivo '{nombre_archivo}' no existe.")
        return None, None, "", []

    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()

    sumandos = []
    for linea in contenido.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        try:
            val = float(linea.replace('.', '').replace(',', '.'))
            sumandos.append(val)
        except ValueError:
            print(f"⚠️  Línea ignorada (no numérica): {linea}")

    duplicados = [v for v, c in Counter(sumandos).items() if c > 1]
    aviso = ""
    if duplicados:
        aviso = "\n⚠️  Atención: Se detectaron valores duplicados en el archivo:\n"
        for val in duplicados:
            aviso += f"   - {locale.format_string('%.3f', val)} aparece {sumandos.count(val)} veces\n"
        aviso += "   Estos duplicados pueden generar combinaciones equivalentes.\n"
        print(aviso)
    else:
        print(GREEN + "✅ No se detectaron valores duplicados en el archivo." + RESET)
    return sumandos, contenido, aviso, duplicados


def detectar_equivalentes(soluciones):
    """Detecta combinaciones equivalentes por duplicados."""
    grupos = defaultdict(list)
    for i, (comb, _) in enumerate(soluciones, 1):
        clave = tuple(sorted(round(v, 3) for v in comb))
        grupos[clave].append(i)
    return {k: v for k, v in grupos.items() if len(v) > 1}


def guardar_resultados(nombre_salida, soluciones, objetivo, margen, tiempo_total, contenido, aviso,
                       fecha_inicio, fecha_fin, equivalentes, duplicados, condicion_margen,
                       nota_margen, decision_usuario, margen_original, sin_solucion=False):
    """Guarda los resultados en un archivo de texto."""
    centavos = int(round(margen * 100))
    rango_inf = objetivo - margen
    rango_sup = objetivo + margen
    with open(nombre_salida, 'w', encoding='utf-8') as f:
        f.write("🔢 RESULTADOS DE COMBINACIONES GOOGLE OR-TOOLS (Argentina)\n")
        f.write("=" * 80 + "\n")
        f.write(f"🗓️ Inicio: {fecha_inicio}\n🕕 Fin: {fecha_fin}\n")
        f.write(f"🎯 Objetivo: {locale.format_string('%.2f', objetivo)}\n")
        f.write(f"💰 Margen ingresado originalmente: {margen_original}\n")
        f.write(f"💰 Margen final utilizado: ±{margen:.2f} pesos (±{centavos} centavos)\n")
        f.write(f"📈 Rango válido: desde {locale.format_string('%.2f', rango_inf)} hasta {locale.format_string('%.2f', rango_sup)}\n")
        f.write(f"⚙️ Condición aplicada: {condicion_margen}\n")
        if nota_margen:
            f.write(f"{nota_margen}\n")
        if decision_usuario:
            f.write(f"📣 Decisión del usuario ante margen negativo: {decision_usuario}\n")
        f.write(f"🕒 Tiempo total: {tiempo_total:.3f} segundos\n")
        f.write("=" * 80 + "\n\n")

        if sin_solucion:
            f.write("❌ Solver determinó que el problema no tiene solución exacta al centavo.\n")
            f.write("   Una diferencia mínima (por ejemplo, de un centavo) pudo causar este resultado vacío.\n\n")
            f.write("=" * 80 + "\nCódigo realizado por Vincenzo Natale,   vnatale52@gmail.com\n")
            return

        f.write("📄 CONTENIDO DEL ARCHIVO DE SUMANDOS:\n")
        f.write("-" * 80 + "\n")
        f.write(contenido.strip() + "\n")
        f.write("-" * 80 + "\n\n")

        if duplicados:
            f.write(aviso + "\n")
        else:
            f.write("✅ No se detectaron valores duplicados.\n\n")

        for i, (comb, suma) in enumerate(soluciones, 1):
            if abs(suma - objetivo) < 0.0001:
                etiqueta = "[EXACTA]"
                nota = "Coincide exactamente con el objetivo (sin margen aplicado)."
            elif rango_inf <= suma <= rango_sup:
                etiqueta = "[MARGEN]"
                nota = "Se utilizó el margen de error (dentro del rango permitido)."
            else:
                etiqueta = "[NO VÁLIDA]"
                nota = "Resultado fuera del rango permitido (no válido según el margen)."

            f.write(f"--- Solución {i} {etiqueta} ---\n")
            for val in sorted(comb):
                f.write(f"   {locale.format_string('%.2f', val)}\n")
            f.write(f"Suma total: {locale.format_string('%.2f', suma)}\n")
            f.write(f"{nota}\n\n")

        f.write("-" * 80 + "\n")
        if equivalentes:
            f.write("⚠️  Se detectaron combinaciones equivalentes:\n")
            for comb, idx in equivalentes.items():
                f.write(f"   - {', '.join('Solución ' + str(i) for i in idx)}\n")
        else:
            f.write("✅ No se detectaron combinaciones equivalentes generadas por duplicados.\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("Código realizado por Vincenzo Natale,   vnatale52@gmail.com\n")


def main():
    print("=" * 95)
    print("        🔢 COMBINADOR DE SUMAS CON GOOGLE OR-TOOLS (Argentina) ")
    print("=" * 95)
    print("⚠️  IMPORTANTE: el archivo de entrada NO debe usar el punto como separador de miles.\n"
          "   Ejemplo correcto: 12.345 debe escribirse como 12345\n")

    archivo = input("📄 Ingrese el nombre del archivo de sumandos (por ejemplo, sumandos.txt): ").strip()
    sumandos, contenido, aviso, duplicados = cargar_sumandos(archivo)
    if not sumandos:
        print("❌ No se pudieron cargar sumandos válidos.")
        return

    objetivo_str = input("🎯 Ingrese el objetivo (coma decimal): ").strip()
    try:
        objetivo = float(objetivo_str.replace('.', '').replace(',', '.'))
    except ValueError:
        print("❌ Valor inválido para objetivo.")
        return

    margen_str = input("± Ingrese el margen de error permitido (default 0,01, solo positivo o cero): ").strip()
    nota_margen = ""
    decision_usuario = ""
    margen_original = margen_str if margen_str else "0,01"

    if not margen_str:
        margen = 0.01
    else:
        try:
            margen = float(margen_str.replace('.', '').replace(',', '.'))
            if margen < 0:
                print(RED + f"\n⚠️ Se ingresó un margen negativo ({margen:.2f}). Solo se permiten valores cero o positivos." + RESET)
                resp = input("¿Desea usar el valor absoluto (+{:.2f})? [S/N]: ".format(abs(margen))).strip().upper()
                if resp == "S":
                    margen = abs(margen)
                    decision_usuario = f"El usuario aceptó usar el valor absoluto (+{margen:.2f})."
                    nota_margen = f"⚠️ Margen negativo corregido automáticamente a +{margen:.2f}."
                    print(GREEN + f"✔️ Margen corregido a +{margen:.2f}.\n" + RESET)
                else:
                    margen = 0
                    decision_usuario = "El usuario rechazó el valor absoluto. Se usó margen 0 (exacto)."
                    nota_margen = "⚠️ Se rechazó el margen negativo. Se usará margen 0 (solución exacta)."
                    print(YELLOW + "Margen establecido en 0 (sin error permitido).\n" + RESET)
        except ValueError:
            print("⚠️ Margen inválido. Se usará 0,01.")
            margen = 0.01

    centavos = int(round(margen * 100))
    rango_inf = objetivo - margen
    rango_sup = objetivo + margen
    print(f"\n💰 Margen ingresado originalmente: {margen_original}")
    print(f"💰 Margen de error final: ±{margen:.2f} pesos (±{centavos} centavos)")
    print(f"📈 Rango válido: desde {rango_inf:.2f} hasta {rango_sup:.2f}\n")

    n = len(sumandos)
    total_combinaciones = 2 ** n
    fecha_inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🕓 Inicio: {fecha_inicio}")
    print(f"Analizando {n} sumandos → {total_combinaciones:,} combinaciones posibles\n")

    resultados, tiempo_total, condicion_margen = resolver_con_margen(sumandos, objetivo, margen)
    fecha_fin = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    base, _ = os.path.splitext(archivo)
    nombre_salida = f"soluciones_{os.path.basename(base)}.txt"

    if resultados:
        equivalentes = detectar_equivalentes(resultados)
        print(GREEN + f"\n✅ {len(resultados)} soluciones halladas dentro del margen." + RESET)
        print(f"🕒 Tiempo: {tiempo_total:.3f} s\n")

        for i, (comb, suma) in enumerate(resultados, 1):
            if abs(suma - objetivo) < 0.0001:
                color = GREEN
                mensaje = "✅ Coincide exactamente con el objetivo (sin margen aplicado)."
                etiqueta = "[EXACTA]"
            elif rango_inf <= suma <= rango_sup:
                color = YELLOW
                mensaje = "✔️ Se utilizó el margen de error (dentro del rango permitido)."
                etiqueta = "[MARGEN]"
            else:
                color = RED
                mensaje = "⚠️ Resultado fuera del rango permitido (no válido según el margen)."
                etiqueta = "[NO VÁLIDA]"

            header = f"--- Solución {i} {etiqueta} ---"
            print(color + header + RESET)
            for v in sorted(comb):
                print("   ", locale.format_string('%.2f', v))
            print(f"Suma total: {locale.format_string('%.2f', suma)}")
            print(color + mensaje + RESET + "\n")

        guardar_resultados(nombre_salida, resultados, objetivo, margen, tiempo_total,
                           contenido, aviso, fecha_inicio, fecha_fin,
                           equivalentes, duplicados, condicion_margen,
                           nota_margen, decision_usuario, margen_original)

    else:
        print(YELLOW + "\n❌ Solver determinó que el problema no tiene solución exacta al centavo.\n"
              "   Una diferencia mínima (por ejemplo, de un centavo) pudo causar este resultado vacío.\n" + RESET)
        guardar_resultados(nombre_salida, [], objetivo, margen, tiempo_total,
                           contenido, aviso, fecha_inicio, fecha_fin,
                           {}, duplicados, condicion_margen,
                           nota_margen, decision_usuario, margen_original, sin_solucion=True)


if __name__ == "__main__":
    main()
