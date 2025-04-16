#!/usr/bin/env python3
"""
أداة تهيئة قاعدة البيانات لمنتدى DzTeck

هذه الأداة تقوم بإنشاء هيكل قاعدة البيانات وإضافة بعض البيانات الافتراضية للتجربة
"""

import os
import time
from werkzeug.security import generate_password_hash
from main import app
from models import db, User, Thread, Reaction

def init_database():
    """تهيئة قاعدة البيانات وإضافة بيانات تجريبية"""
    
    with app.app_context():
        # إنشاء الجداول
        db.create_all()
        
        # إضافة مستخدمين افتراضيين
        # فقط إذا لم يكن هناك مستخدمين سابقين
        if User.query.count() == 0:
            admin = User(
                username="Admin",
                password_hash=generate_password_hash("Admin123!"),
                email="admin@dzteck.com",
                points=100,
                created_at=time.time()
            )
            
            moderator = User(
                username="Moderator",
                password_hash=generate_password_hash("Mod123!"),
                email="moderator@dzteck.com",
                points=50,
                created_at=time.time()
            )
            
            tech_user = User(
                username="TechGuru",
                password_hash=generate_password_hash("Tech123!"),
                email="tech@dzteck.com",
                points=25,
                created_at=time.time()
            )
            
            db.session.add_all([admin, moderator, tech_user])
            db.session.commit()
            print("✅ تمت إضافة المستخدمين الافتراضيين")
            
            # إضافة مواضيع افتراضية
            thread1 = Thread(
                title="أول موضوع في المنتدى",
                content="هذا هو أول موضوع تجريبي! مرحباً بالجميع في منتدى DzTeck. شاركونا آراءكم.",
                author_id=admin.id,
                timestamp=time.time() - 86400 # يوم واحد مضى
            )
            
            thread2 = Thread(
                title="اقتراحات لتطوير المنتدى",
                content="هل لديك اقتراح لجعل المنتدى أفضل؟ شاركه معنا هنا. نحن نستمع!",
                author_id=moderator.id,
                timestamp=time.time() - 7200 # ساعتان مضت
            )
            
            thread3 = Thread(
                title="نقاش حول أحدث التقنيات",
                content="ما رأيكم في آخر التطورات في عالم الذكاء الاصطناعي والحوسبة السحابية؟",
                author_id=tech_user.id,
                timestamp=time.time() - 900 # 15 دقيقة مضت
            )
            
            db.session.add_all([thread1, thread2, thread3])
            db.session.commit()
            print("✅ تمت إضافة المواضيع الافتراضية")
            
            # إضافة بعض التفاعلات
            reaction1 = Reaction(
                thread_id=thread1.id,
                user_id=moderator.id,
                emoji="like",
                timestamp=time.time() - 80000
            )
            
            reaction2 = Reaction(
                thread_id=thread1.id,
                user_id=tech_user.id,
                emoji="love",
                timestamp=time.time() - 70000
            )
            
            reaction3 = Reaction(
                thread_id=thread2.id,
                user_id=admin.id,
                emoji="like",
                timestamp=time.time() - 6000
            )
            
            db.session.add_all([reaction1, reaction2, reaction3])
            db.session.commit()
            print("✅ تمت إضافة التفاعلات الافتراضية")
        else:
            print("⚠️ تم تخطي إضافة البيانات لأن قاعدة البيانات تحتوي بالفعل على مستخدمين")
        
        print("✅ تم تهيئة قاعدة البيانات بنجاح")

if __name__ == "__main__":
    init_database()