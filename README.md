server {
    listen 80;
    server_name wonjin-mall.p-e.kr;

    location /static/ {
        root /home/donghyeok/secutity_web/Fronts;
	try_files $uri $uri/ =404;
    }

    # 💡 모든 요청을 Flask로 프록시
    location / {
        proxy_pass http://192.168.10.10:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	proxy_set_header X-Forwarded-Proto $scheme;
    }
}
