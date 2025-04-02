import os
import sqlite3
import requests
from tqdm import tqdm  # لشريط التقدم المطور


def download_file(url, save_path=None):
    """
    دالة محسنة لتنزيل الملفات مع معالجة الأخطاء وشريط تقدم
    """
    try:
        # إجراء الطلب مع متابعة التقدم
        response = requests.get(url, stream=True)
        response.raise_for_status()  # التحقق من وجود أخطاء

        # تحديد اسم الملف من الرابط إذا لم يتم تحديد مسار الحفظ
        if save_path is None:
            filename = url.split('/')[-1].split('?')[0]
            save_path = os.path.join(os.getcwd(), filename)

        # التأكد من وجود مجلد الحفظ
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # الحصول على حجم الملف
        total_size = int(response.headers.get('content-length', 0))

        print(f"\nجاري تنزيل: {os.path.basename(save_path)}")
        print(f"حجم الملف: {total_size / (1024 * 1024):.2f} MB" if total_size else "حجم الملف غير معروف")

        # استخدام tqdm لشريط التقدم
        with open(save_path, 'wb') as f, tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=os.path.basename(save_path)
        ) as bar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # تجاهل keep-alive chunks
                    f.write(chunk)
                    bar.update(len(chunk))

        print(f"تم تنزيل الملف بنجاح إلى: {save_path}")
        return save_path

    except requests.exceptions.RequestException as e:
        print(f"\nفشل التنزيل: {str(e)}")
        return None
    except Exception as e:
        print(f"\nحدث خطأ غير متوقع: {str(e)}")
        return None


def check_existing_files(names, resolution):
    """
    التحقق من الملفات الموجودة مسبقًا
    """
    existing_files = []
    for name in names:
        filename = f"{name[0]}_{resolution}k.exr"
        if os.path.exists(filename):
            existing_files.append(filename)
    return existing_files


def main():
    print("Welcome to Poly Haven HDRI Downloader")
    print("Developed by Abdularhman Baggash")

    try:
        # الاتصال بقاعدة البيانات
        conn = sqlite3.connect('poly_haven_images.db')
        cursor = conn.cursor()

        # جلب جميع الأسماء من الجدول
        cursor.execute("SELECT name FROM hdri_images ORDER BY name")
        all_names = cursor.fetchall()

        if not all_names:
            print("لا توجد أسماء في قاعدة البيانات!")
            return

        # عرض خيارات الدقة
        print("\nاختر دقة الملفات:")
        print("1. 1k (أصغر حجم، أقل جودة)")
        print("2. 2k")
        print("3. 4k")
        print("4. 8k (أكبر حجم، أعلى جودة)")
        print("5. 16k (أكبر حجم، أعلى جودة)")

        res_options = {'1': '1', '2': '2', '3': '4', '4': '8', '5': '16'}
        choice = input("ادخل رقم الخيار (1-5): ")
        resolution = res_options.get(choice, '4')  # Default to 4k

        # التحقق من الملفات الموجودة
        existing = check_existing_files(all_names, resolution)
        if existing:
            print(f"\nوجدت {len(existing)} ملف موجود مسبقًا:")
            for file in existing[:5]:  # عرض أول 5 ملفات فقط لتجنب الإطالة
                print(f"- {file}")
            if len(existing) > 5:
                print(f"...و {len(existing) - 5} ملفات أخرى")

            cont = input("هل تريد الاستمرار في تنزيل الملفات المتبقية؟ (y/n): ")
            if cont.lower() != 'y':
                return

        # بدء عملية التنزيل
        print(f"\nبدء تنزيل {len(all_names)} ملف بدقة {resolution}k...")

        success_count = 0
        for i, (name,) in enumerate(all_names, 1):
            filename = f"{name}_{resolution}k.exr"
            if not os.path.exists(filename):
                url = f"https://dl.polyhaven.org/file/ph-assets/HDRIs/exr/{resolution}k/{filename}"
                result = download_file(url)
                if result:
                    success_count += 1
                    print(f"{i}. {name} - تم التنزيل بنجاح")
                else:
                    print(f"{i}. {name} - فشل التنزيل")
            else:
                print(f"{i}. {name} - موجود مسبقًا")

        print(f"\nتم تنزيل {success_count} من أصل {len(all_names)} ملف بنجاح")

    except sqlite3.Error as e:
        print(f"خطأ في قاعدة البيانات: {str(e)}")
    except Exception as e:
        print(f"حدث خطأ غير متوقع: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()