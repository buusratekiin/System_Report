from time import sleep
import random
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor, as_completed



def random_mnconvert(ip,port):
        height=random.randint(1,1000)
        width=random.randint(1,1000)
        quality=random.randint(1,100)
        image=random.randint(1,4)
        return "http://{}:{}/mnconvert(quality={},height={},width={})/test/{}.jpg".format(ip,port,quality,height,width,image)


async def main_convert(ip,port,secs):
        secs = int(int(secs) + 0.5)
        timeout = time.time() + int(secs) 
        while True:  
            headers = {'Host': 'test.nemeroth.com', 'VHost': 'test.nemeroth.com', 'VOrigin': 'test.nemeroth.com', 'VScheme': 'https'}
            async with aiohttp.ClientSession(headers=headers) as session:
                ret = await asyncio.gather(get(random_mnconvert(ip,port), session))
            if time.time() > timeout:
             break
               


async def get(url, session):
    try:
        async with session.get(url=url,timeout=1) as response:
            resp = await response.read()
            print("Successfully got url {} with resp of status {}.".format(url, response.status))
            
    except Exception as e:
        print(e.__dict__)
        print("Unable to get url {} due to {}.".format(url, e.__class__))



def stress_request(secs,ip,port):
    timeout = time.time() + int(secs)  
    while True:
        asyncio.run(main_convert(ip,port,secs))
        if time.time() > timeout:
             break
 
        

    print("ok")
        
       
    

   


   



      
    
    






