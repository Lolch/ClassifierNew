from datetime import datetime
import pytz
import re
import settings
import os

class Email:
    def __init__(self, filepath):
        self.filepath = filepath
        self.contents = self.getFileContents(filepath)
        self.body = self.getBody()
        self.date = self.getDateTz()
        self.sender = self.getFeature('From')
        self.recipient = self.getFeature('To')
        self.subject = self.getFeature('Subject')
        self.bodyLines = self.body.splitlines()
    
    # Read file
    def getFileContents(self, email):
        fp = os.path.join(settings.CORPUS_PATH, email[2:])
        f = open(fp, 'r', encoding='latin1')
        contents = f.read()
        f.close()
        return contents
    
    # Get contents of email
    def getBody(self):
        contains = re.search('X-FileName: (.*?)\Z', self.contents, re.DOTALL) # text between last line of file header & end of file
        found = ''
        if contains:
            found = contains.group(1)
            found = found.split('\n',1)[-1] # remove final line of header from text
        return found[1:]
    
    # Return the value for a feature in the email header
    def getFeature(self, feature):
        if feature == 'To':
            contains = re.findall(feature + ': (.*?)\nSubject', self.contents, re.DOTALL)
        else:
            contains = re.findall(feature + ': (.*?)\n', self.contents) # get text between colon and newline
        if contains:
            return contains[0]
        else: return ''
    
    # Get the timezone string
    def getTimeZone(self):
        tzstring = self.getFeature('Date', self.contents)
        return tzstring[-11:] # remove date and time from start of string
    
    # turn date string into datetime object
    def formatDate(self, date):
        date = date[:-12] # remove timezone
        date = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S')
        return date
    
    # Get date converted to eastern timezone
    def getDateTz(self):
        dateString = self.getFeature('Date')
        #timezone = dateString[-4:-1]
        date = self.formatDate(dateString) # create datetime object
        date_pacific = pytz.timezone('US/Pacific').localize(date)
        date_eastern = date_pacific.astimezone(pytz.timezone('US/Eastern'))
        return date_eastern
    
    # Return name of sender. Name is before first '.', '@', or space (whichever is shorter)
    def getSenderFirstName(self):
        sender = self.getFeature('From')
        
        sendername = sender.split('.')[0]
        sendername = sendername.split('@')[0]
        sendername = sendername.split()[0]
        
        return sendername
    
    # Return list of names of recipients (if there are any)
    def getRecipientFirstNames(self):
        toText = self.getFeature('To')
        
        recipientList = []
        if toText: # if there is a recipient listed
            recipients = toText.split(',') # create a list of all recipients
            for recipient in recipients:
                recipient = recipient.strip() # remove whitespace
                recipientname = recipient.split('.')[0]
                recipientname = recipientname.split('@')[0]
                recipientname = recipientname.split()[0]
                recipientList.append(recipientname)
                
        return recipientList
    
    # Get given number line from email body
    def getLine(self, lineNo):
        number = int(lineNo)-1
        return self.bodyLines[number]
    
    # Calulate proportion of way given line is through email body
    def getPosition(self, lineNo):
        return int(lineNo)/len(self.bodyLines)
    
    # Return number of lines in email body
    def getNoLines(self):
        return len(self.bodyLines)
    
    
    
#e1 = Email('./maildir/allen-p/straw/2.')
#print(e1.date)
#print(e1.sender)
#print(e1.recipient)
#print(e1.subject)
#print(e1.body)
#print('------')
#print(e1.getLine(2))
