from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from exam_user.models import Category, Exam, Question, ExamAttempt
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None and (user.is_admin or user.is_superuser):
            login(request, user)
            return redirect('controller_admin:dashboard')
        else:
            return render(request, 'controller_admin/login.html', {
                'error': 'Invalid credentials or insufficient privileges. Admins and superusers only.'
            })
    
    return render(request, 'controller_admin/login.html')

# Optional: Admin logout
def admin_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return redirect('controller_admin:admin_login')
def admin_required(user):
    return user.is_authenticated and user.is_admin


def dashboard(request):
    categories_count = Category.objects.count()
    exams_count = Exam.objects.count()
    attempts_count = ExamAttempt.objects.count()

    context = {
        'categories_count': categories_count,
        'exams_count': exams_count,
        'attempts_count': attempts_count,
    }
    return render(request, 'controller_admin/dashboard.html', context)


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'controller_admin/category_list.html', {'categories': categories})


def category_add(request):
    if request.method == 'POST':
        Category.objects.create(
            name=request.POST['name'],
            description=request.POST.get('description', '')
        )
        return redirect('controller_admin:category_list')
    return render(request, 'controller_admin/category_add.html')


def category_detail(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return render(request, 'controller_admin/category_detail.html', {'category': category})


def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name = request.POST['name']
        category.description = request.POST.get('description', '')
        category.save()
        messages.success(request, f'Category "{category.name}" updated successfully!')
        return redirect('controller_admin:category_detail', pk=category.id)
    return render(request, 'controller_admin/category_edit.html', {'category': category})


def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category_name = category.name
        category.delete()
        messages.success(request, f'Category "{category_name}" deleted successfully!')
        return redirect('controller_admin:category_list')
    return render(request, 'controller_admin/category_delete.html', {'category': category})





def exam_add(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        Exam.objects.create(
            category=category,
            name=request.POST['name'],
            description=request.POST.get('description', ''),
            duration_minutes=request.POST['duration_minutes'],
            number_of_questions=request.POST['number_of_questions'],
            start_date=request.POST['start_date'],
            end_date=request.POST['end_date'],
            pass_percentage=request.POST.get('pass_percentage', 40.0)
        )
        return redirect('controller_admin:category_detail', pk=category_id)
    return render(request, 'controller_admin/exam_add.html', {'category': category})


def exam_detail(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    questions = exam.questions.all()
    return render(request, 'controller_admin/exam_detail.html', {'exam': exam, 'questions': questions})


def exam_edit(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        exam.name = request.POST['name']
        exam.description = request.POST.get('description', '')
        exam.duration_minutes = request.POST['duration_minutes']
        exam.number_of_questions = request.POST['number_of_questions']
        exam.start_date = request.POST['start_date']
        exam.end_date = request.POST['end_date']
        exam.pass_percentage = request.POST.get('pass_percentage', 40.0)
        exam.save()
        messages.success(request, f'Exam "{exam.name}" updated successfully!')
        return redirect('controller_admin:exam_detail', pk=exam.id)
    return render(request, 'controller_admin/exam_edit.html', {'exam': exam})


def exam_delete(request, pk):
    exam = get_object_or_404(Exam, pk=pk)
    category_id = exam.category.id
    if request.method == 'POST':
        exam_name = exam.name
        exam.delete()
        messages.success(request, f'Exam "{exam_name}" deleted successfully!')
        return redirect('controller_admin:category_detail', pk=category_id)
    return render(request, 'controller_admin/exam_delete.html', {'exam': exam, 'category_id': category_id})


def question_add(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.method == 'POST':
        q = Question(
            exam=exam,
            question_text=request.POST['question_text'],
            option_type=request.POST['option_type'],
            correct_answer=request.POST['correct_answer'],
            marks=request.POST.get('marks', 1.0)
        )
        if q.option_type == 'text':
            q.option_a = request.POST['option_a']
            q.option_b = request.POST['option_b']
            q.option_c = request.POST['option_c']
            q.option_d = request.POST['option_d']
        else:
            q.option_a_image = request.FILES.get('option_a_image')
            q.option_b_image = request.FILES.get('option_b_image')
            q.option_c_image = request.FILES.get('option_c_image')
            q.option_d_image = request.FILES.get('option_d_image')
        q.save()
        return redirect('controller_admin:exam_detail', pk=exam_id)
    return render(request, 'controller_admin/question_add.html', {'exam': exam})


def question_edit(request, pk):
    question = get_object_or_404(Question, pk=pk)
    exam_id = question.exam.id
    
    if request.method == 'POST':
        question.question_text = request.POST['question_text']
        question.option_type = request.POST['option_type']
        question.correct_answer = request.POST['correct_answer']
        question.marks = request.POST.get('marks', 1.0)
        
        if question.option_type == 'text':
            question.option_a = request.POST['option_a']
            question.option_b = request.POST['option_b']
            question.option_c = request.POST['option_c']
            question.option_d = request.POST['option_d']
            # Clear image fields
            question.option_a_image = None
            question.option_b_image = None
            question.option_c_image = None
            question.option_d_image = None
        else:
            question.option_a_image = request.FILES.get('option_a_image', question.option_a_image)
            question.option_b_image = request.FILES.get('option_b_image', question.option_b_image)
            question.option_c_image = request.FILES.get('option_c_image', question.option_c_image)
            question.option_d_image = request.FILES.get('option_d_image', question.option_d_image)
            # Clear text fields
            question.option_a = ''
            question.option_b = ''
            question.option_c = ''
            question.option_d = ''
        
        question.save()
        messages.success(request, 'Question updated successfully!')
        return redirect('controller_admin:exam_detail', pk=exam_id)
    
    return render(request, 'controller_admin/question_edit.html', {
        'question': question,
        'exam_id': exam_id
    })


def question_delete(request, pk):
    question = get_object_or_404(Question, pk=pk)
    exam_id = question.exam.id
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted successfully!')
        return redirect('controller_admin:exam_detail', pk=exam_id)
    
    return render(request, 'controller_admin/question_delete.html', {
        'question': question,
        'exam_id': exam_id
    })



def attempt_list(request):
    # Exclude superusers from the list
    attempts = ExamAttempt.objects.select_related('user', 'exam').exclude(user__is_superuser=True)
    return render(request, 'controller_admin/attempt_list.html', {'attempts': attempts})