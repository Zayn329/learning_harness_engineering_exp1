def test_project_model_repr(app, create_project):
    project = create_project(name="Alchemy", active=True)
    with app.app_context():
        assert repr(project) == f"<Project {project.project_name}>"


def test_task_model_repr(app, create_task):
    task = create_task(task_desc="Test Task")
    with app.app_context():
        assert repr(task) == f"<Task {task.task}>"


def test_task_model_priority_default(app, create_task):
    task = create_task(task_desc="Default Priority Task")
    with app.app_context():
        assert task.priority == "Medium"


def test_task_model_priority_explicit(app, create_project):
    from task_manager import db
    from task_manager.models import Tasks

    project = create_project(name="Priority Project")
    task = Tasks(project_id=project.project_id, task="Urgent Task", status=True, priority="High")
    db.session.add(task)
    db.session.commit()

    with app.app_context():
        assert task.priority == "High"


def test_task_model_priority_invalid_fallback(app, create_project):
    from task_manager import db
    from task_manager.models import Tasks

    project = create_project(name="Invalid Priority Project")
    task = Tasks(project_id=project.project_id, task="Invalid Task", status=True, priority="Urgent")
    db.session.add(task)
    db.session.commit()

    with app.app_context():
        assert task.priority == "Medium"
