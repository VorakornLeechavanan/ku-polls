from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.views import generic
from .models import Choice, Question
from django.urls import reverse

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now()).order_by('-pub_date')


class DetailView(generic.DetailView):
    model = Question
    template_name = 'detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())

    def dispatch(self, request, *args, **kwargs):
        """
        The application will return to the index page if the question is not
        in between the range of the publication time.
        """
        txt = Question.objects.get(id=kwargs["pk"])
        if not self.get_object().can_vote():
            messages.warning(request, f'''The question "{txt}" is unpublished.''')
            return redirect('polls:index')
        return super().dispatch(request, *args, **kwargs)


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'results.html'

    def dispatch(self, request, *args, **kwargs):
        """
        The application will return to the index page if the question is not
        in between the range of the publication time.
        """
        txt = Question.objects.get(id=kwargs["pk"])
        if not self.get_object().can_vote():
            messages.warning(request, f'''The question "{txt}" is unpublished.''')
            return redirect('polls:index')
        return super().dispatch(request, *args, **kwargs)


def vote(request, question_id):
    """
    The system will warn if the user submitted without selecting any single choice.
    Otherwise, vote scores will be increased.
    """
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))

