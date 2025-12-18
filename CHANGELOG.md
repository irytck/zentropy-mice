# Changelog

## [Unreleased]
- Inicial: esquema SQL, docker-compose, notebooks de limpieza y cálculo de emisiones.
- MVP calculadora: script Python basado en Excel.

### Added
- Physical transport energy model based on vehicle consumption and energy conversion factors.
- New tables: transport_vehicle, transport_energy_factor, participant_transport_km.
- Initial transport energy calculator (kJ-based).

### Changed
- Deprecated `trip` table for daily transport calculations.