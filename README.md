# Inquisitor
Inquisitor is a utility tool designed to perform ARP poisoning on a network and eavesdrop on FTP traffic.
This is a project with an educational objective, it is therefore deployed in a Docker environment. Two containers are created, an FTP server and a client. Random commands are passed from the client to the server.
However, it is possible to run Inquisitor in a real environment, using the python script present in the **/demo/inquisitor** folder.

----

## Prerequisites:

- Docker: Ensure that you have Docker installed and running on your system.

----

## Setup & Usage:

1. **Help**
To see all available commands and their descriptions, run:

``make help``

2. **Launch the Demo**
To launch the demo (ftp server + ftp client) setup in the background, run:

``make up-demo``

3. **Run Inquisitor**
To execute Inquisitor and start ARP poisoning and listening for FTP traffic, use the following:

- For default output:

``make run-inquisitor``

- For verbose output:

``make run-inquisitor-v``

4. **Shutdown the Demo**
To stop and remove the demo setup, run:

``make down-demo``

5. **Monitor Logs**
To view the logs of the demo setup, use:

``make logs-demo``

7. **Fetch Addresses / ARP table**
To retrieve the addresses and ARP Table of the demo setup, execute:

``make show-arp``

8. **Cleanup**
To stop the demo and clean up all Docker resources, use:

``make fclean``

----

## ARP Poisoning

### Definition:

ARP poisoning, also known as ARP spoofing or ARP cache poisoning, is a type of attack in which an attacker sends falsified Address Resolution Protocol (ARP) messages over a local area network (LAN). The goal of the attack is to associate the attacker's MAC address with the IP address of another node, such as the default gateway. This type of attack can lead to the attacker intercepting, modifying, or blocking communications to and from the victim.

### How ARP Poisoning Works:

- **Mapping**: At the heart of ARP is a simple mapping of 32-bit IP addresses to MAC addresses. Each computer maintains a table, known as the ARP cache, which stores this mapping.

- **Trust**: ARP operates on a basis of trust – it assumes that any ARP response received is genuine. There's no method of authentication in place.

- **Attack**: An attacker can exploit this trust by sending fake ARP responses. No ARP request is required; the attacker can send unsolicited ARP responses.

- **Result**: The attacker's MAC address is paired with the IP of a legitimate device on the network. This means that any traffic meant for that IP will go to the attacker instead.

In this code, we do not explicitly relay packets from one target to another. However, when we poison the ARP table, we indicate to targets that the MAC address associated with the IP address of the other target is actually the MAC address of our (attacker) machine. So the targets send us the packets.

**But then, how do these packets reach their original destination?**

**The answer lies in the default behavior of modern operating systems**, which act as "transparent" hosts for packets not intended for them. **When the attacker's machine receives a packet intended for another IP address** (even if the packet was sent to the attacker's MAC address due to ARP poisoning), it recognizes that this packet is not not for her. Rather than deleting it, **the operating system defaults it to its true destination**. It is this behavior that allows packets to reach their destination even after being intercepted by the attacker's machine.


### Implications of ARP Poisoning:

1. **Man-in-the-Middle (MitM) Attack**: ARP poisoning can be used to perform a MitM attack where the attacker intercepts the traffic between two victims, potentially altering the data before forwarding it.

2. **Denial of Service (DoS) Attack**: The attacker can also use ARP poisoning to block the victim's communications by not forwarding the victim's traffic.

3. **Data Theft**: By intercepting the victim's traffic, sensitive data such as login credentials can be stolen.

----

## Note:

ARP poisoning and packet sniffing can be malicious activities when performed without proper authorization. Always ensure that you have the necessary permissions when using this tool, especially on networks that you don't own. Use Inquisitor responsibly!
