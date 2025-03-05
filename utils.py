"""
This file is for the handler classes. Handlers authenticate through a particular portal.
They can then perform several methods to fetch or save information from that portal.
Information available is limited to the information available to the current GIS user, handled by ArcGIS authentication.
"""
import arcpy
from arcgis.gis import GIS
import csv
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import logging
import os.path
import smtplib
import time


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="activity.log"
)

# If you want email notifications when backups finish, assign email_recipient to an email address as string.
email_recipient = None

def send_email(recipient):
    with open('creds.json') as f:
        # Store login credentials in another unversioned file. Access them through this.
        data = json.load(f)

    SMTP_SERVER = data['smtp']['domain']
    SMTP_PORT = data['smtp']['port']
    EMAIL_ADDRESS = data['smtp']['address']
    EMAIL_PASSWORD = data['smtp']['password']  # Use an App Password if using gmail domain
    RECIPIENT = recipient  # The recipient's email. For multiple, call this in a loop

    with open("stats.json", "r") as file:
        stats = json.load(file)

    # Convert JSON to a formatted string
    json_string = json.dumps(stats, indent=4)

    # Create the email
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT
    msg["Subject"] = "JSON Data from Python"

    # Attach JSON string as email body
    msg.attach(MIMEText(json_string, "plain"))

    # Send email via SMTP
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print("Email sent successfully!")
            logging.info(f"Emailed {recipient} with stats")
    except Exception as e:
        print(f"Failed to send email to {recipient}: {e}")
        logging.error(f"Failed to send email to {recipient}: {e}")

