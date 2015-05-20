#!/usr/bin/python


# General stuff
import unittest
import selenium.webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time

import re
import urllib


# Spacescout-specific stuff
import maildata
import mailcheck
import ssdata
import netid
from netid import weblogin


# Connect all our IMAP connections to save time later
# TODO: Make this only happen if we're actually doing mail tests
#for em in maildata.emails.values():
#    em.connect()

# Load settings from files
urlbase = ssdata.urlbase
testnetid = netid.testnetid

# Get the last email in a mailUser object's inbox
def getLastMail(user):
    return(user.getlast())

# Navigate to login page and send email
def sendEmail(driver, Space = ssdata.exampleSpace, emails = None, From = None, Subject = None, Message = None):
    """Navigates the specified webdriver to the page to share the given space. 
    
    sendEmail(driver, Space = exampleSpace, emails = None, From = None, Subject = None, Message = None)

    Fills in the form according to emails (an iterable containing the email addresses to put in the "to" field), From, Subject, and Message.
    """

    d = driver
    url = ssdata.shareurl %{'id' : str(Space)}
    d.get(url)

    # If we need to sign in, do that
    if d.title == 'UW NetID Weblogin':
        weblogin(d)
        time.sleep(1)

    time.sleep(1)

    # Check to make sure the back button goes to the right place
    e = driver.find_element_by_xpath('//a[@title="Back to space details"]')
    url = e.get_attribute('href')
    expurl = ssdata.spaceurl % {'id' : str(Space)}
    if not(expurl ==  url):
        pass
        # TODO
        #raise(Exception('Did not find correct back button href. \nExpected "%s", got "%s"' %(expurl, url)))

    # If these were supplied, fill out the corresponding fields
    # It's necessary to use 'if X != None' rather than 'if X'
    # because a blank string will bool() to false. 
    if From != None:
        e = d.find_element_by_name('sender')
        e.clear()
        e.send_keys(From)

    if emails != None:
        try:
            # Grab page source in case we need to debug later
            source = d.page_source.encode('utf8')
            try: # The autocomplete script changes this box
                e = d.find_element_by_name('recipient')
                e.clear()
            except:
                time.sleep(1)
                #e = d.find_element_by_id('id_recipient-tokenfield')
                e = d.find_element_by_class_name('tt-input')
                e.clear()

            # Put in each recipient address
            for user in emails:
                #address = maildata.emails[user].address
                address = user
                # Have to send a tab after each one
                e.send_keys(address + '\t')
        # Debugging stuff:
        # If it couldn't find the box, dump the source collected earlier
        # so that we can figure out why. 
        except Exception as E:
            outfile = open('source-%s.html' %str(int(time.time())), 'wb')
            outfile.write(source)
            outfile.close()
            raise(E)

    if Subject != None:
        e = d.find_element_by_name('subject')
        e.clear()
        e.send_keys(Subject)


    if Message != None:
        e = d.find_element_by_name('message')
        e.clear()
        e.send_keys(Message)

    # Submit the form
    e = d.find_element_by_id('formSubmit_button')
    time.sleep(1)
    e.submit()
    time.sleep(1)

# Checks to see if pattern is in string, accounting for 
# different types of newlines by converting all newlines
# in both strings to line feeds
def msgCheck(pattern, string):
    if pattern in string: # Simple check first
        return True
    newPattern = re.sub('(\r\n|\r|\n)', '\n', pattern)
    newString = re.sub('(\r\n|\r|\n)', '\n', string)
    return newPattern in newString




