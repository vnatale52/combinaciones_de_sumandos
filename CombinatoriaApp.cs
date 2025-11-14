using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Diagnostics;

namespace CombinatoriaSumandos
{
    public class CombinatoriaApp
    {
        private readonly CultureInfo argentineCulture = new CultureInfo("es-AR");
        
        public async Task Run()
        {
            Console.WriteLine("=".PadRight(95, '='));
            Console.WriteLine("        🔢 COMBINATORIA DE SUMANDOS CON ALGORITMO OPTIMIZADO (Argentina) ");
            Console.WriteLine("=".PadRight(95, '='));
            Console.WriteLine("⚠️  IMPORTANTE: Use formato argentino:\n" +
                            "   - Coma (,) como separador decimal: 1234,56\n" +
                            "   - SIN punto como separador de miles: escriba 12345 en lugar de 12.345\n");

            // Cargar archivo de sumandos
            double[] sumandos = null;
            string contenidoArchivo = "";
            string avisoDuplicados = "";
            string controlFormatos = "";
            bool tieneErroresFormato = false;

            while (true)
            {
                Console.Write("📄 Ingrese el nombre del archivo de sumandos (por ejemplo, sumandos.txt): ");
                string archivo = Console.ReadLine()?.Trim();

                var resultadoCarga = await CargarSumandos(archivo);
                if (!resultadoCarga.Exitoso)
                {
                    Console.WriteLine("❌ No se pudieron cargar sumandos válidos.");
                    return;
                }

                sumandos = resultadoCarga.Sumandos;
                contenidoArchivo = resultadoCarga.Contenido;
                avisoDuplicados = resultadoCarga.AvisoDuplicados;
                controlFormatos = resultadoCarga.ControlFormatos;
                tieneErroresFormato = resultadoCarga.TieneErroresFormato;

                Console.WriteLine($"\n🔎 Control de formato del archivo:");
                Console.WriteLine(controlFormatos);

                if (tieneErroresFormato)
                {
                    Console.WriteLine("❌ ERROR: El archivo contiene valores con formato incorrecto.");
                    Console.WriteLine("Por favor, corrija el archivo para usar formato argentino:");
                    Console.WriteLine("   - Use coma (,) como separador decimal");
                    Console.WriteLine("   - NO use punto (.) como separador de miles");
                    Console.Write("\n¿Desea reintentar con otro archivo o el mismo corregido? (S/N): ");
                    string respuesta = Console.ReadLine()?.Trim().ToUpper();
                    if (respuesta != "S")
                    {
                        Console.WriteLine("Operación cancelada.");
                        return;
                    }
                }
                else
                {
                    break;
                }
            }

            // Solicitar objetivo
            double objetivo = 0;
            while (true)
            {
                Console.Write("\n🎯 Ingrese el objetivo (formato argentino, ej: 19,35 o 1234567): ");
                string objetivoStr = Console.ReadLine()?.Trim();
                var verificacion = VerificarFormatoCadena(objetivoStr);

                if (verificacion.EsValido && verificacion.Valor.HasValue)
                {
                    objetivo = verificacion.Valor.Value;
                    Console.WriteLine($"✅ {verificacion.Mensaje}");
                    break;
                }
                else
                {
                    Console.WriteLine($"❌ ERROR: {verificacion.Mensaje}");
                    Console.WriteLine("Por favor, ingrese el objetivo en formato argentino (coma decimal, sin punto de miles).");
                }
            }

            // Solicitar margen
            double margen = 0.01;
            string margenOriginal = "0,01";
            string notaMargen = "";
            string decisionUsuario = "";

            while (true)
            {
                Console.Write("± Ingrese el margen de error o dispersión (ej: 0,01) [presione Enter para 0,01]: ");
                string margenStr = Console.ReadLine()?.Trim();

                if (string.IsNullOrEmpty(margenStr))
                {
                    margen = 0.01;
                    margenOriginal = "0,01";
                    break;
                }

                margenOriginal = margenStr;
                var verificacion = VerificarFormatoCadena(margenStr);

                if (verificacion.EsValido && verificacion.Valor.HasValue)
                {
                    if (verificacion.Valor.Value < 0)
                    {
                        Console.WriteLine($"\n❌ ERROR: Se ingresó un margen negativo ({verificacion.Valor.Value:F2}).");
                        Console.WriteLine("Solo se permiten valores cero o positivos.");
                        Console.WriteLine("Por favor, reingrese el margen en formato argentino con valor positivo o cero.");
                        continue;
                    }
                    margen = verificacion.Valor.Value;
                    Console.WriteLine($"✅ {verificacion.Mensaje}");
                    break;
                }
                else
                {
                    Console.WriteLine($"❌ ERROR: {verificacion.Mensaje}");
                    Console.WriteLine("Por favor, ingrese el margen en formato argentino (coma decimal, sin punto de miles).");
                }
            }

            int centavos = (int)Math.Round(margen * 100);
            double rangoInf = objetivo - margen;
            double rangoSup = objetivo + margen;

            Console.WriteLine($"\n📊 Resumen de parámetros:");
            Console.WriteLine($"🎯 Objetivo: {objetivo:F2}");
            Console.WriteLine($"💰 Margen ingresado: {margenOriginal}");
            Console.WriteLine($"💰 Margen de error o dispersión: ±{margen:F2} pesos (±{centavos} centavos)");
            Console.WriteLine($"📈 Rango válido: desde {rangoInf:F2} hasta {rangoSup:F2}\n");

            int n = sumandos.Length;
            long totalCombinaciones = (long)Math.Pow(2, n);
            string fechaInicio = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
            Console.WriteLine($"🕓 Inicio: {fechaInicio}");
            Console.WriteLine($"Analizando {n} sumandos → {totalCombinaciones:N0} combinaciones posibles\n");

            var stopwatch = Stopwatch.StartNew();
            var resultados = EncontrarCombinaciones(sumandos, objetivo, margen);
            stopwatch.Stop();

            string fechaFin = DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss");
            double tiempoTotal = stopwatch.Elapsed.TotalSeconds;

            string nombreBase = Path.GetFileNameWithoutExtension("sumandos");
            string nombreSalida = $"soluciones_{nombreBase}.txt";

            if (resultados.Any())
            {
                var equivalentes = DetectarEquivalentes(resultados);
                Console.WriteLine($"\n✅ {resultados.Count} soluciones halladas dentro del margen.");

                TimeSpan tiempo = TimeSpan.FromSeconds(tiempoTotal);
                string tiempoFormateado = $"{tiempo.Hours:00}:{tiempo.Minutes:00}:{tiempo.Seconds:00}";
                Console.WriteLine($"🕒 Tiempo total: {tiempoTotal:F3} segundos  |  {tiempoFormateado} (hh:mm:ss)\n");

                for (int i = 0; i < resultados.Count; i++)
                {
                    var (combinacion, suma) = resultados[i];
                    string etiqueta, nota, mensaje;
                    ConsoleColor color;

                    if (Math.Abs(suma - objetivo) < 0.0001)
                    {
                        color = ConsoleColor.Green;
                        mensaje = "✅ Coincide exactamente con el objetivo (sin margen aplicado).";
                        etiqueta = "[EXACTA]";
                        nota = "EXACTO";
                    }
                    else if (suma >= rangoInf && suma <= rangoSup)
                    {
                        color = ConsoleColor.Yellow;
                        mensaje = "✔️ Se utilizó el margen de error o dispersión (dentro del rango permitido).";
                        etiqueta = "[MARGEN]";
                        nota = "HALLADA APLICANDO MARGEN";
                    }
                    else
                    {
                        color = ConsoleColor.Red;
                        mensaje = "⚠️ Resultado fuera del rango permitido (no válido según el margen).";
                        etiqueta = "[NO VÁLIDA]";
                        nota = "NO VÁLIDA";
                    }

                    Console.ForegroundColor = color;
                    Console.WriteLine($"--- Solución {i + 1} {etiqueta} ---");
                    Console.ResetColor();

                    foreach (var valor in combinacion.OrderBy(v => v))
                    {
                        Console.WriteLine($"   {valor:F2}");
                    }
                    Console.WriteLine($"Suma total: {suma:F2} ({nota})");
                    Console.ForegroundColor = color;
                    Console.WriteLine(mensaje);
                    Console.ResetColor();
                    Console.WriteLine();
                }

                await GuardarResultados(nombreSalida, resultados, objetivo, margen, tiempoTotal,
                                      contenidoArchivo, avisoDuplicados, fechaInicio, fechaFin,
                                      equivalentes, new List<double>(), $"objetivo ± {margen:F2}",
                                      notaMargen, decisionUsuario, margenOriginal, controlFormatos);
            }
            else
            {
                Console.WriteLine("\n❌ No se encontraron combinaciones dentro del margen especificado.\n" +
                                "   Una diferencia mínima (por ejemplo, de un centavo) pudo causar este resultado vacío.\n");
                await GuardarResultados(nombreSalida, new List<(double[], double)>(), objetivo, margen, tiempoTotal,
                                      contenidoArchivo, avisoDuplicados, fechaInicio, fechaFin,
                                      new Dictionary<string, List<int>>(), new List<double>(), $"objetivo ± {margen:F2}",
                                      notaMargen, decisionUsuario, margenOriginal, controlFormatos, true);
            }
        }

