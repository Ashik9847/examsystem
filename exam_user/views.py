from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import random
from .models import Category, Exam, Question, ExamAttempt, Answer
from .models import User
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        if password != confirm_password:
            return render(request, 'exam_user/register.html', {
                'error': 'Passwords do not match'
            })
        
        if User.objects.filter(username=username).exists():
            return render(request, 'exam_user/register.html', {
                'error': 'Username already taken'
            })
        
        # Create normal user (is_admin=False by default)
        user = User.objects.create_user(
            username=username,
            password=password,
            is_admin=False  # Regular user
        )
        login(request, user)  # Auto-login after registration
        return redirect('exam_user:index')
    
    return render(request, 'exam_user/register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_admin or user.is_superuser:
                return redirect('controller_admin:dashboard')
            return redirect('exam_user:index')
        else:
            return render(request, 'exam_user/login.html', {
                'error': 'Invalid username or password'
            })
    return render(request, 'exam_user/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('exam_user:login')

@login_required
def index(request):
    categories = Category.objects.all()
    return render(request, 'exam_user/index.html', {'categories': categories})

@login_required
def category_detail(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    active_exams = category.exams.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now())
    
    # Get exams this user has already completed
    completed_exam_ids = ExamAttempt.objects.filter(
        user=request.user,
        exam__category=category,
        is_completed=True
    ).values_list('exam_id', flat=True)
    
    # Pass to template
    context = {
        'category': category,
        'exams': active_exams,
        'user_completed_exams': active_exams.filter(id__in=completed_exam_ids)
    }
    return render(request, 'exam_user/category_detail.html', context)

@login_required
def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if not exam.is_active():
        messages.error(request, "This exam is not currently active.")
        return redirect('exam_user:index')

    # Check if user already attempted this exam
    if ExamAttempt.objects.filter(user=request.user, exam=exam, is_completed=True).exists():
        messages.warning(request, "You have already completed this exam. You cannot take it again.")
        return redirect('exam_user:index')

    # If already started but not completed (e.g. page refresh), redirect to ongoing attempt
    ongoing_attempt = ExamAttempt.objects.filter(user=request.user, exam=exam, is_completed=False).first()
    if ongoing_attempt:
        return redirect('exam_user:take_exam', attempt_id=ongoing_attempt.attempt_id)

    # Create new attempt
    attempt = ExamAttempt.objects.create(user=request.user, exam=exam)
    
    all_questions = list(exam.questions.all())
    selected_questions = random.sample(all_questions, min(len(all_questions), exam.number_of_questions))
    attempt.questions_data = [q.id for q in selected_questions]
    attempt.total_marks = sum(q.marks for q in selected_questions)
    attempt.save()

    messages.success(request, f"Exam started! Attempt ID: {attempt.attempt_id}")
    return redirect('exam_user:take_exam', attempt_id=attempt.attempt_id)

@login_required
def take_exam(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, attempt_id=attempt_id, user=request.user, is_completed=False)

    elapsed_seconds = (timezone.now() - attempt.start_time).total_seconds()
    if elapsed_seconds > attempt.exam.duration_minutes * 60:
        return redirect('exam_user:submit_exam', attempt_id=attempt_id)

    questions = Question.objects.filter(id__in=attempt.questions_data)
    remaining_seconds = max(0, int(attempt.exam.duration_minutes * 60 - elapsed_seconds))

    if request.method == 'POST':
        for question in questions:
            selected = request.POST.get(f'question_{question.id}')
            if selected:
                Answer.objects.update_or_create(
                    attempt=attempt,
                    question=question,
                    defaults={'selected_answer': selected}
                )
        if 'submit' in request.POST or remaining_seconds <= 0:
            return redirect('exam_user:submit_exam', attempt_id=attempt_id)

    existing_answers = {ans.question.id: ans.selected_answer for ans in attempt.answers.all()}

    return render(request, 'exam_user/take_exam.html', {
        'attempt': attempt,
        'questions': questions,
        'existing_answers': existing_answers,
        'remaining_seconds': remaining_seconds,
    })

@login_required
def submit_exam(request, attempt_id):
    attempt = get_object_or_404(ExamAttempt, attempt_id=attempt_id, user=request.user)
    if not attempt.is_completed:
        attempt.score = sum(ans.marks_obtained for ans in attempt.answers.all())
        attempt.percentage = (attempt.score / attempt.total_marks * 100) if attempt.total_marks > 0 else 0
        attempt.is_completed = True
        attempt.end_time = timezone.now()
        attempt.save()
    return render(request, 'exam_user/results.html', {'attempt': attempt})

@login_required
def search_result(request):
    exam_id = request.POST.get('exam_id') or request.GET.get('exam_id')
    if not exam_id:
        return redirect('exam_user:index')
    
    # WRONG → This looks for primary key (integer id)
    # attempt = get_object_or_404(ExamAttempt, id=exam_id)

    # CORRECT → Use the custom attempt_id field (the 8-char code)
    attempt = get_object_or_404(ExamAttempt, attempt_id=exam_id)
    
    # Security: Only allow the owner or admin to view
    if attempt.user != request.user and not (request.user.is_admin or request.user.is_superuser):
        return redirect('exam_user:index')
    
    return render(request, 'exam_user/results.html', {'attempt': attempt})





