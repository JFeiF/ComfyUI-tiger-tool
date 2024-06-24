from PIL import Image
import numpy as np
import torch
import os
import folder_paths
import random
import sys

class ForStart:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "total": ("INT", {"default": 0, "min": 0, "max": 99999}),
                "stop": ("INT", {"default": 1, "min": 1, "max": 999}),
                "i": ("INT", {"default": 0, "min": 0, "max": 99999}),
            }
        }
    RETURN_TYPES = ("INT","INT","INT")
    RETURN_NAMES = ("总数","循环次数","seed")
    FUNCTION = "for_start_fun"

    CATEGORY = "🐅 tiger tool/计次循环"

    def for_start_fun(self,total,stop,i):
        random.seed(i)
        return (total,i,random.randint(0,sys.maxsize),)

NODE_CLASS_MAPPINGS = {
    "ForStart": ForStart
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "ForStart": "计次循环首"
}


from PIL import Image
import numpy as np
import requests
import json
from .utils.uitls import AlwaysEqualProxy


class ForEnd:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        
        return {
            "required": {
                "total": ("INT", {"forceInput": True}),
                "i": ("INT",{"forceInput": True}),
                "port": ("INT", {"default": 8188, "min": 1, "max": 99999}),
                "obj": (AlwaysEqualProxy("*"),),
            },
        }
    RETURN_TYPES = ()
    FUNCTION = "for_end_fun"
    OUTPUT_NODE = True

    CATEGORY = "🐅 tiger tool/计次循环"

    def for_end_fun(self,total,i,port,obj):
        
        r = requests.get("http://127.0.0.1:"+str(port)+"/queue")
        result = r.text
        #print(result)
        data = json.loads(result)
        #rdata=data[list(data.keys())[0]]
        rdata=data['queue_running'][0] if len(data['queue_running'])>0 else []
        index=0
        if len(rdata)>0:
            pdata=json.loads('{}')
            pdata['client_id']=rdata[3]['client_id']
            pdata['extra_data']={'extra_pnginfo':rdata[3]['extra_pnginfo']}
            pdata['prompt']=rdata[2]
            for key in list(pdata['prompt'].keys()):
                if pdata['prompt'][key]['class_type']=='ForStart':
                    index=i//pdata['prompt'][key]['inputs']['stop']
                    i=i+pdata['prompt'][key]['inputs']['stop']
                    pdata['prompt'][key]['inputs']['i']=i
                    break
            if i>=total:
                return { "ui": { "text":'循环结束' } }
            r = requests.post("http://127.0.0.1:"+str(port)+"/prompt",json=pdata)
            result = r.text

        return { "ui": { "text":"第"+str(index+1)+"次循环结果："+result} }

NODE_CLASS_MAPPINGS = {
    "ForEnd": ForEnd
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ForEnd": "计次循环尾"
}


# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import json
import urllib.error
import urllib.parse
import urllib.request
from zhipuai import ZhipuAI


Niu_url = 'http://api.niutrans.com/NiuTransServer/translation?'
json_file = "apikeys.json"

def get_ext_dir(subpath=None, mkdir=False):
    dir = os.path.dirname(__file__)
    if subpath is not None:
        dir = os.path.join(dir, subpath)
    dir = os.path.abspath(dir)
    if mkdir and not os.path.exists(dir):
        os.makedirs(dir)
    return dir

# 小牛翻译
def niu_Translation(text,language,json_file,Niu_url):
    json_file = get_ext_dir(json_file)
    with open(json_file, 'r', encoding='utf-8') as file:
        keys = json.load(file)
        niu_apikey = keys.get('NiutransApikey')
        # print(niu_apikey)
    if language == "en":
        tgt_lan = "zh"
        data = {"from": tgt_lan, "to": language, "apikey": niu_apikey, "src_text": text}
        data_en = urllib.parse.urlencode(data)
        req = Niu_url + "&" + data_en
        res = urllib.request.urlopen(req)
        res = res.read()
        res_dict = json.loads(res)
        if "tgt_text" in res_dict:
            result = res_dict['tgt_text']
        else:
            result = res
        return result
    elif language == "zh":
        tgt_lan = "en"
        data = {"from": tgt_lan, "to": language, "apikey": niu_apikey, "src_text": text}
        data_en = urllib.parse.urlencode(data)
        req = Niu_url + "&" + data_en
        res = urllib.request.urlopen(req)
        res = res.read()
        res_dict = json.loads(res)
        if "tgt_text" in res_dict:
            result = res_dict['tgt_text']
        else:
            result = res
        return result
    