        private List<(double[] Combinacion, double Suma)> EncontrarCombinaciones(double[] sumandos, double objetivo, double margen)
        {
            var resultados = new List<(double[], double)>();
            int n = sumandos.Length;

            // Usar un enfoque iterativo en lugar de recursivo para mejor performance
            for (long mask = 1; mask < (1L << n); mask++)
            {
                double suma = 0;
                var combinacion = new List<double>();

                for (int i = 0; i < n; i++)
                {
                    if ((mask & (1L << i)) != 0)
                    {
                        suma += sumandos[i];
                        combinacion.Add(sumandos[i]);
                    }
                }

                if (Math.Abs(suma - objetivo) <= margen)
                {
                    resultados.Add((combinacion.ToArray(), suma));
                }
            }

            return resultados;
        }

        private Dictionary<string, List<int>> DetectarEquivalentes(List<(double[] Combinacion, double Suma)> soluciones)
        {
            var grupos = new Dictionary<string, List<int>>();

            for (int i = 0; i < soluciones.Count; i++)
            {
                var (combinacion, _) = soluciones[i];
                var clave = string.Join("|", combinacion.OrderBy(v => v).Select(v => Math.Round(v, 3).ToString("F3")));

                if (!grupos.ContainsKey(clave))
                {
                    grupos[clave] = new List<int>();
                }
                grupos[clave].Add(i + 1);
            }

            return grupos.Where(kv => kv.Value.Count > 1)
                        .ToDictionary(kv => kv.Key, kv => kv.Value);
        }

