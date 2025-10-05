import os
import win32com.client
import vtscan
from pathlib import Path

class OutlookEvents:
    # this simple function moves an email from the inbox folder to quarantine
    def transfer_to_quarantine(self, outlook, message):
        folder_name = "Quarantine"
        inbox = outlook.GetDefaultFolder(6)
        quarantine_folder = None

        try:
            quarantine_folder = inbox.Folders[folder_name]
        except Exception:
            quarantine_folder = inbox.Folders.Add(folder_name)

        message.Move(quarantine_folder)
        print("Successfully transfered to 'Quarantine' folder")

    # here we catch new mail items
    def OnNewMailEx(self, entry_id_collection):
        # create outlook object
        outlook_app = win32com.client.Dispatch("Outlook.Application")
        outlook_handle = outlook_app.GetNamespace("MAPI")

        # create vt object (check vtscan.py)
        vt_service = vtscan.VTUpload()

        # dir, for saving attachments, so specify your path here
        # i choosed path directory
        attachment_dir = Path.home()

        # entry_id_collection is a string containing comma-separated EntryIDs
        # for newly received items.
        for entry_id in entry_id_collection.split(','):
            try:
                mail_item = outlook_handle.GetItemFromID(entry_id)
                # olMail = 43 (constant for MailItem)
                if mail_item.Class == 43:
                    print(f"New email received: {mail_item.Subject}")

                    # is mail contains at least one attachment?
                    if mail_item.Attachments.Count > 0:
                        # here we create a folder to save attachments
                        if not os.path.exists(attachment_dir):
                            os.makedirs(attachment_dir)

                        # iterate over all attachments
                        # if at least one attachment is suspicious, we send it to quarantine
                        for attachment in mail_item.Attachments:
                            save_path = os.path.join(attachment_dir, attachment.FileName)
                            attachment.SaveAsFile(save_path)
                            print(f"Saved attachment: '{attachment.FileName}' to '{save_path}'")
                            verdict = vt_service.get_report(save_path)

                            if verdict:
                                # transfer mail to quarantine folder
                                self.transfer_to_quarantine(outlook_handle, mail_item)

            except Exception as e:
                print(f"Error processing email: '{e}'")

def main():
    outlook_app = win32com.client.DispatchWithEvents('Outlook.Application', OutlookEvents)
    print("Listening for new emails...")
    
    import pythoncom
    pythoncom.PumpMessages()

if __name__ == "__main__":
    main()
