import dxpy
import pandas as pd
import re
import os
import sys
import datetime
import config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from jinja2 import Environment, select_autoescape, FileSystemLoader
from tqdm import tqdm
import argparse

"""
Automate End of Duty Tasks
Python 3
Developer: Igor Malashchuk
Email: igor.malashchuk@nhs.net
Date released: 08/07/2022

To run the script: 
python automateEODT.py -7d
"""
version = "Version 2.0.0"


cur_path_script = os.path.realpath(__file__)
cur_path_list = cur_path_script.split("/")
cur_path = "/".join(cur_path_list[: (len(cur_path_list) - 2)])
env_path = "/".join(cur_path_list[: (len(cur_path_list) - 1)])
print(cur_path)
pattern = re.compile("(project-\S+)__\S+__")
env = Environment(
    loader=FileSystemLoader(env_path + "/email_templates"),
    autoescape=select_autoescape(["html"]),
)
template = env.get_template("email.html")

def download_url(file_ID, project_ID):
    """
    Create a url for a file in DNAnexus
    """
    dxfile = dxpy.DXFile(file_ID)
    download_link = dxfile.get_download_url(
        duration=60 * 60 * 24 * 5,  # 60 sec x 60 min x 24 hours * 5 days
        preauthenticated=True,
        project=project_ID,
    )
    return download_link[0]


def find_project_data(project_id, _folder, filename):
    """
    Search DNAnexus to find files based on a regexp pattern
    """
    data = list(
        dxpy.bindings.search.find_data_objects(
            project=project_id,
            name=filename,
            name_mode="regexp",
            describe=True,
            folder=_folder,
        )
    )
    return data

def find_project_name(project_id):
    """
    Find the name of a project when giving a file ID
    """
    project_data = dxpy.bindings.dxproject.DXProject(dxid=project_id)
    return project_data.describe().get("name")

def find_projects(project_name, _length):
    """
    Search DNAnexus to find projects based on regex pattern and amount of time from now
    """
    data = list(
        dxpy.bindings.search.find_projects(
            name=project_name,
            name_mode="regexp",
            created_after=_length,
            level="VIEW",
            describe=True,
        )
    )
    return data


def find_project_executions(project_id):
    """
    Find number of executions/jobs for a given project and retrieve outcomes of the jobs e.g. done, running, failed etc.
    """
    data = list(dxpy.bindings.search.find_executions(project=project_id, describe=True))
    jobs = []
    for job in data:
        state = job.get("describe").get("state")
        jobs.append(state)
    _jobs = list(set(jobs))
    len(data)
    return _jobs, len(data)


def create_download_links(project_data, project_name, file_type):
    """
    Generate URL links from a list of data and produce a pandas dataframe
    """
    data = []
    info_message = "creating Download links for {} project: {}".format(
        project_name[0], project_name[1]
    )
    print(info_message)
    for object in tqdm(project_data):
        file_name = object.get("describe").get("name")
        folder = object.get("describe").get("folder")
        object_id = object.get("id")
        project_id = object.get("project")
        type_of_file = file_type
        url = download_url(object_id, project_id) + "/" + file_name
        merged_data = [file_name, folder, type_of_file, url]
        data.append(merged_data)
    return pd.DataFrame(data, columns=["name", "folder", "type", "url"])


def find_project_description(project_id):
    """
    Find the description of the project
    """
    project_data = dxpy.bindings.dxproject.DXProject(dxid=project_id)
    return project_data.describe()


def find_previouse_files(folder):
    """
    Find previously generates CSV files to determine if the project needs processing
    """
    projects_csv = {}
    for filename in os.listdir(cur_path + "/" + folder):
        try:
            project = pattern.search(filename)[1]
        except:
            project = ""
        projects_csv[project] = {}
    return projects_csv


