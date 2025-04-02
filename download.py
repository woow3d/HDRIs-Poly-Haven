import os
import sqlite3
from glob import glob

# تحديد مسار المجلد المطلوب
folder_path = r'E:\prgram\program me\poly haven\HDRIs • Poly Haven_files'

# الاتصال بقاعدة البيانات
conn = sqlite3.connect('poly_haven_images.db')
cursor = conn.cursor()

# إنشاء الجدول إذا لم يكن موجوداً
cursor.execute('''CREATE TABLE IF NOT EXISTS hdri_images
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE)''')

# الحصول على قائمة بجميع ملفات png في المجلد
png_files = glob(os.path.join(folder_path, '*.png'))

# استخراج الأسماء بدون الامتداد
names = [os.path.splitext(os.path.basename(file))[0] for file in png_files]

# إضافة الأسماء إلى قاعدة البيانات
added_count = 0
for name in names:
    try:
        cursor.execute("INSERT INTO hdri_images (name) VALUES (?)", (name,))
        added_count += 1
    except sqlite3.IntegrityError:
        continue  # تجاهل الأسماء المكررة
    except Exception as e:
        print(f"خطأ عند إضافة {name}: {str(e)}")

conn.commit()

print(f"تمت معالجة {len(png_files)} ملف")
print(f"تمت إضافة {added_count} اسم جديد")
print(f"تم تجاهل {len(png_files) - added_count} اسم موجود مسبقاً")

conn.close()