        private async Task<ResultadoCarga> CargarSumandos(string nombreArchivo)
        {
            if (!File.Exists(nombreArchivo))
            {
                Console.WriteLine($"❌ El archivo '{nombreArchivo}' no existe.");
                return new ResultadoCarga { Exitoso = false };
            }

            string contenido = await File.ReadAllTextAsync(nombreArchivo);
            var lineas = contenido.Split('\n')
                                .Select(l => l.Trim())
                                .Where(l => !string.IsNullOrEmpty(l))
                                .ToArray();

            var sumandos = new List<double>();
            var detallesControl = new List<string>();
            bool tieneErroresFormato = false;

            foreach (string linea in lineas)
            {
                var verificacion = VerificarFormatoCadena(linea);
                detallesControl.Add($"{linea} -> {verificacion.Mensaje}");

                if (!verificacion.EsValido)
                {
                    tieneErroresFormato = true;
                }

                if (verificacion.Valor.HasValue)
                {
                    sumandos.Add(verificacion.Valor.Value);
                }
                else
                {
                    detallesControl.Add($"   ⚠️ Línea ignorada (no numérica o no convertible): {linea}");
                }
            }

            // Detectar duplicados
            var duplicados = sumandos.GroupBy(x => x)
                                   .Where(g => g.Count() > 1)
                                   .Select(g => g.Key)
                                   .ToList();

            string aviso = "";
            if (duplicados.Any())
            {
                aviso = "\n⚠️  Atención: Se detectaron valores duplicados en el archivo:\n";
                foreach (var valor in duplicados)
                {
                    int count = sumandos.Count(v => Math.Abs(v - valor) < 0.001);
                    aviso += $"   - {valor:F3} aparece {count} veces\n";
                }
                aviso += "   Estos duplicados pueden generar combinaciones equivalentes.\n";
            }
            else
            {
                aviso = "✅ No se detectaron sumandos repetidos.\n";
            }

            string controlTexto = "Control de formato aplicado al archivo de entrada (Argentina):\n" +
                                string.Join("\n", detallesControl) + "\n";

            return new ResultadoCarga
            {
                Exitoso = sumandos.Any(),
                Sumandos = sumandos.ToArray(),
                Contenido = contenido,
                AvisoDuplicados = aviso,
                ControlFormatos = controlTexto,
                TieneErroresFormato = tieneErroresFormato
            };
        }