def archive_after7days(folder):
    """
    Archive CSV after seven days
    """
    today = datetime.date.today()
    files = (
        file
        for file in os.listdir(cur_path + folder)
        if os.path.isfile(os.path.join(cur_path + folder, file))
    )
    for filename in files:
        try:
            project = pattern.sosearch(filename)[1]
            date_modified = datetime.date.fromtimestamp(
                find_project_description(project).get("modified") / 1000
            )
            _delta = today - date_modified
            print("number of days modified from now: {}".format(_delta.days))
            if _delta.days > 7:
                os.replace(
                    cur_path + folder + "/" + filename,
                    cur_path + folder + "/archive/" + filename,
                )
        except:
            project = ""


def create_text_file(filepath):
    """
    This function is used to generate a text file with project name as a way to make sure that
    """
    date_now = datetime.datetime.now().strftime("%Y_%m_%d_%H:%M:%S")
    f = open(filepath, "a")
    f.write("CSV file has been created and emailed to mokaguys on {}".format(date_now))
    f.close()


class Project:
    """
    Create a Class for One Project
    """

    def __init__(self, proj_id, project_type, amazon_username, amazon_password):
        self.id = proj_id
        self.name = find_project_name(proj_id)
        self.jobs = find_project_executions(proj_id)
        self.proj_type = project_type
        self.folder = "/" + project_type + "/"
        self.amazon_user = amazon_username
        self.amazon_pw = amazon_password

    def message(self):
        """
        Message that no target files have been found for a specific project
        """
        message = "no files were found for {} project: {}".format(
            self.proj_type, self.name
        )
        print(message)

    def send_email(self, to, email_subject, email_message, list_df, filenames):
        """
        Input = email address, email_subject, email_message, email_priority (optional, default = standard priority)
        Uses smtplib to send an email.
        Returns = None
        """
        # create message object
        # m = Message()
        email_content = MIMEMultipart()
        # set priority
        # m["X-Priority"] = str(email_priority)
        # set subject
        email_content["Subject"] = email_subject
        # set body
        email_content["From"] = config.email_send_from
        email_content["To"] = to
        msgText = MIMEText("<b>%s</b>" % (email_message), "html")
        email_content.attach(msgText)
        for count, df in enumerate(list_df):
            attachment = MIMEApplication(df.to_csv())
            attachment["Content-Disposition"] = 'attachment; filename=" {}"'.format(
                "{}.csv".format(filenames[count])
            )
            email_content.attach(attachment)
        # m.set_payload(email_message)
        # server details
        server = smtplib.SMTP(host=config.host, port=config.port, timeout=10)
        server.set_debuglevel(
            False
        )  # verbosity turned off - set to true to get debug messages
        server.starttls()  # notifies a mail server that the contents of an email need to be encrypted
        server.ehlo()  # Identify yourself to an ESMTP server using EHLO
        server.login(self.amazon_user, self.amazon_pw)  # uses gstt relay to send emails, see config.py file
        server.sendmail(config.email_send_from, to, email_content.as_string())


# WES Project
class WES(Project):
    """
    Class for WES Project that inherits information from Project
    """

    def data(self):
        """
        Find files in the project that are required to be placed on the trust computer:
        chanjo_txt
        """
        self.files = find_project_data(self.id, "/coverage", "\S+.chanjo_txt$")

    def make_csv_and_email(self):
        """
        Create CSV and send email
        """
        if len(self.files) >= 1:
            download_links = create_download_links(
                self.files, [self.proj_type, self.name], "coverage"
            )
            filename = (
                self.id + "__" + self.proj_type + "__" + self.name + "_chanjo_txt.csv"
            )
            # Email content:
            # Subject:
            subject = "{} run: ".format(self.proj_type) + self.name
            # Text message specific to the project
            text = ""
            # Fill the template html
            html = template.render(
                TSO_message=text,
                num_jobs=self.jobs[1],
                jobs_executed=self.jobs[0],
                project_name=self.name,
                num_of_csv=1,
                number_of_files=len(download_links.index),
            )
            self.send_email(
                config.email_send_to, subject, html, [download_links], [filename]
            )
        else:
            print("The number of items for chanjo_txt:{}".format(len(self.files)))

