import json, requests

class UnifiVideoServerComm:
    '''
        A basic python api to interface with the unifi nvr system
        Most of this was gleamed from the unofficial unifi video api.
        https://unifivideo1.docs.apiary.io/#reference/0/camera-recording/get-camera-recording?console=1
    '''
    def __init__(self,serverIP,serverPort):
        self.serverIP = serverIP
        self.serverPort = serverPort
        self.cookies = None #Will be set on login
        self.defaultHeaders = {'Content-Type': 'application/json'}
        #This is bad. Only doing this because unifi doesn't have a valid certificate
        self.verify = False
        requests.packages.urllib3.disable_warnings() 
        
    def login(self, username, password):
        '''
            Login to the server using the specified username and password.
            Returns False if the login attempt failed.
            This must be called prior to any other method.
        '''
        url = 'https://{}:{}/api/2.0/login'.format(self.serverIP,self.serverPort)
        headers = {'Content-Type': 'application/json'}
        jsonData = {'email':username, 'password':password}
        r = requests.post(url, json=jsonData, verify=False, headers=headers)
        if (r.status_code == requests.codes.ok):
            self.cookies = r.cookies
            return True
        else:
            print("Login Failed! Check the password and server address.")
            return False
    
    def getServerInfo(self):
        url = 'https://{}:{}/api/2.0/server/'.format(self.serverIP,self.serverPort)
        r = requests.get(url, verify=self.verify, headers=self.defaultHeaders, cookies=self.cookies)
        if (r.status_code == requests.codes.ok):
            return json.loads(r.content)['data'][0] #Always assume there is only one server
        else:
            return None
    
    def getCameraInfo(self):
        '''
            Returns a array of all cameras on the system
        '''
        url = 'https://{}:{}/api/2.0/camera/'.format(self.serverIP,self.serverPort)
        r = requests.get(url, verify=self.verify, headers=self.defaultHeaders, cookies=self.cookies)
        if (r.status_code == requests.codes.ok):
            return json.loads(r.content)['data']
        else:
            return None
    
    def getCameraSnapShot(self, cameraID):
        '''
            Returns snapshot data (.jpg file) of the camera specified by cameraID from the last recording
        '''
        url = 'https://{}:{}/api/2.0/snapshot/camera/{}'.format(self.serverIP,self.serverPort,cameraID)
        r = requests.get(url, verify=self.verify, headers=self.defaultHeaders, cookies=self.cookies)
        if (r.status_code == requests.codes.ok):
            return r.content
        else:
            return None
    
    def downloadRecording(self, recordingID, destinationFile):
        '''
            Downloads a recording from the server and saves it to the specified location.
            destinationFile must be a complete file path and name. EX: '/tmp/downloadedFile.mp4'
            Returns True on success
        '''
        url = 'https://{}:{}/api/2.0/recording/{}/download'.format(self.serverIP,self.serverPort,recordingID)
        r = requests.get(url, verify=self.verify, headers=self.defaultHeaders, cookies=self.cookies)
        if (r.status_code == requests.codes.ok):
            with open(destinationFile,'wb') as recordingFile:
                recordingFile.write(r.content)
                recordingFile.close()
                return True
        else:
            print('Failed to retrieve file from server')
        return False
    
    def getRecordingCameraName(self, recordingID):
        '''
            Looks up a recording gets the camera _id and calls getCameraName to return the camera name
        '''
        url = 'https://{}:{}/api/2.0/recording/{}'.format(self.serverIP,self.serverPort,recordingID)
        r = requests.get(url, verify=self.verify, headers=self.defaultHeaders, cookies=self.cookies)
        if (r.status_code == requests.codes.ok):
            responseJSON = json.loads(r.content)['data']
            responseJSON = responseJSON[0] #Only one element in the list. Select it.
            responseJSON = responseJSON['cameras'][0] #Get the cameras list and select element 0 (for some reason unifi believes multiple cameras can record to a single recording)
            return self.getCameraName(responseJSON) #Lookup the cameraName using the camera _id
        else:
            return None
    
    def getCameraName(self, cameraID):
        '''
            @Returns string with the name of the camera or None if there is no match
        '''
        for camera in self.getCameraInfo():
            if camera['_id'] == cameraID: #Check to see if the camera _id matches
                return camera['name']
            else:
                pass #Not this camera. Continue
        return None

    def getLastRecordingIDs(self, numRecordings = 10):
        '''
            Returns the last numberRecordings from the server in the form of a array
        '''
        url = 'https://{}:{}/api/2.0/recording?&idsOnly=true&sortBy=startTime&sort=desc'.format(self.serverIP,self.serverPort)
        r = requests.get(url, verify=self.verify, headers=self.defaultHeaders, cookies=self.cookies)
        if (r.status_code == requests.codes.ok):
            return json.loads(r.content)['data'][:numRecordings] #Only return up to numberRecordings
        else:
            return None

if __name__ == '__main__':
    #Specify the server IP and Port
    server = UnifiVideoServerComm('SERVER_IP','SERVER_PORT_USUALLY_7443')
    #Login to the server
    server.login('USERNAME', 'USER_PASSWORD')
    
    #As a test get the name of the first camera in the system
    print(server.getCameraInfo()[0]['name'])
    
    #Print the last 10 recording ids and the camera name that recorded it
    for recordingID in server.getLastRecordingIDs():
        cameraName = server.getRecordingCameraName(recordingID)
        output = 'Camera: {} recorded ID: {}'.format(cameraName,recordingID)
        print(output)
    for element in server.getCameraInfo()[0]:
        print element



    
