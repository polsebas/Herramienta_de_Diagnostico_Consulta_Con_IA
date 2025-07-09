# Sistema de Autenticación

## Descripción General
El sistema de autenticación proporciona mecanismos seguros para verificar la identidad de los usuarios y gestionar sus sesiones.

## Métodos de Autenticación

### Autenticación por Usuario y Contraseña
El método más común que permite a los usuarios acceder con sus credenciales:
- Validación de formato de email
- Verificación de contraseña segura
- Bloqueo temporal tras múltiples intentos fallidos

### Autenticación Multi-Factor (MFA)
Sistema de doble verificación que requiere:
- Credenciales principales (usuario/contraseña)
- Código temporal (TOTP) o SMS
- Claves de seguridad física (FIDO2)

### OAuth 2.0 y OpenID Connect
Integración con proveedores externos:
- Google OAuth
- Microsoft Azure AD
- GitHub OAuth
- Facebook Login

## Gestión de Sesiones

### Tokens JWT
Los tokens JWT se utilizan para mantener las sesiones:
- **Access Token**: Corta duración (15-60 minutos)
- **Refresh Token**: Larga duración (7-30 días)
- **ID Token**: Información del usuario (OpenID Connect)

### Configuración de Tokens
```json
{
  "access_token_expiry": "15m",
  "refresh_token_expiry": "7d",
  "issuer": "https://api.example.com",
  "audience": "https://app.example.com"
}
```

## Seguridad

### Encriptación de Contraseñas
- Algoritmo: bcrypt con salt de 12 rondas
- Verificación segura contra timing attacks
- Migración automática a algoritmos más seguros

### Protección contra Ataques

#### Brute Force
- Rate limiting por IP
- Bloqueo progresivo de cuentas
- CAPTCHA después de 3 intentos fallidos

#### Session Hijacking
- Tokens con fingerprint del navegador
- Rotación automática de tokens
- Invalidación en múltiples dispositivos

#### CSRF Protection
- Tokens CSRF en formularios
- Validación de origen de requests
- SameSite cookies

## Base de Datos

### Tabla de Usuarios
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    mfa_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Tabla de Sesiones
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    refresh_token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    ip_address INET,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### Autenticación
- `POST /auth/login` - Iniciar sesión
- `POST /auth/logout` - Cerrar sesión
- `POST /auth/refresh` - Renovar token
- `POST /auth/register` - Registrar usuario

### Gestión de Usuario
- `GET /auth/profile` - Obtener perfil
- `PUT /auth/profile` - Actualizar perfil
- `POST /auth/change-password` - Cambiar contraseña
- `POST /auth/forgot-password` - Recuperar contraseña

### MFA
- `POST /auth/mfa/enable` - Habilitar MFA
- `POST /auth/mfa/disable` - Deshabilitar MFA
- `POST /auth/mfa/verify` - Verificar código MFA

## Logging y Auditoría

### Eventos Registrados
- Inicio de sesión exitoso/fallido
- Cambio de contraseña
- Habilitación/deshabilitación de MFA
- Bloqueo de cuenta
- Acceso desde nueva ubicación

### Alertas de Seguridad
- Múltiples intentos fallidos
- Acceso desde IP sospechosa
- Cambio de contraseña desde nueva ubicación
- Deshabilitación de MFA

## Configuración de Entorno

### Variables Requeridas
```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@localhost/db

# JWT
JWT_SECRET=your-super-secret-key
JWT_ALGORITHM=HS256

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

## Monitoreo

### Métricas Clave
- Tasa de éxito de autenticación
- Tiempo de respuesta de endpoints
- Número de sesiones activas
- Intentos de acceso fallidos

### Dashboards
- Actividad de usuarios en tiempo real
- Análisis de patrones de acceso
- Alertas de seguridad
- Estadísticas de uso de MFA 