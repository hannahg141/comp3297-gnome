from django.db import models
from enum import Enum


class ProjectStatus(Enum):
    CURRENT = "current"
    COMPLETE = "complete"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class SprintStatus(Enum):
    CURRENT = "current"
    COMPLETE = "complete"
    NOTYETSTARTED = "not yet started"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class PBIStatus(Enum):
    IN_PROGRESS = "in progress"
    COMPLETE = "complete"
    NOT_YET_STARTED = "not yet started"
    INCOMPLETE = "incomplete"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class PBIPriority(Enum):
    VERY_HIGH = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    VERY_LOW = 5

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]

class TaskStatus(Enum):
    IN_PROGRESS = "in progress"
    COMPLETE = "complete"
    NOT_YET_STARTED = "not yet started"

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class Project(models.Model):
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=200, default=ProjectStatus.CURRENT.value, choices=ProjectStatus.choices())

    def save(self, *args, **kwargs):
        is_new = True if not self.id else False
        super(Project, self).save(*args, **kwargs)
        if is_new:
            product_backlog = ProductBacklog(name=self.name+" product backlog", project=self)
            product_backlog.save()

    def __str__(self):
        return self.name
   
    def get_absolute_url(self):
       return reverse("home",kwargs={"id": self.id})

    @property
    #returns all completed sprints
    def all_sprints(self):
        holder = ProductBacklog.objects.get(project=self.id)
        return SprintBacklog.objects.filter(productBacklogID=holder.id,status=SprintStatus.COMPLETE.value)
    
    #fills lists with all the names of completed sprints 
    @property
    def velocity_chart_names(self):
        holder = []
        for Sprint in self.all_sprints:
            holder.append(Sprint.name)
        return holder
    #fills list with estimated hours for completed sprints
    @property
    def velocity_chart_actual(self):
        holder = []
        for Sprint in self.all_sprints:
            holder.append(Sprint.sprint_actual_effort_hours)
        return holder

    #fills list with actual hours for completed sprints
    @property
    def velocity_chart_estimated(self):
        holder = []
        for Sprint in self.all_sprints:
            holder.append(Sprint.sprint_cummulative_effort_hours)
        return holder

class ProductBacklog(models.Model):
    name = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        is_new = True if not self.id else False
        super(ProductBacklog, self).save(*args, **kwargs)
        if is_new:
            sprint_backlog = SprintBacklog(name=self.name+" sprint0", productBacklogID=self)
            sprint_backlog.save()

    def pbiList(self):
        return ProductBacklogItem.objects.filter(productBacklogID=self.id).order_by('priority')

class SprintBacklog(models.Model):
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=200, default=SprintStatus.NOTYETSTARTED.value, choices=SprintStatus.choices())
    productBacklogID = models.ForeignKey(ProductBacklog, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def productBacklog(self):
        return ProductBacklog.objects.get(self.productBacklogID)

    def pbiList(self):
        return ProductBacklogItem.objects.filter(sprintBacklogID=self.id).order_by('priority')

    @property
    def sprint_total_story_points(self):
        x = 0
        for PBI in self.pbiList():
            x += PBI.pointEstimate
        return x

    @property
    def sprint_cummulative_effort_hours(self):
        x = 0
        for PBI in self.pbiList():
            x += PBI.tasks_cummulative_effort_hours
        return x

    @property
    def sprint_actual_effort_hours(self):
        x = 0
        for PBI in self.pbiList():
            x += PBI.tasks_actual_effort_hours
        return x

    @property
    def sprint_work_remaining(self):
        return self.sprint_cummulative_effort_hours - self.sprint_actual_effort_hours

class ProductBacklogItem(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    pointEstimate = models.IntegerField(choices=[(x,str(x)) for x in {1,2,3,5,8,13,20,40}])
    productBacklogID = models.ForeignKey(ProductBacklog, on_delete=models.CASCADE)
    sprintBacklogID = models.ForeignKey(SprintBacklog, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(max_length=50, default=PBIStatus.NOT_YET_STARTED.value, choices=PBIStatus.choices())
    priority = models.IntegerField(blank=True, null=False, default=PBIPriority.NORMAL.value, choices=PBIPriority.choices())

    def __str__(self):
        return self.name

    def tasks(self):
        return Task.objects.filter(pbi=self)

    def tasks_complete(self):
        return Task.objects.filter(pbi=self, status=TaskStatus.COMPLETE.value)

    def tasks_in_progress(self):
        return Task.objects.filter(pbi=self, status=TaskStatus.IN_PROGRESS.value)

    def tasks_not_yet_started(self):
        return Task.objects.filter(pbi=self.pk, status=TaskStatus.NOT_YET_STARTED.value)

    @property
    def tasks_cummulative_effort_hours(self):
        x = 0
        for Task in self.tasks():
            if (type(Task.estimatedEffortHours) is float):
                x += Task.estimatedEffortHours
        return x

    @property
    def tasks_actual_effort_hours(self):
        x = 0
        for Task in self.tasks():
            if (type(Task.actualEffortHours) is float):
                x += Task.actualEffortHours
        return x
    @property
    def tasks_work_remaining(self):
        return self.tasks_cummulative_effort_hours - self.tasks_actual_effort_hours

class Task(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=500)
    estimatedEffortHours = models.FloatField()
    actualEffortHours = models.FloatField(blank=True, null=True)
    status = models.CharField(max_length=50, default=TaskStatus.NOT_YET_STARTED.value, choices=TaskStatus.choices())
    pbi = models.ForeignKey(ProductBacklogItem, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    def tasks_estimated_effort_hours(self):
        return self.estimatedEffortHours
