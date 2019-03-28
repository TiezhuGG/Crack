#coding:utf-8
'''
    极验官网登录验证码破解程序

    拆解为以下几步：
    1.打开页面，输入信息
    2.分别获取有无缺口的验证码图片，并做缺口识别
    3.设计滑块的移动轨迹
    4.拖拽滑块到缺口位置完成验证
'''

import time
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class GeetestCrack():
    def __init__(self, email, password):
        self.url = 'https://auth.geetest.com/login/'
        self.browser = webdriver.Chrome()
        self.wait = WebDriverWait(self.browser, timeout=10)
        self.email = email
        self.password = password

    def get_geetest_button(self):
        """
        获取初始验证按钮
        :return: 按钮对象
        """
        button = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_radar_tip')))
        return button

    def get_screenshot(self):
        '''
        获取整个网页截图
        :return: 截图对象
        '''
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))
        return screenshot

    def get_position(self):
        '''
        获取验证码图片位置
        :return:
        '''
        img = self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'geetest_canvas_img')))
        time.sleep(2)
        # 获取图片的位置
        location = img.location
        # 获取图片的尺寸
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size['width']
        return (top, bottom, left, right)

    def get_geetest_image(self, name='captcha.png'):
        '''
        通过网页截图截取验证码图片
        :return: 图片对象
        '''
        top, bottom, left, right = self.get_position()
        print('验证码图片位置：', top, bottom, left, right)
        screenshot = self.get_screenshot()
        # 截图验证码图片
        captcha = screenshot.crop((left, top, right, bottom))
        return captcha

    def get_gap(self, image1, image2):
        '''
        获取缺口偏移量
        :param image1: 带缺口的验证码图片
        :param image2: 不带缺口的验证码图片
        :return: 偏移量
        '''
        # 缺口与滑块在同一水平线，缺口又在滑块的右侧，所以直接从滑块右侧开始寻找即可
        # 这里直接设置遍历的起始横坐标start为60(即从滑块右侧开始寻找，识别处的位置就是缺口位置)
        start = 60
        # 设置阈值为60
        threhold = 60

        # 遍历图片每个坐标点
        for i in range(start, image1.size[0]):
            for j in range(image1.size[1]):
                # 对比两张图片对应像素点的RGB数据
                rgb1 = image1.load()[i, j]
                rgb2 = image2.load()[i, j]
                res1 = abs(rgb1[0] - rgb2[0])
                res2 = abs(rgb1[1] - rgb2[1])
                res3 = abs(rgb1[2] - rgb2[2])
                if not (res1 < threhold and res2 < threhold and res3 < threhold):
                    return i
        return i - 9

    def get_track(self, offset):
        '''
        根据偏移量获取移动轨迹
        :param offset: 偏移量
        :return: 移动轨迹
        '''
        offset += 20  # 先滑过一点，最后再反着滑动回来
        v = 0
        t = 0.2
        # 向右的移动轨迹
        forward_tracks = []
        # 当前位移
        current = 0
        # 减速阈值(加速到mid位置时开始减速)，这里设置前3/5路程是加速过程，后2/5路程为减速过程
        mid = offset * 3 / 5
        while current < offset:
            if current < mid:
                a = 2
            else:
                a = -3
            # 移动距离s = vt + 0.5 * a * t^2
            s = v * t + 0.5 * a * (t ** 2)
            # 当前速度v = v + at
            v = v + a * t
            # 当前位移
            current += s
            # 加入轨迹
            forward_tracks.append(round(s))

        # 反向滑动到准确位置
        back_tracks = [-2, -2, -2, -2, -2, -1, -3, -4]

        return {'forward_tracks': forward_tracks, 'back_tracks': back_tracks}

    def move_to_gap(self, slider, tracks):
        '''
        拖动滑块到缺口处
        :param slider: 滑块
        :param tracks: 轨迹
        :return:
        '''
        ActionChains(self.browser).click_and_hold(slider).perform()
        for track in tracks['forward_tracks']:
            ActionChains(self.browser).move_by_offset(xoffset=track, yoffset=0).perform()
        time.sleep(0.5)
        for back_track in tracks['back_tracks']:
            ActionChains(self.browser).move_by_offset(xoffset=back_track, yoffset=0).perform()
        ActionChains(self.browser).move_by_offset(xoffset=-3, yoffset=0).perform()
        ActionChains(self.browser).move_by_offset(xoffset=3, yoffset=0).perform()
        # 0.5秒后再释放鼠标，否则会被识别出来
        time.sleep(0.5)
        ActionChains(self.browser).release().perform()

    def get_slider(self):
        '''
        获取验证码滑块
        :return: 滑块对象
        '''
        slider = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return slider

    def input_info(self):
        email = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#base > div.content-outter > div > div > div:nth-child(3) > div > form > div:nth-child(1) > div > div > div > input')))
        password = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#base > div.content-outter > div > div > div:nth-child(3) > div > form > div:nth-child(2) > div > div:nth-child(1) > div > input')))
        email.send_keys(self.email)
        password.send_keys(self.password)

    def login(self):
        submit = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'ivu-btn')))
        submit.click()
        time.sleep(5)
        print('登录成功')

    def main(self):
        # 打开网页
        self.browser.get(self.url)
        # 最大化浏览器窗口
        self.browser.maximize_window()
        # 输入账号和密码
        self.input_info()
        # 获取初始验证按钮并点击
        button = self.get_geetest_button()
        button.click()
        # 获取带缺口的验证码图片
        image1 = self.get_geetest_image('captcha1.png')
        # 执行js改变css样式，显示背景图(完整的验证码图片)
        self.browser.execute_script('document.querySelectorAll("canvas")[2].style=""')
        # 获取不带缺口的验证码图片
        image2 = self.get_geetest_image('captcha2.png')
        # 获取滑块对象
        slider = self.get_slider()
        # 获取偏移量
        offset = self.get_gap(image1, image2)
        print('offset', offset)
        # 减去缺口位移
        offset -= 6
        # 获取移动轨迹
        tracks = self.get_track(offset)
        # 模拟拖动滑块至缺口处
        self.move_to_gap(slider, tracks)
        time.sleep(1)
        # 判断是否验证成功
        try:
            success = self.wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'geetest_success_radar_tip_content'), '验证成功'))
            if not success:
                print('验证失败了，正在重试')
                self.main()
            else:
                self.login()
        except Exception:
            self.main()

if __name__ == '__main__':
    crack = GeetestCrack('88261196@qq.com', 'lhf101400')
    crack.main()