# نظام إدارة الجامعة الإلكتروني

مشروع تعليمي مبني باستخدام Python وFlask وSQLite وHTML/CSS.

## التشغيل على Windows
1. ثبّت Python 3.10 أو أحدث.
2. افتح موجه الأوامر داخل مجلد المشروع.
3. نفّذ:
   `py -m venv .venv`
   `.venv\\Scripts\\activate`
   `py -m pip install -r requirements.txt`
   `py app.py`
4. افتح http://127.0.0.1:5000

## حسابات تجريبية
- admin / admin123
- staff / staff123
- teacher / teacher123

## ملاحظات
هذا نموذج تعليمي محلي وليس جاهزاً للنشر الإنتاجي. غيّر SECRET_KEY، وأضف حماية CSRF وضوابط صلاحيات واختبارات قبل أي استخدام حقيقي.
