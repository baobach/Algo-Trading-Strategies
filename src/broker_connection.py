# Import the required module from the fyers_apiv3 package
from fyers_apiv3 import fyersModel
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options 
import time
import pyotp as tp
from config import Settings

class BrokerConnection:
    def __init__(self, client_id, secret_key, user_name, totp_key, pin1, pin2, pin3, pin4):
        self.client_id = client_id
        self.secret_key = secret_key
        self.user_name = user_name
        self.totp_key = totp_key
        self.pin1 = pin1
        self.pin2 = pin2
        self.pin3 = pin3
        self.pin4 = pin4
        self.response_type = "code"
        self.redirect_uri = "https://www.google.com/"
        self.state = "sample_state"
        self.grant_type = "authorization_code"

    def connect(self):

        # Create a session model with the provided credentials
        session = fyersModel.SessionModel(
            client_id = self.client_id,
            secret_key = self.secret_key, 
            redirect_uri = self.redirect_uri, 
            response_type = self.response_type, 
            grant_type = self.grant_type
        )

        # Generate the auth code using the session model
        response = session.generate_authcode()


        # Initialize a Chrome webdriver
        driver = webdriver.Chrome()

        #options = Options()
        #options.add_argument('--headless=new')

        #Initializing Chrome Webdriver
        #driver = webdriver.Chrome(options=options)


        # Open the URL using the webdriver
        driver.get(response)

        time.sleep(1)
        login_with_client_id_x_path='//*[@id="login_client_id"]'
        elem = driver.find_element(By.XPATH, login_with_client_id_x_path)
        elem.click()
        time.sleep(1)
        client_id_x_path='//*[@id="fy_client_id"]'
        elem2 = driver.find_element(By.XPATH, client_id_x_path)
        elem2.send_keys("XM26206")
        elem2.send_keys(Keys.RETURN)
        time.sleep(1)

        t=tp.TOTP(self.totp_key).now()



        driver.find_element(By.XPATH,'//*[@id="first"]').send_keys(t[0])
        driver.find_element(By.XPATH,'//*[@id="second"]').send_keys(t[1])
        driver.find_element(By.XPATH,'//*[@id="third"]').send_keys(t[2])
        driver.find_element(By.XPATH,'//*[@id="fourth"]').send_keys(t[3])
        driver.find_element(By.XPATH,'//*[@id="fifth"]').send_keys(t[4])
        driver.find_element(By.XPATH,'//*[@id="sixth"]').send_keys(t[5])

        driver.find_element(By.XPATH, '//*[@id="confirmOtpSubmit"]').click()
        time.sleep(1)

        driver.find_element(By.ID,"verifyPinForm").find_element(By.ID,"first").send_keys(self.pin1)
        driver.find_element(By.ID,"verixfyPinForm").find_element(By.ID,"second").send_keys(self.pin2)
        driver.find_element(By.ID,"verifyPinForm").find_element(By.ID,"third").send_keys(self.pin3)
        driver.find_element(By.ID,"verifyPinForm").find_element(By.ID,"fourth").send_keys(self.pin4)

        driver.find_element(By.XPATH,'//*[@id="verifyPinSubmit"]').click()

        time.sleep(1)
        newurl = driver.current_url
        auth_code = newurl[newurl.index('auth_code=')+10:newurl.index('&state')]

        # Close the webdriver
        driver.close()

        # Set the authorization code in the session object
        session.set_token(auth_code)

        # Generate the access token using the authorization code
        response = session.generate_token()

        # Set the access token in the session object
        access_token = response['access_token']

        return access_token
    
if __name__ == "__main__":
    broker = BrokerConnection(Settings().client_id, Settings().secret_key, Settings().user_name, Settings().totp_key, Settings().pin1, Settings().pin2, Settings().pin3, Settings().pin4)
    print(broker.connect())
