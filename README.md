# IAM Project

This repository contains code and configuration for a local development environment for an IAM system (Keycloak + admin panel + nginx reverse proxy).  

> Note: This environment is for educational and testing purposes only (development mode).  

---

## 1. Requirements

- Linux (Debian/Ubuntu recommended)  
- Docker  
- Docker Compose  

Check versions:  
```bash
docker --version
docker-compose --version
```
## 2. Project Structure
```
iam-project/
├─ docker-compose.yml         # container definitions: Keycloak, Postgres, Nginx
├─ nginx.conf                 # reverse proxy configuration
├─ app/                       # IAM admin panel (your web application)
├─ rms/                	      # Requests Management System (Flask application)
├─ sql/                       # example database scripts (audit, provisioning)
├─ examples/                  # example CSV/Excel files for import
└─ README.md
```

## 3. Running the Environment
1. Make sure ports 80, 8080, 8081, 5000 and 5432 are free.
2. Add a local domain entry in /etc/hosts:
```bash
127.0.0.1 iam.local
127.0.0.1 admin.iam.local
127.0.0.1 rms.local
```
3. Start containers:
```bash
docker-compose up -d
```
4. Check status:
```bash
docker ps
```
You should see containers:

- app, rms → port 5000
- postgres → port 5432
- keycloak → port 8080 (HTTP, dev mode)
- nginx    → port 80

## 4. Keycloak

- Admin panel: http://localhost:8080 or http://iam.local

#### Default login for development:  
Username: admin
Password: admin

In production, use HTTPS and strong passwords.

## 5. Admin Panel (Flask)

- Local URL: http://admin.iam.local
- Configured via Nginx subdomain: requests to admin.iam.local are proxied to the Flask admin app running in Docker (app:5000).

## 6. Requests Management System (Flask)

- Local URL: http://rms.local
- Configured via Nginx subdomain: requests to rms.local are proxied to the Flask rms app running in Docker (rms:5000).

## 6. Nginx (Reverse Proxy)

- All requests to http://iam.local are forwarded to the Keycloak container (proxy_pass http://keycloak:8080/)
#### Benefits:
- Clean local URL
- Ability to add HTTPS, filtering, or load balancing later
- Client does not need to know Keycloak port or container

## 7. Docker Tips

Enter a container:
```bash
docker exec -it iam-project_keycloak_1 bash
```
Check logs:
```bash
docker logs iam-project_keycloak_1
docker logs iam-project_nginx_1
sudo docker-compose logs -f app
```
Restart containers:
```bash
docker-compose down
docker-compose up -d
```
## 8. Security Notes

- Do not commit real user data or passwords to the repo
- Keep .env or any sensitive configuration local
- Public repo is suitable for educational/demonstration purposes

## 8. Next Steps

- Develop Requests Management System app
- Automation for provisioning / deprovisioning
- Audit and reporting
- Integration with CSV/Excel and Postgres database
