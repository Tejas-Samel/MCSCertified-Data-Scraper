from __future__ import print_function

import json
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import configparser
from datetime import datetime

config = configparser.ConfigParser()

class googleSheetsHandler:

    # The ID and range of a sample spreadsheet.
    def __init__(self) -> None:

        config.read("googleConfig.ini")

        self.SCOPES = [config.get('DEFAULT', 'SCOPES')]
        self.SPREADSHEET_ID = config.get('DEFAULT', 'SPREADSHEET_ID')
        self.SHEET_NAME = config.get('DEFAULT', 'SHEET_NAME')
        config.set('DEFAULT','SCOPES','shfbsjufha')
        self.SCOPES = [config.get('DEFAULT', 'SCOPES')]

        self.service = self.connector()

    def connector(self):
        """
        Validates and connects to the google Sheet and returns the service
        """
        creds = None

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        # print(creds.valid)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                ####################################################################################
                ####################################################################################
                ###### credentials.json IS Json FILE CREDENTIALS DOWNLOADED FROM GOOGLE PROJECT#####  
                ####################################################################################
                ####################################################################################

                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('sheets', 'v4', credentials=creds)

            # Call the Sheets API
            return service.spreadsheets()
            

        except HttpError as err:
            print(err)

    def insertData(self, data):
        try:

            result = self.service.values().update(spreadsheetId=self.SPREADSHEET_ID,
                                                  range=self.SHEET_NAME, valueInputOption='USER_ENTERED',
                                                  body={
                                                      "values": data,
                                                  }
                                                  ).execute()
            print(result)
        except HttpError as e:
            if e.status_code == 400:

                print("##########################################")
                print("Sheet Does Not Exist")
                print("##########################################")
                print("Do You Want to create Sheet")
                print("ENTER YES OR NO \n")
                choice = str(input())
                print("\n")
                print("##########################################")

                if "yes" in choice.lower():
                    self.createSheet()
                else:
                    exit()
            else:
                print("95")
                print(e.__str__())
        except Exception as exceptionError:
            print("97")
            print(exceptionError.__str__())

    def readData(self):
        try:
            print("##########################################")
            print("ENTER SHEET NAME \n")
            sheet_name = str(input())
            print("##########################################")


            result = self.service.values().get(spreadsheetId=self.SPREADSHEET_ID,
                                        range=sheet_name).execute()

            if len(result.get('values')) ==0:
                print("NO DATA IN GOOGLE SHEETS")
            else:
                filename = datetime.now().strftime('%Y %m %d %H %M %S').__str__() + '.json'
                with open(filename,'w',encoding='utf-8') as f:
                    f.write(json.dumps(result))

                    print("##########################################")
                    print(f"Data is written in File   {filename} ")
                    print("##########################################")


            # print(type(result))
        except HttpError as e:
            if e.status_code == 400:

                print("##########################################")
                print("Sheet Does Not Exist")
                print("##########################################")
                print("Do You Want to create Sheet")
                print("ENTER YES OR NO \n")
                choice = str(input())
                print("\n")
                print("##########################################")

                if "yes" in choice.lower():
                    self.createSheet()
                else:
                    exit()

            else:
                print(e.__str__())
        except Exception as e:
            print(e.__str__())

    def createSheet(self):
        print("##########################################")
        print("ENTER SHEET NAME\n")
        sheet_name = str(input())
        print("\n##########################################")

        spreadsheetproperties = {
            'properties': {
                'title': sheet_name
            }
        }
        try:
            spreadsheet = self.service.create(body=spreadsheetproperties
                                                    ).execute()
            self.SPREADSHEET_ID = spreadsheet.get('spreadsheet')
            self.SHEET_NAME = spreadsheet.get('properties')['title']
            config.set('DEFAULT','SPREADSHEET_ID',value=self.SPREADSHEET_ID)
            config.set('DEFAULT','SHEET_NAME',value=self.SHEET_NAME)
            print("\n##########################################")
            print("NEW SPREADSHEET CREATED")
            print(f"SpreadsheetId: {self.SPREADSHEET_ID} \n title: {self.SHEET_NAME}")
            print("\n##########################################")

        except Exception as e:
            print(e.__str__())
        print(spreadsheet)

    def removeAllDataFromSheet(self):
        try:
            self.service.values().clear(spreadsheetId=self.SPREADSHEET_ID,
                                        range=self.SHEET_NAME).execute()
        except Exception as exceptionError:
            print(exceptionError.__str__())


# g= googleSheetsHandler()
# g.createSheet()