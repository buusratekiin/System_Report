from multiprocessing import context
from .models import Input
from django.shortcuts import render, redirect
from admin_datta.forms import RegistrationForm, LoginForm, UserPasswordChangeForm, UserPasswordResetForm, UserSetPasswordForm
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.views.generic import CreateView
from django.contrib.auth import logout
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import socket,random,aiohttp,requests
from django.http import StreamingHttpResponse
from django.utils.decorators import method_decorator
from home.models import WarnerResponse
from django.db.models import Sum
from django_q.tasks import async_task,result,Task
from django_q.monitor import Stat
from django_q.brokers import get_broker
from django.http import JsonResponse
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from wand.image import Image
from core.settings import MEDIA_ROOT,WATERMARK_ROOT
import os
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render
from django.contrib.auth import get_user 
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from smtplib import SMTP
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser



class Watermark(View):
   def __init__(self):
      self.context = {
        'segment': 'watermark'
       }
      pass
   def get(self,request):
       
       return render(request, "pages/watermark.html", self.context)
      
      
   def post(self,request):
       if request.FILES and request.FILES['file']:
            file = request.FILES['file']
            if file.name.endswith('.png') or file.name.endswith('.jpg') or file.name.endswith('.jpeg') or file.name.endswith('.gif') or file.name.endswith('.webp') or file.name.endswith('avif'):  
              imageName = '{}'.format(random.randint(10000, 99999))
              file_name = imageName
              file_content = ContentFile(file.read())
              default_storage.save(file_name, file_content)
              context = {'message': f'{file_name} file upload ok.','file_name':file_name, 'segment': 'watermark'}
              return render(request, 'pages/watermark.html', context)
            else:
               context = {'error': 'untype media', 'segment': 'watermark'}
               return render(request, 'pages/watermark.html', context)
                
       else:
            context = {'error': 'file cannot upload', 'segment': 'watermark'}
            return render(request, 'pages/watermark.html', context)
   
   def waterconvert(request):
    file_name = str(request.POST.getlist('file_name')[0])
    input_file = MEDIA_ROOT + file_name
    output_file = MEDIA_ROOT + 'watermark-{}'.format(file_name)
    watermark_file = WATERMARK_ROOT + 'medianova.png' # yarın dışardan gelmesi beklenirse kolaylık olsun
    with Image(filename =input_file) as image:
        with Image(filename =watermark_file) as water:
            
            water_width = int(image.width / 1.8)
            water_height = int(image.height / 2.8)
            
            water.resize(water_width, water_height)
           
            with image.clone() as watermark:
                x = (image.width - water.width) // 2
                y = (image.height - water.height) // 2
                watermark.watermark(water, 0.5, x, y)
                watermark.save(filename =output_file)
    return JsonResponse({'watermark_file': "assets/images/convert/watermark-{}".format(file_name),"ok":"ok" }, safe=False)

def get_size(path):
        size = os.path.getsize(path)
        if size < 1024:
            return f"{size} bytes"
        elif size < pow(1024,2):
            return f"{round(size/1024, 2)} KB"
        elif size < pow(1024,3):
            return f"{round(size/(pow(1024,2)), 2)} MB"
        elif size < pow(1024,4):
            return f"{round(size/(pow(1024,3)), 2)} GB"


