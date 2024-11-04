from django.db import models
from devices.models import Device

# Create your models here.
class Transactions(models.Model):
    device_id = models.ForeignKey(Device, on_delete=models.CASCADE)
    payment_id = method = models.CharField(max_length=100)
    amount = models.FloatField()
    method = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    photo_url_done = models.TextField(default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Transaction #{self.payment_id} from {self.device_id} through {self.method}"