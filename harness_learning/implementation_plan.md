# Implementation Plan: Task Priority Feature

## 1. Discovered Repository Facts vs Proposed Design Choices

### A. Discovered Repository Facts
1. Tasks currently possess `task_id`, `project_id`, `task`, and `status`.
2. Task creation occurs in two routes: `/add` (Web HTML form) and `/api/tasks` (REST JSON API).
3. The test suite uses a shared fixture `create_task` in `conftest.py` which passes positional/keyword arguments to `Tasks(...)`.
4. The database is initialized via `db.create_all()` in `task_manager/__init__.py`.

### B. Proposed Design Choices (Task Priority Feature)
1. **Priority Values**: Represented as strings: `"Low"`, `"Medium"`, `"High"`.
2. **Default Priority**: Set to `"Medium"` across models, web forms, and REST endpoints.
3. **Database Representation**: `db.Column(db.String(10), default="Medium")`.

---

## 2. Multi-Dimensional Backward Compatibility Analysis

To guarantee that adding priority introduces zero regressions across existing code and tests:

1. **Model Constructor Compatibility**:
   * *Strategy*: `Tasks.__init__(self, project_id, task, status=True, priority="Medium")`
   * *Impact*: Existing calls like `Tasks(project_id, task)` or `Tasks(project_id, task, status)` continue working without argument count mismatches.
2. **Test Fixture Compatibility**:
   * *Strategy*: If `Tasks.__init__` has a default parameter `priority="Medium"`, existing test fixtures like `create_task` in `conftest.py` automatically work without requiring mandatory changes.
3. **API Payload Compatibility**:
   * *Strategy*: `GET /api/tasks` includes `"priority"` as an additive key. `POST /api/tasks` and `PUT /api/tasks/<id>` use `.get("priority", "Medium")` and `.get("priority", task.priority)` respectively.
   * *Impact*: Clients omitting `"priority"` in JSON payloads continue functioning seamlessly.
4. **Database & Schema Compatibility**:
   * *Strategy*: New SQLite instances created via `db.create_all()` include the `priority` column automatically. For existing development databases, falling back gracefully or recreating the test DB handles the change cleanly.
5. **Form Input & Rendering Compatibility**:
   * *Strategy*: `request.form.get("priority", "Medium")` safely defaults if an old form submission lacks the input. The Jinja2 template checks for `task.priority` or displays default styling.

---

## 3. Justification of Minimum Change Against Alternatives

| Proposed Approach | Alternative 1: Integer Priority Levels (1, 2, 3) | Alternative 2: Custom DB Enum / PostgreSQL Enum | Alternative 3: Separate Priority Table | Alternative 4: Migration Framework (Alembic) |
| :--- | :--- | :--- | :--- | :--- |
| **Choice**: String (`"Low"`, `"Medium"`, `"High"`) | **Rejected**: Requires mapping integers to human-readable labels in UI and API docs. | **Rejected**: SQLite does not natively support SQL ENUM types; requires dialect-specific workarounds. | **Rejected**: Creates unnecessary join queries (`JOIN priority`) for a simple 3-level attribute. Overengineers data model. | **Rejected**: Project uses `db.create_all()` without Alembic migration infrastructure. Introducing Alembic adds unnecessary complexity. |
| **Justification**: Storing strings (`String(10)`) is human-readable, natively supported by SQLite/SQLAlchemy, and requires zero extra dependencies. |

---

## 4. Behavior-Oriented Acceptance Criteria (Definition of Done)

The implementation will be considered complete **ONLY** when the following externally observable behaviors are satisfied:

* **AC 1 (Default Priority Assignment)**:
  When a task is created without specifying priority (via Web UI or REST API), the system assigns it `"Medium"` priority.
* **AC 2 (Explicit Priority Creation via Web UI)**:
  When a user selects `"High"` or `"Low"` priority in the web form and submits, the created task reflects that priority in the task list.
* **AC 3 (Explicit Priority Creation via REST API)**:
  When a JSON payload containing `{"priority": "High"}` is POSTed to `/api/tasks`, the returned 201 response payload contains `"priority": "High"`.
* **AC 4 (Priority Updates via REST API)**:
  When a JSON payload containing `{"priority": "Low"}` is PUT to `/api/tasks/<id>`, subsequent GET requests to `/api/tasks/<id>` return `"priority": "Low"`.
* **AC 5 (REST API Payload Contract)**:
  All task objects returned by `GET /api/tasks` and `GET /api/tasks/<id>` contain the `"priority"` key.
* **AC 6 (Zero Regression Guarantee)**:
  All 55 pre-existing unit tests pass without failure or modification of existing test logic.

---

## 5. Implementation Task List (Separated from Acceptance Criteria)
*(To be executed only when feature development begins)*

1. Add `priority` column to `Tasks` in `task_manager/models.py`.
2. Update `/add` form handling in `task_manager/routes.py`.
3. Update REST endpoints (`/api/tasks`) in `task_manager/routes.py`.
4. Update web UI template `task_manager/templates/index.html`.
5. Add unit tests for priority behavior in `tests/`.
