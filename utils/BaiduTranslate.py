# coding=utf-8

import http.client
import hashlib
import urllib
import random
import json
from time import sleep

class BaiduTranslate():
    def __init__(self , appid , secretKey):
        self.appid = appid
        self.secretKey = secretKey
    
    def translate(self, q_list:list):
        
        httpClient = None
        myurl = 'http://api.fanyi.baidu.com/api/trans/vip/translate'

        fromLang = 'auto' 
        toLang = 'zh'  
        
        q = "\n".join(q_list)
        
        
        salt = random.randint(32768, 65536)
        sign = self.appid + q + str(salt) + self.secretKey
        sign = hashlib.md5(sign.encode()).hexdigest()
        myurl = myurl + '?appid=' + self.appid + '&q=' + urllib.parse.quote(q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign
        
        try:
            httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
            httpClient.request('GET', myurl)

            # response是HTTPResponse对象
            response = httpClient.getresponse()
            result_all = response.read().decode("utf-8")
            result = json.loads(result_all)
            # print(result)

            res_str_list = result.get("trans_result")
            
            out_list = []
            for res in res_str_list:
                res_str = res.get("dst")
                out_list += res_str.split("\n")
                
                
            
            return out_list

        except Exception as e:
            print (e)
        finally:
            if httpClient:
                httpClient.close()
    
    def trans_long_list(self, q_list:list):
        MAX_BYTES = 6000  # 设置最大字节数
        out_list = []
        current_chunk = []
        current_bytes = 0

        for q in q_list:
            q_bytes = len(q.encode('utf-8'))  # 获取当前字符串的字节长度
            if current_bytes + q_bytes <= MAX_BYTES:
                current_chunk.append(q)
                current_bytes += q_bytes
            else:
                # 当前批次已满，先翻译它
                print("translating chunk of size: {} bytes".format(current_bytes))
                out_list += self.translate(current_chunk)
                sleep(2)  # 休眠2秒

                # 开始新批次
                current_chunk = [q]  # 当前字符串开始新批次
                current_bytes = q_bytes

        # 翻译最后一个批次（如果有）
        if current_chunk:
            print("translating final chunk of size: {} bytes".format(current_bytes))
            out_list += self.translate(current_chunk)

        return out_list

    

    
if __name__ == '__main__':
    import os
    script_path = os.path.dirname(os.path.abspath(__file__))
    api_path = os.path.join(script_path, "../data/baidu.api")
    with open(api_path, "r") as f:
        test_list = f.readlines()
        appid = test_list[0].strip()
        secretKey = test_list[1].strip()
    
    test_list = ["hello world", "hello universe", 'hello earth']
    
    translator = BaiduTranslate(appid, secretKey)
    print(translator.translate(test_list))
        
        