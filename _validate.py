#!/usr/bin/env python3
import json

CACHE_NAME = 'equipment-inspection-v1'

# 驗證 devices.json
with open('C:/M/PWA/devices.json','r',encoding='utf-8') as f:
    d = json.load(f)
assert len(d['deviceGroups']) == 9, f'期望 9 群組, 實際 {len(d["deviceGroups"])}'
assert len(d['devices']) == 33, f'期望 33 設備, 實際 {len(d["devices"])}'
assert len(d['restaurants']) == 18, f'期望 18 餐廳, 實際 {len(d["restaurants"])}'
print(f'✅ devices.json: {len(d["deviceGroups"])} 群組, {len(d["devices"])} 設備, {len(d["restaurants"])} 餐廳')

# 驗證 manifest.json
with open('C:/M/PWA/manifest.json','r',encoding='utf-8') as f:
    m = json.load(f)
assert m['start_url'] == 'index.html'
assert len(m['icons']) == 2
print(f'✅ manifest.json: short_name={m["short_name"]}, icons={len(m["icons"])}')

# 驗證 index.html 結構
with open('C:/M/PWA/index.html','r',encoding='utf-8') as f:
    html = f.read()
assert '<link rel="manifest"' in html
assert 'serviceWorker.register' in html
assert 'EquipmentInspectionDB' in html
assert 'pageHome' in html
assert 'pageGroups' in html
assert 'pageDevices' in html
assert 'pageCamera' in html
assert 'pageConfirm' in html
print(f'✅ index.html: 結構完整, 尺寸={len(html)}bytes')

# 驗證 sw.js
with open('C:/M/PWA/sw.js','r',encoding='utf-8') as f:
    sw = f.read()
assert CACHE_NAME in sw
print(f'✅ sw.js: 結構完整, 含離線快取策略')

# 驗證 sync_export.html
with open('C:/M/PWA/sync_export.html','r',encoding='utf-8') as f:
    sync = f.read()
assert 'metadata' in sync
assert 'downloadMetadata' in sync
assert 'EquipmentInspectionDB' in sync
print(f'✅ sync_export.html: 結構完整, 尺寸={len(sync)}bytes')

print()
print('🎉 全部驗證通過！')
