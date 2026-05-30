import requests
import json
import time
from datetime import datetime
import gzip
import io

class MultiSiteCheckIn:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Connection': 'keep-alive',
        })
        
    def decode_response(self, response):
        """解码可能被压缩的响应内容"""
        try:
            # 检查响应编码
            if 'gzip' in response.headers.get('Content-Encoding', ''):
                return gzip.decompress(response.content).decode('utf-8', errors='ignore')
            elif 'zstd' in response.headers.get('Content-Encoding', ''):
                # zstd 压缩需要额外处理，这里返回原始文本
                return response.text
            else:
                return response.text
        except:
            return response.text
        
    def checkin_sjs66(self):
        """sjs66.com 签到"""
        print("\n" + "="*50)
        print("正在执行 sjs66.com 签到...")
        print("="*50)
        
        # 从您提供的请求头中提取最新的 cookie
        sjs66_cookie = (
            'SgL6_2132_saltkey=bzcgu5sn; '
            'SgL6_2132_lastvisit=1779336665; '
            'SgL6_2132_auth=aee7dv0PChiCJSxEUbs2usQB%2Fdziv2HsFqLPlNT%2FjMWRzeukevkwDPMcvhjISp8V8q7RZtGA%2Bs1gdmWjB%2F%2FmQa%2Ff; '
            'SgL6_2132_lastcheckfeed=6483%7C1779343265; '
            'SgL6_2132_atarget=1; '
            'SgL6_2132_smile=4D1; '
            'SgL6_2132_nofavfid=1; '
            'SgL6_2132_forum_lastvisit=D_57_1779414465D_48_1779515775; '
            'SgL6_2132_visitedfid=67D40D57D48D73; '
            '510d60127c8aaada09de672c2554438d=c557f98c3d91fdbebd1749c357568e8a; '
            'SgL6_2132_sid=0; '
            'SgL6_2132_ulastactivity=1780117221%7C0; '
            'cf_clearance=xdYadqfmA9zzj3obmX5.gVTYWM8Fp9cUCeQPXAmBQis-1780117223-1.2.1.1-l7G0q5EM3sxyE_6pLymr5wcEUa6b7Dt2J_2YPjelllWUapC9Y0k.3JpXxcl9qKHOQ6torDeRCmF1LLqbNgc8mGMHatj..qsChm97o2V87laynTbdh5QLOLIyaNblx.8MItfalgx_cu.Bo1Gex6XQX8XksEgF22h.f5JDDdrQiLV3DXKn0Ccy7sSnJg7Nivd1AQIKgkBQlT6laqMWFKNzxp9arxzQKDGiOXE6l4FkODt1QBdTZ9KsVJfEGoIPxCeY2c99qnabMMtTG4OKUHI1fw0O8FloA29GY6pMXgh4yQjf8nWD6Yywm58kp8U0bbVuB5_oXHCPSMnii419BzJ1tw; '
            'SgL6_2132_sendmail=1; '
            'SgL6_2132_lastact=1780117241%09home.php%09space; '
            'SgL6_2132_home_diymode=1'
        )
        
        # 构建请求头
        headers = {
            'Host': 'sjs66.com',
            'Referer': 'https://sjs66.com/home.php?mod=space&uid=6483',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': sjs66_cookie,
            'Accept': '*/*',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Ch-UA': '"Chromium";v="148", "Microsoft Edge";v="148", "Not/A)Brand";v="99"',
            'Sec-Ch-UA-Mobile': '?0',
            'Sec-Ch-UA-Platform': '"Windows"',
            'Priority': 'u=1, i',
        }
        
        # 构建签到URL - 使用最新的 formhash
        url = 'https://sjs66.com/k_misign-sign.html'
        params = {
            'operation': 'qiandao',
            'format': 'global_usernav_extra',
            'formhash': 'eca79a81',  # 最新的 formhash
            'inajax': '1',
            'ajaxtarget': 'k_misign_topb'
        }
        
        try:
            response = self.session.get(url, params=params, headers=headers)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 解码响应内容
                content = self.decode_response(response)
                
                # 打印响应内容用于调试
                print(f"响应内容: {content}")
                
                # 检查签到结果
                if '今日已签' in content:
                    print("✓ sjs66.com 签到结果: 今日已签")
                elif '签到成功' in content:
                    print("✓ sjs66.com 签到结果: 签到成功！")
                elif '已经签到' in content:
                    print("✓ sjs66.com 签到结果: 已经签到过了")
                elif 'success' in content.lower():
                    print("✓ sjs66.com 签到结果: 签到成功")
                else:
                    # 检查是否有错误信息
                    if 'error' in content.lower():
                        print(f"? sjs66.com 响应包含错误: {content[:100]}")
                    else:
                        print(f"? sjs66.com 未知响应: {content[:100]}")
            else:
                print(f"× sjs66.com 签到失败: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"× sjs66.com 请求出错: {e}")
            import traceback
            traceback.print_exc()
    
    def checkin_yyg_app(self):
        """yyg.app 签到"""
        print("\n" + "="*50)
        print("正在执行 yyg.app 签到...")
        print("="*50)
        
        url = 'https://yyg.app/wp-admin/admin-ajax.php'
        
        # 注意：这些 cookie 可能已过期，需要更新
        yyg_cookie = (
            'wordpress_sec_646d318c66f2c4c0e1e8624adee79b87=w%20wd%7C1780549759%7CqOz6E2kKo27e23lKj4LOHZrvg0Z9FOE5xZCT7rSWWbz%7C94a7c18ab8cfde45f2850a830b68d99b56e0411302b2639002dceb34e444f8e5; '
            'SITE_TOTAL_ID=ab491cf368396b8ca62e32c98087fe92; '
            'wordpress_logged_in_646d318c66f2c4c0e1e8624adee79b87=w%20wd%7C1780549759%7CqOz6E2kKo27e23lKj4LOHZrvg0Z9FOE5xZCT7rSWWbz%7C7a844f25f483a1561543fcdb6c13fea8f9ca6002cc26aef9e1de8c88ef649069; '
            'history_search=%5B%22%5Cu50ac%5Cu7720%26type%3Dpost%22%2C%22%5Cu8150%5Cu5316%26type%3Dpost%22%2C%22%5Cu5973%5Cu6559%5Cu5e08%26type%3Dpost%22%2C%22%5Cu5251%5Cu661f%26type%3Dpost%22%2C%22%5Cu5c18%5Cu767d%5Cu7981%5Cu533a%26type%3Dpost%22%5D; '
            '_ga=GA1.1.141563258.1768277006; '
            'PHPSESSID=25e4vde8t5air71fnr1kr8qdn4; '
            'server_name_session=9ed527fe0a78f697a86400a9241e5d25'
        )
        
        headers = {
            'Host': 'yyg.app',
            'Origin': 'https://yyg.app',
            'Referer': 'https://yyg.app/',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': yyg_cookie,
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Sec-Ch-UA': '"Microsoft Edge";v="148", "Chromium";v="148", "Not/A)Brand";v="99"',
            'Sec-Ch-UA-Mobile': '?0',
            'Sec-Ch-UA-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        
        data = {'action': 'user_checkin'}
        
        try:
            response = self.session.post(url, headers=headers, data=data)
            print(f"状态码: {response.status_code}")
            
            # 打印原始响应用于调试
            print(f"原始响应: {response.text[:200]}")
            
            # 尝试解析JSON响应
            try:
                result = response.json()
                
                if isinstance(result, dict):
                    message = result.get('msg', '无返回信息')
                    error_status = result.get('error', False)
                    
                    if error_status == True:
                        print(f"✓ yyg.app 签到结果: 已签到或无需签到 - {message}")
                    else:
                        print(f"✓ yyg.app 签到结果: 成功！ - {message}")
                        
                    if 'ys' in result:
                        print(f"状态类型: {result['ys']}")
                elif isinstance(result, (int, str)):
                    print(f"✓ yyg.app 响应: {result}")
                else:
                    print(f"? yyg.app 未知响应类型: {type(result)}")
                    
            except json.JSONDecodeError as je:
                text_response = response.text.strip()
                if text_response:
                    if "已签到" in text_response or "already" in text_response.lower():
                        print("✓ yyg.app 签到结果: 今日已签")
                    elif "成功" in text_response or "success" in text_response.lower():
                        print("✓ yyg.app 签到结果: 签到成功")
                    else:
                        print(f"yyg.app 文本响应: {text_response[:100]}")
                else:
                    print(f"× yyg.app JSON解析错误: {je}")
                    
        except Exception as e:
            print(f"× yyg.app 请求出错: {e}")
            
    def checkin_all(self):
        """执行所有签到"""
        print("\n" + "="*60)
        print(f"开始自动签到 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 执行 sjs66.com 签到
        self.checkin_sjs66()
        
        # 等待1秒，避免请求过于频繁
        time.sleep(1)
        
        # 执行 yyg.app 签到
        self.checkin_yyg_app()
        
        print("\n" + "="*60)
        print("所有签到任务完成！")
        print("="*60)

def main():
    """主函数"""
    print("多站点自动签到脚本")
    print("支持站点: sjs66.com, yyg.app")
    print("-" * 40)
    
    checker = MultiSiteCheckIn()
    
    # 执行所有签到
    checker.checkin_all()
    
    # 询问用户是否要重新运行
 #   while True:
      #  choice = input("\n是否重新运行签到？(y/n): ").lower()
    #    if choice == 'y':
  #          checker.checkin_all()
   #     elif choice == 'n':
   #         print("程序退出。")
   #         break
   #     else:
   #         print("请输入 y 或 n。")

if __name__ == "__main__":
    main()
