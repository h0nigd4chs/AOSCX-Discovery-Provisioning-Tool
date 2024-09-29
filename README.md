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
python -m pip install scapy netmiko
```

## Verwendung

### 1. **Discovery-Modus:**

Das Skript beginnt mit einem Discovery-Prozess, bei dem es nach Aruba CX Switches im Netzwerk sucht. Dazu musst du ein Netzwerk-Interface auswählen, das überwacht werden soll.

```bash
python ultra.py
```

Das Skript wird dich fragen, ob du den Discovery-Prozess starten möchtest, wir empfehlen hier mal 5 Minuten druchlaufen zu lassen, da manche Switche Zeit brauchen obwohl sie entdeckt wurden:

```
Möchten Sie den Scan (Discovery) durchführen? [Empfehlung: min. 5 Minuten laufen lassen](y/n):
```

Falls **ja**, wird das Skript DHCP-Requests überwachen und gefundene Geräte in die Datei `dhcp_devices.csv` schreiben.

### 2. **Provisionierung:**

Nach dem Discovery-Prozess wird das Skript die gefundenen Geräte automatisch konfigurieren. Hierbei erhält jeder Switch einen eindeutigen Hostnamen und die vordefinierten Befehle (wie das Setzen von VLANs und Passworten) werden ausgeführt.

Das Skript fragt anschließend, ob die Provisionierung gestartet werden soll:

```
Möchten Sie mit der Provisionierung beginnen? (y/n):
```

Falls **ja**, wird das Skript eine SSH-Verbindung zu jedem Gerät herstellen und die Konfiguration anwenden.

### 3. **Erfolgsmeldung:**

Nach erfolgreicher Konfiguration und 'write memory' wird folgende Meldung ausgegeben:

```
PROVISIONIERUNG ERFOLGREICH BEENDET! Tool by fre4ki & h0nigd4chs
```

### Individuelle Hostnamen

Der erste Switch wird mit dem Hostnamen `pyswitch01` konfiguriert, der zweite mit `pyswitch02` und so weiter.

## CSV-Datei `dhcp_devices.csv`

Diese Datei wird nach dem Discovery-Prozess erstellt und enthält die gefundenen Geräte. Sie hat folgendes Format:

```
MAC-Adresse, IP-Adresse, Option 60
```

Die Provisionierung basiert auf den IP-Adressen, die in dieser Datei gespeichert sind.

## Konfigurationsbefehle

Folgende Befehle werden auf jedem Switch ausgeführt:

- **Hostname setzen**: `hostname pyswitchXX` (wobei `XX` eine laufende Nummer ist)
- **Benutzerpasswort setzen**: `user admin password plaintext admin`
- **VLANs konfigurieren**:
  - VLAN 105: `vlan 105 name TEST_105`
  - VLAN 106: `vlan 106 name TEST_106`
  - VLAN 107: `vlan 107 name TEST_107`
  
Jeder Befehl wird auf den Switches per SSH ausgeführt.

## Log-Dateien

Jede SSH-Sitzung wird in einer Log-Datei gespeichert. Die Log-Dateien werden im Format `session_log_<IP-Adresse>.txt` erstellt, z. B. `session_log_192.168.1.1.txt`.

## Anpassungen

Falls du Anpassungen an den Konfigurationsbefehlen oder den Hostnamen vornehmen möchtest, kannst du dies im Skript im Abschnitt `command_list` tun:

```python
command_list = [
    f'conf t',
    f'hostname {hostname}',
    'user admin password plaintext admin',
    'vlan 105',
    'name  TEST_105',
    'vlan 106',
    'name  TEST_106',
    'vlan 107',
    'name  TEST_107',
]
```

## Contributors

Vielen Dank an die folgenden Personen, die zu diesem Projekt beigetragen haben:

- fre4ki(https://github.com/fre4ki) – hat bei der Entwicklung des Tools mitgearbeitet


## Lizenz

MIT License

Copyright (c) 2024 h0nigd4chs

Hiermit wird unentgeltlich jeder Person, die eine Kopie der Software und der zugehörigen Dokumentationen (die "Software") erhält, die Erlaubnis erteilt, uneingeschränkt mit der Software zu handeln, einschließlich ohne Einschränkung dem Recht, sie zu verwenden, zu kopieren, zu verändern, zusammenzuführen, zu veröffentlichen, zu verbreiten, zu unterlizenzieren und zu verkaufen, und Personen, die die Software erhalten, diese Rechte zu gewähren, unter den folgenden Bedingungen:

Der obige Urheberrechtshinweis und dieser Erlaubnishinweis sind in allen Kopien oder wesentlichen Teilen der Software beizufügen.

DIE SOFTWARE WIRD OHNE JEDE AUSDRÜCKLICHE ODER IMPLIZIERTE GARANTIE BEREITGESTELLT, EINSCHLIESSLICH DER GARANTIE DER MARKTFÄHIGKEIT, DER EIGNUNG FÜR EINEN BESTIMMTEN ZWECK UND DER NICHTVERLETZUNG. IN KEINEM FALL SIND DIE AUTOREN ODER URHEBER RECHTLICH HAFTBAR FÜR JEGLICHE ANSPRÜCHE, SCHÄDEN ODER ANDERE VERPFLICHTUNGEN, OB AUS EINEM VERTRAGSVERHÄLTNIS, EINEM UNRECHTMÄSSIGEN HANDELN ODER ANDERWEITIG, DIE AUS DER SOFTWARE ODER DER VERWENDUNG ODER ANDEREN GESCHÄFTEN MIT DER SOFTWARE ENTSTEHEN.

