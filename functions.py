def import_or_install2(package,installOnly=False):
    #src: https://www.activestate.com/resources/quick-reads/how-to-install-python-packages-using-a-script/
    dev_print_installedpackages = False
    try:
        __import__(package)
        print('Package {} is being used.'.format(package))
    except ImportError:
        import sys
        import subprocess
        # check original_installed_packages
        reqs0 = subprocess.check_output([sys.executable, '-m', 'pip','freeze'])
        original_installed_packages = [r.decode().split('==')[0] for r in reqs0.split()]
        if(package in original_installed_packages):
            print(f'Package {package} exists.')
        else:
            print(f'Package {package} does not exist and will be installed.')

        # implement pip as a subprocess:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        # process output with an API in the subprocess module:
        reqs = subprocess.check_output([sys.executable, '-m', 'pip','freeze'])
        
        if(dev_print_installedpackages):
            installed_packages = [r.decode().split('==')[0] for r in reqs.split()]
            print(installed_packages)

        if(not(package in original_installed_packages)):
            print('Package {} has been installed.'.format(package))
        if(installOnly):return
        
        try:
            __import__(package)
        except ImportError:
            print(f'{bcolors.FAIL}Package "{package}" can not be imported. Notify the developer to update.{bcolors.ENDC}')

def uninstall(package):
    #src: https://stackoverflow.com/questions/5189199/bypass-confirmation-prompt-for-pip-uninstall
    import subprocess
    subprocess.check_call(['pip', 'uninstall', '-y',package])
    
#Class for colours of printouts
#src: https://stackoverflow.com/questions/287871/how-to-print-colored-text-in-python
disable_bcolors = False
class bcolors:
    if(disable_bcolors):
        HEADER = ''
        OKBLUE = ''
        OKCYAN = ''
        OKGREEN = ''
        WARNING = ''
        FAIL = ''
        ENDC = ''
        BOLD = ''
        UNDERLINE = ''
    else:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKCYAN = '\033[96m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

global log_file_path
log_file_path=""
# to handle logging to file
# src: https://stackoverflow.com/questions/14906764/how-to-redirect-stdout-to-both-file-and-console-with-scripting
class Logger(object):  
    def __init__(self):
        import sys
        self.terminal = sys.stdout
        file_path = log_file_path or "python_logs"
        self.log = open(file_path, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  

    def flush(self):
        #this flush method is needed for python 3 compatibility.
        #this handles the flush command by doing nothing.
        #you might want to specify some extra behavior here.
        pass    

#check operating system
def get_platform():
    import sys
    platforms = {
        'linux1':'Linux',
        'linux2':'Linux',
        'darwin':'OS X',
        'win32':'Windows',
        'win64':'Windows',
    }
    if sys.platform not in platforms:
        return sys.platform
    
    return platforms[sys.platform]

#Get inner text of element in selenium
def get_text_excluding_children(driver, element):
    return driver.execute_script("""
    return jQuery(arguments[0]).contents().filter(function() {
        return this.nodeType == Node.TEXT_NODE;
    }).text();
    """, element)

# function to take care of downloading file
def enable_download_headless(browser,download_dir):
    #src: https://medium.com/@moungpeter/how-to-automate-downloading-files-using-python-selenium-and-headless-chrome-9014f0cdd196
    browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    browser.execute("send_command", params)

# function to highlight elements using selenium for debugging
def highlight(element, effect_time=1, color="red", border=5):
    # src: https://stackoverflow.com/questions/52207164/python-selenium-highlight-element-doesnt-do-anything
    # call this function like so: highlight(parent_elem, 3, "blue", 5)
    import time
    from selenium.webdriver.common.action_chains import ActionChains
    
    """Highlights (blinks) a Selenium Webdriver element"""
    driver = element._parent
    # move to element
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()
    # apply style
    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",element, s)
    original_style = element.get_attribute('style')
    apply_style("border: {0}px solid {1};".format(border, color))
    time.sleep(effect_time)
    apply_style(original_style)

# throttle network in kbps
def driver_throttle_network(driver,dl_throttle=250,up_throttle=250,v_latency=5,v_offline=False):
    #src: https://stackoverflow.com/questions/27881485/network-throttling-with-chrome-and-selenium
    if(dl_throttle<=1):dl_throttle=1
    if(up_throttle<=1):up_throttle=1
    if(v_latency<=0):v_latency=0
    print(f'{bcolors.WARNING}throttling network (kbps).{bcolors.ENDC} dl_throttle:{dl_throttle}, up_throttle:{up_throttle}, latency:{v_latency}ms')
    driver.set_network_conditions(
        offline=v_offline,
        latency=v_latency,  # additional latency (ms)
        download_throughput=dl_throttle/8 * 1024,  # maximal throughput
        upload_throughput=up_throttle/8 * 1024 # maximal throughput
    )
def driver_reset_throttle_network(driver):
    print(f'{bcolors.OKGREEN}throttling network reset.{bcolors.ENDC}')
    driver.set_network_conditions(
        offline=False,
        latency=0,  # additional latency (ms)
        download_throughput=500000 * 1024,  # maximal throughput
        upload_throughput=500000 * 1024 # maximal throughput
    )