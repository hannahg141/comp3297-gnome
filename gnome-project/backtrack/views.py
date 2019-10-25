from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from backtrack.models import Project, ProductBacklog, SprintBacklog
import logging

from django.views.generic.edit import CreateView

# Create your views here.

logging.basicConfig(level=logging.DEBUG)


class ViewProjects(TemplateView):
    template_name = "project_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.all()
        return context

class ViewProjects2(TemplateView):
    template_name = "project_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project_list1'] = Project.objects.filter(status ="current")
        context['project_list2'] = Project.objects.filter(status="complete")
        return context


class ViewProject(TemplateView):
    template_name = "project.html"

    def get_context_data(self, **kwargs):
        logging.debug(kwargs)
        project = self.kwargs['project']
        context = super().get_context_data(**kwargs)
        context['project'] = Project.objects.get(id=project)
        context['sprint_list'] = SprintBacklog.objects.filter(project=project)
        return context


class ProjectsViewAll(ListView):
    template_name = "project_list.html"
    model = Project

    logging.debug('This will get logged')


class CreateNewProjectView(CreateView):
    template_name="project_form.html"
    model=Project
    fields=['name', 'status']


