import requests


def get_photos_group(user_web_url):
    get_group_api = f'{user_web_url}/apis/api.plugin.halo.run/v1alpha1/plugins/PluginPhotos/photogroups'
    response = requests.get(get_group_api)

    if response.status_code == 200:
        items = response.json()['items']

        # 收集并排序数据
        sorted_items = sorted(items, key=lambda x: x['spec']['displayName'])

        # 构建输出字符串，包括序号
        output = '\n'.join([f"{idx + 1}. {item['spec']['displayName']} ({item['metadata']['name']})"
                            for idx, item in enumerate(sorted_items)])

        return output
    else:
        return f"Error: Unable to fetch data, status code {response.status_code}"


def get_group_name_by_index(user_web_url, index):
    # 获取图片组列表
    get_group_api = f'{user_web_url}/apis/api.plugin.halo.run/v1alpha1/plugins/PluginPhotos/photogroups'
    response = requests.get(get_group_api)

    if response.status_code == 200:
        items = response.json()['items']

        # 确保提供的序号在有效范围内
        if 1 <= index <= len(items):
            # 根据序号获取对应的图片组名称
            selected_item = sorted(items, key=lambda x: x['spec']['displayName'])[index - 1]
            group_name = selected_item['metadata']['name']
            return group_name
        else:
            return "Invalid index. Please provide a valid index."
    else:
        return f"Error: Unable to fetch data, status code {response.status_code}"


def upload_photos(access_token, user_web_url, media_id, user_token):
    media_url = f"https://api.weixin.qq.com/cgi-bin/media/get?access_token={access_token}&media_id={media_id}"
    response = requests.get(media_url, stream=True)

    if response.status_code == 200:
        image_data = response.content

        # 将图片发送到其他API
        upload_api = f"{user_web_url}/apis/api.console.halo.run/v1alpha1/attachments/upload"
        files = {
            'file': ('image.png', image_data, 'image/png'),  # 文件
            'policyName': (None, 'default-policy'),  # 额外的文本字段
            # 可以添加更多字段
        }
        headers = {
            'Authorization': 'Bearer '
                             f'{user_token}',
        }
        upload_response = requests.request("POST", upload_api, headers=headers, files=files)

        if upload_response.status_code == 200:
            print("图片成功上传到其他API")
            # 返回图片地址和名字
            print(upload_response.json()['metadata']['annotations']['storage.halo.run/uri'])
            return upload_response.json()['metadata']['annotations']['storage.halo.run/uri']
        else:
            return False


if __name__ == '__main__':
    get_photos_group('https://www.jiewen.run')
