// SPDX-License-Identifier: MPL-2.0

#include <Arduino_Modulino.h>
#include <Arduino_RouterBridge.h>

// Create object instances
ModulinoThermo thermo;
ModulinoLight light;

unsigned long previousMillis = 0; 	// Stores last time values were updated
const long interval = 1000; 		// Every second

void setup() {
  Bridge.begin();

  // Initialize Modulino I2C communication
  Modulino.begin(Wire1);

  // Detect and connect to modules
  thermo.begin();
  light.begin();
}

void loop() {
  unsigned long currentMillis = millis(); // Get the current time
  
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // Leer temperatura y humedad
    float celsius = thermo.getTemperature();
    float humidity = thermo.getHumidity();

    // Leer luz (según doc oficial)
    light.update();
    int lux_raw = light.getLux();
    float lux = (float)lux_raw;

    // Enviar los 3 parámetros a Python
    Bridge.notify("record_sensor_samples", celsius, humidity, lux);
  }
}