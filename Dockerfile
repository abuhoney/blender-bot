FROM python:3.11-slim

# نثبت المتغيرات الأساسية
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# مجلد العمل
WORKDIR /app

# نحدث pip ونثبت المتطلبات أول عشان الكاش
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ننسخ باقي ملفات المشروع
COPY . .

# Render يستخدم PORT من Environment
EXPOSE 10000

# تشغيل البوت
CMD ["python", "app.py"]
