from pdfminer.high_level import extract_text as extract_text_from_pdf
import docx2txt
import re
import time
from hrvatar.AI.queryAI import askGPT3


class Parse:
    def __init__(self, resume_path):
        self.resume_path = resume_path
        if self.resume_path.split(".")[-1] == "docx":
            txt = docx2txt.process(self.resume_path)
            if txt:
                self.resume_txt = txt.replace("\t", " ")
            else:
                self.resume_txt = None
        elif self.resume_path.split(".")[-1] == "pdf":
            self.resume_txt = extract_text_from_pdf(self.resume_path)

    def get_name(self):
        if self.resume_txt is not None:
            query = f"""Extract Full name of the person from geven resume text.
            Write the Name only in response within tags of <name></name> :
            \n{self.resume_txt}"""
            names = askGPT3(query)
            pattern = r"<name>(.*?)</name>"
            match = re.search(pattern, names)
            if match:
                name = match.group(1)
            else:
                name = None
            return name
        else:
            return None

    def get_phoneNumber(self):
        phone_number = str()

        if self.resume_txt is not None:
            query = f"""Extract all given phone numbers of the person from
            given resume text. Write the numbers only in response within tags
            of <phone></phone> (each number in its seperate tag):
            \n{self.resume_txt}"""
            phone_number = askGPT3(query)
            pattern = r"<phone>(.*?)</phone>"
            match = re.search(pattern, phone_number)
            if match:
                phone_number = match.group(1)
            else:
                phone_number = None
            return phone_number
        else:
            return None

    def get_email(self):
        EMAIL_REG = re.compile(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+")
        emails = re.findall(EMAIL_REG, self.resume_txt)
        if emails:
            return emails[0]
        else:
            return None

    def get_skills(self):
        query = f"""What skills are mentioned in the following text, write only name of the skills, in start of each skill write <S> and in end </S>. Do not write anything else :
        {self.resume_txt}"""
        skills_response = askGPT3(query)
        if skills_response:
            skills = re.findall(r"<S>(.*?)</S>", skills_response)
            return skills
        else:
            return None

    def get_schools(self):
        query = f"""Given a resume text, extract the education of the person
        mentioned.For each education, enclose it within <e> and </e> tags.
        Within the same <e> and </e> tags, include the title enclosed in
        <title> and </title>tags, the start date enclosed in <start> and
        </start> tags, if start date is not mentioned put NA, the end date (write 'ongoing' if the person is still
        going to that school) enclosed in <end> and </end> tags, and the
        school name enclosed in <school> and </school> tags. Only the main
        title of each experience should be extracted. Note that if there is only one date then it is the end date for that education, make start date NA:
        {self.resume_txt}"""
        text = askGPT3(query)
        if text:
            schools = re.findall(r"<e>(.*?)</e>", text, re.DOTALL)

            schools_dict = {}
            for school in schools:
                title_match = re.search(r"<title>(.*?)</title>", school)
                start_match = re.search(r"<start>(.*?)</start>", school)
                end_match = re.search(r"<end>(.*?)</end>", school)
                institute_match = re.search(r"<school>(.*?)</school>", school)

                title = title_match.group(1) if title_match else "NA"
                start = start_match.group(1) if start_match else "NA"
                end = end_match.group(1) if end_match else "NA"
                institute = institute_match.group(1) if institute_match else "NA"

                if title != "NA":
                    schools_dict[title] = {
                        "start": start,
                        "end": end,
                        "Institute": institute,
                    }

            return schools_dict if schools_dict else None
        else:
            return None

    def get_experience(self):
        query = f"""Given a resume text, extract the experiences of the person
        mentioned. For each experience, enclose it within <e> and </e> tags.
        Within the same <e> and </e> tags, include the title enclosed in
        <title> and </title> tags, the start date enclosed in <start> and
        </start> tags, the end date (write 'ongoing' if the person is still
        working on that experience) enclosed in <end> and </end> tags, and the
        company name enclosed in <company> and </company> tags. Only the main
        title of each experience should be extracted. Note that if there is only one date for any experience then it is the starting date most probably put NA in end date :
        {self.resume_txt}"""
        text = askGPT3(query)
        if text:
            experiences = re.findall(r"<e>(.*?)</e>", text, re.DOTALL)

            experience_dict = {}
            for exp in experiences:
                title_match = re.search(r"<title>(.*?)</title>", exp)
                start_match = re.search(r"<start>(.*?)</start>", exp)
                end_match = re.search(r"<end>(.*?)</end>", exp)
                company_match = re.search(r"<company>(.*?)</company>", exp)

                title = title_match.group(1) if title_match else "NA"
                start = start_match.group(1) if start_match else "NA"
                end = end_match.group(1) if end_match else "NA"
                company = company_match.group(1) if company_match else "NA"

                if title != "NA":
                    experience_dict[title] = {
                        "start": start,
                        "end": end,
                        "company": company,
                    }

            return experience_dict if experience_dict else None
        else:
            return None

    def check_applicable_for_job(self, requirements):
        print(len(self.resume_txt))
        query = f"""Given: {requirements}
        is the candidate with following resume applicable for the job:
        {self.resume_txt}
        if user passes minimum requirements write <response>yes</response> else write <response>no></response>
        """

        # query = f"""Given the job description : {job_description}
        # is the candidate with following Resume

        # {self.resume_txt}

        # See if the user passes all types of minimum requirements only. say yes or no in <response></response> tags
        # and reason in <reason></reason> tag.:
        # """
        text = askGPT3(query=query)
        print(text)
        response_match = re.search(r"<response>(.*?)</response>", text)
        # reason_match = re.search(r"<reason>(.*?)</reason>", text)
        if response_match:
            return response_match.group(1)
        else:
            return None


if __name__ == "__main__":
    parser = Parse(r"resources\\Resume-HassanSanaullah-2.pdf")

    description = """Job Title: Python Developer / AI Engineer

                    Job Summary:

                    We are seeking a highly skilled and experienced Python Developer/AI Engineer to join our team. As a Python Developer, you will play a crucial role in developing innovative software solutions and contributing to our projects in the fields of software development, machine learning, and artificial intelligence. If you are passionate about creative coding, problem-solving, and have a proven track record of using Python and other technologies to create cutting-edge solutions, we want to hear from you.

                    Key Responsibilities:

                    Collaborate with cross-functional teams to design, develop, and implement software solutions using Python and related technologies.
                    Develop intuitive and user-friendly GUI applications using Tkinter and PyQt.
                    Utilize web scraping techniques with BeautifulSoup and Scrapy to gather valuable data.
                    Optimize Python scripts and code for improved performance and efficiency.
                    Conduct Software Quality Assurance (SQA) testing to ensure the reliability and stability of our applications.
                    Engage closely with clients, gathering requirements, addressing feedback, and delivering high-quality solutions.
                    Tackle complex programming challenges with creativity and precision.
                    Manage multiple projects simultaneously, meeting deadlines efficiently and effectively.
                    Stay up-to-date with the latest industry trends and technologies, especially in AI and machine learning.
                    Qualifications:

                    student of Bachelor's degree in Computer Science, Artificial Intelligence, or a related field.
                    Strong knowledge of Python, C++, and backend development.
                    Proficiency in AI and machine learning technologies.
                    Experience with web scraping tools like BeautifulSoup and Scrapy.
                    Previous experience in GUI development with Tkinter and PyQt.
                    Strong problem-solving skills and a creative approach to coding challenges.
                    Excellent communication and teamwork skills.
                    Ability to work independently and deliver high-quality results.
                    Prior experience with Software Quality Assurance (SQA) is a plus.
                    Certifications:

                    Machine Learning Algorithms (optional but beneficial).
                    Join our team and be a part of an innovative and dynamic environment where your skills and expertise will be valued. Apply now to contribute to our exciting projects and shape the future of software development, AI, and machine learning.

                    This job description aligns with the candidate's skills and experience mentioned in the provided resume, emphasizing their experience as a Python Developer and their proficiency in AI and machine learning technologies.

                """
    print(parser.check_applicable_for_job(description))
