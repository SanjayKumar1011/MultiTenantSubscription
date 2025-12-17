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
# Day 3 – RBAC, Invite Users & Tenant‑Safe Querying

This document explains **what we built on Day 3**, **why it matters**, and **how it actually works in Django + DRF**. This day is critical for real backend credibility.

---

## 🎯 Day 3 Goal

Make the system **multi‑tenant safe** and **role aware** so that:

* Users only see their own organization’s data
* Owners/Admins can invite users
* Backend enforces rules (not frontend)

---

## 1️⃣ RBAC (Role‑Based Access Control)

### What is RBAC?

RBAC means **what a user can do depends on their role**.

In our system:

* **OWNER** → full access
* **ADMIN** → manage users, projects
* **MEMBER** → read/write limited resources

---

### Why RBAC is mandatory

Without RBAC:

* Any authenticated user could invite others
* Any user could access admin data

RBAC ensures:

* Business rules live in backend
* Security is not UI‑dependent

---

### Permission Class Example

```python
from rest_framework.permissions import BasePermission

class IsOwnerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['OWNER', 'ADMIN']
```

**How it works**

* DRF automatically calls `has_permission()`
* If it returns `False` → 403 Forbidden

---

## 2️⃣ Invite User API

### Why Invite API is needed

End users **cannot create users directly**.

Instead:

* OWNER / ADMIN invites a user
* User is created under same organization

---

### Who invited the user?

We store it explicitly:

```python
invited_by = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    related_name='invited_users'
)
```

This answers:

* Who added this user?
* Audit trail

---

### Invite User Flow

1. Authenticated user calls invite API
2. Backend checks role (RBAC)
3. New user is created under same organization
4. `invited_by` is stored

---

### Example Invite Response

```json
{
  "message": "User invited successfully",
  "user": {
    "id": 4,
    "username": "Mallesh",
    "email": "mallesh@gmail.com",
    "role": "ADMIN",
    "invited_by": "Usha",
    "organization": "HOME"
  }
}
```

This is **production‑grade API design**.

---

## 3️⃣ Tenant‑Safe Querying (MOST IMPORTANT)

### The Core Problem

If you do this:

```python
Project.objects.all()
```

❌ Any user can see **all organizations’ data**.

---

### Tenant‑Safe Principle

> Every query must be scoped by the user’s organization.

---

### Example: Project App (Conceptual)

Assume a `Project` belongs to an organization:

```python
class Project(models.Model):
    name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
```

---

### Tenant‑Safe ViewSet

```python
class ProjectViewSet(ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(
            organization=self.request.user.organization
        )
```

---

### ❓ "But we are not calling get_queryset() anywhere"

You **never call it manually**.

DRF internally calls:

* `get_queryset()` for

  * list
  * retrieve
  * update
  * delete

So every request is automatically tenant‑scoped.

---

### Another Tenant‑Safe Example (Orders)

```python
class OrderViewSet(ModelViewSet):
    def get_queryset(self):
        return Order.objects.filter(
            organization=self.request.user.organization
        )
```

Result:

* User from Org A → sees only Org A orders
* User from Org B → sees only Org B orders

---

### Why this is interview‑critical

> "We enforced tenant isolation at the queryset level to prevent cross‑organization data leakage."

---

## ✅ Day 3 Summary

✔ RBAC implemented via permission classes
✔ Invite user API built
✔ Audit trail (`invited_by`) added
✔ Tenant‑safe querying understood
✔ Backend security enforced correctly

