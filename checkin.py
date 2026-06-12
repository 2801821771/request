# -*- coding: utf-8 -*-
import sys
import io
import os

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import time
import re
from datetime import datetime
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class MultiSiteCheckIn:
    def __init__(self):
        # 微信推送配置（替换成你的token）
        self.PUSH_TOKEN = "6b0de67e34949106bc3f83900bc267371468837923"
        
        # 检测是否在 GitHub Actions 环境中运行
        self.is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
        
        # 设置请求头 - 增强版，模拟真实浏览器
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Microsoft Edge";v="149", "Chromium";v="149", "Not?A_Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        }
        
        # sjs66.com 的 cookies 和 formhash
        self.sjs66_cookies = self.parse_cookie_string(
            'SgL6_2132_saltkey=bzcgu5sn; '
            'SgL6_2132_lastvisit=1779336665; '
            'SgL6_2132_auth=aee7dv0PChiCJSxEUbs2usQB%2Fdziv2HsFqLPlNT%2FjMWRzeukevkwDPMcvhjISp8V8q7RZtGA%2Bs1gdmWjB%2F%2FmQa%2Ff; '
            'SgL6_2132_atarget=1; '
            'SgL6_2132_smile=4D1; '
            'SgL6_2132_nofavfid=1; '
            'SgL6_2132_sid=0; '
            'SgL6_2132_st_p=6483%7C1780831145%7Ce226f8f95712324ebbd8920efbb72203; '
            'SgL6_2132_visitedfid=58D67D40D57D48; '
            'SgL6_2132_viewid=tid_607849; '
            'SgL6_2132_ulastactivity=1780831145%7C0; '
            'cf_clearance=Gk7r5vx42VrJcGDKootpzAJqrh7l1DxcWe846DPcMGI-1780831161-1.2.1.1-LTI_K27NKNCLAHonB7TMzHSm2ET9PdxDd2ggrCYNaTWrv1fODILQTl6D7gmGU4l7YfiMZT7kfHoSfNBrt8rTtyLH5qHOh2ZHme_Q6PIMb3GvlnPzstmbqnjyIsYMnRZA14ufRE8UVCle35ZYcT4d2pKdrSlEQQkWUsuESZfszs94QUJdDljXQZhxf2Y4Str8NPCbdCgJZ8dAY.YNf71C5APwlnqt_ccD4LmlDn9RrcPylPcTMjtfXiBBZC3A9VnfSvDC1o8yy8g9zSKTQRZ5SwrCdjOvR1tDZAB_vrx6p4EHlRMLosicg9C50EN9urrW8ux82yOpQEvtUYqYlyLr8A; '
            'SgL6_2132_seccodecS0=6990.a78fa1128e16df3fa7; '
            'f9b880159d6a689a496b90c25326ec99=a31c9fc5335ae4fd44d0270545ee557c; '
            'SgL6_2132_misigntime=1780831435; '
            'SgL6_2132_lastcheckfeed=6483%7C1780831444; '
            'SgL6_2132_lastact=1780831632%09plugin.php%09'
        )
        
        self.sjs66_formhash = 'eca79a81'
        
        # yyg.app 的 cookies
        self.yyg_cookie = (
            'wordpress_sec_646d318c66f2c4c0e1e8624adee79b87=w%20wd%7C1781776893%7Cxc2x7wf1bwRGG1zZk2mtbDeP6kZwEMwsm7FogobIezI%7C9cedc2bd36b5fe96cdd5a643ad6cd74dfc071def9d37067ee200bbd9ba7e5175; '
            'history_search=%5B%22%5Cu50ac%5Cu7720%26type%3Dpost%22%2C%22%5Cu8150%5Cu5316%26type%3Dpost%22%2C%22%5Cu5973%5Cu6559%5Cu5e08%26type%3Dpost%22%2C%22%5Cu5251%5Cu661f%26type%3Dpost%22%2C%22%5Cu5c18%5Cu767d%5Cu7981%5Cu533a%26type%3Dpost%22%5D; '
            'wordpress_logged_in_646d318c66f2c4c0e1e8624adee79b87=w%20wd%7C1781776893%7Cxc2x7wf1bwRGG1zZk2mtbDeP6kZwEMwsm7FogobIezI%7C173e23ca5c1c58395c644819eb7c8f60ed5131b10ec7b574b4cd05de6cd17fe7; '
            'PHPSESSID=ellg4ojoo84n1pmds0jbni4aq3; '
            'server_name_session=3091bc4b73c05f1b366131a2036903bc'
        )
    
    def parse_cookie_string(self, cookie_string):
        """解析 cookie 字符串为字典"""
        cookies = {}
        for item in cookie_string.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                cookies[key] = value
        return cookies
    
    def send_wechat_push(self, title, content):
        """发送微信推送通知"""
        try:
            push_url = f"https://push.showdoc.com.cn/server/api/push/{self.PUSH_TOKEN}?title={title}&content={content}"
            response = requests.get(push_url, timeout=10)
            if response.status_code == 200:
                print(f"[微信推送] 发送成功: {title}")
                return True
            else:
                print(f"[微信推送] 发送失败: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"[微信推送] 发送异常: {e}")
            return False
    
    def checkin_sjs66(self):
        """使用 requests 签到 sjs66.com"""
        print("\n" + "="*50)
        print("正在执行 sjs66.com 签到...")
        print("="*50)
        
        try:
            # 创建 session
            session = requests.Session()
            
            # 设置 headers - 使用增强版
            session.headers.update(self.headers)
            
            # 设置 cookies
            session.cookies.update(self.sjs66_cookies)
            
            # 如果是在 GitHub Actions 中，添加延迟避免被检测
            if self.is_github_actions:
                print("检测到 GitHub Actions 环境，添加额外延迟...")
                time.sleep(3)
            
            # 第一步：访问首页，获取最新的 formhash
            print("正在访问 sjs66.com...")
            try:
                response = session.get('https://sjs66.com', timeout=30, verify=False)
                print(f"首页访问状态码: {response.status_code}")
                
                if response.status_code == 200:
                    # 尝试从页面中提取 formhash
                    formhash_match = re.search(r'name="formhash" value="([a-f0-9]+)"', response.text)
                    if formhash_match:
                        self.sjs66_formhash = formhash_match.group(1)
                        print(f"获取到新的 formhash: {self.sjs66_formhash}")
                    else:
                        print(f"使用预设 formhash: {self.sjs66_formhash}")
                else:
                    print(f"首页访问返回 {response.status_code}，使用预设 formhash")
                    
            except Exception as e:
                print(f"访问首页出错: {e}，继续使用预设 formhash")
            
            # 添加延迟避免请求过快
            time.sleep(2)
            
            # 第二步：执行签到
            print("正在执行签到...")
            sign_url = f'https://sjs66.com/plugin.php?id=k_misign:sign&operation=qiandao&formhash={self.sjs66_formhash}'
            
            # 添加 AJAX 请求头
            headers_ajax = self.headers.copy()
            headers_ajax.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': 'https://sjs66.com/',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
            })
            
            # 多次尝试签到（最多3次）
            max_retries = 3
            for attempt in range(max_retries):
                if attempt > 0:
                    print(f"第 {attempt + 1} 次尝试...")
                    time.sleep(3)
                
                response = session.get(sign_url, headers=headers_ajax, timeout=30, verify=False)
                
                print(f"签到响应状态码: {response.status_code}")
                
                if response.status_code == 200:
                    response_text = response.text
                    print(f"签到响应内容: {response_text[:200]}")
                    
                    # 判断签到结果
                    if '今日已签' in response_text:
                        print("[成功] sjs66.com: 今日已签")
                        return "今日已签"
                    elif '签到成功' in response_text:
                        print("[成功] sjs66.com: 签到成功")
                        return "签到成功"
                    elif '您已经签到过了' in response_text:
                        print("[成功] sjs66.com: 今日已签")
                        return "今日已签"
                    elif '<![CDATA[' in response_text:
                        match = re.search(r'<!\[CDATA\[(.*?)\]\]>', response_text, re.DOTALL)
                        if match:
                            result_msg = match.group(1)
                            print(f"[成功] sjs66.com: {result_msg}")
                            return result_msg
                    elif '成功' in response_text or '奖励' in response_text:
                        print(f"[成功] sjs66.com: 签到成功")
                        return "签到成功"
                    else:
                        print(f"[成功] sjs66.com: 签到请求已发送")
                        return "签到请求已发送"
                elif response.status_code == 403:
                    print(f"[警告] 第 {attempt + 1} 次尝试返回 403")
                    if attempt == max_retries - 1:
                        return None
                else:
                    error_msg = f"HTTP {response.status_code}"
                    print(f"[失败] sjs66.com: {error_msg}")
                    return None
            
            return None
                
        except requests.exceptions.Timeout:
            print("[失败] sjs66.com: 请求超时")
            return None
        except Exception as e:
            error_msg = str(e)
            print(f"[失败] sjs66.com: {error_msg}")
            return None
    
    def checkin_yyg_app(self):
        """使用 requests 签到 yyg.app"""
        print("\n" + "="*50)
        print("正在执行 yyg.app 签到...")
        print("="*50)
        
        try:
            url = 'https://yyg.app/wp-admin/admin-ajax.php'
            headers = {
                'Host': 'yyg.app',
                'Origin': 'https://yyg.app',
                'Referer': 'https://yyg.app/',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'User-Agent': self.headers['User-Agent'],
                'Sec-Ch-Ua': '"Microsoft Edge";v="149", "Chromium";v="149", "Not?A_Brand";v="99"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
            }
            data = {'action': 'user_checkin'}
            
            response = requests.post(url, headers=headers, cookies=self.parse_cookie_string(self.yyg_cookie), 
                                    data=data, timeout=10, verify=False)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print(f"返回: {result}")
                    if result.get('error') == True:
                        msg = result.get('msg', '今日已签')
                        print(f"[成功] yyg.app: {msg}")
                        return msg
                    else:
                        print(f"[成功] yyg.app: 签到成功")
                        return "签到成功"
                except:
                    if "已签到" in response.text or "already" in response.text.lower():
                        print("[成功] yyg.app: 今日已签")
                        return "今日已签"
                    else:
                        print("[成功] yyg.app: 签到成功")
                        return "签到成功"
            else:
                error_msg = f"HTTP {response.status_code}"
                print(f"[失败] {error_msg}")
                return None
        except Exception as e:
            error_msg = str(e)
            print(f"[失败] {error_msg}")
            return None
    
    def checkin_all(self):
        """执行所有签到"""
        print("\n" + "="*60)
        print(f"开始自动签到 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if self.is_github_actions:
            print("运行环境: GitHub Actions")
        print("="*60)
        
        results = {}
        
        # sjs66.com - 使用 requests
        result1 = self.checkin_sjs66()
        results["sjs66.com"] = result1 if result1 else "失败"
        
        time.sleep(2)
        
        # yyg.app - 使用 requests
        result2 = self.checkin_yyg_app()
        results["yyg.app"] = result2 if result2 else "失败"
        
        print("\n" + "="*60)
        print("签到结果汇总:")
        for site, status in results.items():
            print(f"  {site}: {status}")
        print("="*60)
        
        # 构建推送内容
        summary = "签到结果\n\n"
        for site, status in results.items():
            summary += f"{site}: {status}\n"
        
        # 检查是否有失败
        has_failure = any(status == "失败" for status in results.values())
        if has_failure:
            summary += "\n部分站点签到失败"
        
        summary += f"\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 发送最终结果通知
        self.send_wechat_push("签到结果", summary)
        
        return not has_failure


def main():
    print("网站自动签到脚本 (纯 Requests 模式 + 微信推送)")
    print("支持站点: sjs66.com, yyg.app")
    print("-" * 40)
    print("无需 Edge 驱动，使用 HTTP 请求直接签到")
    print()
    
    # 检测是否在 GitHub Actions 中运行
    is_github_actions = os.getenv('GITHUB_ACTIONS') == 'true'
    
    try:
        checker = MultiSiteCheckIn()
        success = checker.checkin_all()
        
        print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if success:
            print("所有站点签到成功！")
        else:
            print("部分站点签到失败")
        
        # 只在非 GitHub Actions 环境中等待用户输入
        if not is_github_actions:
            input("\n按 Enter 键退出...")
        
        exit(0 if success else 1)
    except Exception as e:
        error_msg = str(e)
        print(f"程序错误: {error_msg}")
        try:
            # 尝试发送错误通知
            checker = MultiSiteCheckIn()
            checker.send_wechat_push("签到脚本运行错误", f"错误信息：{error_msg}\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except:
            pass
        
        # 只在非 GitHub Actions 环境中等待用户输入
        if not is_github_actions:
            input("\n按 Enter 键退出...")
        exit(1)


if __name__ == "__main__":
    main()
