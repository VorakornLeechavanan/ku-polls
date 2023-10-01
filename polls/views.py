from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect
from django.views import generic
from .models import Choice, Question, Vote
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

# Create your views here.


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects\
            .filter(pub_date__lte=timezone.now()).order_by('-pub_date')


class DetailView(generic.DetailView):
    model = Question
    template_name = 'detail.html'

    def get(self, request, *args, **kwargs):
        """
        Previous submitted choice will be selected in case
        a user redo the question.
        """
        question = Question.objects.get(id=kwargs["pk"])
        selected_choice = None
        if request.user.is_authenticated:
            try:
                voting = Vote.objects.get(user=request.user,
                                          choice__question=question)
                selected_choice = voting.choice
            except Vote.DoesNotExist:
                pass
        return render(request, 'detail.html', {"question": question,
                                               "selected_choice":
                                                   selected_choice})

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects\
            .filter(pub_date__lte=timezone.now())

    def dispatch(self, request, *args, **kwargs):
        """
        The application will return to the index page if the question is not
        in between the range of the publication time.
        """
        txt = Question.objects.get(id=kwargs["pk"])
        if not self.get_object().can_vote():
            messages.warning(request,
                             f'''The question "{txt}" is unpublished.''')
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
            messages.warning(request,
                             f'''The question "{txt}" is unpublished.''')
            return redirect('polls:index')
        return super().dispatch(request, *args, **kwargs)


def get_client_ip(request):
    """Get the visitor’s IP address using request headers."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@login_required
def vote(request, question_id):
    """
    The system will warn if the user submitted
    without selecting any single choice.
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
    this_user = request.user
    try:
        vote_obj = Vote.objects.get(user=this_user, choice__question=question)
        vote_obj.choice = selected_choice
    except Vote.DoesNotExist:
        vote_obj = Vote(user=this_user, choice=selected_choice)
    vote_obj.save()
    messages.success(request, "Voted Successfully")
    return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


def signup(request):
    """Register a new user."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # get named fields from the form data
            username = form.cleaned_data.get('username')
            # password input field is named 'password1'
            raw_passwd = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_passwd)
            login(request, user)
            return redirect('polls:index')
        # what if form is not valid?
        # we should display a message in signup.html
    else:
        # create a user form and display it the signup page
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