        private (bool EsValido, string Mensaje, double? Valor) VerificarFormatoCadena(string cadena)
        {
            if (string.IsNullOrWhiteSpace(cadena))
            {
                return (false, "Línea vacía", null);
            }

            string raw = cadena.Trim();
            bool tienePunto = raw.Contains('.');
            bool tieneComa = raw.Contains(',');

            if (tienePunto)
            {
                string mensaje = $"❌ Formato inválido: contiene punto (.) — posible separador de miles: '{raw}'.";
                
                try
                {
                    // Intentar conversión automática
                    string convertida = raw.Replace(".", "").Replace(",", ".");
                    if (double.TryParse(convertida, NumberStyles.Any, CultureInfo.InvariantCulture, out double valor))
                    {
                        return (false, mensaje + " Se intentó conversión automática para continuar.", valor);
                    }
                }
                catch
                {
                    // Ignorar errores de conversión
                }

                return (false, mensaje + " No se pudo convertir automáticamente.", null);
            }
            else
            {
                if (tieneComa)
                {
                    try
                    {
                        string convertida = raw.Replace(",", ".");
                        if (double.TryParse(convertida, NumberStyles.Any, CultureInfo.InvariantCulture, out double valor))
                        {
                            return (true, "✅ Formato correcto (coma decimal).", valor);
                        }
                    }
                    catch
                    {
                        // Ignorar errores
                    }
                    return (false, "❌ Línea con coma pero no convertible.", null);
                }
                else
                {
                    if (double.TryParse(raw, NumberStyles.Any, CultureInfo.InvariantCulture, out double valor))
                    {
                        return (true, "✅ Formato correcto (entero sin separadores).", valor);
                    }
                    return (false, "❌ No convertible como número.", null);
                }
            }
        }

