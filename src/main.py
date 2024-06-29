import logging
import json
import time
import datetime

from tempfile import mkdtemp
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import telegram
import asyncio

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def initialise_driver():
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-tools")
    chrome_options.add_argument("--no-zygote")
    chrome_options.add_argument("--single-process")
    chrome_options.add_argument(f"--user-data-dir={mkdtemp()}")
    chrome_options.add_argument(f"--data-path={mkdtemp()}")
    chrome_options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    chrome_options.add_argument("--remote-debugging-pipe")
    chrome_options.add_argument("--verbose")
    chrome_options.add_argument("--log-path=/tmp")
    chrome_options.binary_location = "/opt/chrome/chrome-linux64/chrome"

    service = Service(
        executable_path="/opt/chrome-driver/chromedriver-linux64/chromedriver",
        service_log_path="/tmp/chromedriver.log"
    )

    driver = webdriver.Chrome(
        service=service,
        options=chrome_options
    )

    return driver

def main(driver) -> None:
    print(datetime.datetime.now())
    print("Starting")
    msg = ""
    try:
        print("driver")
        driver.get("https://visas-de.tlscontact.com/visa/ie/ieDUB2de/home")
        asyncio.sleep(1)
        elem = driver.find_element(By.XPATH, "//*[contains (text(),'Login')]")
        elem.click()
        print("Found login")
        asyncio.sleep(5)
        elem = driver.find_element(By.NAME, "username")
        elem.clear()
        elem.send_keys("name")
        elem = driver.find_element(By.NAME, "password")
        elem.clear()
        elem.send_keys("pw")
        elem.send_keys(Keys.RETURN)
        print("Managed login")
        asyncio.sleep(2)
        driver.get("https://visas-de.tlscontact.com/appointment/ie/ieDUB2de/2524620")
        print("Appointments")
        asyncio.sleep(15)
        print("sending message")
        if "Sorry, there is no available appointment at the moment, please check again later." not in driver.page_source:
            print("appointment found")
            msg = "appointment found"
        else:
            msg = "nothing"
            print("nothing")
    except Exception as e:
        print(str(e))
        msg = 'Error + ' + str(e)
    print("finished")
    driver.close()
    return msg

async def send_ms(msg):
    bot = telegram.Bot("6469377202:AAE2-tphnAU3uzRyfuEMsYnbvnI25H2jhFo")
    print("got bot and sending : " + str(msg))
    with bot:
        await bot.send_message(text=msg, chat_id=13446158)
        time.sleep(1)

def lambda_handler(event, context):
    msg = main(initialise_driver())
    asyncio.run(send_ms(msg))

    response = {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(msg)
    }

    return response

if __name__ == '__main__':
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    options = FirefoxOptions()
    options.add_argument("--headless")
    msg = main(driver = webdriver.Firefox(options=options))
    asyncio.run(send_ms(msg))