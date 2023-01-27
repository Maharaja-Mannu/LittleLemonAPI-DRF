from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()

    def __str__(self) -> str:
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.SmallIntegerField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)


class Person(models.Model):
    first_name = models.TextField()
    last_name = models.TextField()

    def __str__(self):
        return f"{self.first_name}, {self.last_name}"
