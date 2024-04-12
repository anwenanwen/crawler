import os
import time
import json
import urllib
import pymysql
import requests
from datetime import datetime

def download_image(url, directory, index):
    """下载图片并保存到指定路径，同时返回图片的URL"""
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            filename = f'{directory}/{index}.jpg'
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"已下载: {filename}")
            return url  # 返回图片的URL
        else:
            print(f"下载失败: {url}")
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    return None


def save_image_to_db(keyword, filename, url):
    # 连接数据库配置，根据你的数据库信息修改
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '123456',
        'database': 'anwen',
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    # 建立数据库连接
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            # 创建表（如果尚未存在），此操作可以根据需要移动到脚本的其他部分
            cursor.execute('''  
                CREATE TABLE IF NOT EXISTS images (  
                    id INT AUTO_INCREMENT PRIMARY KEY,  
                    keyword VARCHAR(255) NOT NULL,  
                    image_path VARCHAR(255) NOT NULL,  
                    image_url VARCHAR(255) NOT NULL  
                )  
            ''')
            # 插入图片记录（存储图片路径和URL）
            sql = "INSERT INTO images (keyword, image_path, image_url) VALUES (%s, %s, %s)"
            cursor.execute(sql, (keyword, filename, url))
            # 提交事务
            connection.commit()
    finally:
        connection.close()  # 关闭数据库连接

def create_directory_with_keyword(keyword):
    """使用关键字和日期创建新文件夹"""
    current_time = datetime.now().strftime('%Y%m%d')
    new_directory_name = f'{keyword}_{current_time}'
    new_directory = f'images/{new_directory_name}'
    if not os.path.exists(new_directory):
        os.makedirs(new_directory)
    return new_directory

def get_image_data(keyword, headers, start):
    url = (
        'https://image.baidu.com/search/acjson?tn=resultjson_com&'  
        f'logid=9017738387423771510&ipn=rj&ct=201326592&is=&fp=result&fr=&word={urllib.parse.quote(keyword)}'  
        f'&cg=girl&queryWord={urllib.parse.quote(keyword)}&cl=2&lm=-1&ie=utf-8&oe=utf-8&adpicid=&st=-1&z='  
        '&ic=0&hd=&latest=&copyright=&s=&se=&tab=&width=&height=&face=0&istype=2&qc=&nc=1'  
        f'&expermode=&nojc=&isAsync=&pn={start}&rn=30&gsm=1e&1704438469116='
    )
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 确保请求成功
        data = json.loads(response.text)
        return data.get('data', [])  # 如果没有数据，返回一个空列表
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return []  # 网络异常时返回一个空列表
def main():
   keyword = input('请输入下载图片的关键字：')
   headers = {
       'Accept': 'text/plain, */*; q=0.01',
       'Accept-Language': 'zh-CN,zh;q=0.9',
       'Connection': 'keep-alive',
       'Cookie': 'BDqhfp=%E7%BE%8E%E5%A5%B3%26%260-10-1undefined%26%260%26%261; BIDUPSID=8005CA7FE9E4FD81A70DA4F648964B91; PSTM=1698111628; BAIDUID=8005CA7FE9E4FD8171441541BB84A81F:SL=0:NR=10:FG=1; MCITY=-268%3A; BDUSS_BFESS=JJaWZtaX5VcHg4Yi1CY0MtTX5RYzNxekVKVFgydVVWMW1lZXVRdWlzQ2tBWFJsRUFBQUFBJCQAAAAAAAAAAAEAAAAbI04GtdjJz7XE0Me~1QAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKR0TGWkdExlM0; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=39998_40008_40016_40045_39825; BAIDUID_BFESS=8005CA7FE9E4FD8171441541BB84A81F:SL=0:NR=10:FG=1; BDRCVFR[X_XKQks0S63]=mk3SLVN4HKm; userFrom=www.baidu.com; firstShowTip=1; BA_HECTOR=05210ga1040g00agakal20ahnkjbdl1ipfafv1s; ZFY=i2zXA6GRjg:AZCDpA5IZYBrux1XFf1SCl:Bo6JxkW8tCY:C; indexPageSugList=%5B%22%E7%BE%8E%E5%A5%B3%22%2C%22shell%20moba%22%2C%22shell%20finalshell%22%2C%22shell%20xshell5%22%2C%22shell%20xshell%22%2C%22qq%E9%A3%9E%E8%BD%A6%22%2C%22%E7%A9%BF%E8%B6%8A%E7%81%AB%E7%BA%BF%20%E7%94%9F%E5%8C%96%E6%A8%A1%E5%BC%8F%22%2C%22%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%9C%BA%E6%9E%B6%22%2C%22%E6%9C%BA%E6%9E%B6%22%5D; cleanHistoryStatus=0; BDRCVFR[dG2JNJb_ajR]=mk3SLVN4HKm; BDRCVFR[-pGxjrCMryR]=mk3SLVN4HKm; ab_sr=1.0.1_NTE4YzlkNGExZThhYjFmNzM5MDUyYjM5ZDNjN2M1NTdmZWE5ZTlkMjczZWViYmI1ZDYxMjJhNmE3NDI4MzI3NzI1NzM2MzUzYTE3Njg2MjI4Y2M1MjEyYWVjNGVhZDE4NzMzMzUyZWU5YTNjYmNmODZhMDc4ZDdmOWVjNDg3ODM0YTk4NDYyMzIwZTBkMThjZjE1YjA5YjMxZGY1MjFhMw==',
       'Host': 'image.baidu.com',
       'Referer': 'https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=-1&st=-1&fm=index&fr=&hs=0&xthttps=111110&sf=1&fmq=&pv=&ic=0&nc=1&z=&se=1&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=%E7%BE%8E%E5%A5%B3&oq=%E7%BE%8E%E5%A5%B3&rsp=-1',
       'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
       'Sec-Ch-Ua-Mobile': '?0',
       'Sec-Ch-Ua-Platform': '"Windows"',
       'Sec-Fetch-Dest': 'empty',
       'Sec-Fetch-Mode': 'cors',
       'Sec-Fetch-Site': 'same-origin',
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
       'X-Requested-With': 'XMLHttpRequest'
   }
   directory = create_directory_with_keyword(keyword)  # 使用关键字和日期创建新文件夹
   start = 0
   index = 1  # 图片下载的名称序号
   # 确保目录存在
   if not os.path.exists(directory):
       os.makedirs(directory)
   while True:
       data = get_image_data(keyword, headers, start)
       if not data:  # 如果没有数据则退出循环
           break
       current_time = datetime.now().strftime('%Y%m%d_%H%M%S')  # 获取当前时间，不包含毫秒
       for item in data:
           if 'thumbURL' in item:
               image_url = item['thumbURL']
               # 使用新目录和时间标签作为保存路径
               filename = f'{directory}/{current_time}_{index}.jpg'
               download_image(image_url, directory, f'{current_time}_{index}.jpg')  # 下载图片
               save_image_to_db(keyword, filename, image_url)  # 存储图片信息到数据库
               index += 1
       start += 30  # 下一页
       # 添加一个退出条件，例如下载100张图片后退出循环
       if index > 100:
           break
       time.sleep(1)  # 休眠一秒，防止请求过快被服务器拒绝


if __name__ == '__main__':
   main()