class AutoMod:
    def __init__(self):
        with open('creds.json') as f:
            # Store login credentials in another unversioned file.
            data = json.load(f)

        # Access the value you need
        self.username = data['agol']['username']
        self.password = data['agol']['password']
        print(f"Attempting login as {self.username}")
        logging.info(f"Attempting login as {self.username}")

        try:
            self.gis = GIS('home')
            logging.info(f"Logged in to {self.gis} as {self.username}")
        except Exception as e:
            logging.critical(f"Could not log in to {self.gis} as {self.username}.\nError:{e}")
            print(e)

        self._output_csv = ''
        self._GRACE_PERIOD_DAYS: int = 60

    def get_services_in_no_web_maps(self):
        from arcgis.mapping import WebMap

        # List of AGOL services.
        services = (self.gis.content.search(query="", item_type="Feature Service", max_items=1000))
        total_services_queried = len(services)
        print(services, "\n", f"There are {total_services_queried} of this type")

        for service in services:
            logging.info(service)

        logging.info(f"There are {total_services_queried} of this type")

        # Search AGOL for Web Maps.
        web_maps = self.gis.content.search(query="", item_type="Web Map", max_items=1000)
        print(web_maps)

        # We want to go through each Web Map in web_maps.
        # For each Web Map, every service found in that web map will be removed from our list.
        # By the end, only services not found in a Web Map will remain in the services list.
        for item in web_maps:
            # creates a WebMap object from input webmap item
            web_map = WebMap(item)
            # accesses basemap layer(s) in WebMap object
            base_maps = web_map.basemap['baseMapLayers']
            # accesses layers in WebMap object
            layers = web_map.layers
            # loops through basemap layers
            for bm in base_maps:
                # tests whether the bm layer has a styleUrl(VTS) or url (everything else)
                if 'styleUrl' in bm.keys():
                    for service in services:
                        if service.url in bm['styleUrl']:
                            # We want to remove a service from the services list if the url is found here.
                            services.remove(service)
                            print(f"Removed {service}")
                elif 'url' in bm.keys():
                    for service in services:
                        if service.url in bm['url']:
                            services.remove(service)
            # loops through layers
            for layer in layers:
                # tests whether the layer has a styleUrl(VTS) or url (everything else)
                if hasattr(layer, 'styleUrl'):
                    for service in services:
                        if service.url in layer.styleUrl:
                            services.remove(service)
                elif hasattr(layer, 'url'):
                    for service in services:
                        if service.url in layer.url:
                            services.remove(service)

        arcpy.AddMessage('The following services are not used in any web maps:')

        logging.info(f"Found {len(services)} feature services not present in any web map.\nServices are as follows:\n")

        for service in services:
            arcpy.AddMessage(f"{service.title} : {arcpy.GetActivePortalURL() + r'home/item.html?id=' + service.id}")
            logging.info(f"{service.title} : {arcpy.GetActivePortalURL() + r'home/item.html?id=' + service.id}")

        arcpy.AddMessage(f"Of {total_services_queried} services, there are {len(services)} unused in your portal")
        return services

    def get_inactive_users(self, search_user='*', return_type=list):

        output_csv = fr'.\outputs\users_inactive_{self._GRACE_PERIOD_DAYS}_days_before_{str(datetime.now())[:9]}.csv'

        self._output_csv = output_csv
        user_list = self.gis.users.search(query=search_user, max_users=1000)
        if return_type == list:
            user_dict = {}
            for item in user_list:
                if item.lastLogin != -1 and time.localtime(item.lastLogin / 1000) < self.get_inactive_date():
                    user_dict[item.username] = [item.firstName,
                                                item.lastName,
                                                time.strftime('%m/%d/%Y', time.localtime(item.lastLogin / 1000))
                                                ]
            return user_dict
        with open(output_csv, 'w', encoding='utf-8') as file:
            csvfile = csv.writer(file, delimiter=',', lineterminator='\n')
            csvfile.writerow(
                ["Username",  # CSV headers
                 "LastLogOn",
                 "Name",
                 ])

            for item in user_list:
                # Date math is to determine if the user's lastLogin attribute is within the grace period.
                if item.lastLogin != -1 and time.localtime(item.lastLogin / 1000) < self.get_inactive_date():
                    csvfile.writerow([item.username,  # modify according to whatever properties you want in your report
                                      time.strftime('%m/%d/%Y', time.localtime(item.lastLogin / 1000)),
                                      item.firstName + ' ' + item.lastName
                                      ])

    def get_inactive_date(self):
        current_time_struct = time.localtime()

        # Convert time.struct_time object to a datetime object
        current_datetime = datetime.fromtimestamp(time.mktime(current_time_struct))

        # Subtract days
        new_datetime = current_datetime - timedelta(self._GRACE_PERIOD_DAYS)

        # Convert back to time.struct_time object
        new_time_struct = new_datetime.timetuple()
        return new_time_struct

    def download_item(self, item, download_format):

        try:
            print(f"Working on {item.title}...")
            logging.info(f"Working on {item.title}...")
            # Creates another AGOL item in the same portal in file geodatabase (.gdb) format.
            result = item.export('{}_{}'.format(item.title, item.owner), download_format)
            last_name = self.gis.properties.user.lastName
            process_time = time.strftime('%m-%d-%Y', time.localtime())

            # Download the AGOL .gdb that was just created, not the original item.
            result.download(f"outputs//AGOL_{last_name}__{process_time}")
            print(f"Processed {item.title}")
            logging.info(f"Processed {item.title}")
            # The AGOL .gdb is still there taking up space in the portal, so clean it up. Leave original layer intact.
            result.delete()

        except Exception as e:
            print(e)
            logging.error(f"Could not download {item.title} id {item.id}")
            return None

        return item.id, item.title, item.owner


    def download_items_locally(self, download_format='File Geodatabase', ids_to_download=None):
        arcpy.AddMessage("Logged in as " + str(self.gis.properties.user.username))
        downloaded_items = {}
        try:
            # Search items by username
            items = self.gis.content.search(query='owner:*', item_type='Feature *', max_items=500)
            for item in items:
                print(item.id, item.title, item.owner)

            print(f"Search found {len(items)} items in this portal available.")
            logging.info(f"Search found {len(items)} items in this portal available.")

            if ids_to_download:
            # Loop through each item and if equal to Feature service then download it
                for item in items:
                    if item.id in ids_to_download:
                        item_downloaded = self.download_item(item,download_format)
                        if item_downloaded is not None:
                            downloaded_items[item_downloaded[0]] = [item_downloaded[1], item_downloaded[2]]
                return downloaded_items

            for item in items:
                logging.info(f"Downloading {item.title} item id {item.id} by {item.owner}...")
                item_downloaded = self.download_item(item, download_format)
                if item_downloaded is not None:
                    downloaded_items[item_downloaded[0]] = [item_downloaded[1], item_downloaded[2]]
                    logging.info(f"Downloaded {item.title} item id {item.id} successfully.")
        except Exception as e:
            print(e)
            logging.error(e)

        logging.info(f"Completed download of {len(downloaded_items)} items.")

        return downloaded_items

    def transfer_content(self, transfer_from_user: str, transfer_to_user: str):
        old_user_object = self.gis.users.get(transfer_from_user)
        print(f'Transferring content to {self.gis.users.get(transfer_to_user).username}')
        user_content = old_user_object.items()
        folders = old_user_object.folders

        for item in user_content:
            try:
                item.reassign_to(transfer_to_user)
            except Exception as e:
                print(f"{e}\nItem may have been already assigned to the user.")

        for folder in folders:
            self.gis.content.create_folder(folder['title'], transfer_to_user)
            folder_items = old_user_object.items(folder=folder['title'])
            for item in folder_items:
                item.reassign_to(transfer_to_user, target_folder=folder['title'])

    def bulk_transfer_content(self, transfer_from_users: list, transfer_to_user: str):
        for user in transfer_from_users:
            self.transfer_content(user, transfer_to_user)

