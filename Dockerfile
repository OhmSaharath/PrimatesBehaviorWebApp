# STEP 1: ใช้ Official Python Image เวอร์ชัน 3.12 เป็น Base Image
FROM python:3.12-slim

# ตั้งค่า Environment Variables เพื่อประสิทธิภาพที่ดีใน Docker
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# STEP 2: สร้าง Working Directory ภายในคอนเทนเนอร์
WORKDIR /app

# STEP 3: ติดตั้ง System Dependencies ที่จำเป็น
#         (ตัวอย่าง: สำหรับคอมไพล์ mysqlclient)
RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev \
    pkg-config \
    make \
    && rm -rf /var/lib/apt/lists/*

# STEP 4: ติดตั้ง Pipenv ซึ่งเป็นเครื่องมือจัดการ package
RUN pip install pipenv

# STEP 5: คัดลอกไฟล์ Pipfile เพื่อใช้ Docker cache ให้เกิดประโยชน์สูงสุด
#         ทำให้ไม่ต้องติดตั้ง dependencies ใหม่ทุกครั้งที่แก้โค้ด
COPY Pipfile Pipfile.lock ./

# STEP 6: ใช้ Pipenv เพื่อติดตั้ง Python Dependencies ทั้งหมดจาก Pipfile.lock
#         --system: ติดตั้งลงใน site-packages ของระบบ (ไม่ต้องสร้าง virtualenv ซ้อนใน container)
RUN pipenv install --system --deploy --ignore-pipfile

# STEP 7: คัดลอกไฟล์โปรเจกต์ทั้งหมดเข้ามาในคอนเทนเนอร์
COPY . .

# STEP 8: บอกให้ Docker รู้ว่าคอนเทนเนอร์นี้จะทำงานที่ Port 8000
EXPOSE 8000

# STEP 9: ใช้ Gunicorn ซึ่งเป็น Production-grade server เพื่อรันแอปพลิเคชัน
# ใช้ Gunicorn ในโหมด development พร้อม auto-reload
CMD ["gunicorn", "--workers=3", "--bind", "0.0.0.0:8000", "PrimatesGame.wsgi:application"]