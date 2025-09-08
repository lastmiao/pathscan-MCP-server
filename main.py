import json
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from pprint import pprint
from fastmcp import  FastMCP
import requests
import config
import concurrent.futures

mcp = FastMCP("path scanner",port=8000)

# 配置存储路径
SCAN_RESULT_DIR = Path("scan_results")
SCAN_RESULT_DIR.mkdir(exist_ok=True)

def dir_scan(url)->str:
    """
    对网站进行目录扫描, 返回扫描后的结果

    Args:
        url(str):需要进行目录扫描的网站
    Returns:
        返回扫描结果文件的的文件路径
    """
    # 生成结果文件路径
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = SCAN_RESULT_DIR / f"scan_{timestamp}.json"

    # 构建扫描命令 
    python_global_path = config.GLOBAL_PYTHON_PATH             
    base_cmd = [
        python_global_path,
        "./dirsearch/dirsearch.py",
        "-u", url,
        "-o", str(output_file),
        "--format=json",
        "-q",
        "--no-color",
    ]
    subprocess.run(
        base_cmd,
        check=True,
        text=True 
    )
    print("扫描完成")
    #返回扫描结果的文件路径
    return str(output_file)


def process_data(output_file_path)->dict:
    """
    将目录扫描的结果进行简化, 只保留响应码和对应的路径
    """
    
    with open(output_file_path,"r",encoding="UTF-8") as file:
        output_data = json.load(file)
    
    #创建一个值为list的dict
    an = defaultdict(list)


    output_data = output_data.get("results")
    for i_json in output_data:
        i_status = i_json.get("status")
        i_url = i_json.get("url")
        an[i_status].append(i_url)
    
    pprint(dict(an))
    return dict(an)#不然的话会多打印出an的数据类型


@mcp.tool()
def pathscan_andProcess(url:str)->dict:
    """
    对网站进行路径扫描

    Args:
        url(str类型):需要进行路径扫描的网站的URL
    Returns:
        返回结构化的json数据, key为响应码, values为响应码对应的URL列表
    """
    error_json = {"err":""}
    try:
        output_file_path = dir_scan(url)
        scan_andProcess_an = process_data(output_file_path)
    except Exception as e:
        error_json["err"]=str(e)
        return error_json
    return scan_andProcess_an



@mcp.tool()
def get_urlContents_byFireCrawl(urls: list[str], thread_count: int = 8) -> dict:
    """
    使用firecrawl对网页内容进行爬取, 并返回清洗后的结果
    使用线程池并行处理请求
    
    Args:
        urls (list): 一个列表, 内容是URL
        thread_count (int): 线程池大小, 默认为8
    Returns:
        返回一个json格式的数据, key是URL, value是URL对应的内容
    """
    def scrape_website(url: str) -> str:
        """
        调用firecrawl的API接口进行网页内容的抓取并清洗
        """
        api_url = f"http://{config.FIRECRAWL_HOST}:{config.FIRECRAWL_PORT}/v1/scrape"
        headers = {'Content-Type': 'application/json'}
        data = {"url": url, "formats": ["markdown"]}
        
        try:
            response = requests.post(api_url, headers=headers, json=data, timeout=10)
            response.raise_for_status()  # 检查HTTP错误
            result = response.json()
            
            # 检查API返回的错误
            if 'error' in result:
                return f"Firecrawl error: {result['error']}"
                
            return result.get('data', {}).get('markdown', '')
        except requests.exceptions.RequestException as e:
            return f"Request failed: {str(e)}"
        except json.JSONDecodeError:
            return "Invalid JSON response"
        except Exception as e:
            return f"Unexpected error: {str(e)}"
    
    results = {}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=thread_count) as executor:
        future_to_url = {executor.submit(scrape_website, url): url for url in urls}

        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                results[url] = future.result()
            except Exception as e:
                results[url] = f"Processing error: {str(e)}"
    
    return results


if __name__ == "__main__":
    mcp.run("sse")