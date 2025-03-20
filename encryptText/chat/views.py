from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .forms import MessageForm
from .models import Message
import requests
from django.http import JsonResponse, HttpResponseNotFound
from django.conf import settings
from django.contrib import messages

#####################################
## Encrypt Messages
#####################################

@login_required
def send_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)

            reciever = message.receiver
            sender = request.user
            # payload to be encrypted
            payload = {
                'message': message.content,
                'sender': sender.id,
                'reciever': reciever.id
            }
            
            reverse_proxy_url = settings.QANAPI_URL

            # Define headers for authentication and destination
            headers = {
                'X-Qanapi-Authorization': settings.QANAPI_AUTH,  
                'X-Qanapi-Fields': 'message',
                'Content-Type': 'application/json',
            }

            try:
                # Send the data to the reverse proxy.
                response = requests.post(reverse_proxy_url, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()
                encrypted_text = data.get('message')

                Message.objects.create(
                    sender=sender,
                    receiver=reciever,
                    content=encrypted_text
                )
                messages.success(request, 'Message sent successfully!')
                return redirect('send_message')

            except requests.RequestException as e:
                # Log error or notify the user as needed.
                print("Error sending message to reverse proxy:", e)
            
            return redirect('inbox')
    else:
        form = MessageForm()
    return render(request, 'chat/send_message.html', {'form': form})


########################################
## Decrypt Messages
########################################

@login_required
def decrypt_message(request, message_id):
    try:
        # Only allow the receiver to decrypt their own message.
        message = Message.objects.get(id=message_id, receiver=request.user)
    except Message.DoesNotExist:
        return HttpResponseNotFound("Message not found")

    payload = {
        'message': message.content,
    }
    
    reverse_proxy_url = settings.QANAPI_URL

    headers = {
        'X-Qanapi-Authorization': settings.QANAPI_AUTH,
        'X-Qanapi-fields': 'message',
        'X-Qanapi-Mode' : 'decrypt'
    }
    
    try:
        response = requests.post(reverse_proxy_url, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        decrypted_text = data.get('message')
        return JsonResponse({'status': 'success', 'message': decrypted_text})

    except requests.RequestException as e:
        print("Error sending message for decryption:", e)
    
    return redirect('inbox')

########################################
## Other functions 
########################################

@login_required
def inbox(request):
    messages = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'chat/inbox.html', {'messages': messages})

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def user_list(request):
    # Exclude the current user from the list
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/user_list.html', {'users': users})

def home(request):
    if request.user.is_authenticated:
        return redirect('inbox')
    return render(request, 'home.html') 
