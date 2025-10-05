import requests
import hashlib
import json
import time


# https://docs.virustotal.com/docs/api-overview
class VTUpload:
    # init basic variables
    def __init__(self):
        self.filename = None
        self.key = None

        # you can change it (i dont recommend making the threshold big, on the contrary, keep it small)
        # if > 3 vendors agree that it's a malware, we issue a positive verdict
        self.verdict_threshold = 3
        self.verdict = None
        
        # nobody stores keys/tokens like this, but I don't give a fuck))
        with open('apikey.txt', "r") as f:
            self.key = f.read()
            
        # define headers for requests
        self.headers = {
            "accept": "application/json",
            "x-apikey": self.key
        }

        self.url = "https://www.virustotal.com/api/v3/"
        self.analysis_url = "https://www.virustotal.com/api/v3/analyses/"
        self.upload_url = "https://www.virustotal.com/api/v3/files"

    # get sha256 file hash
    def get_hash(self, filename):
        with open(filename,"rb") as f:
            bytes = f.read()
            hash = hashlib.sha256(bytes).hexdigest()
            return (hash)
    
    # get report by hash or upload it
    def get_report(self, filename):
        hash = self.get_hash(filename)
        response = requests.get(self.upload_url + '/' + hash, headers=self.headers)
        # if status = 200, so virustotal have report already
        if response.status_code == 200:
            response_struct = response.json()
            last_analysis_stats = response_struct['data']['attributes']['last_analysis_stats']
            print(last_analysis_stats)            
            if last_analysis_stats['malicious'] > self.verdict_threshold:
                self.verdict =  True
            else:
                self.verdict = False
        # if not, we need to upload it
        else: 
            self.upload(filename)

    # get status by analysis id
    def get_analysis_status(self, id):
        response = requests.get(self.analysis_url + id, headers=self.headers)
        if response.status_code == 200:
            response_struct = response.json()
            status = response_struct['data']['attributes']['status']
            return status

    # try to upload file or/and get report
    def upload(self, filename):
        binary_file = { "file": (filename, open(filename, "rb")) }
        upload_response = requests.post(self.upload_url, files=binary_file, headers=self.headers)

        if upload_response.status_code == 200:
            response_struct = upload_response.json()
            analysis_id = response_struct['data']['id']
            status = self.get_analysis_status(analysis_id)
            # waiting for the analysis to be completed (status != queued)
            while status == "queued":
                # you can set the sleep-value lower, it is unlikely to affect performance in any way.
                time.sleep(15)
                status = self.get_analysis_status(analysis_id)
            self.get_report(filename)
        else:
            print("error while uploading")
