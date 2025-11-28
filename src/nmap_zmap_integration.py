import xml.etree.ElementTree as ET
import csv
import json
import nmap


def parse_nmap_output(file_path):

    tree = ET.parse(file_path)
    root = tree.getroot()
    hosts = []
    for host in root.findall('host'):
        host_info = {
            'ip': host.find('address').get('addr'),
            'hostname': host.find('hostnames/hostname').get('name') if host.find('hostnames/hostname') is not None else 'Unknown',
            'ports': []
        }
        for port in host.find('ports').findall('port'):
            port_info = {
                'portid': port.get('portid'),
                'protocol': port.get('protocol'),
                'service': port.find('service').get('name') if port.find('service') is not None else 'Unknown'
            }
            host_info['ports'].append(port_info)
        hosts.append(host_info)
    return hosts


def parse_zmap_output(file_path):
    """Parses ZMap scan output in CSV format.

    Args:
        file_path (str): Path to the ZMap scan output file (CSV).

    Returns:
        list: A list of dictionaries, each representing a host with its IP and a default port (80).
    """

    hosts = []
    try:
        with open(file_path, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                hosts.append({'ip': row['saddr'], 'port': '80'})
    except FileNotFoundError:
        print(f"Warning: ZMap output file {file_path} not found. Continuing without ZMap data.")
    return hosts


def integrate_data(nmap_data, zmap_data):
    """Integrates data from Nmap and Zmap scans.

    Args:
        nmap_data (list): List of dictionaries representing hosts from Nmap scan.
        zmap_data (list): List of dictionaries representing hosts from Zmap scan.

    Returns:
        list: A list of dictionaries with integrated data for each host (IP, hostname, ports).
    """

    integrated_data = {host['ip']: host for host in nmap_data}
    for host in zmap_data:
        if host['ip'] in integrated_data:
            integrated_data[host['ip']]['ports'].append({'portid': '80', 'protocol': 'tcp', 'service': 'http'})
        else:
            integrated_data[host['ip']] = {
                'ip': host['ip'],
                'hostname': 'Unknown',
                'ports': [{'portid': '80', 'protocol': 'tcp', 'service': 'http'}]
            }
    return list(integrated_data.values())


def run_integration(nmap_file='nmap_scan.xml', zmap_file='zmap_scan.csv'):
    """Runs the integration process for Nmap and Zmap scan data.

    Args:
        nmap_file (str, optional): Path to the Nmap scan output file (XML). Defaults to 'nmap_scan.xml'.
        zmap_file (str, optional): Path to the Zmap scan output file (CSV). Defaults to 'zmap_scan.csv'.

    Returns:
        list: A list of dictionaries with integrated data for each host (IP, hostname, ports).
    """

    nmap_data = parse_nmap_output(nmap_file)
    zmap_data = parse_zmap_output(zmap_file)
    integrated_data = integrate_data(nmap_data, zmap_data)
    with open('integrated_output.json', 'w') as f:
        json.dump(integrated_data, f, indent=4)
    return integrated_data


def run_nmap_scan(target, arguments='-sV'):
    nm = nmap.PortScanner()
    nm.scan(target, arguments=arguments)
    return nm

if __name__ == "__main__":
    # This block is for testing the integration independently
    target = '127.0.0.1'  # Replace with your target
    
    # Run Nmap scan
    nm = run_nmap_scan(target)
    nm.save_scan_to_file('nmap_scan.xml')
    
    # Run integration
    integrated_data = run_integration()
    
    print(json.dumps(integrated_data, indent=4))