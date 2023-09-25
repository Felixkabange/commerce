from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError, models
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError


from .models import User, Listing, Bid, Comment


def index(request):
    listings = Listing.objects.filter(isActive=True)
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required     
def create(request):
    if request.method == "POST":
        title = request.POST['title']
        image = request.FILES['image']
        description = request.POST['description']
        category = request.POST['category']
        price = request.POST['price']
        new_listing = Listing.objects.create(author=request.user, title=title, image=image, price=int(price), description=description, category=category)
        new_listing.save()
        return HttpResponseRedirect(reverse("index")) 
    else:
       return render(request, "auctions/create.html")
    
def listing(request, id):
    listing = get_object_or_404(Listing, pk=id, isActive=True)
    show_comments = Comment.objects.filter(listing=listing)
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "show_comments": show_comments
    })

@login_required
def add_to_watchlist(request, id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=id, isActive=True)
        user = request.user

        if listing in user.listingwatchlist.all():
            user.listingwatchlist.remove(listing)
            message_text = f"{listing.title} removed from your watchlist."
        else:
            user.listingwatchlist.add(listing)
            message_text = f"{listing.title} added to your watchlist."

        messages.success(request, message_text)
        return HttpResponseRedirect(reverse("listing", args=[id]))
    else:
        return render(request, "auctions/listing.html")
    
def bid(request, id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=id, isActive=True)
        bid_amount = request.POST['bid']
        
        try:
            bid_amount = int(bid_amount)
            if bid_amount <= 0:
                raise ValueError("Bid must be a positive integer.")
        except ValueError:
            messages.error(request, "Invalid number. Bid must be a positive integer.")
            return HttpResponseRedirect(reverse("listing", args=[id]))
        
        # Get the current highest bid for the listing
        highest_bid = Bid.objects.filter(listing=listing).aggregate(models.Max('bid'))['bid__max']
        
        if not highest_bid:
            highest_bid = listing.price  # If no bids yet, use the starting price
        
        # Check if the bid meets the criteria
        if bid_amount > highest_bid and bid_amount >= listing.price:
            # Check if the user has already placed a bid on this listing
            existing_bid = Bid.objects.filter(listing=listing, author=request.user).first()
            
            if existing_bid:
                existing_bid.bid = bid_amount
                existing_bid.save()
            else:
                new_bid = Bid.objects.create(author=request.user, listing=listing, bid=bid_amount)
                new_bid.save()
            
            listing.price = bid_amount
            listing.save()
            messages.success(request, "Bid placed successfully!")
            return HttpResponseRedirect(reverse("listing", args=[id]))
        else:
            messages.error(request, "Bid must be greater than the current highest bid and at least equal to the starting price.")
            return HttpResponseRedirect(reverse("listing", args=[id]))
    else:
        return render(request, "auctions/listing.html")
    
def closeListing(request, id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=id, isActive=True)
        user = request.user

        if listing.author == user:
            # Set isActive to False
            listing.isActive = False
            listing.save()

            # Find the highest bid for the listing
            highest_bid = Bid.objects.filter(listing=listing).order_by('-bid').first()
            if highest_bid:
                winner = highest_bid.author
                messages.success(request, f"Listing successfully closed! {winner.username} is the winner.")
            else:
                messages.success(request, "Listing successfully closed!")
            
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/listing.html")
    else:
        return render(request, "auctions/listing.html")
    
def addComment(request, id):
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=id, isActive=True)
        user = request.user
        comment = request.POST.get('comment')  # Use get() to avoid KeyError if 'comment' is not in POST data
        
        if not comment:
            return HttpResponseBadRequest("Comment cannot be empty.")
        
        if user == listing.author:
            return HttpResponseForbidden("You cannot comment on your own listing.")
            
        new_comment = Comment.objects.create(author=user, listing=listing, message=comment)
        new_comment.save()
        
        return HttpResponseRedirect(reverse("listing", args=[id]))
    else:
        return HttpResponseBadRequest("Invalid request method.")
    
@login_required
def watchlist(request):
    user = request.user
    watchlist_items = user.listingwatchlist.filter(isActive=True)  # Filter active listings
    inactive_listings = user.listingwatchlist.filter(isActive=False)  # Filter inactive listings

    # Create a message for inactive listings
    inactive_message = None
    if inactive_listings.exists():
        inactive_message = "The following listings are no longer active: " + ", ".join([listing.title for listing in inactive_listings])

    return render(request, "auctions/watchlist.html", {
        "watchlist_items": watchlist_items,
        "inactive_message": inactive_message,
    })

def categories(request):
    # Retrieve all distinct categories from active listings
    categories = Listing.objects.filter(isActive=True).values('category').distinct()

    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def listings_by_category(request, category_name):
    listings = Listing.objects.filter(category=category_name, isActive=True)
    
    return render(request, "auctions/listings_by_category.html", {
        "category_name": category_name,
        "listings": listings
    })
                
            
            
        
    

