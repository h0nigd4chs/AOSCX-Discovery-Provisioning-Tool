# Aruba CX Initial Config Tool

Dieses Python-Skript automatisiert den Discovery-Prozess von Aruba CX Switches im Netzwerk und konfiguriert sie mit spezifischen Parametern. Es basiert auf **Scapy** und **Netmiko**, um DHCP-Requests zu überwachen und anschließend auf den gefundenen Switches Konfigurationsbefehle auszuführen. Jeder Switch erhält dabei einen individuellen Hostnamen.

## Funktionen

- **DHCP Discovery**: Überwacht den Netzwerkverkehr auf DHCP-Requests und protokolliert gefundene Geräte in einer CSV-Datei.
- **Individuelle Hostnamen**: Konfiguriert jeden gefundenen Switch mit einem eindeutigen Hostnamen (z. B. `pyswitch01`, `pyswitch02`, etc.).
- **Switch-Konfiguration**: Führt automatisch vordefinierte Konfigurationsbefehle auf jedem Switch aus, wie die Erstellung von VLANs und das Setzen eines Benutzerpassworts.
- **Logging**: Erstellt ein Session-Log für jeden konfigurierten Switch, um die ausgeführten Befehle und Rückmeldungen zu dokumentieren.

## Voraussetzungen

Stelle sicher, dass folgende Python-Bibliotheken installiert sind:

- [Scapy](https://scapy.net/)
- [Netmiko](https://github.com/ktbyers/netmiko)

Um die erforderlichen Pakete zu installieren, kannst du den folgenden Befehl ausführen:

```bash
pip install scapy netmiko

