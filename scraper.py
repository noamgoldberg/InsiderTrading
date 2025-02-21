from typing import Union, Optional, List
import pandas as pd
import time
from express_vpn import connect_vpn
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import fake_headers
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

class Scraper:
    def __init__(self, headless: bool = True, disable_gpu: bool = True, incognito: bool = False):
        self.driver = self._get_chrome_driver(headless, disable_gpu, incognito)
    
    def _get_chrome_driver(self, headless: bool, disable_gpu: bool, incognito: bool) -> webdriver.Chrome:
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
            header = fake_headers.Headers(
                browser="chrome",  
                os="win",  
                headers=False 
            )
            customUserAgent = header.generate()['User-Agent']
            options.add_argument(f"user-agent={customUserAgent}")
        if disable_gpu:
            options.add_argument("--disable-gpu")
        if incognito:
            options.add_argument("--incognito")
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def get(self, url: str) -> None:
        self.driver.get(url)
    
    def find_element(self, by: str = By.ID, value: str | None = None) -> WebElement:
        return self.driver.find_element(by=by, value=value)
    
    def find_elements(self, by: str = By.ID, value: str | None = None) -> List[WebElement]:
        return self.driver.find_elements(by=by, value=value)
    
    def scrape_tables(self) -> List[pd.DataFrame]:
        tables = self.driver.find_elements(By.TAG_NAME, "table")
        dfs = [pd.read_html(table.get_attribute('outerHTML'))[0] for table in tables]
        return dfs

    def close(self):
        self.driver.quit()