# Test class for email-related things
class ss_email(unittest.TestCase):
    
    # Load webdriver
    def setUp(self):
        self.driver = selenium.webdriver.Firefox()
        self.driver.maximize_window()
        self.action = ActionChains(self.driver)


    # Send a space to mailtest with the default settings
    def test_one_space(self):
        self.send_and_check_email()
        
    # Test sending to multiple addresses at once
    def test_multiple_emails(self):
        self.send_and_check_email(emails = ('external1', 'gmail1'))
    
    # Send a space to mailtest with a custom subject
    def test_custom_subject(self):
        self.send_and_check_email(Subject = 'Blah blah')

    # Send a space to 'lisatest' 
    def test_gmail(self):
        self.send_and_check_email(emails = ('gmail1',))

    # Test a custom body
    def test_custom_body(self):
        self.send_and_check_email(Message = 'This is a test custom body')

    # Test a custom body with multiple lines
    def test_custom_body_multiline(self):
        self.send_and_check_email(Message = 'This is a\ncustom body\nwith multiple\nlines.')

    # Test a custom "from"
    def test_custom_from(self):
        self.send_and_check_email(From = 'test@test.com')

    # Test another space
    def test_another_space(self):
        self.send_and_check_email(Space = 4337)

    
    # Failure tests

    # Make sure failure to supply a "To" address gives an error
    def test_no_to_address(self):
        sendEmail(self.driver)
        e = self.driver.find_element_by_xpath('//span[@class="alert-error"]')
        self.assertEquals(e.text, u'Required field')

    # Make sure invalid "To" address gives us an error
    def test_invalid_to_address(self):
        sendEmail(self.driver, emails = ('asdf',))
        e = self.driver.find_element_by_xpath('//span[@class="alert-error"]')
        self.assertIn('not a valid e-mail address', e.text)

    # Make sure missing "From" address gives us an error
    def test_no_from_address(self):
        sendEmail(self.driver, emails = ('test@test.com',), From = '')
        e = self.driver.find_element_by_xpath('//span[@class="alert-error"]')
        self.assertEquals(e.text, u'Required field')
        
    # Make sure invalid "From" address gives us an error
    def test_invalid_from_address(self):
        sendEmail(self.driver, emails = ('test@test.com',), From = 'asdf')
        e = self.driver.find_element_by_xpath('//span[@class="alert-error"]')
        self.assertIn('Enter a valid e-mail address', e.text)

    




    # Function for sending a space via the email page
    def send_and_check_email(self, driver = None, emails = ('external1',), Space = ssdata.exampleSpace, From = None, Subject = None, Message = None):
        """Sends an email via the share page, and checks to make sure it was received
        
        send_and_check_email(driver = None, emails = ('eternal1',), Space = exampleSpace, From = None, Subject = None, Message = None)
        
        If driver is not specified, then self.driver will be assumed. All the arguments are optional, and will not be specified nor checked. 
        """
        
        users = []
        for user in emails:
            users.append(maildata.emails[user])

        rcpts = []
        for user in emails:
            rcpts.append(maildata.emails[user].address)
            
        if not(driver):
            driver = self.driver

        sendEmail(driver, Space, rcpts, From, Subject, Message)


        time1 = time.time()
        
        time.sleep(2)

        # Back button broken 
        # TODO
        e = driver.find_element_by_xpath('//a[@title="Back to space details"]')
        url = e.get_attribute('href')

        #self.assertEquals(ssdata.spaceurl %{'id' : str(Space)}, url)
        
        e.click()

        #self.assertEquals(ssdata.spaceurl %{'id' : str(Space)}, driver.current_url)


        time.sleep(max(time1 - time.time() + maildata.delay, 0))
        
        for user in users:

            msg = getLastMail(user)
            rcpt = user.address

            
            if Subject:
                self.assertEqual(Subject, msg.Subject)
            else:
                self.assertEqual('Check out this space I found on SpaceScout', msg.Subject)

            if From:
                self.assertEqual(From, msg.From)

            self.assertEqual(rcpt, msg.To)


            if Message:
                for msgbody in msg.body:
                    self.assertTrue(msgCheck(Message, msgbody.text), 'Custom message %s not found in body %s' %(Message, msgbody.text))
                    
            

        

    def tearDown(self):
        self.driver.close()

# End of email stuff

# Favorites testing stuff

def go_to_space(d, Space):
    """Navigates to a space page with the specified ID."""
    d.get(ssdata.spaceurl % {'id' : str(Space)})

def favorite_current_space(d):
    """Clicks the favorite button on the current space page."""
    e = get_favorite_button(d) 
    e.click()

def ss_login(d):
    """Browses to the login page and logs in."""
    d.get(ssdata.loginurl)
    netid.weblogin(d)

def get_favorite_button(d):
    """Returns the favorite button for the current space page."""
    return d.find_element_by_xpath('//button[@id="favorite_space"]')

def go_to_favorites(d):
    """Browses to the favorites page."""
    d.get(ssdata.faveurl)
    
