from ortools.sat.python import cp_model
import locale
import os
import time
from datetime import datetime, timedelta
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
BOLD = "\033[1m"
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


def verificar_formato_linea(linea):
    """
    Verifica si la línea respeta el formato argentino: no usar punto como separador de miles
    y usar coma como separador decimal cuando corresponda.
    Devuelve (es_valida, mensaje_detalle, valor_parseado_o_None)
    """
    raw = linea.strip()
    if raw == "":
        return False, "Línea vacía", None
    tiene_punto = "." in raw
    tiene_coma = "," in raw
    # Consideramos que el uso de punto es inválido (se interpreta como separador de miles)
    # pero permitimos convertirlo automáticamente para continuar la ejecución (reemplazando puntos).
    if tiene_punto:
        msg = f"❌ Formato inválido: contiene punto (.) — posible separador de miles: '{raw}'."
        # Intentaremos convertir sustituyendo '.' por '' y ',' por '.' para parsear
        try:
            val = float(raw.replace('.', '').replace(',', '.'))
            return False, msg + " Se intentó conversión automática para continuar.", val
        except Exception:
            return False, msg + " No se pudo convertir automáticamente.", None
    else:
        # Si no tiene puntos, aceptamos tanto entero (sin coma) como decimal con coma
        if tiene_coma:
            # debe poder convertirse al reemplazar la coma por punto
            try:
                val = float(raw.replace(',', '.'))
                return True, "✅ Formato correcto (coma decimal).", val
            except Exception:
                return False, "❌ Línea con coma pero no convertible.", None
        else:
            # entero sin separadores: válido
            try:
                val = float(raw)
                return True, "✅ Formato correcto (entero sin separadores).", val
            except Exception:
                return False, "❌ No convertible como número.", None


