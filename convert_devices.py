#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
將「設備回饋模板庫.json」轉換為 PWA 用的 devices.json（精簡版）
產出路徑: C:\M\PWA\devices.json
"""

import json
import os

# 輸入/輸出路徑
INPUT_PATH = r'C:\M\各店日巡\設備回饋模板庫.json'
OUTPUT_PATH = r'C:\M\PWA\devices.json'

# 餐廳列表（PM 規格書指定 18 間）
RESTAURANTS = [
    {"code": "S203", "name": "中和中正店"},
    {"code": "S217", "name": "中和店"},
    {"code": "S205", "name": "永和店"},
    {"code": "S208", "name": "板橋店"},
    {"code": "S210", "name": "新店店"},
    {"code": "S211", "name": "土城店"},
    {"code": "S212", "name": "樹林店"},
    {"code": "S213", "name": "三重店"},
    {"code": "S215", "name": "蘆洲店"},
    {"code": "S218", "name": "汐止店"},
    {"code": "S221", "name": "泰山店"},
    {"code": "S222", "name": "林口店"},
    {"code": "S223", "name": "桃園店"},
    {"code": "S225", "name": "中壢店"},
    {"code": "S227", "name": "平鎮店"},
    {"code": "S228", "name": "八德店"},
    {"code": "S229", "name": "楊梅店"},
    {"code": "S446", "name": "板橋府中店"},
]

def main():
    # 讀取原始模板庫
    with open(INPUT_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    pwa_data = {
        "version": "1.0",
        "generatedAt": "2026-07-06",
        "deviceGroups": [],
        "devices": {},
        "restaurants": RESTAURANTS
    }

    # 萃取每個群組與裝置
    for group_name, group_data in data['device_groups'].items():
        grp = {
            "name": group_name,
            "key": group_data['group_key'],
            "icon": group_data['icon'],
            "description": group_data['description'],
            "devices": []
        }

        for device_name in group_data['devices']:
            device_info = data['devices'].get(device_name, {})
            feedback = device_info.get('feedback_templates', {})

            # 萃取異常類型（排除「正常」）
            abnormal_types = []
            for t_key in feedback:
                if t_key != '正常':
                    abnormal_types.append({
                        "key": t_key,
                        "label": t_key.replace('異常_', ''),
                        "template": feedback[t_key].get('template', ''),
                        "severity": feedback[t_key].get('severity', 'medium'),
                        "action": feedback[t_key].get('action', ''),
                        "vendor": feedback[t_key].get('vendor_hint', '')
                    })

            device_entry = {
                "name": device_name,
                "key": device_info.get('device_key', device_name),
                "abnormalTypes": abnormal_types
            }
            grp['devices'].append(device_entry)

            # 加入 devices 對照表
            pwa_data['devices'][device_name] = {
                "key": device_info.get('device_key', device_name),
                "group": group_name,
                "groupIcon": group_data['icon'],
                "abnormalTypes": abnormal_types
            }

        pwa_data['deviceGroups'].append(grp)

    # 寫出
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(pwa_data, f, ensure_ascii=False, indent=2)

    # 統計
    total_devices = sum(len(g['devices']) for g in pwa_data['deviceGroups'])
    print(f'✅ devices.json 已產生')
    print(f'   群組數: {len(pwa_data["deviceGroups"])}')
    print(f'   裝置數: {total_devices}')
    print(f'   餐廳數: {len(pwa_data["restaurants"])}')
    print(f'   輸出路徑: {OUTPUT_PATH}')

if __name__ == '__main__':
    main()
