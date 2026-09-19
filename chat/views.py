from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from .services.groq_service import groq_service
from .models import Conversation, Message, LunaImagePrompt

from tracker.templatetags.markdown_extras import markdown_filter


@login_required
def conversation_list(request):
    """
    Displays all conversations.

    If there are no conversations, the template can show:
    'Create your conversation'
    """
    request.session["private_access"] = False

    conversations = Conversation.objects.all()

    return render(
        request,
        "chat/conversation_list.html",
        {
            "conversations": conversations,
        },
    )


@require_POST
@login_required
def conversation_create(request):
    """
    Create a new conversation using a custom title.
    """
    title = request.POST.get(
        "title",
        ""
    ).strip()

    if not title:
        title = "New Chat"

    conversation = Conversation.objects.create(
        title=title
    )

    return redirect(
        "chat:conversation_detail",
        slug=conversation.slug,
    )


@login_required
def conversation_detail(request, slug):
    """
    Display the chat page for a conversation.
    """
    conversation = get_object_or_404(
        Conversation,
        slug=slug,
    )

    conversations = Conversation.objects.all()

    return render(
        request,
        "chat/chat.html",
        {
            "conversation": conversation,
            "conversations": conversations,
            "messages": conversation.messages.all(),
        },
    )


@require_POST
@login_required
def conversation_update(request, slug):
    """
    Rename an existing conversation.
    """
    conversation = get_object_or_404(
        Conversation,
        slug=slug,
    )

    title = request.POST.get(
        "title",
        ""
    ).strip()

    if title:
        conversation.title = title
        conversation.save()

    return redirect(
        "chat:conversation_detail",
        slug=conversation.slug,
    )


@login_required
def conversation_delete_confirm(request, slug):
    """
    Display confirmation page before deleting a conversation.
    """
    conversation = get_object_or_404(
        Conversation,
        slug=slug,
    )

    return render(
        request,
        "chat/conversation_delete_confirm.html",
        {
            "conversation": conversation,
        },
    )


@require_POST
@login_required
def conversation_delete(request, slug):
    """
    Delete a conversation and all associated messages.
    """
    conversation = get_object_or_404(
        Conversation,
        slug=slug,
    )

    conversation.delete()

    return redirect(
        "chat:conversation_list"
    )


@require_POST
@login_required
def chat_message(request, slug):

    # -----------------------------------------
    # USER NAME
    # -----------------------------------------

    user_name = request.user.get_full_name().strip()

    if not user_name:
        user_name = request.user.username


    # -----------------------------------------
    # GET CONVERSATION
    # -----------------------------------------

    conversation = get_object_or_404(
        Conversation,
        slug=slug,
    )


    # -----------------------------------------
    # GET USER MESSAGE
    # -----------------------------------------

    user_content = request.POST.get(
        "message",
        ""
    ).strip()


    if not user_content:

        return JsonResponse(
            {
                "error": "Message cannot be empty."
            },
            status=400,
        )


    # -----------------------------------------
    # SAVE USER MESSAGE
    # -----------------------------------------

    Message.objects.create(
        conversation=conversation,
        role="user",
        content=user_content,
    )


    # -----------------------------------------
    # BUILD CONVERSATION HISTORY
    # -----------------------------------------

    db_messages = conversation.messages.all()

    messages = [
        {
            "role": message.role,
            "content": message.content,
        }
        for message in db_messages
    ]


    try:

        # -----------------------------------------
        # GENERATE LUNA RESPONSE
        # -----------------------------------------

        result = groq_service.generate(
            messages,
            user_name=user_name,
        )


        assistant_content = result.get(
            "text",
            ""
        )


        # -----------------------------------------
        # SAVE ASSISTANT MESSAGE
        # -----------------------------------------

        if assistant_content.strip():

            Message.objects.create(
                conversation=conversation,
                role="assistant",
                content=assistant_content,
            )

            conversation.save()


        # -----------------------------------------
        # RESPONSE
        # -----------------------------------------

        return JsonResponse(
            {
                "response": assistant_content,

                "html": markdown_filter(
                    assistant_content
                ),
            }
        )


    except Exception as exc:

        print(
            f"Groq generation error: {exc}"
        )

        return JsonResponse(
            {
                "error": "Error generating response."
            },
            status=500,
        )
    
@login_required
def luna_images(request):
    # 🔒 Private access required
    user_profile = getattr(request.user, "userprofile", None)

    if user_profile is None or not user_profile.special_privilege_password:
        django_messages.error(request, "You do not have access to private images.")
        return redirect("tracker:task_list")

    if not request.session.get("private_access"):
        return redirect("private_access", "chat:luna_images")

    images = LunaImagePrompt.objects.filter(
        is_active=True
    ).order_by("?")

    return render(request, "chat/luna_images.html", {
        "images": images,
    })