import requests
import random
class Spider:
    def __init__(self,timeout=5,user_agents=None,proxies=None):
        self.timeout=timeout
        self.running=True
        self.user_agents=user_agents if user_agents else []
        self.proxies=proxies if proxies else []
    def spider(self,url,other,cookies=None,method='GET',return_bytes=False):
        headers={
            'User-Agent':random.choice(self.user_agents) if self.user_agents else None,
            'Cookie':random.choice(cookies) if cookies else None
        }
        proxy=random.choice(self.proxies) if self.proxies else None
        kwargs={
            'url':url,
            'proxies':proxy,
            'headers':headers,
            'timeout':self.timeout
        }
        if method=='GET':
            kwargs['params']=other
        elif method=='POST':
            kwargs['data']=other
        else:
            raise ValueError(f'Unsupported method:{method}')
        try:
            response=requests.request(method,**kwargs)
            response.raise_for_status()
        except requests.Timeout as e:
            print(f'Timeout Error:{e}')
        except requests.exceptions.RequestException as e:
            print(f'Request failed:{e}')
        if not return_bytes:
            return response.text
        else:
            return response.content
