import os
import subprocess
import re
import json
from pathlib import Path

def get_ngrok_url():
    """Get the current ngrok URL"""
    try:
        # Try using ngrok API first
        result = subprocess.run(['ngrok', 'api', 'tunnels', 'list'], 
                              capture_output=True, text=True)
        tunnels = json.loads(result.stdout)
        
        # Find the first https tunnel
        for tunnel in tunnels.get('tunnels', []):
            if tunnel.get('proto') == 'https':
                return tunnel.get('public_url', '').replace('https://', '')
    except Exception as e:
        print(f"Error getting ngrok URL from API: {e}")
        try:
            # Fallback to checking ngrok process output
            result = subprocess.run(['ngrok', 'http', '8000', '--log=stdout'], 
                                  capture_output=True, text=True)
            # Look for the forwarding URL in the output
            for line in result.stdout.split('\n'):
                if 'https://' in line and 'ngrok-free.app' in line:
                    match = re.search(r'https://([^/]+)', line)
                    if match:
                        return match.group(1)
        except Exception as e:
            print(f"Error getting ngrok URL from process: {e}")
    return None

def update_env_file(ngrok_host=None):
    """Update the environment file with current settings"""
    env_file = Path('myenv/tokenemailandtelegram.txt')
    
    # Read existing environment variables
    env_vars = {}
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # Update environment variables
    env_vars['DJANGO_ENVIRONMENT'] = 'development'
    env_vars['DJANGO_DEBUG'] = 'True'
    
    if ngrok_host:
        env_vars['NGROK_HOST'] = ngrok_host
        print(f"Setting NGROK_HOST to: {ngrok_host}")
    else:
        # Remove NGROK_HOST if it exists
        env_vars.pop('NGROK_HOST', None)
        print("No ngrok host found, using localhost")
    
    # Write back to file
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"Environment file updated at: {env_file}")

def main():
    """Main function to manage environment"""
    # Get current ngrok URL
    ngrok_host = get_ngrok_url()
    
    if ngrok_host:
        print(f"Found ngrok URL: {ngrok_host}")
        update_env_file(ngrok_host)
    else:
        print("No ngrok tunnel found. Using localhost settings.")
        update_env_file()

if __name__ == '__main__':
    main() 