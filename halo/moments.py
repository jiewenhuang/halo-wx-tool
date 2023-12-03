import requests
import json
import os
# 保存瞬时的文本内容
def set_moments_text(user_id, content):
    with open(f"{user_id}_temp.json", "w") as file:
        data = {
                  "spec": {
                    "content": {
                      "raw": f"<p>{content}</p>",
                      "html": f"<p>{content}</p>",
                      "medium": [

                      ]
                    },
                    "releaseTime": "",
                    "owner": "",
                    "visible": "PUBLIC",
                    "tags": [

                    ]
                  },
                  "metadata": {
                    "generateName": "moment-"
                  },
                  "kind": "Moment",
                  "apiVersion": "moment.halo.run/v1alpha1"
                }
        json.dump(data, file)
        return True
#     获取瞬时添加图片
def set_moments_photos(user_id, photos_url):
    with open(f"{user_id}_temp.json", "r") as file:
        data = json.load(file)
        print(data)
        data['spec']["content"]["medium"].append({
            "type": "PHOTO",
            "url": photos_url,  # 图片 URL
            "originType": "image/webp"
        })
    with open(f"{user_id}_temp.json", "w") as file:
        json.dump(data, file)
        print('图片添加成功')
        return True
#     发布瞬时
def post_moments(user_url, user_id,user_token):
    post_moments_api = f'{user_url}/apis/api.plugin.halo.run/v1alpha1/plugins/PluginMoments/moments'
    with open(f"{user_id}_temp.json", "r") as file:
        payload = file.read()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer '
                             f'{user_token}',
        }
        response = requests.request("POST", url=post_moments_api, headers=headers, data=payload)
        if response.status_code == 200:
            print('发布成功')
            # 删除临时文件
            os.remove(f"{user_id}_temp.json")
            return True
        else:
            print(f'发布失败，错误代码：{response.status_code}')
            return False
