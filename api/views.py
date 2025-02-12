from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from gallery_server.settings import MEDIA_ROOT, BASE_DIR

from datetime import datetime
import os
# Create your views here.

@csrf_exempt
def new_image(request: HttpRequest):
    if request.method == "POST":
        if request.FILES:
            now = datetime.now()
            ano = str(now.year)
            mes = str(now.month)
            dia = str(now.day)
            hora = str(now.hour)
            now = str(now.strftime('%Hhr%Mmin%Ss'))
            _device_uuid = str(request.headers.get('Device-Uuid'))
            ensure_dir_exists('images')
            ensure_dir_exists(os.path.join('images', _device_uuid))
            ensure_dir_exists(os.path.join('images', _device_uuid, ano))
            ensure_dir_exists(os.path.join('images', _device_uuid, ano, mes))
            ensure_dir_exists(os.path.join('images', _device_uuid, ano, mes, dia))
            ensure_dir_exists(os.path.join('images', _device_uuid, ano, mes, dia, hora))
            _file = request.FILES.get('imageFile')
            _file_size_in_Kb = round(_file.size/1024, 2)
            _file_name = os.path.join('images', _device_uuid, ano, mes, dia, hora, f'{now}.jpg')
            
            with open(_file_name, "wb") as destination:
                for chunk in _file.chunks():
                    destination.write(chunk)
            return JsonResponse({
                'status': '201',
                'message': f'file {now}.jpg - {_file_size_in_Kb}Kb created'
            })
    return JsonResponse({
        'status': '204',
        'message': 'file not uploaded.'
    })
    
def images(request:HttpRequest, path:str=None):
    _paths = path.split("/")
    print(path)
    print(_paths)
    # if path:
    content = os.listdir(os.path.join(BASE_DIR, *_paths))
    # else:
    #     content = os.listdir(MEDIA_ROOT)
    # print(content)
    return JsonResponse({'dirs':content})


def ensure_dir_exists(directory:str):
    if not os.path.exists(directory):
        os.mkdir(directory)
