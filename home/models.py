# home/models.py

from django.db import models
from django.utils import timezone

class GradingScale(models.Model):
    """
    Grading Scale Model based on Tkinter's grading_scales table.
    Stores the rules for GPA calculation as a JSON field.
    """
    name = models.CharField(max_length=100, unique=True)
    rules = models.JSONField(default=dict)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Student(models.Model):
    """
    Student Model based on Tkinter's students table.
    Used for school/college results.
    """
    name = models.CharField(max_length=200)
    entry_date = models.DateTimeField(default=timezone.now)
    cumulative_gpa = models.FloatField(default=0.0)
    num_subjects = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Subject(models.Model):
    """
    Subject Model based on Tkinter's subjects table.
    Links back to the Student model with a ForeignKey.
    Used for school/college results.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=100)
    mark = models.FloatField()
    credits = models.IntegerField(default=0)
    semester = models.CharField(max_length=50, blank=True, null=True)
    grade = models.CharField(max_length=10, blank=True, null=True)
    subject_gpa = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.student.name})"

# ----------------------------------------------------------------------
# NEW MODELS FOR UNIVERSITY RESULTS
# ----------------------------------------------------------------------

class UniversityResult(models.Model):
    """
    Model for university students.
    Separated from the Student model to handle different logic and data.
    """
    name = models.CharField(max_length=200)
    entry_date = models.DateTimeField(default=timezone.now)
    cumulative_gpa = models.FloatField(default=0.0)
    num_subjects = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class UniversitySubject(models.Model):
    """
    Model for subjects of university students.
    Links back to the UniversityResult model.
    """
    student = models.ForeignKey(UniversityResult, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=100)
    mark = models.FloatField()
    credits = models.IntegerField(default=0)
    semester = models.CharField(max_length=50, blank=True, null=True)
    grade = models.CharField(max_length=10, blank=True, null=True)
    subject_gpa = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.student.name})"