class SNP(Project):
    """
    Class for SNP Project that inherits information from Project
    """

    def data(self):
        """
        Find files in the project that are required to be placed on the trust computer:
        sites_present_reheader_filtered_normalised.vcf
        """
        self.files = find_project_data(
            self.id, "/output", "\S+.sites_present_reheader_filtered_normalised.vcf$"
        )

    def make_csv_and_email(self):
        """
        Create CSV and send email
        For detailed comments see WES
        """
        if len(self.files) >= 1:
            download_links = create_download_links(
                self.files, [self.proj_type, self.name], "output"
            )
            filename = self.id + "__" + self.proj_type + "__" + self.name + "_VCFs.csv"
            subject = "{} run: ".format(self.proj_type) + self.name
            text = ""
            html = template.render(
                TSO_message=text,
                num_jobs=self.jobs[1],
                jobs_executed=self.jobs[0],
                project_name=self.name,
                num_of_csv=1,
                number_of_files=len(download_links.index),
            )
            # Send email with csv attchment:
            self.send_email(
                config.email_send_to, subject, html, [download_links], [filename]
            )
        else:
            print("The number of items for VCF:{}".format(len(self.files)))

class MokaPipe(Project):
    """
    Class for MokaPipe Project that inherits information from Project
    """

    def data(self):
        """
        Find files in the project that are required to be placed on the trust computer:
        exon_level.txt
        combined_bed_summary
        """
        coverage = find_project_data(self.id, "/coverage", "\S+.exon_level.txt$")
        rpkm = find_project_data(self.id, "/conifer_output", "combined_bed_summary\S+")
        fh_prs = find_project_data(self.id, "/PRS_output", "\S+.txt$")
        self.files = [rpkm, coverage, fh_prs]

    def make_csv_and_email(self):
        """
        Create CSV and send email
        For detailed comments see WES
        """
        rpkm = self.files[0]
        coverage = self.files[1]
        fh_prs = self.files[2]
        if len(rpkm) >= 1 and len(coverage) >= 1:
            print("The number of items for RPKM:{}; for coverage: {}; for FH_PRS: {}".format(len(rpkm), len(coverage), len(fh_prs)))
            download_RPKM_links = create_download_links(
                rpkm, [self.proj_type, self.name], "RPKM"
            )
            download_coverage_links = create_download_links(coverage, [self.proj_type, self.name], "coverage")
            if len(fh_prs) >= 1:
                download_FHPRS_links = create_download_links(
                    fh_prs, [self.proj_type, self.name], "FH_PRS"
                )
                df_list = pd.concat(
                    [download_RPKM_links, download_coverage_links, download_FHPRS_links]
                )
            else:
                df_list = pd.concat([download_RPKM_links, download_coverage_links])
            MokaPipe_filename = (
                self.id + "__" + self.proj_type + "__" + self.name + ".csv"
            )
            subject = "{} run: ".format(self.proj_type) + self.name
            text = ""
            html = template.render(
                TSO_message=text,
                num_jobs=self.jobs[1],
                jobs_executed=self.jobs[0],
                project_name=self.name,
                num_of_csv=1,
                number_of_files=len(download_RPKM_links.index)
                + len(download_coverage_links.index),
            )
            self.send_email(
                config.email_send_to,
                subject,
                html,
                [df_list],
                [MokaPipe_filename],
            )
            print(
                "CSV file(s) generated succesffully and email sent to {} for project: {}".format(
                    config.email_send_to, self.name
                )
            )
        else:
            print(
                "The number of items for RPKM:{}; for coverage: {}; for FH_PRS: {}".format(
                    len(rpkm), len(coverage), len(fh_prs)
                )
            )