class EnterpriseMod:
    def __init__(self):
        with open('creds.json') as f:
            # Store login credentials in another unversioned file. Access them through this.
            data = json.load(f)

        # Access the values from json
        self.username = data['egdb']['username']
        self.password = data['egdb']['password']
        self.sde = data['sde']

        print(self.username)
        logging.info(f"Attempting login as {self.username}")

        try:
            logging.info(f"Attempting login as {self.username}")
            self.gis = GIS('https://maps.mercercounty.org/portal', self.username, self.password)
            print(f'Logged in as {self.gis.properties.user.username}')
            logging.info(f'Logged in to portal as {self.username}')

        except Exception as e:
            print(e)
            logging.critical(f"Could not log in to portal as {self.username}\nError:{e}")

    def download_items_locally(self):
        downloaded_items = {'last backup started': time.strftime('%H:%M-_on_%m-%d-%Y'),
                            'egdb backup': {}}
        sde_path = self.sde
        local_gdb_path = os.path.join(os.getcwd(), "outputs", fr"egdb_backup_{time.strftime('%H%M-_on_%m-%d-%Y')}.gdb")
        logging.info(f"Attempting Enterprise GDB backup through {sde_path}.\nDestination: {local_gdb_path}")
        # Ensure output GDB exists
        if not arcpy.Exists(local_gdb_path):
            logging.warning(f'Local file geodatabase does not exist. Creating .gdb in directory.')
            arcpy.CreateFileGDB_management(os.path.dirname(local_gdb_path), os.path.basename(local_gdb_path))

        # Set workspace to the Enterprise GDB
        arcpy.env.workspace = sde_path

        # Get feature classes
        feature_classes = arcpy.ListFeatureClasses()
        print(feature_classes)
        logging.info(f'Found {len(feature_classes)} feature classes through .sde file.')
        datasets = arcpy.ListDatasets(feature_type="Feature") or []

        # Copy standalone feature classes
        for fc in feature_classes:
            #if fc not in ['DBO.TreesGT5in_2019']:
                #continue
            try:
                source_fc = os.path.join(sde_path, fc)
                dest_fc = os.path.join(local_gdb_path, fc)
                print(f"Copying {fc}...")
                logging.info(f'Copying {fc.__str__()}...')
                arcpy.CopyFeatures_management(source_fc, dest_fc)
                downloaded_items['egdb backup'][fc] = {
                    'status': 'copied successfully',
                    'timestamp': time.strftime('%H%M_on_%m-%d-%Y'),
                    'error' : None,
                    'path' : dest_fc.split('\\')[-2:]
                    }
                logging.info(f'{fc.__str__()} copied successfully.')
            except Exception as e:
                downloaded_items['egdb backup'][fc] = {
                    'status': 'copying failed',
                    'timestamp': time.strftime('%H%M_on_%m-%d-%Y'),
                    'error' : str(e)
                    }
                logging.error(f'Failed to copy {fc.title}\nError: {e}')
            finally:
                downloaded_items['last backup completed'] = time.strftime('%H%M-_on_%m-%d-%Y')
                pass
        logging.info(f'Updating "stats.json" with status of {len(downloaded_items)} items.')
        with open('stats.json', 'w') as outfile:
            json.dump(downloaded_items, outfile)

        return downloaded_items

    def list_users(self):
        users_tuple = arcpy.ListUsers(self.sde)
        users = {}
        for user in users_tuple:
            users[user.ID] = (user.Name, user.ClientName, user.ConnectionTime, user.IsDirectConnection)
        return users


if __name__ == '__main__':
    em = EnterpriseMod()
    em.download_items_locally()
    am = AutoMod()
    am.download_items_locally()
    if email_recipient is not None:
        send_email(email_recipient)