class Bt(View):
   def __init__(self):
       self.context = {
        'segment': 'bt',
       }

   def get(self,request):
       five_days_ago = timezone.now() - timedelta(days=5)
       inputs_last_5_days = Input.objects.filter(datetime__gte=five_days_ago)
       self.context = {
        'inputs': inputs_last_5_days,
       }
           
       return render(request, "pages/bt.html", self.context)

   @staticmethod
   def send(request):
        try:
            subject = "VMD Sistem Haftalık Raporu "
            #message = "sa"
            #content = "Subject: {0}\n\n{1}".format(subject, message)
            #content = "Subject: {0}\n\n".format(subject)
            content2 = request.POST.get('content', '')

            mail = smtplib.SMTP(host='posta.turksat.com.tr', port=587)

            mail.ehlo()
            mail.starttls()
            mail.ehlo()
            mail.login('vmyd-rapor', 'OQxRkZX0CgO9uwRRJosR')

            html = """
            <html>
    <head>
    </head>
    <body style="font-family: Arial, sans-serif;background-color: #f0f0f0;">
        <div style="max-width: 800px; margin: 20px auto;padding: 20px;background-color: #fff;border-radius: 10px;box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);" class="container">
            <img style=" max-width: 20%;height: auto;border-radius: 5px;margin-bottom: 20px;" src="https://www.turksat.com.tr/sites/default/files/2020-04/turksat_logotip_cmyk-01.png" alt="Turksat Logo">
            
            <p >Sayın Yetkili;</p>
            <p>Veri Merkezi Haftalık Raporu aşağıda listelenmiştir.</p>
            
            <div style="margin-top: 20px;color: black;line-height: 1.6;">
                {0}
            </div>
            
            <p>İyi çalışmalar dilerim.</p>
            <p>Saygılarımla.</p>
            
            <div style="font-style: italic;"></div>
             <div style="margin-top: 5px;color: black;font-weight: bold; font-size: 9px;">
                <p>***SORUMLULUK REDDİ BEYANI: Bu rapor sadece bilgi amaçlıdır. Veri doğruluğu konusunda herhangi bir garanti verilmemektedir. Şirketimiz, rapordaki bilgilerin kullanılmasından kaynaklanan herhangi bir sorumluluğu kabul etmez. Lütfen raporu dikkatlice inceleyin ve gerektiğinde uzman bir danışmana başvurun.***</p>
            </div>
        </div>
    </body>
</html>
            """.format(content2)

            msg = MIMEMultipart()
            msg.attach(MIMEText(html, 'html'))
            msg['Subject'] = 'VMYD Sistem Haftalık Raporu '

            mail.sendmail('vmyd-rapor@turksat.com.tr', 'busratekin73@gmail.com', msg.as_string())
            print("Mail gönderildi")
            five_days_ago = timezone.now() - timedelta(days=5)
            Input.objects.filter(datetime__gte=five_days_ago).update(send=True)
            mail.quit()
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            print("Hata oluştu!\n{0}".format(e))
            return JsonResponse({'status': 'error', 'message': str(e)})
   
  

   def post(self,request):
      if request.method == 'POST':
        input_text = request.POST.get('input_text', '')
        username = request.user.username
        #print(input_text)
        #print(username)
        if input_text:
            #Input.objects.create(input_text=input_text)
            Input.objects.create(input_text=input_text, user=username)
            
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Input is empty'})
      else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
      
   def delete(self, request, input_id):
        try:
            input_obj = Input.objects.get(pk=input_id)
            input_obj.delete()
            return JsonResponse({'status': 'success'})
        except Input.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Input does not exist'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error: {str(e)}'})
      
   def test(request):
    username = None
    if request.user.is_authenticated():
        username = request.user.username
        Input.user=username

   


class Avif(View):
   def __init__(self):
       self.context = {
        'segment': 'avif',
       }
        
   def convert(request):
           
            file_name = str(request.POST.getlist('file_name')[0])
            input_file = MEDIA_ROOT + file_name
            output_file_Avif = "{}.avif".format(input_file)
            output_file_Webp = "{}.webp".format(input_file)
            with Image(filename=input_file) as img:
                img.format = 'avif'
                #img.compression_quality = 80
                img.save(filename=output_file_Avif)
            with Image(filename=input_file) as img:
                img.format = 'webp'
                img.compression_quality = 80 
                img.save(filename=output_file_Webp)
            webp_size = get_size(output_file_Webp)
            avif_size = get_size(output_file_Avif)
            origin_size = get_size(input_file)  
            return JsonResponse({'origin_file': "assets/images/convert/{}".format(file_name),'avif_file':"assets/images/convert/{}.avif".format(file_name),'webp_file':"assets/images/convert/{}.webp".format(file_name),"origin_size":origin_size,"webp_size":webp_size,"avif_size": avif_size,"ok":"ok" }, safe=False)
  
   def get(self,request):
           
     return render(request, "pages/avif.html", self.context)
   
   def post(self,request):
      if request.FILES and request.FILES['file']:
            file = request.FILES['file']
            if file.name.endswith('.png') or file.name.endswith('.jpg') or file.name.endswith('.jpeg') or file.name.endswith('.gif') or file.name.endswith('.webp') or file.name.endswith('avif'):  
              imageName = '{}'.format(random.randint(10000, 99999))
              file_name = imageName
              file_content = ContentFile(file.read())
              default_storage.save(file_name, file_content)
              context = {'message': f'{file_name} file upload ok.','file_name':file_name, 'segment': 'avif'}
              return render(request, 'pages/avif.html', context)
            else:
               context = {'error': 'untype media', 'segment': 'avif'}
               return render(request, 'pages/avif.html', context)
                
      else:
            context = {'error': 'file cannot upload', 'segment': 'avif'}
            return render(request, 'pages/avif.html', context)
    
    
   
     



