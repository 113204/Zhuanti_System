from django.db import models


# Create your models here.
# 使用者資訊
class User(models.Model):
    email = models.CharField(primary_key=True, max_length=45)
    name = models.CharField(max_length=45)
    password = models.CharField(max_length=45)
    gender = models.IntegerField()
    permission = models.IntegerField()
    address = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)

    class Meta:
        managed = False
        db_table = 'user'
