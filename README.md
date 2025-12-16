# Multi-Tenant SaaS Backend (Django + DRF)

This project demonstrates a production-ready backend architecture
with JWT authentication, multi-tenancy, role-based access control,
and clean API design.

Built incrementally with documented engineering decisions.


## DAY 1 – Foundation & Authentication

### 🎯 Goal

Build a **clean, production-safe authentication base** with multi-tenancy support.

---

### 1️⃣ Why we used `AbstractUser`

**What we did**
We extended Django’s `AbstractUser` instead of `AbstractBaseUser`.

**Why**

* Keeps Django’s authentication stable
* Avoids custom manager complexity
* `createsuperuser`, admin, permissions work out-of-the-box
* No custom auth requirements yet

**Interview-ready reason**

> We used AbstractUser to extend Django’s default auth behavior while adding tenant and role context, avoiding unnecessary complexity.

---

### 2️⃣ User Model

**What**

* Added `role` (OWNER / ADMIN / MEMBER)
* Linked user to `Organization`

**Why**

* Role-based access control (RBAC)
* Multi-tenant isolation

**How (Conceptually)**

* One user belongs to one organization
* Organization owns multiple users

---

### 3️⃣ Organization Model

**What**

* Represents a tenant

**Why**

* Clean tenant boundary
* Scales well for SaaS systems

---

### 4️⃣ JWT Authentication

**What**

* Used JWT for stateless authentication

**Why**

* Works for web + mobile
* No server-side sessions
* Industry standard

**Flow**

1. User logs in
2. API returns access token
3. Client sends token in `Authorization` header

---

### 5️⃣ `/api/me/` Endpoint

**What**

* Returns current authenticated user

**Why**

* Used by frontend after login
* Verifies token validity

**How**

* DRF extracts user from JWT
* `request.user` is populated automatically

-------------------------------------------------------------------------------------------------------------------------------------------------

## DAY 2 – Signup & Tenant Creation

### 🎯 Goal

Allow **end users** to self-register and automatically create an organization.

---

### 1️⃣ Why Signup API is Needed

**Problem**

* `createsuperuser` is admin-only
* End users cannot access Django shell

**Solution**

* Public Signup API
* Automatically creates:

  * Organization
  * OWNER user

---

### 2️⃣ Signup Serializer

**What**
Serializer responsible for:

* Validating input
* Creating organization
* Creating user

---

### Serializer Code Breakdown

```python
class SignupSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(write_only=True)
```

**Why**

* `organization_name` is not a User field
* Used only during signup

---

```python
class Meta:
    model = User
    fields = ('username', 'email', 'password', 'organization_name')
```

**Why**

* Explicit fields avoid over-posting
* Safer API

---

```python
def create(self, validated_data):
```

**How this gets called**

* DRF automatically calls `create()` when:

  ```python
  serializer.is_valid()
  serializer.save()
  ```

---

```python
org_name = validated_data.pop('organization_name')
```

**Why**

* User model doesn’t have this field
* Remove it before creating User

---

```python
organization = Organization.objects.create(name=org_name)
```

**Why**

* New tenant created per signup

---

```python
user = User.objects.create_user(
    **validated_data,
    organization=organization,
    role='OWNER'
)
```

**Why**

* `create_user` hashes password
* First user becomes OWNER

---

### 3️⃣ Field Validation

```python
def validate_organization_name(self, value):
```

**How it is called**

* DRF automatically calls:

  * `validate_<fieldname>`
  * During `serializer.is_valid()`

**Why**

* Prevent duplicate organizations
* Enforce business rules

---

### 4️⃣ Signup Response Design

**Why custom response**

* Don’t expose password
* Give frontend meaningful data

**Example Response**

```json
{
  "message": "Signup successful",
  "user": {
    "id": 3,
    "username": "Usha",
    "email": "Usha@gmail.com",
    "role": "OWNER",
    "organization": {
      "id": 2,
      "name": "HOME"
    }
  }
}
```
------------------------------------------------------------------------------------------------------------------
