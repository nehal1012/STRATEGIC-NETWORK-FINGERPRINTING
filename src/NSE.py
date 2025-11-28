import subprocess

def run_nmap_script(target, script):
    try:
        result = subprocess.run(['nmap', '--script', script, target], capture_output=True, text=True, check=True)
        return {"Output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"Error": "Nmap scan failed", "Message": str(e.output)}

def run_nmap_scan(target, options):
    try:
        result = subprocess.run(['nmap'] + options + [target], capture_output=True, text=True, check=True)
        return {"Output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"Error": "Nmap scan failed", "Message": str(e.output)}

def run_nse_script(target, script):
    try:
        result = subprocess.check_output(['nmap', '--script', script, target])
        return result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap script: {e}")
        return {"error": str(e)}