testspace = ssdata.exampleSpace

class ss_faves(unittest.TestCase):

    def setUp(self):
        self.driver = selenium.webdriver.Firefox()
        self.driver.maximize_window()
    
    # Tests only logging in. Logs out afterwards. 
    def test_login_only(self):
        d = self.driver
        d.get(ssdata.urlbase)
        time.sleep(2)
        try:
            d.find_element_by_link_text('Log in')
        except:
            self.fail('Could not find log in button')
        go_to_space(d, testspace)
        time.sleep(2)
        e = d.find_element_by_link_text('Log in')
        e.click()
        time.sleep(2)
        netid.weblogin(d)
        time.sleep(8)
        try:
            d.find_element_by_link_text('Log out')
        except:
            self.fail('Could not find log out button')
        
            
    # Tests favoriting and unfavoriting a space. 
    def test_favorite_and_unfavorite(self):
        s = testspace
        d = self.driver

        ss_login(self.driver)
        time.sleep(2)
        go_to_space(d, s)
        time.sleep(8)
        e = get_favorite_button(d)
        e.click()
        time.sleep(1)
        self.assertEquals(e.text, 'Favorited')
        e.click()
        time.sleep(1)
        self.assertEquals(e.text, 'Favorite')

    # Tests favoriting a space, and checks the favorites page
    # to make sure it's there. 
    def test_favorite_and_check(self):
        s = testspace
        d = self.driver

        ss_login(self.driver)
        time.sleep(2)
        go_to_space(d, ssdata.exampleSpace)
        time.sleep(8)
        favorite_current_space(d)
        time.sleep(1)
        go_to_favorites(d)
        time.sleep(2)
        e = d.find_element_by_xpath('//a[@data-id="%s"]' %str(s))
        e.click()
        time.sleep(2)
        try:
            e = d.find_element_by_xpath('//a[@data-id="%s"]' %str(s))
            raise Exception('Space still in favorites after being removed')
        except selenium.common.exceptions.NoSuchElementException as e:
            pass
        except Exception as e:
            raise e

    # Tests to see that upon favoriting a space while logged out, you
    # are then redirected to the login page. If you choose to log in, 
    # then the space will be favorited. 
    def test_favorite_logged_out(self):
        s = testspace
        d = self.driver

        go_to_space(d, s)
        time.sleep(1)

        favorite_current_space(d)
        time.sleep(1)

        try:
            a = d.switch_to_alert()
            a.dismiss()
        except:
            pass

        netid.weblogin(d)

        time.sleep(8)

        e = d.find_element_by_xpath('//button[@id="favorite_space"]')
        self.assertEquals(e.text, 'Favorited')

        favorite_current_space(d)
        time.sleep(1)

        e = d.find_element_by_xpath('//button[@id="favorite_space"]')
        self.assertEquals(e.text, 'Favorite')

    # Tests to see if browsing to the favorites page while logged
    # out will redirect you to the login page, and then back to the 
    # favorites page after logging out. 
    def test_favorites_login_redirect(self):
        d = self.driver
        go_to_favorites(d)
        time.sleep(2)

        self.assertIn('weblogin.washington.edu', d.current_url)

        netid.weblogin(d)
        time.sleep(2)

        self.assertEquals(ssdata.faveurl, d.current_url)


    # Test favoriting a space that is already favorited while being
    # logged out. 
    # Expected: User is prompted to log in. After logging in, 
    # space stays favorited. 
    def test_already_favorited_logged_out(self):
        d = self.driver
        s = testspace
        
        ss_login(d)
        time.sleep(2)
        go_to_space(d, s)
        time.sleep(5)
        favorite_current_space(d)
        
        d2 = selenium.webdriver.Firefox()
        
        go_to_space(d2, s)
        time.sleep(5)
        favorite_current_space(d2)
        time.sleep(2)
        try:
            a = d2.switch_to_alert()
            a.dismiss()
        except:
            pass
    
        netid.weblogin(d2)
        time.sleep(5)

        e = get_favorite_button(d2)
        self.assertEquals(e.text, 'Favorited')
        e.click()
        time.sleep(1)
        self.assertEquals(e.text, 'Favorite')

        d2.close()




    def tearDown(self):
        self.driver.close()

        

if __name__ == '__main__':
    unittest.main()
