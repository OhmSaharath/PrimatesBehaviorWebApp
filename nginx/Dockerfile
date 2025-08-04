# ใช้ Official Nginx Image
FROM nginx:1.25-alpine

# ลบคอนฟิกเริ่มต้นของ Nginx
RUN rm /etc/nginx/conf.d/default.conf

# คัดลอกไฟล์คอนฟิกที่เราสร้างไว้เข้าไปแทนที่
COPY nginx.conf /etc/nginx/conf.d/