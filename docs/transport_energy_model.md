## Contexto

Este documento describe el **modelo físico de cálculo de energía de transporte urbano**
en el proyecto Zentropy MICE.

El modelo consume exclusivamente datos derivados de eventos de movilidad urbana
almacenados en la tabla `participant_transport_event` y factores físicos definidos
en `transport_vehicle` y `transport_energy_factor`.

Este modelo **no accede directamente a datos de encuesta** ni realiza tareas de ETL.

---

## Modelo físico–relacional (transporte urbano)

Relación conceptual entre entidades:

participant  
└── participant_transport_event  
  └── transport_vehicle  
    └── transport_energy_factor  

Salida conceptual del cálculo:

participant_transport_energy  
(tabla derivada, no persistente en esta fase)

---

## Evento de entrada

Cada fila en `participant_transport_event` representa un evento homogéneo de movilidad urbana:

| Campo | Descripción |
|------|------------|
| participant_id | Identificador del congresista |
| vehicle_id | Tipo de vehículo utilizado |
| context_id | Contexto del desplazamiento (congreso / ocio) |
| distance_km | Distancia recorrida en km |
| distance_method | observed / average / synthetic |
| assumption_flag | Indica si el valor se basa en supuestos |

---

## Modelo de cálculo energético

### Energía por evento

La energía consumida en un evento de movilidad se calcula como:

```math
E_{e} = distance_{e} \times C_v \times F_e
````

Donde:

* ( distance_e ): distancia del evento (km)
* ( C_v ): consumo energético del vehículo (l/km o kWh/km)
* ( F_e ): factor de conversión energética (kJ/l o kJ/kWh)

---

### Energía total por participante

La energía total de transporte de un participante se obtiene agregando todos sus eventos:

```math
E_p = \sum_{e \in p} E_e
```

---

## Consideraciones metodológicas

* El cálculo energético se realiza **a nivel de evento**, no a nivel agregado.
* La agregación por participante, congreso o ciudad se realiza **posteriormente**.
* La incertidumbre asociada a distancias estimadas se conserva mediante
  `distance_method` y `assumption_flag`.

---

## Relación con la entropía

La energía total calculada constituye una de las entradas del modelo de entropía
del sistema, que se implementará en una fase posterior.

---

## Origen de los datos

Los eventos de entrada son generados por el pipeline ETL descrito en:

`docs/etl_pipeline.md`

```