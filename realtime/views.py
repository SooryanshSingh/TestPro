from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from Home.models import Exam, Answer, Response, Mark, Timer
from django.http import JsonResponse
from django.utils.timezone import now
from agora_token_builder import RtcTokenBuilder
import time
from django.conf import settings



@login_required
def test_with_chat(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all()
    is_proctor = request.user.groups.filter(name='Proctor').exists()

    if exam.attempted:
        return redirect('test_end', exam_id=exam.id)

    if request.method == 'POST':
        total_marks = 0

        for question in questions:
            answer_id = request.POST.get(f'answer_{question.id}')

            if not answer_id:
                continue

            answer = get_object_or_404(Answer, pk=int(answer_id))

            Response.objects.create(
                question=question,
                exam=exam,
                student=request.user,
                text=answer.text
            )

            if answer.is_correct:
                total_marks += 1

        Mark.objects.create(
            exam=exam,
            user=request.user,
            marks=total_marks,
            company=exam.company
        )

        exam.attempted = True
        exam.save(update_fields=["attempted"])

        return redirect('test_end', exam_id=exam.id)

    return render(request, 'test.html', {
        'exam': exam,
        'questions': questions,
        'is_proctor': is_proctor,
    })
    
  
@login_required
def proctor(request, exam_id, session_id):
    is_proctor = request.user.groups.filter(name='Proctor').exists()

    if not is_proctor:
        return HttpResponseForbidden("You are not authorized to access this page.")

    return render(
        request,
        "proctor.html",
        {
            'exam_id': exam_id,
            'session_id': session_id
        }
    )


@login_required
def proctor_dash(request, exam_id):
    print("This one")
    is_proctor = request.user.groups.filter(name='Proctor').exists()

    if not is_proctor:
        return HttpResponseForbidden("You are not authorized to access this page.")

    return render(
        request,
        "pdash.html",
        {
            'exam_id': exam_id
        }
    )



@login_required
def test_end(request,exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    exam.attempted = True
    exam.save()

  

    return render(request, 'test_end.html')

def get_remaining_time(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    
    timer, created = Timer.objects.get_or_create(exam=exam)

    if not timer.start_time:
        timer.start_time = now()
        timer.save()

    remaining_time = timer.get_remaining_time()
    
    return JsonResponse({"remaining_time": remaining_time})


def get_agora_token(request, exam_id):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({"error": "unauth"}, status=401)

    app_id = settings.AGORA_APP_ID
    app_cert = settings.AGORA_APP_CERT

    channel_name = f"exam_{exam_id}"
    uid = user.id  

    expiration = int(time.time()) + 3600

    token = RtcTokenBuilder.buildTokenWithUid(
        app_id,
        app_cert,
        channel_name,
        uid,
        1,  
        expiration
    )

    return JsonResponse({
        "token": token,
        "appId": app_id,
        "channel": channel_name,
        "uid": uid
    })
