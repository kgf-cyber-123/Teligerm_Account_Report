#_____ DAVLOPER BY KALYAN KING -()
#___ TELIGERM : KGF CYBER TEAM 🍐
import os
import requests
from time import sleep
from configparser import ConfigParser
from os import system, name
from threading import Thread, active_count
import csv
import phonenumbers
from phonenumbers import PhoneNumber, PhoneNumberFormat
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from bs4 import BeautifulSoup
import random
from emailtools import generate
import re

software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value, SoftwareName.EDGE.value, SoftwareName.OPERA.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MAC.value]

user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=1200)

THREADS = 600
PROXIES_TYPES = ('http', 'socks4', 'socks5')

errors = open('errors.txt', 'a+')

time_out = 15
success_count = 0
error_count = 0
username = ""

# Fixed headers from the request
BASE_HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.9,hi;q=0.8,es;q=0.7,pt;q=0.6',
    'cache-control': 'max-age=0',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://telegram.org',
    'priority': 'u=0, i',
    'referer': 'https://telegram.org/support',
    'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1'
}

def generate_random_phone_number():
    while True:
        country_code = "+{}".format(random.randint(1, 999))
        national_number = str(random.randint(1000000000, 9999999999))
        phone_number_str = country_code + national_number
        try:
            phone_number = phonenumbers.parse(phone_number_str)
            if phonenumbers.is_valid_number(phone_number):
                return phonenumbers.format_number(phone_number, PhoneNumberFormat.E164)
        except phonenumbers.phonenumberutil.NumberParseException:
            continue

def get_random_line(filename, username):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            if not lines:
                return f"Please unban {username}"
            line = random.choice(lines).strip()
            return line.replace('{username}', username)
    except FileNotFoundError:
        return f"Please unban {username}"

def extract_csrf_token(html):
    """Extract CSRF token from the form if present"""
    soup = BeautifulSoup(html, 'html.parser')
    token_input = soup.find('input', {'name': 'csrf_token'})
    if token_input:
        return token_input.get('value', '')
    return None

def control(proxy, proxy_type, username):
    global success_count
    global error_count
    
    USER_AGENT = user_agent_rotator.get_random_user_agent()
    headers = BASE_HEADERS.copy()
    headers['user-agent'] = USER_AGENT
    
    url = 'https://telegram.org/support'
    
    try:
        # Step 1: GET request to get cookies and form
        session = requests.Session()
        response = session.get(url, proxies={'http': f'{proxy_type}://{proxy}', 'https': f'{proxy_type}://{proxy}'}, timeout=time_out, headers=headers)
        
        if response.status_code != 200:
            error_count += 1
            return
        
        # Extract CSRF token if present
        csrf_token = extract_csrf_token(response.text)
        
        # Parse the form
        soup = BeautifulSoup(response.text, 'html.parser')
        form = soup.find('form', action="/support")
        
        if not form:
            error_count += 1
            return
        
        # Generate random data
        message = get_random_line('message.txt', username)
        email = generate('gmail')
        phone = generate_random_phone_number()
        
        # Build form data
        data = {}
        
        # Get all input fields
        for input_tag in form.find_all(['input', 'textarea']):
            name = input_tag.get('name')
            if name:
                if name == 'csrf_token' and csrf_token:
                    data[name] = csrf_token
                elif 'email' in name.lower():
                    data[name] = email
                elif 'phone' in name.lower():
                    data[name] = phone
                elif 'problem' in name.lower() or 'message' in name.lower():
                    data[name] = message
                else:
                    data[name] = input_tag.get('value', '')
        
        # Also check for textarea specifically for message
        textarea = form.find('textarea')
        if textarea:
            textarea_name = textarea.get('name')
            if textarea_name:
                data[textarea_name] = message
        
        # Step 2: POST request with exact headers
        post_headers = headers.copy()
        post_headers['cookie'] = '; '.join([f"{k}={v}" for k, v in session.cookies.items()])
        post_headers['content-length'] = str(len('&'.join([f"{k}={v}" for k, v in data.items()])))
        
        response = session.post(url, data=data, headers=post_headers, timeout=time_out)
        
        if response.status_code == 200:
            print(f"✅ Report Successful | Email: {email} | Phone: {phone} | Proxy: {proxy}:{proxy_type}\n")
            success_count += 1
        else:
            print(f"❌ Report Failed | Status: {response.status_code} | Proxy: {proxy}:{proxy_type}")
            error_count += 1
            
    except requests.exceptions.Timeout:
        error_count += 1
    except requests.exceptions.ConnectionError:
        error_count += 1
    except Exception as e:
        error_count += 1
        errors.write(f'{e}\n')

def get_views_from_saved_proxies(proxy_type, proxies, username):
    for proxy in proxies:
        if proxy.strip():
            control(proxy.strip(), proxy_type, username)

def start_view():
    while True:
        threads = []
        for proxy_type in PROXIES_TYPES:
            try:
                with open(f"{proxy_type}_proxies.txt", 'r') as file:
                    proxies = [p.strip() for p in file.readlines() if p.strip()]
                
                # Filter to only working proxies
                chunked_proxies = [proxies[i:i + 70] for i in range(0, len(proxies), 70)]
                
                for chunk in chunked_proxies:
                    thread = Thread(target=get_views_from_saved_proxies, args=(proxy_type, chunk, username))
                    threads.append(thread)
                    thread.start()
                    
            except FileNotFoundError:
                print(f"⚠️ {proxy_type}_proxies.txt not found")
                continue
        
        for t in threads:
            t.join()
        
        sleep(2)  # Small delay between loops

E = '\033[1;31m'
B = '\033[2;36m'
G = '\033[1;32m'
S = '\033[1;33m'
W = '\033[0m'

def check_views():
    global success_count
    global error_count
    
    while True:
        os.system('cls' if name == 'nt' else 'clear')
        os.system("xdg-open https://t.me/+2IyuPFRtd5E1ZTFl")
        print(f'''
{G}██╗░░██╗░██████╗░███████╗
██║░██╔╝██╔════╝░██╔════╝
█████═╝░██║░░██╗░█████╗░░
██╔═██╗░██║░░╚██╗██╔══╝░░
██║░╚██╗╚██████╔╝██║░░░░░
╚═╝░░╚═╝░╚═════╝░╚═╝░░░░░
{B}========================
{G} DAVLOPER : Kalyan KING 
{G} TOOL : TELIGERM iD REPOTED
{G}║ {B}Active Threads   {W}: {B}{active_count()}{' ' * (20 - len(str(active_count())))}{G}║
{G}║ {S}Successful Reports{W}: {S}{success_count}{' ' * (24 - len(str(success_count)))}{G}║
{G}║ {E}Failed Reports   {W}: {E}{error_count}{' ' * (24 - len(str(error_count)))}{G}║
{G}╚═══════════════════════════════════════════════════╝
        ''')
        sleep(4)

if __name__ == "__main__":
    username = input("Enter username or link to report: ")
    
    # Extract username from link if needed
    if 't.me/' in username:
        username = username.split('t.me/')[-1].split('/')[0]
    
    print(f"{G}Starting reports for: {S}{username}{W}")
    
    Thread(target=start_view).start()
    Thread(target=check_views).start()