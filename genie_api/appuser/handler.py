from django.shortcuts import render

from genie_api.common.json_shit import require_json_args, JsonResponse, JsonResponseBadRequest

# Create your views here.
@require_json_args('guid')
def create_user(request):
    guid = request.json['guid']
    return JsonResponse(guid)