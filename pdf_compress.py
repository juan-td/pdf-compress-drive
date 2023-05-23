import pickle
import drive_functions as gdrive
import googleapiclient.discovery
import os
import json
from dotenv import load_dotenv
import pandas as pd
from pylovepdf.ilovepdf import ILovePdf
import logging

load_dotenv()


def compress_pdf(filename, compression=None):
    ilovepdf = ILovePdf(os.environ.get("ILP_PUBLIC_KEY"), verify_ssl=True)
    task = ilovepdf.new_task("compress")
    task.add_file(filename)
    task.set_output_folder("compressed")
    task.execute()
    task.download()
    task.delete_current_task()


def remove_all_file_revisions(drive_service):
    first_iter = True
    next_page_token = None
    while next_page_token or first_iter:
        first_iter = False
        files_list, next_page_token = gdrive.list_files(
            drive_service,
            page_size=1000,
            #q="mimeType='application/pdf'",
            pageToken=next_page_token,
        )
        for file in files_list:
            if file["owners"][0]["me"]:
                print(f'Looking for revisions in {file["name"]}')
                try:
                    revisions = (
                        drive_service.revisions()
                        .list(
                            fileId=file["id"],
                            fields="revisions(id, kind, mimeType, modifiedTime)",
                        )
                        .execute()["revisions"]
                    )
                except:
                    continue
                
                revisions = pd.DataFrame(revisions).sort_values(
                    "modifiedTime",
                    ascending=True,
                    ignore_index=True,
                )
                for i in range(len(revisions) - 1):
                    try:
                        print(f"Deleting revision {i}...")
                        drive_service.revisions().delete(
                            fileId=file["id"], revisionId=revisions.iloc[i]["id"]
                        ).execute()
                    except:
                        print(f"Couldn\'t delete revision {i} from {file['name']}")

def remove_file_revisions(drive_service, file_id):
    revisions = (
        drive_service.revisions()
        .list(
            fileId=file_id,
            fields="revisions(id, kind, mimeType, modifiedTime)",
        )
        .execute()["revisions"]
        )
    revisions = pd.DataFrame(revisions).sort_values(
            "modifiedTime",
            ascending=True,
            ignore_index=True,
        )
    for i in range(len(revisions) - 1):
        try:
            drive_service.revisions().delete(
                fileId=file_id, revisionId=revisions.iloc[i]["id"]
            ).execute()
            print(f'Revision {i} deleted')
        except:
            print(f"Couldn\'t delete revision")
    

def update_revision_policy(drive_service):
    first_iter = True
    next_page_token = None
    while next_page_token or first_iter:
        first_iter = False
        files_list, next_page_token = gdrive.list_files(
            drive_service,
            page_size=1000,
            pageToken=next_page_token,
        )
        for file in files_list:
            if file["owners"][0]["me"]:
                print(f'Updating policy for {file["name"]}')
                drive_service.files().update(fileId=file['id'],keepRevisionForever=False)
                


if __name__ == "__main__":
    
    with open('compressed_ids.txt','r') as f:
        logged_ids = f.readlines()

    compressed_ids = [id.strip() for id in logged_ids]

    drive_service = gdrive.get_drive_service()

    remove_all_file_revisions(drive_service)
    # files_list, next_page_token = gdrive.list_files(
    #         drive_service,
    #         page_size=198,
    #         q="mimeType='application/pdf'",
    #     )
    
    # compressed_counter = 0
    # for file in files_list:
    #     if file['id'] not in compressed_ids and file['owners'][0]['me']:
    #         print(f'\n---- Compressing {file["name"]} (size: {int(file["size"])/1024**2:.2f} MB) ----\n')

    #         print('Downloading from google drive...\n')
    #         gdrive.download_file(drive_service,file['id'],'downloads/current_file.pdf')

    #         print('Starting compression with ILovePDF\n-----------------------------')
    #         compress_pdf('downloads/current_file.pdf')
    #         print('-----------------------------\n')

    #         print('Uploading file to google drive...')
    #         gdrive.upload_file(drive_service,file['id'],'compressed/current_file.pdf',mime_type='application/pdf')

    #         print('Removing local copies...')
    #         os.remove('downloads/current_file.pdf')
    #         os.remove('compressed/current_file.pdf')

    #         print('Appending file id to compressed ids...')
    #         compressed_ids.append(file['id'])
    #         with open('compressed_ids.txt','a') as f:
    #             f.write(file['id']+'\n')
            
    #         print('Removing old version from google drive...')
    #         remove_file_revisions(drive_service,file['id'])

    #         print(f'File {file["name"]} completed!')
    #         compressed_counter += 1
    #         if compressed_counter >= 14:
    #             break

    # print('All done!')
