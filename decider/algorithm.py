import time
import os
from collections import deque

class ClimateSafetyMonitor:
    def __init__(self, log_file="full_safety_log.csv"):
        """
        Inicializa el monitor de estado dual (Irradiación y Temperatura).
        Se usa como módulo auxiliar, manteniendo el estado de los buffers en memoria.
        """
        self.log_file = log_file
        self.sampling_interval = 5  # segundos
        
        # Buffers independientes para cada métrica (4 horas max)
        self.irrad_buffer = deque(maxlen=2880)
        self.temp_buffer = deque(maxlen=2880)
        
        self.windows = {
            "1min_peak": 12,
            "15min_high": 180,
            "1hour_sustained": 720,
            "4hour_cumulative": 2880
        }
        
        self._init_csv()

    def _init_csv(self):
        """Crea las cabeceras del CSV si el archivo no existe."""
        if not os.path.exists(self.log_file):
            try:
                with open(self.log_file, "w") as f:
                    f.write("Timestamp,Irradiance_Wm2,FeelTemp_C,Energy_1h_MJ,Max_Priority,Solar_Status,Temp_Status\n")
            except Exception as e:
                print(f"[Monitor Error] Could not create CSV: {e}")

    # --- LÓGICA DE IRRADIACIÓN (ENERGÍA) ---
    def _check_irradiance(self):
        thresholds = {
            "1min_peak": 60000,        
            "15min_high": 675000,      
            "1hour_sustained": 2500000, 
            "4hour_cumulative": 9000000 
        }
        results = {}
        count = len(self.irrad_buffer)
        history = list(self.irrad_buffer)

        for name, size in self.windows.items():
            if count >= size:
                segment = history[-size:]
                # Integración: W/m2 * tiempo = Joules
                joules = sum(segment) * self.sampling_interval
                results[name] = {
                    "value": round(joules / 1000000, 3), # Guardamos como MJ
                    "is_dangerous": joules >= thresholds[name]
                }
            else:
                results[name] = {"status": "collecting"}
        return results

    def _get_irrad_verdict(self, results):
        if results.get("1min_peak", {}).get("is_dangerous"): return "CRITICAL_SOLAR", 4
        if results.get("15min_high", {}).get("is_dangerous"): return "DANGER_SOLAR", 3
        if results.get("1hour_sustained", {}).get("is_dangerous"): return "WARNING_SOLAR", 2
        if results.get("4hour_cumulative", {}).get("is_dangerous"): return "CAUTION_SOLAR", 1
        return "SAFE", 0

    # --- LÓGICA DE TEMPERATURA (PROMEDIO) ---
    def _check_temperature(self):
        thresholds = {
            "1min_peak": 45.0,        
            "15min_high": 40.0,       
            "1hour_sustained": 35.0, 
            "4hour_cumulative": 30.0   
        }
        results = {}
        count = len(self.temp_buffer)
        history = list(self.temp_buffer)

        for name, size in self.windows.items():
            if count >= size:
                segment = history[-size:]
                # Para temperatura usamos el promedio, no la suma de energía
                avg_temp = sum(segment) / size
                results[name] = {
                    "value": round(avg_temp, 2),
                    "is_dangerous": avg_temp >= thresholds[name]
                }
            else:
                results[name] = {"status": "collecting"}
        return results

    def _get_temp_verdict(self, results):
        if results.get("1min_peak", {}).get("is_dangerous"): return "CRITICAL_TEMP", 4
        if results.get("15min_high", {}).get("is_dangerous"): return "DANGER_TEMP", 3
        if results.get("1hour_sustained", {}).get("is_dangerous"): return "WARNING_TEMP", 2
        if results.get("4hour_cumulative", {}).get("is_dangerous"): return "CAUTION_TEMP", 1
        return "SAFE", 0

    # --- FUNCIÓN PÚBLICA PRINCIPAL ---
    def update_and_log(self, current_irrad, current_temp):
        """
        Esta es la ÚNICA función que tu main.py necesita llamar cada 5 segundos.
        Actualiza colas, evalúa ambos riesgos y guarda en CSV.
        """
        # 1. Actualizar memoria RAM
        self.irrad_buffer.append(current_irrad)
        self.temp_buffer.append(current_temp)

        # 2. Evaluar peligros
        irrad_results = self._check_irradiance()
        temp_results = self._check_temperature()

        # 3. Obtener veredictos
        i_status, i_priority = self._get_irrad_verdict(irrad_results)
        t_status, t_priority = self._get_temp_verdict(temp_results)

        # La prioridad global es la más grave de las dos
        max_priority = max(i_priority, t_priority)

        # Extraer dato de energía 1h para el log (si ya hay datos suficientes)
        energy_1h_info = irrad_results.get("1hour_sustained", {})
        energy_1h = energy_1h_info.get("value", 0.0) if "value" in energy_1h_info else 0.0

        # 4. Escribir en CSV
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"{timestamp},{current_irrad},{current_temp},{energy_1h},{max_priority},{i_status},{t_status}\n"

        try:
            with open(self.log_file, "a") as f:
                f.write(log_line)
            # Imprime por consola para debuguear durante la hackathon
            print(f"[{timestamp}] P:{max_priority} | Sol:{i_status} | Tmp:{t_status}")
        except Exception as e:
            print(f"[Monitor Error] CSV write failed: {e}")
            
        # Devolvemos la info por si el main quiere mostrarla en una pantalla OLED
        return max_priority, i_status, t_status