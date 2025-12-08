# 🌿 Smart Irrigation System using Raspberry Pi 5, IoT and Edge AI

This project is developed during the Labs of the subject **IoT Architecture**.

## By:
- Malek Ben Khalfallah  
- Wafa Lamloum

Under-graduated Students,  
**Embedded Systems and IoT Bachelors**  
Higher Institute of Multimedia Arts of Manouba (ISAMM),  
University of Manouba, Tunisia

---

## Under the supervision of:
**Hanen KARAMTI**  
Assistant Professor, Computer Science  
Higher Institute of Multimedia Arts of Manouba (ISAMM)  
University of Manouba, Tunisia

---

## Project Title:
**RayTech Smart Irrigation System**


---

## 📌 Description:
This project proposes an intelligent irrigation system that automatically controls water flow for plants based on real-time environmental conditions. Using **IoT sensors**, a **Raspberry Pi 5**, and **local machine learning**, the system determines when a plant needs watering and activates the pump accordingly.

It works **both online and offline**, stores data locally, synchronizes with the cloud when available, and allows the user to monitor and control irrigation through a web interface.

---

## Problem Statement and Objectives:

### Problem:
Traditional irrigation methods suffer from:
- Over-watering and water waste  
- Manual effort and low consistency  
- Lack of awareness of soil moisture, weather conditions, and water needs  
- No automation, no prediction, and no optimization  

### Objectives:
- Measure soil humidity, temperature, and environmental conditions in real-time  
- Predict irrigation needs using embedded machine learning  
- Automate watering based on plant needs and weather conditions  
- Provide remote and local monitoring through a web dashboard  
- Reduce water consumption and improve irrigation efficiency  
- Ensure full offline functionality with data synchronization when online  

---

## Requirements

### 🔧 **Hardware**
- **Raspberry Pi 5** (4–8 GB recommended)  
- Capacitive Soil Moisture Sensor (e.g., SEN0193)  
- Temperature & Humidity Sensor (DHT22)  
- Water Pump (5V)  
- Relay Module (5V or SSR)  
- Water Reservoir Level Sensor (Ultrasonic HC-SR04)
- RainDrop Module
- Jumper wires, breadboard or PCB  
- 5V power supply for pump  
- 5V USB-C supply for Raspberry Pi  
- Optional: RTC Module (DS3231), solar panel, enclosure  

### 💻 **Software**
- Raspberry Pi OS (64-bit)  
- Python 3.10+  
- Flask (Web server)  
- SQLite (local database)  
- scikit-learn or TensorFlow Lite (ML model)  
- Mosquitto (MQTT broker) (optional)  
- OpenWeatherMap API (optional weather integration)  
- Git for version control  

---

## Instructions for Equipment Installation:

1. **Prepare the Raspberry Pi 5**
   - Install Raspberry Pi OS (64-bit)
   - Enable SSH, I2C, and GPIO from `raspi-config`
   - Update system packages:
     ```bash
     sudo apt update && sudo apt upgrade -y
     ```

2. **Connect the Soil Moisture Sensor**
   - VCC → 3.3V  
   - GND → GND  
   - D0 →  GPIO24 (if digital)  

3. **Connect the Temperature/Humidity Sensor (DHT22)**
   - VCC → 3.3V  
   - GND → GND  
   - DATA → GPIO17 

4. **Connect the Relay Module**
   - IN → GPIO pin (e.g., GPIO26)
   - VCC → 5V  
   - GND → GND  
   - Relay output → Pump power line  

5. **Connect the Water Pump**
   
   - Pump + → Relay normally-open terminal  
   - Pump – → Power supply negative  
   - Power supply + → Relay common terminal

   - GND → GND  
   - Relay output → Pump power line  

6. **RainDrop module**
   - VCC  → 3.3V  
   - GND  → GND
   - Sig   → GPIO23
     
7. **Water Reservoir Level Sensor (Ultrasonic HC-SR04)**
   - VCC  → 5V  
   - GND  → GND
   - D0   → GPIO22
   - A0   → GPIO27

8. **Install Project Dependencies**
   ```bash
   pip install flask sqlite3 smbus2 RPi.GPIO scikit-learn