        private async Task GuardarResultados(string nombreSalida, List<(double[] Combinacion, double Suma)> soluciones,
                                           double objetivo, double margen, double tiempoTotal, string contenido,
                                           string aviso, string fechaInicio, string fechaFin,
                                           Dictionary<string, List<int>> equivalentes, List<double> duplicados,
                                           string condicionMargen, string notaMargen, string decisionUsuario,
                                           string margenOriginal, string controlFormatos, bool sinSolucion = false)
        {
            int centavos = (int)Math.Round(margen * 100);
            double rangoInf = objetivo - margen;
            double rangoSup = objetivo + margen;

            TimeSpan tiempo = TimeSpan.FromSeconds(tiempoTotal);
            string tiempoFormateado = $"{tiempo.Hours:00}:{tiempo.Minutes:00}:{tiempo.Seconds:00}";

            using var writer = new StreamWriter(nombreSalida, false, System.Text.Encoding.UTF8);
            
            await writer.WriteLineAsync("🔢 RESULTADOS DE COMBINATORIA DE SUMANDOS (Argentina)");
            await writer.WriteLineAsync("=".PadRight(80, '='));
            await writer.WriteLineAsync($"🗓️ Inicio: {fechaInicio}");
            await writer.WriteLineAsync($"🕕 Fin: {fechaFin}");
            await writer.WriteLineAsync($"🎯 Objetivo (ingresado): {objetivo:F2}");
            await writer.WriteLineAsync($"🔎 Control de formato del objetivo y margen:");
            await writer.WriteLineAsync(controlFormatos);
            await writer.WriteLineAsync($"💰 Margen ingresado originalmente: {margenOriginal}");
            await writer.WriteLineAsync($"💰 Margen final utilizado: ±{margen:F2} pesos (±{centavos} centavos)");
            await writer.WriteLineAsync($"📈 Rango válido: desde {rangoInf:F2} hasta {rangoSup:F2}");
            await writer.WriteLineAsync($"⚙️ Condición aplicada: {condicionMargen}");
            
            if (!string.IsNullOrEmpty(notaMargen))
                await writer.WriteLineAsync(notaMargen);
            
            if (!string.IsNullOrEmpty(decisionUsuario))
                await writer.WriteLineAsync($"📣 Decisión del usuario ante margen negativo: {decisionUsuario}");
            
            await writer.WriteLineAsync($"🕒 Tiempo total: {tiempoTotal:F3} segundos  |  {tiempoFormateado} (hh:mm:ss)");
            await writer.WriteLineAsync("=".PadRight(80, '='));
            await writer.WriteLineAsync();

            if (sinSolucion)
            {
                await writer.WriteLineAsync("❌ No se encontraron combinaciones dentro del margen especificado.");
                await writer.WriteLineAsync("   Una diferencia mínima (por ejemplo, de un centavo) pudo causar este resultado vacío.\n");
                await writer.WriteLineAsync("=".PadRight(80, '='));
                await writer.WriteLineAsync("Código convertido a C# por IA, basado en trabajo original de Vincenzo Natale, vnatale52@gmail.com");
                return;
            }

            await writer.WriteLineAsync("📄 CONTENIDO DEL ARCHIVO DE SUMANDOS:");
            await writer.WriteLineAsync("-".PadRight(80, '-'));
            await writer.WriteLineAsync(contenido.Trim());
            await writer.WriteLineAsync("-".PadRight(80, '-'));
            await writer.WriteLineAsync();

            await writer.WriteLineAsync("🔎 Resultado del control de formato aplicado al archivo de entrada:");
            await writer.WriteLineAsync(controlFormatos);
            await writer.WriteLineAsync();

            if (duplicados.Any())
            {
                await writer.WriteLineAsync(aviso);
            }
            else
            {
                await writer.WriteLineAsync("✅ No se detectaron combinaciones equivalentes generadas por sumandos que estén repetidos.\n");
            }

            for (int i = 0; i < soluciones.Count; i++)
            {
                var (combinacion, suma) = soluciones[i];
                string etiqueta = Math.Abs(suma - objetivo) < 0.0001 ? "[EXACTA]" : 
                                 (suma >= rangoInf && suma <= rangoSup) ? "[MARGEN]" : "[NO VÁLIDA]";
                
                string nota = etiqueta switch
                {
                    "[EXACTA]" => "EXACTO",
                    "[MARGEN]" => "HALLADA APLICANDO MARGEN",
                    _ => "NO VÁLIDA"
                };

                await writer.WriteLineAsync($"--- Solución {i + 1} {etiqueta} ---");
                foreach (var valor in combinacion.OrderBy(v => v))
                {
                    await writer.WriteLineAsync($"   {valor:F2}");
                }
                await writer.WriteLineAsync($"Suma total: {suma:F2} ({nota})");
                await writer.WriteLineAsync();
            }

            await writer.WriteLineAsync("-".PadRight(80, '-'));
            
            if (equivalentes.Any())
            {
                await writer.WriteLineAsync("⚠️  Se detectaron combinaciones equivalentes:");
                foreach (var kvp in equivalentes)
                {
                    await writer.WriteLineAsync($"   - {string.Join(", ", kvp.Value.Select(i => "Solución " + i))}");
                }
            }
            else
            {
                await writer.WriteLineAsync("✅ No se detectaron combinaciones equivalentes generadas por sumandos que estén repetidos.");
            }

            await writer.WriteLineAsync();
            await writer.WriteLineAsync("=".PadRight(80, '='));
            await writer.WriteLineAsync("Código convertido a C# por IA, basado en trabajo original de Vincenzo Natale, vnatale52@gmail.com");
        }
    }

    public class ResultadoCarga
    {
        public bool Exitoso { get; set; }
        public double[] Sumandos { get; set; }
        public string Contenido { get; set; }
        public string AvisoDuplicados { get; set; }
        public string ControlFormatos { get; set; }
        public bool TieneErroresFormato { get; set; }
    }
}