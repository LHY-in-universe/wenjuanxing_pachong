# 引入相关模块
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import random  # 随机数产生
import time  # 延时
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyautogui  # 模拟人手，进行页面滚动
import numpy as np
from selenium.common.exceptions import TimeoutException, NoSuchElementException

#### 方法：题干————》选项 ####
# 滚动方法, scroPx为滚动距离
def scrop(driver, scroPx):
    # 滚动脚本
    js = "var q=document.documentElement.scrollTop=" + str(scroPx)
    # 脚本执行
    driver.execute_script(js)
    # 延时
    time.sleep(1)


def normal_choice(options, mean=0, std=1):
    """
    基于正态分布从选项中随机选择一个
    :param options: 选项列表
    :param mean: 正态分布的均值
    :param std: 正态分布的标准差
    :return: 被选中的选项
    """
    if not options:
        raise ValueError("选项列表不能为空")
    # 生成符合正态分布的随机数
    index = int(np.random.normal(mean, std))
    # 确保索引在选项范围内
    index = max(0, min(index, len(options) - 1))
    return options[index]

# 单选题
def single(driver,m,n):
    # 页面中有16个单选题
    for j in range(m, n):
        # 每个单选题所在的位置
        sinPro = driver.find_elements(By.CSS_SELECTOR, f'#div{j} > div.ui-controlgroup.column1')  # 使用新的方法
        # 每个单选题的答案进行遍历
        for answer in sinPro:
            # 对应每个单选题的选项组合
            ansItem = answer.find_elements(By.CSS_SELECTOR, '.ui-radio')  # 使用新的方法
            # 基于正态分布选择选项
            selected_option = normal_choice(ansItem, 3, 1)
            # 点击选项
            selected_option.click()
            # 答题时间间隔
            time.sleep(random.randint(0, 1))

# 多选题
def multiple_choice(driver, m,n):
    for j in range(m, n):
        try:
            # 显式等待多选题加载
            wait = WebDriverWait(driver, 10)
            mulPro = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, f'#div{j} > div.ui-controlgroup.column1')))
            # 遍历每个多选题
            for answer in mulPro:
                ansItem = answer.find_elements(By.CSS_SELECTOR, '.ui-checkbox')
                if len(ansItem) > 1:
                    selected_options = random.sample(ansItem, k=random.randint(1, 3))
                    for option in selected_options:
                        # 滚动到选项位置
                        driver.execute_script("arguments[0].scrollIntoView();", option)
                        time.sleep(1)
                        # 点击选项
                        if not option.get_attribute("disabled"):
                            driver.execute_script("arguments[0].click();", option)
                            time.sleep(random.randint(0, 1))
                else:
                    print(f"多选题 {j} 选项不足，无法选择多个选项")
        except Exception as e:
            print(f"多选题 {j} 处理失败：{e}")

# 矩阵选择题，一个题
def juzhen(driver):
    # 矩阵行数
    for i in range(1, 6):
        # 矩阵列数
        index = random.randint(2, 6)
        # 对应的每一个选项
        dan = driver.find_element(By.XPATH, f"//tr[@id='drv8_{i}']/td[{index}]/a")  # 使用新的方法
        # 选择
        dan.click()
        time.sleep(random.randint(0, 1))

def matrix_choice(driver, start_id, end_id, num_columns, mean=0, std=1):
    for i in range(start_id, end_id):
        try:
            # 显式等待矩阵量表的每一行加载
            wait = WebDriverWait(driver, 10)  # 最大等待时间为10秒
            mulPro = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, f'#div{i} ')))

            row = wait.until(
                EC.presence_of_element_located((By.XPATH, ".//span[@class='itemTitleSpan']"))
            ).text
            # 显式等待行中的所有列（选项）加载
            columns = wait.until(
                EC.presence_of_all_elements_located((By.XPATH, ".//a[@rate-off rate-offlarge']"))
            )
            if columns:  # 确保选项存在
                # 生成符合正态分布的随机数
                index = int(np.random.normal(mean, std))
                # 确保索引在选项范围内
                index = max(0, min(index, num_columns - 1))
                # 点击选项
                columns[index].click()
                # 答题时间间隔
                time.sleep(random.randint(0, 1))
        except TimeoutException:
            print(f"矩阵量表行 {i} 加载超时：未找到元素")
        except NoSuchElementException:
            print(f"矩阵量表行 {i} 未找到元素")
        except Exception as e:
            print(f"矩阵量表行 {i} 处理失败：{e}")


