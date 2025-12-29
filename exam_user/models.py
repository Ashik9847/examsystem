from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import random
import string

class User(AbstractUser):
    is_admin = models.BooleanField(default=False)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.username

class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Exam(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='exams')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.IntegerField(help_text="Duration in minutes")
    number_of_questions = models.IntegerField(help_text="Number of questions to display")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    pass_percentage = models.FloatField(default=40.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def is_active(self):
        now = timezone.now()
        return self.start_date <= now <= self.end_date

class Question(models.Model):
    OPTION_TYPE_CHOICES = [('text', 'Text'), ('image', 'Image')]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_type = models.CharField(max_length=10, choices=OPTION_TYPE_CHOICES, default='text')
    option_a = models.CharField(max_length=500, blank=True)
    option_b = models.CharField(max_length=500, blank=True)
    option_c = models.CharField(max_length=500, blank=True)
    option_d = models.CharField(max_length=500, blank=True)
    option_a_image = models.ImageField(upload_to='options/', blank=True, null=True)
    option_b_image = models.ImageField(upload_to='options/', blank=True, null=True)
    option_c_image = models.ImageField(upload_to='options/', blank=True, null=True)
    option_d_image = models.ImageField(upload_to='options/', blank=True, null=True)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    marks = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"Q{self.id}: {self.question_text[:50]}"

class ExamAttempt(models.Model):
    attempt_id = models.CharField(max_length=10, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(default=0.0)
    total_marks = models.FloatField(default=0.0)
    percentage = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    questions_data = models.JSONField(default=list)  # list of question IDs

    class Meta:
        ordering = ['-start_time']

    def save(self, *args, **kwargs):
        if not self.attempt_id:  # Changed here
            self.attempt_id = self.generate_exam_id()  # Changed here
        super().save(*args, **kwargs)

    def generate_exam_id(self):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not ExamAttempt.objects.filter(attempt_id=code).exists():  # Changed here
                return code

    def __str__(self):
        return f"{self.attempt_id} - {self.user.username}"  # Changed here

class Answer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    is_correct = models.BooleanField(default=False)
    marks_obtained = models.FloatField(default=0.0)

    class Meta:
        unique_together = ['attempt', 'question']

    def save(self, *args, **kwargs):
        self.is_correct = self.selected_answer == self.question.correct_answer
        self.marks_obtained = self.question.marks if self.is_correct else 0.0
        super().save(*args, **kwargs)