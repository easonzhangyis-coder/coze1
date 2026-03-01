#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, '/workspace/projects/src')

from storage.database.db import get_session
from storage.database.knowledge_manager import KnowledgeManager

db = get_session()
try:
    manager = KnowledgeManager()
    
    test_data = [
        {
            "title": "劳动合同法 - 违法解除劳动合同的赔偿标准",
            "content": "根据《中华人民共和国劳动合同法》第48条规定：用人单位违反本法规定解除或者终止劳动合同的，应当依照本法第四十七条规定的经济补偿标准的二倍向劳动者支付赔偿金。经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。",
            "category": "劳动法",
            "tags": "违法解除,赔偿标准"
        },
        {
            "title": "工伤认定的标准和流程",
            "content": "根据《工伤保险条例》第14条规定：职工有下列情形之一的，应当认定为工伤：（一）在工作时间和工作场所内，因工作原因受到事故伤害的；（二）工作时间前后在工作场所内，从事与工作有关的预备性或者收尾性工作受到事故伤害的。",
            "category": "劳动法",
            "tags": "工伤认定"
        }
    ]
    
    for data in test_data:
        manager.create_knowledge(db, **data)
        print(f"Inserted: {data['title']}")
    
    print(f"Success: {len(test_data)} records")
    
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    db.close()
