from datetime import time, timedelta
from zoneinfo import ZoneInfo

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from accounts.factories import UserFactory
from study_preference.factories import StudyPreferenceFactory
from study_session.factories import StudySessionFactory
from study_session.models import StudySession
from study_task.factories import StudyTaskFactory
from study_task.models import StudyTask
from subject.factories import SubjectFactory


class Command(BaseCommand):
    help = "Create a realistic StudyOps development dataset."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete and recreate the demo account and all of its data.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = "demo_student"
        User = get_user_model()
        existing_user = User.objects.filter(username=username).first()

        if existing_user is not None:
            if not options["reset"]:
                raise CommandError(
                    f"Demo user '{username}' already exists. "
                    "Run seed_data --reset to recreate it."
                )
            existing_user.delete()

        user = UserFactory(
            username=username,
            email="demo@student.test",
            password="studyops123",
        )

        StudyPreferenceFactory(
            user=user,
            timezone="Asia/Beirut",
            earliest_study_time=time(8, 0),
            latest_study_time=time(22, 0),
            preferred_session_minutes=45,
            buffer_minutes=10,
        )

        subjects = {
            "data_structures": SubjectFactory(
                user=user,
                name="Data Structures",
                code="CS201",
                semester=1,
            ),
            "databases": SubjectFactory(
                user=user,
                name="Database Systems",
                code="CS220",
                semester=1,
            ),
            "discrete_math": SubjectFactory(
                user=user,
                name="Discrete Mathematics",
                code="MATH210",
                semester=1,
            ),
            "technical_writing": SubjectFactory(
                user=user,
                name="Technical Writing",
                code="ENG205",
                semester=1,
            ),
        }

        beirut = ZoneInfo("Asia/Beirut")
        local_now = timezone.localtime(timezone.now(), beirut)

        def at_day(days_from_now, hour, minute=0):
            return (local_now + timedelta(days=days_from_now)).replace(
                hour=hour,
                minute=minute,
                second=0,
                microsecond=0,
            )

        tasks = {
            "data_structures_exam": StudyTaskFactory(
                user=user,
                subject=subjects["data_structures"],
                title="Prepare for Data Structures exam",
                description=(
                    "Review complexity, trees, heaps, hashing, graphs, BFS, and DFS."
                ),
                task_type=StudyTask.TaskType.EXAM,
                task_status=StudyTask.TaskStatus.IN_PROGRESS,
                task_priority=StudyTask.TaskPriority.HIGH,
                estimated_minutes=360,
                due_date=at_day(8, 10),
            ),
            "avl_assignment": StudyTaskFactory(
                user=user,
                subject=subjects["data_structures"],
                title="Complete AVL tree assignment",
                description="Implement insertion, rotations, and deletion tests.",
                task_type=StudyTask.TaskType.ASSIGNMENT,
                task_priority=StudyTask.TaskPriority.HIGH,
                estimated_minutes=180,
                due_date=at_day(4, 23, 59),
            ),
            "database_project": StudyTaskFactory(
                user=user,
                subject=subjects["databases"],
                title="Design library database schema",
                description="Finish the ER diagram, normalization, and SQL schema.",
                task_type=StudyTask.TaskType.ASSIGNMENT,
                task_priority=StudyTask.TaskPriority.MEDIUM,
                estimated_minutes=240,
                due_date=at_day(6, 18),
            ),
            "sql_quiz": StudyTaskFactory(
                user=user,
                subject=subjects["databases"],
                title="Prepare for SQL quiz",
                description="Practice joins, aggregation, nested queries, and indexes.",
                task_type=StudyTask.TaskType.EXAM,
                task_priority=StudyTask.TaskPriority.HIGH,
                estimated_minutes=120,
                due_date=at_day(3, 9),
            ),
            "discrete_problem_set": StudyTaskFactory(
                user=user,
                subject=subjects["discrete_math"],
                title="Complete graph theory problem set",
                description="Solve the assigned graph, tree, and induction problems.",
                task_type=StudyTask.TaskType.ASSIGNMENT,
                task_priority=StudyTask.TaskPriority.MEDIUM,
                estimated_minutes=150,
                due_date=at_day(5, 20),
            ),
            "discrete_midterm": StudyTaskFactory(
                user=user,
                subject=subjects["discrete_math"],
                title="Prepare for Discrete Mathematics midterm",
                description="Review logic, proofs, combinatorics, and graph theory.",
                task_type=StudyTask.TaskType.EXAM,
                task_priority=StudyTask.TaskPriority.HIGH,
                estimated_minutes=300,
                due_date=at_day(12, 11),
            ),
            "writing_outline": StudyTaskFactory(
                user=user,
                subject=subjects["technical_writing"],
                title="Draft research report outline",
                description="Prepare the thesis, main sections, and initial references.",
                task_type=StudyTask.TaskType.ASSIGNMENT,
                task_priority=StudyTask.TaskPriority.LOW,
                estimated_minutes=120,
                due_date=at_day(10, 17),
            ),
            "completed_reading": StudyTaskFactory(
                user=user,
                subject=subjects["technical_writing"],
                title="Read citation style guide",
                description="Review the required citation and formatting rules.",
                task_type=StudyTask.TaskType.STUDY,
                task_status=StudyTask.TaskStatus.DONE,
                task_priority=StudyTask.TaskPriority.LOW,
                estimated_minutes=45,
                due_date=at_day(-1, 17),
            ),
        }

        session_specs = [
            ("data_structures_exam", 1, 18, 0, 45),
            ("database_project", 2, 19, 0, 45),
            ("discrete_problem_set", 3, 18, 30, 45),
            ("sql_quiz", 1, 20, 0, 45),
            ("writing_outline", 5, 10, 0, 45),
        ]

        for task_name, day, hour, minute, duration in session_specs:
            task = tasks[task_name]
            start_at = at_day(day, hour, minute)
            StudySessionFactory(
                user=user,
                subject=task.subject,
                task=task,
                start_at=start_at,
                end_at=start_at + timedelta(minutes=duration),
                status=StudySession.SessionStatus.SCHEDULED,
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Seeded demo_student with 4 subjects, 8 tasks, "
                "1 preference profile, and 5 scheduled sessions."
            )
        )
        self.stdout.write("Login: demo_student / studyops123")
