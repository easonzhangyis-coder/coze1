#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
插入测试知识库数据
"""

import sys
import os

# 添加项目路径到 PYTHONPATH
sys.path.insert(0, '/workspace/projects/src')

from storage.database.db import get_session
from storage.database.knowledge_manager import KnowledgeManager

def insert_test_data():
    """插入测试知识库数据"""
    db = get_session()
    try:
        manager = KnowledgeManager()
        
        # 测试数据：劳动法相关知识
        test_data = [
            {
                "title": "劳动合同法 - 违法解除劳动合同的赔偿标准",
                "content": "根据《中华人民共和国劳动合同法》第48条规定：用人单位违反本法规定解除或者终止劳动合同的，应当依照本法第四十七条规定的经济补偿标准的二倍向劳动者支付赔偿金。经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。六个月以上不满一年的，按一年计算；不满六个月的，向劳动者支付半个月工资的经济补偿。",
                "category": "劳动法",
                "tags": "违法解除,赔偿标准,经济补偿"
            },
            {
                "title": "劳动争议仲裁的时效规定",
                "content": "根据《中华人民共和国劳动争议调解仲裁法》第27条规定：劳动争议申请仲裁的时效期间为一年。仲裁时效期间从当事人知道或者应当知道其权利被侵害之日起计算。劳动关系存续期间因拖欠劳动报酬发生争议的，劳动者申请仲裁不受本条第一款规定的仲裁时效期间的限制；但是，劳动关系终止的，应当自劳动关系终止之日起一年内提出。",
                "category": "劳动法",
                "tags": "仲裁时效,劳动争议"
            },
            {
                "title": "工伤认定的标准和流程",
                "content": "根据《工伤保险条例》第14条规定：职工有下列情形之一的，应当认定为工伤：（一）在工作时间和工作场所内，因工作原因受到事故伤害的；（二）工作时间前后在工作场所内，从事与工作有关的预备性或者收尾性工作受到事故伤害的；（三）在工作时间和工作场所内，因履行工作职责受到暴力等意外伤害的；（四）患职业病的；（五）因工外出期间，由于工作原因受到伤害或者发生事故下落不明的；（六）在上下班途中，受到非本人主要责任的交通事故或者城市轨道交通、客运轮渡、火车事故伤害的。",
                "category": "劳动法",
                "tags": "工伤认定,工伤保险"
            },
            {
                "title": "民法典 - 侵权责任的构成要件",
                "content": "根据《中华人民共和国民法典》第1165条规定：行为人因过错侵害他人民事权益造成损害的，应当承担侵权责任。侵权责任的构成要件包括：（1）违法行为：行为人实施了违反法律规定的行为；（2）损害事实：造成了受害人财产或人身损害的客观事实；（3）因果关系：违法行为与损害事实之间存在因果关系；（4）主观过错：行为人主观上存在故意或过失。",
                "category": "民法",
                "tags": "侵权责任,构成要件"
            }
        ]
        
        # 插入数据
        for data in test_data:
            manager.create_knowledge(db, **data)
            print(f"✓ 已插入：{data['title']}")
        
        print(f"\n✅ 成功插入 {len(test_data)} 条测试数据")
        
    except Exception as e:
        print(f"❌ 插入测试数据失败：{str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    insert_test_data()
