# TM1 Security — Verified Reference

> **Version note:** The facts in this file were validated against **PA 2.1**.
> When this skill is used for a different version, verify against the target version's docs.
> Replace `<VERSION>` with `latest` (default) or the explicit version from the prompt.

Source: `https://www.ibm.com/docs/en/planning-analytics/<VERSION>?topic=developers-controlling-access-tm1-objects`

---

## Default access for new objects

This is a frequently misstated fact — verify this in any training content.

| Object type | Default access for all groups |
|-------------|-------------------------------|
| Cubes | **None** |
| Dimensions | **None** |
| TI Processes | **None** |
| Chores | **None** |
| Application folders | **Read** ← exception |

When a new object is created, all non-admin groups have **None** access by default
(except application folders which default to Read). The admin group always has full access.

---

## Object-level security rights

The available rights for TM1 objects, from most to least permissive:

| Right | Description |
|-------|-------------|
| **Admin** | Full control including security assignment |
| **Write** | Read and write data |
| **Read** | Read data only |
| **Lock** | Prevent others from modifying the object |
| **Reserve** | Check out the object for exclusive editing |
| **None** | No access |

Application folders support only: **None**, **Read**, **Admin**.

---

## Interaction of security rights

When a user has different rights on multiple objects that define a cell:

> TM1 applies the **most restrictive** security right to the cell.

Example: if a user has Write access to a cube but Read access to a dimension element
that forms part of that cell's address, they can only Read that cell.

---

## Cell-level security

Cell-level security applies to a **specific cell** and **overrides all other TM1
security**. It is the most granular and most powerful security mechanism.

Requirements for cell-level security:
1. A cell security cube must exist for the target cube
2. The cell security cube must follow TM1's naming and dimension conventions
3. The security assignment must be made in the cell security cube

**Teaching note:** Cell-level security should be described as an override mechanism,
not as a replacement for object-level security. Use object-level security as the
foundation; cell-level security for exceptions only.

---

## Authentication modes

| Mode | Name | Description |
|------|------|-------------|
| 1 | TM1 (native) | Username/password stored in TM1 server |
| 2 | CAM (Cognos Access Manager) | Federated via Cognos Gateway |
| 3 | CAM (with integrated security) | CAM with Windows passthrough |
| 5 | IBM Security Directory Server / LDAP | LDAP-based authentication |

Mode 1 is the simplest for development environments. Production enterprise deployments
typically use Mode 2 (CAM) or Mode 5 (LDAP).

---

## Groups and users

- **Groups** hold security rights — rights are assigned to groups, not to individual users.
- **Users** are assigned to one or more groups.
- A user's effective rights = the union of rights from all groups they belong to,
  subject to the most-restrictive-wins rule at the cell level.

The **ADMIN** group has unrestricted access to all objects and cannot be modified.