class Index(View):
   def __init__(self):
      self.warner_resp = WarnerResponse.objects.all()
      self.warner_200 = WarnerResponse.objects.aggregate(Sum('status_code_200'))
      self.warner_200_ex = WarnerResponse.objects.aggregate(Sum('external_status_code_200'))
      self.warner_count = WarnerResponse.objects.count()
   
   def get(self,request):
    
       context = {
        'segment': 'index',
        "ex200" : self.warner_200_ex['external_status_code_200__sum'],
        "resp200" : self.warner_200['status_code_200__sum'],
        "warner_count": self.warner_count,
        "warner_obj" :  self.warner_resp
                        
       }
     
       return render(request, "pages/index.html", context)






class Stress(SuperuserRequiredMixin,View):
  def __init__(self):
    pass
 
     
  def get(self,request):
   context = {
        'parent': 'Stress',
        'segment': 'stress'
      }
   
   return render(request, "pages/stress.html", context)
  
  def post(self,request):
     context = {
        'parent': 'Stress',
        'segment': 'stress'
      }
     gpu_ip_Address = request.POST.get("ip")
     gpu_port = request.POST.get("port")
     gpu_time = request.POST.get("time")
    
     broker = get_broker()
     if self.ip_port_control(gpu_ip_Address,gpu_port):
        for _ in range(8):
          async_task("home.django_cluster.stress_request",int(gpu_time),gpu_ip_Address,gpu_port,broker=broker)
        messages.success(request, "Stress is working" )
        return JsonResponse({'status':"success"}, safe=False)  
     messages.warning(request, 'Check ip and port number') 
     return JsonResponse({'status':"fail"}, safe=False)  
  
  def stress_status(request):
   success = Task.objects.get_queryset().filter(success=True).count()
   fail =  Task.objects.get_queryset().filter(success=False).count()

   return JsonResponse({'success':success,'fail':fail}, safe=False)
  
     
     
  def ip_port_control(self,ip,port):
    try:
      connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      result = connection.connect_ex((
        ip,
        int(port)
      ))
      if result == 0:
        return True
      else:
        return False
    except:
      return False


# Components
@login_required(login_url='/accounts/login/')
def bc_button(request):
  context = {
    'parent': 'basic_components',
    'segment': 'button'
  }
  return render(request, "pages/components/bc_button.html", context)

@login_required(login_url='/accounts/login/')
def bc_badges(request):
  context = {
    'parent': 'basic_components',
    'segment': 'badges'
  }
  return render(request, "pages/components/bc_badges.html", context)

@login_required(login_url='/accounts/login/')
def bc_breadcrumb_pagination(request):
  context = {
    'parent': 'basic_components',
    'segment': 'breadcrumbs_&_pagination'
  }
  return render(request, "pages/components/bc_breadcrumb-pagination.html", context)

@login_required(login_url='/accounts/login/')
def bc_collapse(request):
  context = {
    'parent': 'basic_components',
    'segment': 'collapse'
  }
  return render(request, "pages/components/bc_collapse.html", context)

@login_required(login_url='/accounts/login/')
def bc_tabs(request):
  context = {
    'parent': 'basic_components',
    'segment': 'navs_&_tabs'
  }
  return render(request, "pages/components/bc_tabs.html", context)

@login_required(login_url='/accounts/login/')
def bc_typography(request):
  context = {
    'parent': 'basic_components',
    'segment': 'typography'
  }
  return render(request, "pages/components/bc_typography.html", context)

