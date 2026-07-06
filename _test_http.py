#!/usr/bin/env python3
import json, urllib.request

# 測試 index.html
resp = urllib.request.urlopen('http://localhost:8080/index.html')
html = resp.read().decode()
print(f'index.html: {resp.status} {len(html)}bytes - OK')

# 測試 devices.json
resp = urllib.request.urlopen('http://localhost:8080/devices.json')
d = json.loads(resp.read().decode())
print(f'devices.json: {resp.status} - {len(d["deviceGroups"])} groups, {len(d["devices"])} devices, {len(d["restaurants"])} restaurants - OK')

# 測試 manifest.json
resp = urllib.request.urlopen('http://localhost:8080/manifest.json')
m = json.loads(resp.read().decode())
print(f'manifest.json: {resp.status} - short_name={m["short_name"]} - OK')

# 測試 sw.js
resp = urllib.request.urlopen('http://localhost:8080/sw.js')
sw = resp.read().decode()
print(f'sw.js: {resp.status} {len(sw)}bytes - OK')

# 測試 sync_export.html
resp = urllib.request.urlopen('http://localhost:8080/sync_export.html')
sync = resp.read().decode()
print(f'sync_export.html: {resp.status} {len(sync)}bytes - OK')

print()
print('🎉 所有檔案透過 HTTP Server 測試通過！')
