## Relacion entre las tablas (Transporte). modelo fisico-relacional
participant
   └── participant_transport_km
           └── transport_vehicle
                   └── transport_energy_factor
Salida:
participant_transport_energy
   └── entropy_metric
                            
                            
                            
# Transformaciones de la encuesta limpia. Partimos del dataset limpio con columnas tipo:
id_participant
uso_car_combustion_congreso
uso_car_electric_congreso
uso_car_combustion_ocio
uso_car_electric_ocio
uso_bus_congreso
uso_bus_ocio
dist_km

# Adaptar el ETL para llenar participant_transport_km
     1. Calcular km por modo y participante
     Ejemplo: km_bus_combustion = (uso_bus_congreso * dist_km_alojamiento_PdC)+(uso_bus_ocio * average_dist_km_ocio)
     ¿Como calculamos dist_km_ocio? Podriamos conectar lugar que visito y alojamiento/PdC 

     2. ¿Como determinar tipo de vehículo?
     vehicle_mapping:
     | survey_mode | vehicle_type |
     | ------------------ | ----------------- |
     | bus                 | bus_combustion |
     | metro             |  metro.                 |
     | taxi                 | taxi electric         |

     3. Pasar a formato long = dataframe entrada directa para la calculadora:

     | participant_id | vehicle_type   | km |
     | -------------- | -------------- | -- |
     | 1              | bus_combustion | 5  |
     | 1              | car_electric   | 15 |
     | 2              | metro          | 8  |
     | 2              | bus_electric   | 3  |

# Implementar calculo de Energia transsporte
     1. cálculo de energía de transporte por participante 
     ```math
     E_{p,v} = km_{p,v} \times C_v \times F_e
     ```

     ```math
     E_p = \sum_{v} E_{p,v}
     ```

     **Donde**

     * (E_{p,v}): energía consumida por el participante (p) usando el vehículo (v) ([kJ])
     * (E_p): energía total de transporte del participante (p) ([kJ])
     * (km_{p,v}): kilómetros recorridos por el participante (p) con el vehículo (v) ([km])
     * (C_v): consumo energético por kilómetro del vehículo (v) ([l/km \ \text{o} \ kWh/km])
     * (F_e): factor de conversión energética del tipo de energía asociado al vehículo (v) ([kJ/l \ \text{o} \ kJ/kWh])
     
     
 # Input data is produced by the ETL described in `docs/etl_pipeline.md`.