class TSO(Project):
    """
    Class for TSO500 Project that inherits information from Project
    """

    def data(self):
        """
        Find files in the project that are required to be placed on the trust computer:
        gene_level.txt
        exon_level.txt
        Results.zip
        """
        gene = find_project_data(self.id, "/coverage", "\S+.gene_level.txt$")
        exon = find_project_data(self.id, "/coverage", "\S+.exon_level.txt$")
        results = find_project_data(self.id, "/", "^Results.zip$")
        sompy = find_project_data(
            self.id, "/QC", "\S+_MergedSmallVariants.genome.vcf.stats.csv$"
        )
        self.files = [results, gene + exon, sompy]

    def make_csv_and_email(self):
        """
        Create CSV and send email
        For detailed comments see WES
        """
        results = self.files[0]
        coverage = self.files[1]
        sompy = self.files[2]
        if len(results) >= 1 and len(coverage) >= 1:
            download_results_links = create_download_links(
                results, [self.proj_type, self.name], "Results"
            )
            download_coverage_links = create_download_links(
                coverage, [self.proj_type, self.name], "coverage"
            )
            download_sompy_links = create_download_links(
                sompy, [self.proj_type, self.name], "sompy"
            )
            TSO_filename = self.id + "__" + self.proj_type + "__" + self.name + ".csv"
            subject = "{} run: ".format(self.proj_type) + self.name
            text = "WARNING! TSO500 Results files can take some time to download, please wait"
            html = template.render(
                TSO_message=text,
                num_jobs=self.jobs[1],
                jobs_executed=self.jobs[0],
                project_name=self.name,
                num_of_csv=1,
                number_of_files=len(download_results_links.index)
                + len(download_coverage_links.index),
            )
            self.send_email(
                config.email_send_to,
                subject,
                html,
                [
                    pd.concat(
                        [
                            download_results_links,
                            download_coverage_links,
                            download_sompy_links,
                        ]
                    )
                ],
                [TSO_filename],
            )
            print(
                "CSV file(s) generated succesffully and email sent to {} for project: {}".format(
                    config.email_send_to, self.name
                )
            )
        else:
            print(
                "The number of items for results:{}; for coverage: {}; for sompy: {}".format(
                    len(results), len(coverage), len(sompy)
                )
            )

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='For index images analysis')
    parser.add_argument('--project_id', dest='project_id', type=str, help='app_id', metavar='project_id')
    parser.add_argument('--proj_type', dest='proj_type', type=str, help='project type: WES, SNP, MokaPipe, TSO500')
    parser.add_argument('--amazon_username', dest='amazon_username', type=str, help='amazon email server username')
    parser.add_argument('--amazon_password', dest='amazon_password', type=str, help='amazon email server password')
    parser.add_argument('--DNAnexus_token', dest='DNAnexus_token', type=str, help='DNAmexus authorization token')
    args = parser.parse_args()

    dxpy.set_security_context({"auth_token_type": "Bearer", "auth_token": args.DNAnexus_token})

    """
    Search WES, MokaPipe, SNP and TSO500 projectsu using projects.

    If projects are found a csv file is created with download links for the required files 
    that need to be placed onto the trsut drives
    """
    print("Script: {}".format(version))       
    if args.proj_type == "SNP":
        project = SNP(args.project_id, args.proj_type, args.amazon_username, args.amazon_password)
    elif args.proj_type == "WES":
        project = WES(args.project_id, args.proj_type, args.amazon_username, args.amazon_password)
    elif args.proj_type == "MokaPipe":
        project = MokaPipe(args.project_id, args.proj_type, args.amazon_username, args.amazon_password)
    elif args.proj_type == "TSO500":
        project = TSO(args.project_id, args.proj_type, args.amazon_username, args.amazon_password)
    else:
        print("file job not recognised: {}".format(args.proj_type))
    print(
        "Project_id: {}, Project_name: {}, Project_jobs_status: {}".format(
            project.id, project.name, project.jobs
        )
    )
    print("Getting data")
    project.data()
    if project.files:
        print("Making csv and sending email")
        project.make_csv_and_email()
    else:
        project.message()
    print("Script {} finished running without Errors!".format(version))
