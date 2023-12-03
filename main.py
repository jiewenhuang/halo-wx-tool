import werobot
import threading
from halo import photos
from halo import moments

robot = werobot.WeRoBot(token='')
robot.config["APP_ID"] = ""
robot.config["APP_SECRET"] = ""
# 定时一个半钟执行
access_token = None
def update_token():
    try:
        access_token = robot.client.get_access_token()
        print("Token updated")
    except Exception as e:
        print(f"Error updating token: {e}")

def start_timer():
    threading.Timer(5400, start_timer).start()  # 设置定时器
    update_token()

start_timer()

@robot.text
def hello(message, session):
    user_id = message.source
    print(message.content)
    if message.content == '菜单':
        return f'【绑定账号】绑定账号\n【重置】重置账号\n【瞬时】发布瞬时\n【发布】完成发布\n【菜单】查看菜单'
    # 重置用户信息
    if message.content == '重置':
        session[user_id + '_url_setting'] = False
        session[user_id + '_token_setting'] = False
        session[user_id + '_url'] = ''
        session[user_id + '_token'] = ''
        session[user_id] = ''
        session[user_id + '_moments_isRunning'] = False
        session[user_id + '_moments_photos_isRunning'] = False
        session[user_id + '_photos_isRunning'] = False

        return f'重置成功'
    if message.content == '重置发布':
        session[user_id + '_moments_isRunning'] = False
        session[user_id + '_moments_photos_isRunning'] = False
        session[user_id + '_photos_isRunning'] = False
        return f'重置成功'
    # 查看url
    if message.content == '信息':
        if user_id in session and session[user_id] == user_id:
            return f'你的网站地址：{session[user_id + "_url"]}'
        else:
            return f'你还没有绑定账号，请回复【绑定账号】进行绑定'
    # 绑定账号
    if message.content == '绑定账号':
        if user_id in session and session[user_id] == user_id:
            return f'你已经绑定账号'
        else:
            if user_id + '_url_setting' not in session or not session[user_id + '_url_setting']:
                session[user_id + '_url_setting'] = True
                return f'正在绑定URL：请输入网站完整地址例如：https://www.jiewen.run'
    if session[user_id + '_url_setting']:
        session[user_id + '_url_setting'] = False
        # 去除链接末尾反斜杠
        if message.content[-1] == '/':
            message.content = message.content[:-1]
        session[user_id + '_url'] = message.content
        print(session[user_id + '_url'])
        session[user_id + '_token_setting'] = True
        return f'URL保存成功，请输入api token'
    if session[user_id + '_token_setting']:
        session[user_id + '_token_setting'] = False
        session[user_id + '_token'] = message.content
        print(session[user_id + '_token'])
        session[user_id] = user_id
        return f'绑定成功'
    # 发布瞬时
    if message.content == '瞬时':
        if user_id not in session or session[user_id] != user_id:
            return '您还没有绑定信息，请回复【绑定账号】进行绑定'
        session[user_id + '_moments_isRunning'] = True
        return f'请输入瞬时内容'
    if session.get(user_id + '_moments_isRunning', False):
        session[user_id + '_moments_isRunning'] = False
        r_set_moment_text = moments.set_moments_text(user_id, message.content)
        print(r_set_moment_text)
        if r_set_moment_text:
            session[user_id + '_moments_photos_isRunning'] = True
            return f'文本保存成功，配图请直接发送图片，无需则回复【发布】完成发布'
        else:
            return f'文本保存成功'
    if message.content == '发布':
        if user_id not in session or session[user_id] != user_id:
            return '您还没有绑定信息，请回复【绑定账号】进行绑定'
        else:
            if session[user_id + '_moments_photos_isRunning']:
                r_post_moments = moments.post_moments(session[user_id + '_url'], user_id, session[user_id + '_token'])
                if r_post_moments:
                    session[user_id + '_moments_photos_isRunning'] = False
                    return f'发布成功'
                else:
                    return f'发布失败'
    #  上传图片
    if session.get(user_id + '_photos_isRunning', False):
        g_n = photos.get_group_name_by_index(session[user_id + '_url'], message.content)
        print(g_n)
        session[user_id + '_photos_isRunning'] = False
        return f'图片上传成功，图片组名称：{g_n}'




@robot.image
def blog(message, session):
    media_id = message.MediaId
    user_id = message.source
    if user_id not in session:
        return '您还没有绑定信息，请回复【绑定账号】进行绑定'

    if user_id in session:
        # if not session[user_id + '_post_isRunning']:
        #     # 使用微信的媒体文件下载接口获取图片
        #     r = photos.upload_photos(access_token, session[user_id + '_url'], media_id ,session[user_id + '_token'])
        #     if r:
        #         session[user_id + '_photos_isRunning'] = True
        #         halo_group_name = photos.get_photos_group(session[user_id + '_url'])
        #         return f'靓仔，图片上传成功.请输入序号选择图库分类：\n{halo_group_name}'
        #     return f'图片失败{r}'
        if session[user_id + '_moments_photos_isRunning']:
            r = photos.upload_photos(access_token, session[user_id + '_url'], media_id ,session[user_id + '_token'])
            print(r)
            if r:
                moments.set_moments_photos(user_id, r)
                return f'图片上传成功,请输入【发布】完成发布'
            return f'图片失败{r}'

# 让服务器监听在 0.0.0.0:80
robot.config['HOST'] = ''
robot.config['PORT'] = 1223
robot.run()
