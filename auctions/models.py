from django.contrib.auth.models import AbstractUser
from django.db import models



class User(AbstractUser):
    id = models.BigAutoField(primary_key=True) 
    
    def __str__(self):
        return self.username

class Listing(models.Model):
    id = models.BigAutoField(primary_key=True)  
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='auctions/')  # Store uploaded auction item 
    price = models.IntegerField(default=0)
    isActive = models.BooleanField(default=True)
    description = models.CharField(max_length=400) 
    category = models.CharField(max_length=200) 
    watchlist = models.ManyToManyField(User, blank=True, related_name="listingwatchlist") 

    def __str__(self):
        return self.title
    
class Bid(models.Model):
    id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userBid")
    bid = models.IntegerField(default=0)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default=None, related_name="listing_bid")
    
class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="userComment")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="listingComment")
    message = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.author} comment on {self.listing}" 