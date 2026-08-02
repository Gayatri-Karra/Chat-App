from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
import base64

from django.views.decorators.http import require_POST

from . import models
# Create your views here.

# Decorator to check if user is logged in
def login_required(func):
    def wrapper(request, *args, **kwargs):
        if 'user' not in request.session:
            return redirect('log_in')  

        return func(request, *args, **kwargs)

    return wrapper


def log_in(request):
    user_exist = 0
    if request.method == "POST":
        username = request.POST["name"]
        if models.User.objects.filter(name=username).exists():
            request.session['user'] = username

            return redirect('user_chats')
        else:
            user_exist = 1
    
    context = {
        'user_ex_log': user_exist
    }
    return render(request, 'chat/index.html', context)



def sign_up(request):
    user_exist = 0

    if request.method == "POST":
        username = request.POST["name"]
        try:
            models.User.objects.create(name=username)
            request.session['user'] = username

            return redirect('user_chats')
        except Exception as e:
            user_exist = 1
    
    context = {
        "user_ex": user_exist
    }

    return render(request, "chat/index.html", context)


def log_out(request):
    del request.session['user']
    return redirect('log_in')


@login_required
@require_POST
def friend_requests_view(request, friend_request_id, friend_request_response):
    try:
        user_name = request.session["user"]
        user = models.User.objects.get(name=user_name)
        friend_request = models.FriendRequest.objects.get(id=friend_request_id)

        # Restrict access to authorized friend requests
        if friend_request.to_user == user and not models.Room.objects.filter(members=friend_request.from_user.id).filter(members=friend_request.to_user.id).exists():

            if friend_request_response == "accept":
                chat_object = models.Room()
                chat_object.save()

                user.friends.add(friend_request.from_user)
                chat_object.members.add(friend_request.from_user)
                chat_object.members.add(friend_request.to_user)

            friend_request.delete()
            return JsonResponse({'message': 'Friend request handled successfully'})
        
        return HttpResponse(status=403)
    
    except models.FriendRequest.DoesNotExist:
        return JsonResponse({"error": "Friend request not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



@login_required
def user_page_view(request):
    username = request.session.get('user')
    user = models.User.objects.get(name=username)
    chats = models.Room.objects.filter(members__in=[user.id])
    friend_requests = models.FriendRequest.objects.filter(to_user=user)

    context = {
        "friend_requests": friend_requests,
        "chats": chats,
        "username": username,
        "user": user
    }

    return render(request, 'chat/user_page.html', context)

# --------------------------Not a view--------------------------------------
def createNewMessage(message, conversation_id, user):
    conversation = models.Room.objects.get(room_id=conversation_id)
    new_message = models.Messages.objects.create(
        conversation=conversation, 
        content=message,
        created_by = models.User.objects.get(name=user)
    )

    item = {}
    item['message'] = new_message.content
    item['created_by'] = new_message.created_by.name
    item['created_at'] = new_message.created_at.strftime("%b. %d, %Y, %I:%M %p")

    return item
#---------------------------------------------------------------------------------


@login_required
def messages(request, pk):
    try:
        conversation = models.Room.objects.get(room_id=pk)
        user = models.User.objects.get(name=request.session['user'])
        friend_requests = models.FriendRequest.objects.filter(to_user=user)

        if user not in conversation.members.all():
            raise ValueError("You are not authorized to access messages in this room.")

        if request.method == "POST":
            try:
                data = json.loads(request.body.decode("utf-8"))
                message = data.get('message', '')

                if message:
                    message_json = createNewMessage(message, pk, user)

                    return JsonResponse(message_json)
            except json.JSONDecodeError as e:
                return JsonResponse({'error': "Invalid data format"}, status=400)
            
        context = {
            "friend_requests": friend_requests,
            # "conversation": conversation,
            "user": user,
            "chat_id": pk,
            "shared_key": base64.b64encode(conversation.shared_key).decode('utf-8')
        }
        return render(request, "chat/messages.html", context)
    except models.Room.DoesNotExist:
        return JsonResponse({'error': 'Room not Found'}, status=404)


@login_required
def api_messages(request, pk):
    try:
        conversation = models.Room.objects.get(room_id=pk)
        user = models.User.objects.get(name=request.session['user'])

        if user not in conversation.members.all():
            raise ValueError("You are not authorized to access messages in this room.")
        

        messages = []
        for message in conversation.conversation.all():
            message_info = {
                'message': message.content,
                'created_by': str(message.created_by),
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            messages.append(message_info)
        return JsonResponse({'messages': messages})
    except models.Room.DoesNotExist:
        return JsonResponse({'error': 'Room does not exist'}, status=404)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=403)


@login_required
def new_friend_request(request):
    user = models.User.objects.get(name=request.session['user'])
    incorrect_username = 0
    error = 0

    if request.method == 'POST':
        selected_username = request.POST.get('selected_user')

        try:
            to_user = models.User.objects.get(name=selected_username)
        except models.User.DoesNotExist:
            incorrect_username = 1

        else:
            if models.FriendRequest.objects.filter(from_user=user, to_user=to_user).exists():
                models.FriendRequest.objects.get(from_user=user, to_user=to_user).delete()
            
            try:
                friend_request_object = models.FriendRequest.objects.create(
                    from_user=user,
                    to_user=to_user
                )
                friend_request_object.save()
                return redirect('user_chats')

            except Exception as e:
                error = str(e)

    context = {
        "incorrect_username": incorrect_username,
        "error": error
    }

    return render(request, "chat/create_friend_request.html", context)
