from flask import Flask, render_template, request, jsonify
import re
import requests
from Shodan import get_shodan_data
from Hunter import get_hunter_data
import nmap
import subprocess
import topology
import utils
import json
import xml.etree.ElementTree as ET
import csv
import os
import asyncio
from functools import lru_cache
from datetime import datetime, timedelta

app = Flask(__name__)

# Define the URL and IP pattern for validation
url_pattern = re.compile(
    r'^(?:http|ftp)s?://'
    r'(?:(?:[A-Z0-9?\.]+)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
    r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'
    r'(?::\d+)?'
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

@lru_cache(maxsize=100)
def cached_nmap_scan(ip):
    nm = nmap.PortScanner()
    nm.scan(ip, arguments='-F -sS -sV --version-intensity 0')
    return nm[ip]

async def async_nmap_scan(target):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, cached_nmap_scan, target)

def parse_nmap_output(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        hosts = []
        for host in root.findall('host'):
            # ... (existing code to parse host information)
            return hosts
    except ET.ParseError as e:
        print(f"XML parsing error: {e}")
        return []
    except FileNotFoundError as e:
        print(f"File not found: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def parse_zmap_output(file_path):
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
    nmap_data = parse_nmap_output(nmap_file)
    zmap_data = parse_zmap_output(zmap_file)
    
    if not nmap_data and not zmap_data:
        print("Warning: Both Nmap and ZMap data are missing. No integration performed.")
        return []
    
    integrated_data = integrate_data(nmap_data, zmap_data)
    with open('integrated_output.json', 'w') as f:
        json.dump(integrated_data, f, indent=4)
    return integrated_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
async def index_post():
    if request.method == 'POST':
        query = request.form['query']
        nse_script = request.form.get('nse_script', '')

        print(f"Received query: {query}")
        print(f"Received NSE script: {nse_script}")

        if re.match(url_pattern, query):
            # It's a valid URL
            url_info = get_url_info(query)
            nse_info = run_nse_script(query, nse_script) if nse_script else {}
            return render_template('results.html', url_info=url_info, nse_info=nse_info, type='url')
        elif re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query):
            # Assume it's a domain
            shodan_info = get_shodan_data(query)
            hunter_info = get_hunter_data(query)
            nse_info = run_nse_script(query, nse_script) if nse_script else {}
            return render_template('results.html', shodan_info=shodan_info, hunter_info=hunter_info, nse_info=nse_info, type='domain')
        else:
            # Assume it's an IP address
            shodan_info = get_shodan_data(query)
            hunter_info = get_hunter_data(query)

            # Asynchronous Nmap scan
            nmap_result = await async_nmap_scan(query)
            
            # Debugging: Print the structure of nmap_result
            print("Nmap scan result:", nmap_result)
            
            # Save Nmap results to XML
            nmap_xml_output = nmap_result.get('nmap', {}).get('scaninfo', {}).get('xmloutputversion', '')
            if nmap_xml_output:
                with open('nmap_scan.xml', 'w') as f:
                    f.write(nmap_xml_output)
            
            nmap_info = nmap_result.get('tcp', {})
            nse_info = run_nse_script(query, nse_script) if nse_script else {}

            # Run integration
            integrated_data = run_integration('nmap_scan.xml', 'zmap_scan.csv')

            # Combine data into a network structure
            shodan_data = shodan_info.get('data', [])
            shodan_ips = [entry['ip_str'] for entry in shodan_data] if isinstance(shodan_data, list) else []
            
            nmap_ips = list(nmap_info.keys())

            query = list(set(shodan_ips + nmap_ips))

            network_data = {
                'query': query
            }

            # Construct and visualize topology
            topology_data = topology.bfs_topology(query, network_data)
            G = topology.construct_topology(topology_data)
            topology.visualize_topology(G)

            return render_template('results.html', shodan_info=shodan_info, hunter_info=hunter_info, 
                                   nmap_info=nmap_info, nse_info=nse_info, topology_data=topology_data, 
                                   integrated_data=integrated_data, type='ip')
    return render_template('index.html')


@app.route('/results')
def results():
    integrated_data = run_integration()
    return render_template('results.html', data=integrated_data)

@app.route('/data')
def data():
    with open('integrated_output.json') as f:
        data = json.load(f)
    return jsonify(data)

def get_url_info(url):
    print(f"Retrieving info for URL: {url}")
    return {"url": url, "info": "This is a dummy implementation."}

def run_nse_script(target, script):
    try:
        result = subprocess.check_output(['nmap', '--script', script, target])
        return result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap script: {e}")
        return {"error": str(e)}

# Add Nmap directory to the PATH
nmap_path = r'C:\Program Files (x86)\Nmap'  # Update this path if necessary
if nmap_path not in os.environ['PATH']:
    os.environ['PATH'] += os.pathsep + nmap_path

if __name__ == '__main__':
    app.run(debug=True)
