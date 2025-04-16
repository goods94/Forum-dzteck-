# دليل تثبيت منتدى DzTeck

هذا الدليل سيساعدك على تثبيت وتشغيل منتدى DzTeck على الخادم الخاص بك.

## المتطلبات الأساسية

1. بيئة Python 3.10 أو أحدث
2. قاعدة بيانات PostgreSQL (اختياري، يمكن استخدام SQLite)
3. خادم ويب متوافق مع WSGI (مثل Nginx + Gunicorn)

## خطوات التثبيت

### 1. تحضير البيئة

قم بإنشاء بيئة افتراضية لتثبيت المكتبات:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate     # Windows
```

### 2. تثبيت المكتبات المطلوبة

```bash
pip install -r requirements.txt
```

### 3. إعداد متغيرات البيئة

انسخ ملف `.env.example` إلى `.env` وقم بتعديله حسب احتياجاتك:

```bash
cp .env.example .env
# قم بتعديل ملف .env باستخدام محرر نصوص
```

### 4. إعداد قاعدة البيانات

#### باستخدام PostgreSQL

قم بإنشاء قاعدة بيانات في PostgreSQL ثم قم بتعديل متغير `DATABASE_URL` في ملف `.env`.

#### باستخدام SQLite (الخيار الأبسط)

لا حاجة لأي إعدادات إضافية، سيتم إنشاء ملف قاعدة البيانات تلقائياً.

### 5. تهيئة قاعدة البيانات

قم بتشغيل سكريبت تهيئة قاعدة البيانات:

```bash
python init_db.py
```

### 6. تشغيل المنتدى

#### للتطوير المحلي

```bash
python main.py
```

المنتدى سيكون متاحاً على http://localhost:5000

#### للبيئة الإنتاجية

##### باستخدام Gunicorn

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

##### مع Nginx (موصى به للإنتاج)

قم بإعداد Nginx للعمل كـ reverse proxy أمام Gunicorn. مثال على تكوين Nginx:

```nginx
server {
    listen 80;
    server_name yourwebsite.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## تسجيل الدخول الافتراضي

بعد تهيئة قاعدة البيانات، ستتمكن من تسجيل الدخول باستخدام أي اسم مستخدم بدون كلمة مرور (في الإصدار التجريبي).

في الإصدارات المستقبلية، سيتم تفعيل مصادقة كاملة مع كلمات مرور.

## التخصيص

يمكنك تخصيص المنتدى من خلال:

1. تعديل ملفات CSS في مجلد `assets/css/`
2. تغيير الصورة الرمزية الافتراضية في `assets/images/default-avatar.png`
3. تعديل القوالب في مجلد `templates/`

## الدعم

للحصول على المساعدة أو الإبلاغ عن مشاكل، يرجى زيارة صفحة المشروع على GitHub.