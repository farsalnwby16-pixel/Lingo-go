import re

# 1. تحديث لوحة التحكم (templates/admin.html)
with open('templates/admin.html', 'r', encoding='utf-8') as f:
    admin_html = f.read()

target_option = '<option value="Shadowing">التظليل (Shadowing)</option>'
new_option = '<option value="Shadowing">التظليل (Shadowing)</option>\n                        <option value="Stories">📖 القصص التفاعلية (Stories)</option>'

if target_option in admin_html:
    admin_html = admin_html.replace(target_option, new_option)
    with open('templates/admin.html', 'w', encoding='utf-8') as f:
        f.write(admin_html)
    print("✅ تم إضافة قسم القصص في لوحة الأدمن!")
else:
    print("⚠️ لم يتم العثور على خيار Shadowing في admin.html")


# 2. تحديث واجهة الطالب (templates/index.html)
with open('templates/index.html', 'r', encoding='utf-8') as f:
    index_html = f.read()

if "Stories" not in index_html:
    idx_shadow = index_html.find("Shadowing")
    if idx_shadow != -1:
        idx_endfor = index_html.find("{% endfor %}", idx_shadow)
        if idx_endfor != -1:
            idx_close_div = index_html.find("</div>", idx_endfor)
            if idx_close_div != -1:
                insert_pos = idx_close_div + len("</div>")
                
                cat5_block = """

                <!-- قسم القصص التفاعلية -->
                <div class="cat-title" onclick="toggleCat('cat5')">📖 القصص التفاعلية (Stories) <span>▼</span></div>
                <div class="cat-panel" id="cat5" style="display:none;">
                    {% for l in ['A1','A2','B1','B2','C1','C2'] %}
                        <a href="/?cat=Stories&level={{l}}" class="level-btn {% if current_cat=='Stories' and current_level==l %}active{% endif %}">{{l}}</a>
                    {% endfor %}
                </div>"""
                
                index_html = index_html[:insert_pos] + cat5_block + index_html[insert_pos:]
                
                with open('templates/index.html', 'w', encoding='utf-8') as f:
                    f.write(index_html)
                print("✅ تم إضافة قسم القصص التفاعلية (cat5) في القائمة الجانبية للطالب!")
            else:
                print("❌ لم يتم العثور على إغلاق div بعد endfor")
        else:
            print("❌ لم يتم العثور على endfor بعد Shadowing")
    else:
        print("❌ لم يتم العثور على كلمة Shadowing في index.html")
else:
    print("ℹ️ قسم القصص موجود بالفعل في index.html")

