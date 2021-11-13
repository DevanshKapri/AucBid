from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import SET_DEFAULT
from datetime import timedelta, timezone


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=32, default="Misc")

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f"{self.name}"

    @property
    def count_active_listings(self):
        return Listings.objects.filter(category=self).count()


class Listings(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='lists')
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField()
    list_id = models.BigAutoField(primary_key=True)
    date_listed = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey('Category', blank=True, on_delete=SET_DEFAULT)
    base_price = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    image = models.ImageField(upload_to='images/')
    end_time = models.DateTimeField()

    DURATIONS = (
        (3, "Three Days"),
        (7, "One Week"),
        (14, "Two Weeks"),
        (28, "Four Weeks")
    )

    duration = models.IntegerField(choices=DURATIONS)

    class Meta:
        ordering = ('-end_time',)

    def save(self, *args, **kwargs):
        self.end_time = self.date_listed + timedelta(days=self.duration)
        super().save(*args, **kwargs)

    def is_finished(self):
        if not self.status or self.end_time < timezone.now():
            self.status = False
            return True
        return False 

    def __str__(self):
        return f"Auction #{self.list_id}: {self.title} ({self.user.username})"


class Bid(models.Model):
    bid_id = models.BigAutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField(blank=False)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='place_bid')
    listings = models.ForeignKey('Listings', on_delete=models.CASCADE, related_name='bids_on')

    class Meta:
        ordering = ('-amount',)

    def __str__(self):
        return f"Bid #{self.bid_id}: {self.amount} on {self.listings.title} by {self.user.username}"


class Comment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='commented_by')
    comment_id = models.BigAutoField(primary_key=True)
    comment = models.TextField(blank=False)
    date = models.DateTimeField(auto_now_add=True)
    listings = models.ForeignKey('Listings', on_delete=models.CASCADE, related_name='commented_on')

    def __str__(self):
        return f"Comment #{self.comment_id}: {self.user.username} on {self.listings.title}: {self.comment}"

class Watchlist(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='watchlist_user')
    listings = models.ManyToManyField('Listings', related_name='watchlist_listing', blank=True)

    def __str__(self):
        return f'Watchlist for {self.user.username}' 