# 智谱清言
def zhipu_Translation(text,json_file):
    json_file = get_ext_dir(json_file)
    with open(json_file, 'r', encoding='utf-8') as file:
        keys = json.load(file)
        zhi_apikey = keys.get('ZhipuApikey')
        # print(zhi_apikey)
    client = ZhipuAI(api_key=zhi_apikey) # 请填写您自己的APIKey
    response = client.chat.completions.create(
        model="glm-3-turbo",  # 填写需要调用的模型名称
        messages=[
            {"role": "system", "content": "你是一个中英文翻译工具，你要做的就是严格按照文本格式将单词或句子由英文翻译成中文，直接输出翻译结果，注意每个逗号分开都是独立的单词，需要分开独立翻译，保留数字不进行翻译、不输出任何多余信息,不需要输出任何解释。"},
            {"role": "user", "content": text},
        ],
        stream=False,
        )
    return (response.choices[0].message.content)



class AiTranslation:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {
                "text": ("STRING", {
                    "multiline": True, #True if you want the field to look like the one on the ClipTextEncode node
                    "default": "翻译文本"
                }),
                "api": (["智谱清言", "小牛翻译"],),
                "language": (["en", "zh"],),

            },
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "TransferAiTranslation"

    OUTPUT_NODE = True

    CATEGORY = "🐅 tiger tool"

    def TransferAiTranslation(self, api, language, text):
        if api == "智谱清言":
            text = zhipu_Translation(text, json_file)
        elif api == "小牛翻译":
            text = niu_Translation(text, language, json_file, Niu_url)
        return (text,)




def zhipu(system_prompt,user_prompt,top_p,temperature,max_tokens,model,json_file):
    json_file = get_ext_dir(json_file)
    with open(json_file, 'r', encoding='utf-8') as file:
        keys = json.load(file)
        zhi_apikey = keys.get('ZhipuApikey')
    client = ZhipuAI(api_key=zhi_apikey)
    response = client.chat.completions.create(
    model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        top_p= top_p,
        temperature= temperature,
        max_tokens= max_tokens,
        tools = [{"type":"web_search","web_search":{"enable":False,"search_result":False}}],
        stream=False,
    )
    return (response.choices[0].message.content)
class zhipuqingyan:

    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": {

                "system_prompt": ("STRING", {
                    "multiline": True, 
                    "default": "你是一个乐于解答各种问题的助手，你的任务是为用户提供专业、准确、有见地的建议。"
                }),
                "user_prompt": ("STRING", {
                    "multiline": True, 
                    "default": "你是什么？"
                }),
                "top_p": ("FLOAT", { "default": 0.70,"min": 0.0,"max": 1.0,"step": 0.01,"round": 0.01,"display": "number"}),
                "temperature": ("FLOAT", { "default": 0.95,"min": 0.0,"max": 1.0,"step": 0.01,"round": 0.01,"display": "number"}),
                "max_tokens": ("INT", {"default": 512,"min": 0, "max": 8192,"step": 1,"display": "number"}),

                "model": (["glm-3-turbo", "glm-4-flash"],),
            },
        }


    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    FUNCTION = "Apply_zhipu"

    OUTPUT_NODE = True

    CATEGORY = "🐅 tiger tool"

    def Apply_zhipu(self,system_prompt,user_prompt,top_p,temperature,max_tokens,model):
        text = zhipu(system_prompt,user_prompt,top_p,temperature,max_tokens,model,json_file)
        return (text,)


NODE_CLASS_MAPPINGS = {
    "ForStart": ForStart,
    "ForEnd": ForEnd,
    "AiTranslation": AiTranslation,
    "zhipuqingyan": zhipuqingyan,
 }

NODE_DISPLAY_NAME_MAPPINGS = {
    "ForStart": "计次循环首",
    "ForEnd": "计次循环尾",
    "AiTranslation": "智能翻译",
    "zhipuqingyan": "智谱清言",
 }
