from appium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pymongo
import time

# Appium设置
PLATFORM = 'Android'
DEVICE_NAME = 'Pixel'
APP_PACKAGE = 'com.tencent.mm'
APP_ACTIVITY = '.ui.LauncherUI'
DRIVER_SERVER = 'http://localhost:4723/wd/hub'
# 超时时间
TIMEOUT = 300
# MongoDB设置
MONGO_URL = 'localhost'
MONGO_DB = 'moments'
MONGO_COLLECTION = 'moments'
# 滑动点
FLICK_START_X = 300
FLICK_START_Y = 300
FLICK_DISTANCE = 700

class Moments():
    def __init__(self):
        '''
        初始化
        '''
        # 驱动配置
        self.desired_caps = {
            'platformName': PLATFORM,
            'deviceName': DEVICE_NAME,
            'appPackage': APP_PACKAGE,
            'appActivity': APP_ACTIVITY
        }
        self.driver = webdriver.Remote(DRIVER_SERVER, self.desired_caps)
        self.wait = WebDriverWait(self.driver, TIMEOUT)
        self.client = pymongo.MongoClient(MONGO_URL)
        self.db = self.client[MONGO_DB]
        self.collection = self.db[MONGO_COLLECTION]

    def login(self):
        # 登录按钮
        login = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/e4g')))
        login.click()
        # 点击QQ方式登录
        QQ_login = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/cou')))
        QQ_login.click()
        # 输入账号密码
        account = self.wait.until(EC.presence_of_element_located((By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.ScrollView/android.widget.LinearLayout/android.widget.LinearLayout[1]/android.widget.EditText')))
        account.set_text('88261196')
        time.sleep(1)
        password = self.wait.until(EC.presence_of_element_located((By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.LinearLayout/android.widget.ScrollView/android.widget.LinearLayout/android.widget.LinearLayout[2]/android.widget.EditText')))
        password.set_text('afa101400')
        time.sleep(0.8)
        # 实现登录(提交)
        submit = self.wait.until(EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/cov')))
        submit.click()

    def enter(self):
        # '发现'选项卡
        tab = self.wait.until(
            EC.presence_of_element_located((By.XPATH,'//*[@resource-id="com.tencent.mm:id/bq"]/android.widget.LinearLayout/android.widget.RelativeLayout[3]'))
        )
        tab.click()
        time.sleep(2)
        # 朋友圈
        moments = self.wait.until(
            EC.presence_of_element_located((By.ID, 'com.tencent.mm:id/y6'))
        )
        moments.click()

    def crawl(self):
        while True:
            # 上滑
            self.driver.swipe(FLICK_START_X, FLICK_START_Y + FLICK_DISTANCE, FLICK_START_X, FLICK_START_Y )
            # 当前页面显示的所有状态
            items = self.wait.until(
                EC.presence_of_all_elements_located((By.ID , 'com.tencent.mm:id/ej9'))
            )
            # 遍历每条状态
            for item in items:
                try:
                    # 昵称
                    nickname = item.find_element_by_id('com.tencent.mm:id/b5o').get_attribute('text')
                    # 正文
                    content = item.find_element_by_id('com.tencent.mm:id/ejc').get_attribute('text')
                    data = {
                        'nickname': nickname,
                        'content': content,
                    }
                    print(data)
                except:
                    print('没有这个元素')

    def main(self):
        self.login()
        self.enter()
        self.crawl()

if __name__ == '__main__':
    spider = Moments()
    spider.main()
