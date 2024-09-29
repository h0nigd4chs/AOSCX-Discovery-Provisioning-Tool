import scapy.all as scapy
from scapy.layers.dhcp import DHCP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
import csv
import os
import threading
import time
from netmiko import ConnectHandler

# Filterkriterien für Option 60
option_60_patterns = ["6000", "6100", "6200", "6300", "6400"]

# CSV-Datei Pfad
csv_file = "dhcp_devices.csv"

# Gesehene Geräte speichern (um doppelte Einträge zu vermeiden)
seen_devices = set()

# Flag, um den Discovery-Prozess zu stoppen
stop_discovery = False

# Funktion zur Auswahl des Netzwerk-Interfaces
def select_interface():
    interfaces = scapy.get_if_list()
    print("Verfügbare Netzwerk-Interfaces (ohne Loopback):")
    for i, interface in enumerate(interfaces):
        if interface != "lo":  # Loopback-Interface ausschließen
            ip_addr = scapy.get_if_addr(interface)
            print(f"{i}: {interface} - IP-Adresse: {ip_addr}")
    
    idx = int(input("Bitte das Interface für die Überwachung auswählen: "))
    return interfaces[idx]

# Funktion zum Schreiben in die CSV-Datei
def write_to_csv(mac, ip, option_60):
    global seen_devices
    if (mac, ip, option_60) not in seen_devices:
        seen_devices.add((mac, ip, option_60))
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([mac, ip, option_60])
        print(f"Erkanntes Gerät: {mac}, {ip}, {option_60}")

# Funktion zum Extrahieren der IP-Adresse aus Option 50 (Requested IP Address)
def get_requested_ip(dhcp_options):
    for option in dhcp_options:
        if option[0] == 'requested_addr':
            return option[1]
    return None

# Callback-Funktion für das Scapy-Sniffing
def dhcp_packet_callback(packet):
    if packet.haslayer(DHCP):
        mac_addr = packet[Ether].src
        ip_addr = packet[IP].src if IP in packet else "0.0.0.0"

        if ip_addr == "0.0.0.0":
            ip_addr = get_requested_ip(packet[DHCP].options)
            if ip_addr is None:
                return

        for option in packet[DHCP].options:
            if option[0] == 'vendor_class_id':
                option_60 = option[1].decode('utf-8')
                if any(pattern in option_60 for pattern in option_60_patterns):
                    write_to_csv(mac_addr, ip_addr, option_60)
                break

# Funktion, um den Discovery-Prozess zu beenden
def stop_discovery_on_enter():
    global stop_discovery
    input("Drücken Sie die Eingabetaste, um den Discovery-Prozess zu beenden und fortzufahren...\n")
    stop_discovery = True

# Hauptfunktion für den Discovery-Prozess
def discovery():
    global stop_discovery
    if not os.path.exists(csv_file):
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["MAC-Adresse", "IP-Adresse", "Option 60"])

    interface = select_interface()
    print(f"Überwache DHCP-Requests auf Interface: {interface}")

    # Starte einen Thread, um den Discovery-Prozess mit Enter zu beenden
    discovery_thread = threading.Thread(target=stop_discovery_on_enter)
    discovery_thread.start()

    # Führe den Discovery-Prozess aus, bis Enter gedrückt wird
    while not stop_discovery:
        scapy.sniff(iface=interface, filter="udp and (port 67 or port 68)", prn=dhcp_packet_callback, store=0, timeout=1)

    # Discovery-Prozess wurde beendet
    print("Discovery-Prozess beendet.")

# Funktion, um Hosts aus der CSV-Datei zu lesen
def get_hosts_from_csv(csv_file):
    hosts = []
    try:
        with open(csv_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                hosts.append(row['IP-Adresse'])  # Hier wird die IP-Adresse jeder Zeile hinzugefügt
    except Exception as e:
        print(f"Fehler beim Lesen der CSV-Datei: {e}")
    return hosts

# Funktion, um Konfigurationsbefehle auf einem Host auszuführen
def configure_switch(host_ip, switch_number):
    aruba_cx_switch = {
        'device_type': 'aruba_os',
        'host': host_ip,
        'username': 'admin',
        'password': '',
        'secret': 'secret',
        'global_delay_factor': 4,
        'session_log': f'session_log_{host_ip}.txt'
    }

    try:
        connection = ConnectHandler(**aruba_cx_switch)
        connection.enable()

        # Dynamisch generierter Hostname
        hostname = f"pyswitch{switch_number:02d}"

        command_list = [
            f'conf t',
            f'hostname {hostname}',  # Hier wird der individuelle Hostname gesetzt
            'user admin password plaintext admin',
            'vlan 105',
            'name  TEST_105',
            'vlan 106',
            'name  TEST_106',
            'vlan 107',
            'name  TEST_107',
        ]

        for command in command_list:
            output = connection.send_command(command, expect_string=r'#')
            print(output)

        # Konfiguration speichern
        connection.send_command('write memory', expect_string=r'')

        connection.disconnect()

    except Exception as e:
        print(f"Fehler beim Verbinden oder Ausführen von Befehlen auf {host_ip}: {e}")

# Hauptprogramm für die Provisionierung
def provision():
    hosts = get_hosts_from_csv(csv_file)

    if hosts:
        for index, host_ip in enumerate(hosts, start=1):
            print(f"Verbinde zu Host: {host_ip}")
            configure_switch(host_ip, index)
    else:
        print("Keine Hosts in der CSV-Datei gefunden.")

# Start des kombinierten Workflows
if __name__ == "__main__":
    scan_choice = input("Möchten Sie den Scan (Discovery) durchführen?  [Empfehlung: min. 5 Minuten laufen lassen](y/n): ")
    if scan_choice.lower() == 'y':
        discovery()

        # Überprüfen, ob Geräte gefunden wurden
        if os.stat(csv_file).st_size == 0:
            print("Keine Geräte während des Scans gefunden. Das Skript wird beendet.")
            exit()
    else:
        print("Scan abgebrochen.")
        exit()

    provision_choice = input("Möchten Sie mit der Provisionierung beginnen? (y/n): ")
    if provision_choice.lower() == 'y':
        provision()
    else:
        print("Provisionierung abgebrochen.")
        exit()

    # Erfolgsmeldung nach Abschluss der Provisionierung
    print("\nPROVISIONIERUNG ERFOLGREICH BEENDET UND GESPEICHERT!\n -->Tool by fre4ki & h0nigd4chs")
    input("Drücken Sie die Eingabetaste, um das Skript zu beenden...")
