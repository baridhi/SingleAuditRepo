import os
import ssl
import sys
import time
import urllib.request
from azure.storage.file import FileService, ContentSettings
from ftplib import FTP, error_perm
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from fileinput import filename

class Crawler:
    def __init__(self, config, section):
        self.section = section
        self.downloads_path = config.get(section, 'downloads_path', fallback='/tmp/downloads/')
        if not os.path.exists(self.downloads_path):
            os.makedirs(self.downloads_path)
        elif not os.path.isdir(self.downloads_path):
            print('ERROR:{} downloads_path parameter points to file!'.format(section))
            sys.exit(1)
        if config.getboolean('general', 'headless_mode', fallback=False):
            display = Display(visible=0, size=(1920, 1080))
            display.start()
        self.config = config
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        prefs = {
            'download.default_directory': self.downloads_path,
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'plugins.always_open_pdf_externally': True,
        }
        options.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(chrome_options=options, service_args=["--verbose", "--log-path=/tmp/selenium.log"])
        self.browser.implicitly_wait(10)

        #self.ftp_connect()
        self.file_storage_connect()
        
    def file_storage_connect(self):
        self.file_storage_url = self.config.get('general','fs_server').strip()
        self.file_storage_user = self.config.get('general','fs_username')
        self.file_storage_pwd = self.config.get('general','fs_password')
        self.file_storage_share = self.config.get('general','fs_share')
        self.file_storage_dir = self.config.get('general','fs_directory_prefix')
        self.file_service = FileService(account_name=self.file_storage_user, account_key=self.file_storage_pwd) 
        try:
            if self.file_service.exists(self.file_storage_share):
                print('Connection to Azure file storage successfully established...')
                if len(self.file_storage_dir)>0 and not self.file_service.exists(self.file_storage_share, directory_name=self.file_storage_dir):
                    self.file_service.create_directory(self.file_storage_share, self.file_storage_dir)
                    print('Created directory:' + self.file_storage_dir)
            else:
                print('Filaed to connect to Asure file storage, share does not exist: '+ self.file_storage_share)
        except Exception as ex:
            print('Error connecting to Azure file storage: ', ex)
        
    def ftp_connect(self):
        self.ftp = FTP()
        self.ftp.connect(
            self.config.get('general', 'ftp_server').strip(),
            int(self.config.get('general', 'ftp_port')),
        )
        self.ftp.login(
            user=self.config.get('general', 'ftp_username').strip(),
            passwd=self.config.get('general', 'ftp_password').strip(),
        )
        print('Connection to ftp successfully established...')

    def get(self, url):
        self.browser.get(url)
        time.sleep(3)

    def assert_exists(self, selector):
        _ = self.browser.find_element_by_css_selector(selector)

    def get_elements(self, selector, root=None):
        if root is None:
            root = self.browser
        return root.find_elements_by_css_selector(selector)

    def wait_for_displayed(self, selector):
        element = self.browser.find_element_by_css_selector(selector)
        while not element.is_displayed():
            pass

    def click_by_text(self, text):
        self.browser.find_element_by_link_text(text)
        time.sleep(3)

    def click_xpath(self, path, single=True):
        if single:
            self.browser.find_element_by_xpath(path).click()
        else:
            for el in self.browser.find_elements_by_xpath(path):
                el.click()
        time.sleep(3)

    def click(self, selector, single=True, root=None):
        if root is None:
            root = self.browser
        if single:
            root.find_element_by_css_selector(selector).click()
        else:
            for el in root.find_elements_by_css_selector(selector):
                el.click()
        time.sleep(3)

    def send_keys(self, selector, keys):
        elem = self.browser.find_element_by_css_selector(selector)
        elem.clear()
        elem.send_keys(keys)
        time.sleep(3)

    def open_new_tab(self):
        self.browser.execute_script("window.open('');")
        self.browser.switch_to.window(self.browser.window_handles[1])

    def close_current_tab(self):
        self.browser.close()
        self.browser.switch_to.window(self.browser.window_handles[-1])

    def get_text(self, selector, single=True, root=None):
        if root is None:
            root = self.browser
        if single:
            return root.find_element_by_css_selector(selector).text
        return [el.text for el in root.find_elements_by_css_selector(selector)]

    def get_attr(self, selector, attr, single=True, root=None):
        if root is None:
            root = self.browser
        if single:
            return root.find_element_by_css_selector(selector).get_attribute(attr)
        return [el.get_attribute(attr) for el in root.find_elements_by_css_selector(selector)]

    def execute(self, script):
        self.browser.execute_script(script, [])
        time.sleep(3)

    def deselect_all(self, selector):
        select = Select(self.browser.find_element_by_css_selector(selector))
        select.deselect_all()
        time.sleep(3)

    def select_option(self, selector, option):
        select = Select(self.browser.find_element_by_css_selector(selector))
        select.select_by_visible_text(option)
        time.sleep(3)

    def select_option_by_index(self, selector, index):
        select = Select(self.browser.find_element_by_css_selector(selector))
        if index < len(select.options):
            select.select_by_index(index)
            time.sleep(3)
            return True
        return False

    def back(self):
        self.browser.back()
        time.sleep(3)

    def close(self):
        self.browser.quit()
        self.ftp.quit()

    def download(self, url, filename):
        #print('Downloading', filename, self._get_remote_filename(filename))
        #return
        if url.startswith('https'):
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        else:
            ctx = None
        
        content_length = 1
        retry = 0
        file_size = 0
        file_name = ''
        while file_size != content_length and retry<3:
            try:
                r = urllib.request.urlopen(url, context=ctx)
                content_length = r.length
                file_name = os.path.join(self.downloads_path, filename)
                with open(file_name, 'wb') as f:
                    f.write(r.read())
                    file_size = os.stat(file_name).st_size
                    retry += 1
                    #print('Attempt', retry, 'Downloaded', file_size, 'bytes of', content_length)
            except Exception as e:
                retry +=1
                print('Attempt', retry, 'ERROR: Downloading failed!', url, str(e))
                try:  
                    os.remove(file_name)
                except OSError:
                    pass 


    def _get_remote_filename(self, local_filename):
        raise NotImplemented

    def merge_files(self, filenames):
        pdfline = ' '.join(filenames)
        res_filename = filenames[0].split(' part')[0] + '.pdf'
        command = 'pdftk ' + pdfline + ' cat output ' + res_filename
        os.system(command)
        return res_filename

    def upload_to_ftp(self,filename):
        self.upload_to_file_storage(filename)

    def upload_to_ftp_old(self, filename):
        retries = 0
        while retries<3:
            try:
                path = os.path.join(self.downloads_path, filename)
                #print('Uploading {}'.format(path))
                pdf_file = open(path, 'rb')
                remote_filename = self._get_remote_filename(filename)
                if not remote_filename:
                    return
                directory, filename = remote_filename
                try:
                    self.ftp.cwd('/{}'.format(directory))
                except Exception:
                    self.ftp.mkd('/{}'.format(directory))
                    self.ftp.cwd('/{}'.format(directory))
                if not self.config.getboolean(self.section, 'overwrite_remote_files', fallback=False):
                    #print('Checking if {}/{} already exists'.format(directory, filename))
                    try:
                        self.ftp.retrbinary('RETR {}'.format(filename), lambda x: x)
                        return
                    except error_perm:
                        pass
    
                self.ftp.storbinary('STOR {}'.format(filename), pdf_file)
                #print('{} uploaded'.format(path))
                pdf_file.close()
                retries =3
            except Exception as e:
                print('Error uploading to ftp,', str(e))
                retries+=1
                try:
                    self.ftp.voidcmd("NOOP")
                except Exception as ex:
                    self.ftp_connect()


    def move_to_another(self, filename):
        try:
            entity_type = filename.split('|')[1]
            remote_filename = self._get_remote_filename(filename)
            if not remote_filename:
                return
            if (entity_type == 'County') or (entity_type == 'City') or \
                    (entity_type == 'Township') or (entity_type == 'Village'):
                return
            directory, server_filename = remote_filename
            self.ftp.rename('/General Purpose/{}'.format(server_filename), '/{}/{}'.format(directory, server_filename))
            print('Moved {} to {}'.format(server_filename, directory))
        except Exception as e:
            print(str(e))
            
    def upload_to_file_storage(self,filename):
        retries = 0
        while retries<3:
            try:
                path = os.path.join(self.downloads_path, filename)
                print('Uploading {}'.format(path))
                remote_filename = self._get_remote_filename(filename)
                if not remote_filename:
                    return
                try:
                    directory, filename, year = remote_filename
                except:
                    directory, filename = remote_filename
                if len(self.file_storage_dir)>0:
                    directory = self.file_storage_dir+'/'+directory
                if not self.file_service.exists(self.file_storage_share,directory_name=directory):
                    self.file_service.create_directory(self.file_storage_share,directory)
                if year:
                    directory = self.file_storage_dir+'/'+year
                    if not self.file_service.exists(self.file_storage_share,directory_name=directory):
                        self.file_service.create_directory(self.file_storage_share,directory)
                if not self.config.getboolean(self.section, 'overwrite_remote_files', fallback=False):
                    print('Checking if {}/{} already exists'.format(directory, filename))
                    if self.file_service.exists(self.file_storage_share,directory_name=directory, file_name=filename):
                        print('{}/{} already exists'.format(directory, filename))
                        return
                self.file_service.create_file_from_path(
                    self.file_storage_share,
                    directory,
                    filename,
                    path,
                    content_settings=ContentSettings(content_type='application/pdf'))    
                print('{} uploaded'.format(path))
                retries =3
            except Exception as e:
                print('Error uploading to Asure file storage,', str(e))
                retries+=1