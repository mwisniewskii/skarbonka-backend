from django.db import models


class ControlType(models.IntegerChoices):
    NONE = 1, "None"
    CONFIRMATION = 2, "Confirmation"
    PERIODIC = 3, "Periodic limit"


class UserType(models.IntegerChoices):
    PARENT = 1, "Parent"
    CHILD = 2, "Child"