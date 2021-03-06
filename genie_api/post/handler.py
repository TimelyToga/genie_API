import json
from django.db import transaction
from genie_api.common.json_shit import require_json_args, JsonResponseBadRequest, JsonResponse
from genie_api.common.decorators import require_session
from genie_api.appuser.models import User, Session
from genie_api.post.models import Post

from genie_api.common.ids import generate


# Create your views here.
@require_session
@require_json_args('content')
def create(request):
    content = request.json['content']
    user = Session.user_from_sid(request.json['sid'])

    if not user:
        return JsonResponseBadRequest({'success': False})

    with transaction.atomic():
        post = Post(content=content)
        post.created_by = user
        post.id = generate(Post, 18, 'numeric')
        post.save()

    return JsonResponse({'post_id': post.id, 'poster': post.user_set})

def all(request):
    all_posts = Post.objects.all()
    a = []
    for b in all_posts:
        a.append(b.get_as_data())
    return JsonResponse(a)