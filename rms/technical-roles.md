# Technical Roles - RMS

## Own (own request)

```
request:create							Allows creating a new request
request:display:own						Allows viewing the user's own requests.
request:update:own						Allows modifying the user's own requests.
request:delete:own						Allows deleting the user's own requests.
```
## Subordinates (subordinates' requests)

```
request:display:subordinates			Allows viewing requests of subordinate users.
request:change_status:manager_scope		Allows changing status: submitted → approved or rejected requests of subordinates.
```
## Approved only (e.g., for support)

```
request:display:approved_only			Allows viewing requests that have been approved by a manager (status neither 'submitted' nor 'rejected').
request:change_status:supported_scope	Allows changing status: approved → in_progress → completed
```
## All (full access / administrative)

```
request:display:all						Allows viewing all requests in the system.
request:update:all						Allows updating any request.
request:delete:all						Allows deleting any request.
request:change_status:all				Allows changing the status of any request (e.g., in progress, completed).
```
## Practical notes

1. Technical roles are static and do not depend on the user.

2. Filters like approved_only are application logic, not additional roles.

3. Business roles (Requestor, Manager, Support) are compositions of these technical roles:
```
Requestor		request:create, request:display:own,
			request:update:own, request:delete:own

Manager			request:display:subordinates, request:approve:subordinates,
			request:reject:subordinates

Support			request:display:approved_only,
			request:change_status:supported_scope
```