def answer_matrix_question(driver, question_id):
    try:
        # 定位矩阵量表容器
        matrix_div = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, question_id))
        )


        # 获取所有行
        rows = matrix_div.find_elements(By.XPATH, ".//tr[@class='rowtitle']")

        # 遍历每一行
        for row in rows:
            # 等待评分选项加载
            options = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, ".//a[@class='rate-off rate-offlarge']"))
            )
            if not options:
                print(f"未找到评分选项，跳过此行")
                continue

            # 随机选择一个选项
            random_option = random.choice(options)
            # 点击选项
            random_option.click()

    except Exception as e:
        print(f"操作失败：{e}")


# 脚本执行方法
def launch(nums):
    for i in range(0, nums):
        try:
            # 初始配置，问卷星地址
            url_survey = 'https://www.wjx.cn/vm/OyIbTKT.aspx'
            option = webdriver.ChromeOptions()
            option.add_experimental_option('excludeSwitches', ['enable-automation'])
            option.add_experimental_option('useAutomationExtension', False)
            # 启动浏览器
            driver = webdriver.Chrome()
            driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument',
                                   {'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})
            # 启动要填写的地址
            driver.get(url_survey)
            # 调用单选题方法
            single(driver,1,5)
            time.sleep(random.randint(0, 1))

            multiple_choice(driver,5,6)
            time.sleep(random.randint(0, 1))

            single(driver,6,8)
            time.sleep(random.randint(0, 1))

            multiple_choice(driver,8,9)
            time.sleep(random.randint(0, 1))
            # 自动回答矩阵量表问题
            answer_matrix_question(driver, question_id="div9")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))
            answer_matrix_question(driver, question_id="div10")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))

            multiple_choice(driver,11,12)
            time.sleep(random.randint(0, 1))

            single(driver,12,13)
            time.sleep(random.randint(0, 1))

            answer_matrix_question(driver, question_id="div13")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))
            answer_matrix_question(driver, question_id="div14")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))

            single(driver,15,18)
            time.sleep(random.randint(0, 1))

            answer_matrix_question(driver, question_id="div18")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))

            single(driver,19,20)
            time.sleep(random.randint(0, 1))

            multiple_choice(driver,20,21)
            time.sleep(random.randint(0, 1))

            single(driver,22,23)
            time.sleep(random.randint(0, 1))
            # 涉及到多个矩阵题执行方法
            # for k in range(4):
            #     method_name = f'juzhen{k}'
            #     if method_name in globals():
            #         method = globals()[method_name]
            #         method(driver)
            # 调用滚动屏幕方法

            answer_matrix_question(driver, question_id="div9")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))
            answer_matrix_question(driver, question_id="div10")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))
            answer_matrix_question(driver, question_id="div18")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))
            answer_matrix_question(driver, question_id="div13")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))
            answer_matrix_question(driver, question_id="div14")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))


            answer_matrix_question(driver, question_id="div9")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))
            answer_matrix_question(driver, question_id="div10")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))
            answer_matrix_question(driver, question_id="div18")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))
            answer_matrix_question(driver, question_id="div13")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))
            answer_matrix_question(driver, question_id="div14")  # 替换为实际的问题 ID
            time.sleep(random.randint(0, 1))

            scrop(driver, 600)
            # 提交按钮
            driver.find_element(By.CSS_SELECTOR, '#ctlNext').click()  # 找到提交的css并点击
            time.sleep(4)
            print('已经提交了{}次问卷'.format(int(i) + int(1)))
            time.sleep(400)
        except Exception as e:
            print(f"第 {i + 1} 次问卷提交失败：{e}")
        finally:
            driver.quit()  # 停止

if __name__ == "__main__":
    # 填写问卷次数
    launch(1)