@login_required(login_url='/accounts/login/')
def icon_feather(request):
  context = {
    'parent': 'basic_components',
    'segment': 'feather_icon'
  }
  return render(request, "pages/components/icon-feather.html", context)







class Warner(SuperuserRequiredMixin,View):
  login_required = True
  redirect_field_name = '/accounts/login/'

  def __init__(self):
    self.ip = None
    self.port = None
    self.user = None

  
  def get(self,request):
    context = {
    'parent': 'warner',
    'segment': 'gpu'
    }
    self.user = request.user
    return render(request, 'pages/warner.html',context)
  
          
  def  response_request(self):
      resp = None
      try:
          headers = {'Host': 'erelbi.github.io', 'VHost': 'erelbi.github.io', 'VOrigin': 'erelbi.github.io', 'VScheme': 'https'}
          i=0
          resp200 = 0
          exresp200 = 0

          while i < 100:
                resp = requests.get(Warner.random_request(self),headers=headers)
                i += 1 
                
                if resp.status_code == 200:
                    resp200 += 1
                else:
                    exresp200 += 1
              
                yield "{} status code : {} \n".format(resp.url,resp.status_code)
          a = WarnerResponse.objects.create(ip=self.ip,port=self.port,user=self.user,status_code_200=resp200,external_status_code_200=exresp200)
          print(a)
      except Exception as err:
           return "{}".format(err)
      finally:
         resp.close()
          
  
  def ip_port_control(self,ip,port):
    try:
      connection = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
      result = connection.connect_ex((
        ip,
        int(port)
      ))
      if result == 0:
        return True
      else:
        return False
    except:
      return False

  
  def random_request(self):
      height=random.randint(100,1000)
      width=random.randint(100,1000)
      quality=random.randint(10,100)
      return "http://{}:{}/mnconvert(quality={},height={},width={})/cdn-test/jpg/1mb.jpg".format(self.ip,self.port,quality,height,width)

  
  
  def warner_request(self,ip,port):
      self.ip = ip
      self.port = port
      if  Warner.ip_port_control(self,ip=self.ip,port=self.port):
        stream = Warner.response_request(self)
        response = StreamingHttpResponse(stream, status=200, content_type='text/event-stream')
        response['Cache-Control'] = 'no-cache'
        return response
      else:
           response = StreamingHttpResponse("ip and port check it!", status=400, content_type='text/event-stream')
           response['Cache-Control'] = 'no-cache'
           return response
    


    
 
  



@login_required(login_url='/accounts/login/')
def basic_tables(request):
  context = {
    'parent': 'tables',
    'segment': 'basic_tables'
  }
  return render(request, 'pages/tbl_bootstrap.html', context)

# Chart and Maps
@login_required(login_url='/accounts/login/')
def morris_chart(request):
  context = {
    'parent': 'chart',
    'segment': 'morris_chart'
  }
  return render(request, 'pages/chart-morris.html', context)

@login_required(login_url='/accounts/login/')
def google_maps(request):
  context = {
    'parent': 'maps',
    'segment': 'google_maps'
  }
  return render(request, 'pages/map-google.html', context)

# Authentication
class UserRegistrationView(CreateView):
  template_name = 'accounts/auth-signup.html'
  form_class = RegistrationForm
  success_url = '/accounts/login/'

class UserLoginView(LoginView):
  template_name = 'accounts/auth-signin.html'
  form_class = LoginForm

class UserPasswordResetView(PasswordResetView):
  template_name = 'accounts/auth-reset-password.html'
  form_class = UserPasswordResetForm

class UserPasswrodResetConfirmView(PasswordResetConfirmView):
  template_name = 'accounts/auth-password-reset-confirm.html'
  form_class = UserSetPasswordForm

class UserPasswordChangeView(PasswordChangeView):
  template_name = 'accounts/auth-change-password.html'
  form_class = UserPasswordChangeForm

def logout_view(request):
  logout(request)
  return redirect('/accounts/login/')

@login_required(login_url='/accounts/login/')
def profile(request):
  context = {
    'segment': 'profile',
  }
  return render(request, 'pages/profile.html', context)

@login_required(login_url='/accounts/login/')
def sample_page(request):
  context = {
    'segment': 'sample_page',
  }
  return render(request, 'pages/sample-page.html', context)



