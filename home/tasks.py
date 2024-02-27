from smtplib import SMTP
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from .models import Input
from django_q.tasks import async_task, schedule
from .models import Input


def send_email_task():
    try:
        five_days_ago = timezone.now() - timedelta(days=5)
        inputs = Input.objects.filter(datetime__gte=five_days_ago)
         
        content2 = ""
        for input_item in inputs:
            content2+="<li>"
            content2 += f" {input_item.input_text}"

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
             <div style="margin-top: 5px;color: black; font-size: 9px;">
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
        
    except Exception as e:
        print("Hata oluştu!\n{0}".format(e))

            
        