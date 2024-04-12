from flask import Flask, render_template, request, redirect, url_for
import os
import requests
import json
from datetime import datetime
import urllib.parse
import pymysql
from werkzeug.utils import secure_filename

from crawler import create_directory_with_keyword, get_image_data, download_image, save_image_to_db

app = Flask(__name__)
UPLOAD_FOLDER = 'images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 数据库配置，请根据实际情况修改  
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'anwen',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/download', methods=['POST'])
def download():
    keyword = request.form['keyword']
    start = 0  # 起始页码，可以根据需要调整或添加为请求参数  
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

    # 创建保存图片的目录  
    directory = create_directory_with_keyword(keyword)

    # 获取图片数据  
    image_data = get_image_data(keyword, headers, start)
    for index, item in enumerate(image_data, start=1):
        url = item['objURL']
        # 下载图片  
        downloaded_url = download_image(url, directory, index)
        if downloaded_url:
            filename = os.path.join(directory, f"{index}.jpg")
            # 将图片信息保存到数据库  
            save_image_to_db(keyword, filename, downloaded_url)
    return redirect(url_for('index', message='图片下载完成！'))


if __name__ == '__main__':
    app.run(debug=True)