def cargar_sumandos(nombre_archivo):
    """Carga los sumandos desde un archivo en formato argentino (coma decimal)."""
    if not os.path.exists(nombre_archivo):
        print(f"❌ El archivo '{nombre_archivo}' no existe.")
        return None, None, "", [], ""

    with open(nombre_archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()

    sumandos = []
    detalles_control = []
    tiene_errores_formato = False
    
    for linea in contenido.splitlines():
        linea = linea.strip()
        if not linea:
            continue
        es_valida, mensaje, valor = verificar_formato_linea(linea)
        detalles_control.append(f"{linea} -> {mensaje}")
        if not es_valida:
            tiene_errores_formato = True
        if valor is not None:
            sumandos.append(valor)
        else:
            detalles_control.append(f"   ⚠️ Línea ignorada (no numérica o no convertible): {linea}")

    duplicados = [v for v, c in Counter(sumandos).items() if c > 1]
    aviso = ""
    if duplicados:
        aviso = "\n⚠️  Atención: Se detectaron valores duplicados en el archivo:\n"
        for val in duplicados:
            aviso += f"   - {locale.format_string('%.3f', val)} aparece {sumandos.count(val)} veces\n"
        aviso += "   Estos duplicados pueden generar combinaciones equivalentes.\n"
    else:
        aviso = "✅ No se detectaron sumandos repetidos.\n"

    # Resultado del control de formato
    control_texto = "Control de formato aplicado al archivo de entrada (Argentina):\n"
    control_texto += "\n".join(detalles_control) + "\n"
    return sumandos, contenido, aviso, duplicados, control_texto, tiene_errores_formato


def detectar_equivalentes(soluciones):
    """Detecta combinaciones equivalentes por duplicados."""
    grupos = defaultdict(list)
    for i, (comb, _) in enumerate(soluciones, 1):
        clave = tuple(sorted(round(v, 3) for v in comb))
        grupos[clave].append(i)
    return {k: v for k, v in grupos.items() if len(v) > 1}


def guardar_resultados(nombre_salida, soluciones, objetivo, margen, tiempo_total, contenido, aviso,
                       fecha_inicio, fecha_fin, equivalentes, duplicados, condicion_margen,
                       nota_margen, decision_usuario, margen_original, control_formatos, sin_solucion=False):
    """Guarda los resultados en un archivo de texto."""
    centavos = int(round(margen * 100))
    rango_inf = objetivo - margen
    rango_sup = objetivo + margen

    # Formateo tiempo hh:mm:ss (formato argentino)
    horas = int(tiempo_total // 3600)
    minutos = int((tiempo_total % 3600) // 60)
    segundos = int(tiempo_total % 60)
    tiempo_formateado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
    
    with open(nombre_salida, 'w', encoding='utf-8') as f:
        f.write("🔢 RESULTADOS DE COMBINATORIA DE SUMANDOS (Argentina)\n")
        f.write("=" * 80 + "\n")
        f.write(f"🗓️ Inicio: {fecha_inicio}\n🕕 Fin: {fecha_fin}\n")
        f.write(f"🎯 Objetivo (ingresado): {locale.format_string('%.2f', objetivo)}\n")
        f.write(f"🔎 Control de formato del objetivo y margen:\n{control_formatos}\n")
        f.write(f"💰 Margen ingresado originalmente: {margen_original}\n")
        f.write(f"💰 Margen final utilizado: ±{margen:.2f} pesos (±{centavos} centavos)\n")
        f.write(f"📈 Rango válido: desde {locale.format_string('%.2f', rango_inf)} hasta {locale.format_string('%.2f', rango_sup)}\n")
        f.write(f"⚙️ Condición aplicada: {condicion_margen}\n")
        if nota_margen:
            f.write(f"{nota_margen}\n")
        if decision_usuario:
            f.write(f"📣 Decisión del usuario ante margen negativo: {decision_usuario}\n")
        f.write(f"🕒 Tiempo total: {locale.format_string('%.3f', tiempo_total)} segundos  |  {tiempo_formateado} (hh:mm:ss)\n")
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

        f.write("🔎 Resultado del control de formato aplicado al archivo de entrada:\n")
        f.write(control_formatos + "\n")

        if duplicados:
            f.write(aviso + "\n")
        else:
            # Replace the requested legend text
            f.write("✅ No se detectaron combinaciones equivalentes generadas por sumandos que estén repetidos.\n\n")

        for i, (comb, suma) in enumerate(soluciones, 1):
            etiqueta = "[EXACTA]" if abs(suma - objetivo) < 0.0001 else "[MARGEN]" if (rango_inf <= suma <= rango_sup) else "[NO VÁLIDA]"
            if etiqueta == "[EXACTA]":
                nota = "EXACTO"
            elif etiqueta == "[MARGEN]":
                nota = "HALLADA APLICANDO MARGEN"
            else:
                nota = "NO VÁLIDA"
            f.write(f"--- Solución {i} {etiqueta} ---\n")
            for val in sorted(comb):
                f.write(f"   {locale.format_string('%.2f', val)}\n")
            f.write(f"Suma total: {locale.format_string('%.2f', suma)} ({nota})\n")
            f.write(("\n"))
        f.write("-" * 80 + "\n")
        if equivalentes:
            f.write("⚠️  Se detectaron combinaciones equivalentes:\n")
            for comb, idx in equivalentes.items():
                f.write(f"   - {', '.join('Solución ' + str(i) for i in idx)}\n")
        else:
            f.write("✅ No se detectaron combinaciones equivalentes generadas por sumandos que estén repetidos.\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("Código realizado por Vincenzo Natale,   vnatale52@gmail.com\n")


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


def main():
    print("=" * 95)
    print("        🔢 COMBINATORIA DE SUMANDOS CON GOOGLE OR-TOOLS (Argentina) ")
    print("=" * 95)
    print("⚠️  IMPORTANTE: Use formato argentino:\n"
          "   - Coma (,) como separador decimal: 1234,56\n"
          "   - SIN punto como separador de miles: escriba 12345 en lugar de 12.345\n")

    # Cargar archivo de sumandos con validación estricta
    while True:
        archivo = input("📄 Ingrese el nombre del archivo de sumandos (por ejemplo, sumandos.txt): ").strip()
        sumandos, contenido, aviso, duplicados, control_formatos, tiene_errores_formato = cargar_sumandos(archivo)
        
        if not sumandos:
            print(RED + "❌ No se pudieron cargar sumandos válidos." + RESET)
            return
        
        print(f"\n{BOLD}🔎 Control de formato del archivo:{RESET}")
        print(control_formatos)
        
        if tiene_errores_formato:
            print(RED + "\n❌ ERROR: El archivo contiene valores con formato incorrecto." + RESET)
            print(YELLOW + "Por favor, corrija el archivo para usar formato argentino:" + RESET)
            print("   - Use coma (,) como separador decimal")
            print("   - NO use punto (.) como separador de miles")
            respuesta = input("\n¿Desea reintentar con otro archivo o el mismo corregido? (S/N): ").strip().upper()
            if respuesta != 'S':
                print(RED + "Operación cancelada." + RESET)
                return
        else:
            break

    # Solicitar objetivo con validación estricta
    while True:
        objetivo_str = input("\n🎯 Ingrese el objetivo (formato argentino, ej: 19,35 o 1234567): ").strip()
        obj_valido, obj_mensaje, objetivo = verificar_formato_linea(objetivo_str)
        
        if obj_valido and objetivo is not None:
            print(GREEN + f"✅ {obj_mensaje}" + RESET)
            break
        else:
            print(RED + f"❌ ERROR: {obj_mensaje}" + RESET)
            print(YELLOW + "Por favor, ingrese el objetivo en formato argentino (coma decimal, sin punto de miles)." + RESET)

    # Solicitar margen con validación estricta
    nota_margen = ""
    decision_usuario = ""
    margen_original = ""
    
    while True:
        margen_str = input("± Ingrese el margen de error o dispersión (ej: 0,01) [presione Enter para 0,01]: ").strip()
        
        if not margen_str:
            margen = 0.01
            margen_original = "0,01"
            margen_valido = True
            msg_margen = "✅ Margen por defecto (0,01)."
            break
        
        margen_valido, msg_margen, margen = verificar_formato_linea(margen_str)
        margen_original = margen_str
        
        if margen_valido and margen is not None:
            if margen < 0:
                print(RED + f"\n❌ ERROR: Se ingresó un margen negativo ({locale.format_string('%.2f', margen)})." + RESET)
                print(YELLOW + "Solo se permiten valores cero o positivos." + RESET)
                print(YELLOW + "Por favor, reingrese el margen en formato argentino con valor positivo o cero." + RESET)
                continue
            print(GREEN + f"✅ {msg_margen}" + RESET)
            break
        else:
            print(RED + f"❌ ERROR: {msg_margen}" + RESET)
            print(YELLOW + "Por favor, ingrese el margen en formato argentino (coma decimal, sin punto de miles)." + RESET)

    centavos = int(round(margen * 100))
    rango_inf = objetivo - margen
    rango_sup = objetivo + margen
    
    # Consolidar control de formatos para el archivo de salida
    control_formatos_completo = f"Control de formato del objetivo:\n{obj_mensaje}\n"
    control_formatos_completo += f"Control de formato del margen:\n{msg_margen}\n"
    
    print(f"\n{BOLD}📊 Resumen de parámetros:{RESET}")
    print(f"🎯 Objetivo: {locale.format_string('%.2f', objetivo)}")
    print(f"💰 Margen ingresado: {margen_original}")
    print(f"💰 Margen de error o dispersión: ±{locale.format_string('%.2f', margen)} pesos (±{centavos} centavos)")
    print(f"📈 Rango válido: desde {locale.format_string('%.2f', rango_inf)} hasta {locale.format_string('%.2f', rango_sup)}\n")

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
        # Mostrar tiempo en segundos y hh:mm:ss (formato argentino)
        td = timedelta(seconds=round(tiempo_total))
        horas = int(td.total_seconds() // 3600)
        minutos = int((td.total_seconds() % 3600) // 60)
        segundos = int(td.total_seconds() % 60)
        tiempo_formateado = f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        print(f"🕒 Tiempo total: {locale.format_string('%.3f', tiempo_total)} segundos  |  {tiempo_formateado} (hh:mm:ss)\n")

        for i, (comb, suma) in enumerate(resultados, 1):
            if abs(suma - objetivo) < 0.0001:
                color = GREEN
                mensaje = "✅ Coincide exactamente con el objetivo (sin margen aplicado)."
                etiqueta = "[EXACTA]"
                nota = "EXACTO"
            elif rango_inf <= suma <= rango_sup:
                color = YELLOW
                mensaje = "✔️ Se utilizó el margen de error o dispersión (dentro del rango permitido)."
                etiqueta = "[MARGEN]"
                nota = "HALLADA APLICANDO MARGEN"
            else:
                color = RED
                mensaje = "⚠️ Resultado fuera del rango permitido (no válido según el margen)."
                etiqueta = "[NO VÁLIDA]"
                nota = "NO VÁLIDA"

            header = f"--- Solución {i} {etiqueta} ---"
            print(color + header + RESET)
            for v in sorted(comb):
                print("   ", locale.format_string('%.2f', v))
            print(f"Suma total: {locale.format_string('%.2f', suma)} ({nota})")
            print(color + mensaje + RESET + "\n")

        guardar_resultados(nombre_salida, resultados, objetivo, margen, tiempo_total,
                           contenido, aviso, fecha_inicio, fecha_fin,
                           equivalentes, duplicados, condicion_margen,
                           nota_margen, decision_usuario, margen_original, control_formatos_completo)

    else:
        print(YELLOW + "\n❌ Solver determinó que el problema no tiene solución exacta al centavo.\n"
              "   Una diferencia mínima (por ejemplo, de un centavo) pudo causar este resultado vacío.\n" + RESET)
        guardar_resultados(nombre_salida, [], objetivo, margen, tiempo_total,
                           contenido, aviso, fecha_inicio, fecha_fin,
                           {}, duplicados, condicion_margen,
                           nota_margen, decision_usuario, margen_original, control_formatos_completo, sin_solucion=True)


if __name__ == "__main__":
    main()
