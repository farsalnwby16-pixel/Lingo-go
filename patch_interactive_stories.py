import re

# Update admin.html to include new category
try:
    with open('templates/admin.html', 'r', encoding='utf-8') as f:
        admin_content = f.read()
    
    if 'القصص التفاعلية' not in admin_content:
        new_option = '<option value="القصص التفاعلية (Interactive Stories)">القصص التفاعلية (Interactive Stories)</option>\n'
        admin_content = admin_content.replace('<select name="category" class="form-control" required>', '<select name="category" class="form-control" required>\n' + new_option)
        with open('templates/admin.html', 'w', encoding='utf-8') as f:
            f.write(admin_content)
        print("✅ تم إضافة القسم للوحة التحكم.")
except Exception as e:
    print("إشعار لوحة التحكم:", e)

