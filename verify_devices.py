#!/usr/bin/env python3
import json
with open('C:/M/PWA/devices.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
for g in d['deviceGroups']:
    icon = g['icon']
    print(f'{icon} {g["name"]} ({len(g["devices"])} devices)')
    for dev in g['devices']:
        print(f'   - {dev["name"]} [{len(dev["abnormalTypes"])} abnormal types]')
print(f'Total restaurants: {len(d["restaurants"])}')
print(f'Total devices index: {len(d["devices"])}')
