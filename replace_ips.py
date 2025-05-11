#!/usr/bin/env python3

import re
import sys
import subprocess
import os

def replace_ip_in_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Replace IP addresses with placeholders
        original_content = content
        ip_patterns = [
            r'192\.168\.5\.144',
            r'192\.168\.1\.100',
            r'192\.168\.5\.164'
        ]
        
        for pattern in ip_patterns:
            content = re.sub(pattern, '{ip_address}', content)
            
        # Only write back if changes were made
        if content != original_content:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
            
        return False
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return False

def clean_repo():
    print("Starting IP address cleanup from git repository...")
    
    # Get all files in git history
    result = subprocess.run(
        ['git', 'log', '--pretty=format:', '--name-only', '--diff-filter=d'], 
        capture_output=True, 
        text=True
    )
    
    all_files = set(result.stdout.split('\n'))
    all_files = [f for f in all_files if f and (f.endswith('.md') or f.endswith('.sh'))]
    
    print(f"Found {len(all_files)} potential files to check")
    
    # Create a temporary script for BFG
    with open('replace_ips.txt', 'w') as f:
        f.write('192\\.168\\.5\\.144={ip_address}\n')
        f.write('192\\.168\\.1\\.100={ip_address}\n')
        f.write('192\\.168\\.5\\.164={ip_address}\n')
    
    print("Created replacements file. Now run in your git repo:")
    print("bfg --replace-text replace_ips.txt")
    print("\nIf you don't have BFG Repo-Cleaner, install it from:")
    print("https://rtyley.github.io/bfg-repo-cleaner/")
    print("\nAfter running BFG, complete the cleanup with:")
    print("git reflog expire --expire=now --all && git gc --prune=now --aggressive")

if __name__ == "__main__":
    clean_repo() 