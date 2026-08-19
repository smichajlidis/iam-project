# IAM Project

This repository contains code and configuration for a local development environment for an IAM system (Keycloak + nginx reverse proxy).  

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
├─ rms/                	      # Requests Management System (Flask application)
├─ postgres/                  # database scripts
└─ README.md
```

## 3. Running the environment
### 3.1 Make sure ports 80, 8080, 8081 and 5432 are free.
### 3.2 Add a local domain entry in /etc/hosts:
```bash
127.0.0.1 iam.local
127.0.0.1 rms.local
```
### 3.3 Enter the project's directory and start containers:
```bash
docker-compose up -d
```
### 3.4 Check status:
```bash
docker ps
```
You should see containers:
```
rms         8081:5000
postgres    5432:5432
keycloak    8080:8080
nginx       80:80
```
## 4. Configuring Keycloak
#### 4.1 Access the Keycloak Admin Console

- Admin panel: http://iam.local or http://localhost:8080

**Default login:**  
```
Username: admin  
Password: admin
```
#### 4.2 Create new realm
```
name: 	iam-project
```
#### 4.3 Create new client
```
Client type:		OpenID Connect
Client ID:		rms
Authentication flow:	Standard flow
Root URL: 		http://rms.local
Valid redirect URIs:	http://rms.local/callback
Web origins:		http://rms.local
```
#### 4.4 Add roles to the client
Technical roles are defined in `/rms/technical-roles.md`.
Create the roles listed in that file.
#### 4.5 Add users and assign the appropriate roles
For testing purposes:  
| Name | Username | Business role |
|---|---|---|
| Jan Nowak | nowak | Requestor |
| Anna Kowalska | kowalska | Manager |
| Piotr Wiśniewski | wisniewski | Support |
| Admin Admin | admin | Admin |
#### 4.6 Add Jan Nowak as Anna Kowalska subordinate
##### 4.6.1 Realm settings -> User profile -> Create attribute "subordinates"  
##### 4.6.2 Client scopes -> profile -> Mappers -> add mapper -> By configuration -> User Attribute:
```
Name:			subordinates
User Attribute:		subordinates
Token Claim Name:	subordinates
Add to ID token:      	ON
Add to access token:  	ON
Add to userinfo:      	ON
```
##### 4.6.3 Add "Jan Nowak" as kowalska's subordinate
Open **Users → Anna Kowalska → Attributes** and set:

subordinates = Jan Nowak
### 5. Testing
### 5.1 Access RMS
Open:

- [http://rms.local](http://rms.local)

The application should redirect unauthenticated users to Keycloak.

### 5.2 Test user roles

Use a separate private/incognito browser window for each user to avoid reusing the existing Keycloak session.

Test the following accounts:

For each test:

1. Open a new private/incognito browser window.
2. Open `http://rms.local`.
3. Log in using the credentials of the selected user.
4. Verify that the user has the expected permissions and access.
5. Close the private window before testing another user.

