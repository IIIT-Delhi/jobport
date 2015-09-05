# __author__ = 'naman'

from datetime import datetime
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from storage import OverwriteStorage


class Batch(models.Model):
	title = models.CharField("Name", max_length=120, null=True)
	
	QUALIFICATION = (
		('G', 'UnderGraduate'),
		('P', 'PostGraduate'),
		)
	pg_or_not = models.CharField("Graduate or Post-Graduate", max_length=1, choices=QUALIFICATION, default='G')
	
	createdon = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title


class Job(models.Model):
	def checkdeadline(self):
		if (timezone.now() > self.deadline):	return True
		else:	return False

	company_name = models.CharField("Organization", max_length=200)
	profile = models.CharField("Job Profile", max_length=50)
	location = models.CharField("Location", max_length=50, blank=True, null=True)
	dateofvisit = models.DateTimeField("Date of Visit", default=datetime.now)
	package = models.CharField("Package", max_length=10, blank=True, null=True)
	selectionprocess = models.CharField("Selection Process", max_length=50, blank=True, null=True)

	JOBSTREAMS = (
		('CSE', 'CSE'),
		('ECE', 'ECE'),
		('B', 'Both'),
		)
	job_stream = models.CharField("Job Stream", max_length=3, choices=JOBSTREAMS, default='CSE')

	CATEGORYCHOICES = (
		('AP', 'A+'),
		('A', 'A'),
		('B', 'B'),
		)
	category = models.CharField("Company Category", max_length=2, choices=CATEGORYCHOICES)

	JOBTYPES = (
		('T', 'Technical'),
		('NT', 'Non-Technical'),
		)
	jobtype = models.CharField("Job Type", max_length=2, choices=JOBTYPES, default='T')
	
	batch = models.ManyToManyField(Batch, related_name='jobbatch', null=True)
	cgpa_min = models.FloatField("Minimum CGPA", max_length=2, default=0)
	min_tenthmarks = models.IntegerField("Minimum Class X Marks", max_length=3, default=0)
	min_twelfthmarks = models.IntegerField("Minimum Class XII Marks", max_length=3, default=0)
	
	backs = (
		(0, '0'),
		(1, '1'),
		(2, '2'),
		(3, '3'),
		(4, '4+'),
		)
	max_blacklogs = models.IntegerField("Maximum Backlogs", max_length=2, default=5, choices=backs)

	OPENED_CLOSED = (
		('O', 'Open'),
		('A', 'Applications Closed'),
		('C', 'Closed')
		)
	status = models.CharField("Status", max_length=1, choices=OPENED_CLOSED, default='O')
	
	jobfile = models.FileField("File ", upload_to='jobfiles', default='', storage=OverwriteStorage(), blank=True,
		null=True)

	createdon = models.DateTimeField("Application Creation Date", default=datetime.now)
	deadline = models.DateTimeField("Application Deadline", default=datetime.now)
	deadlineexpired = property(checkdeadline)

	def __str__(self):  # __unicode__ on Python 2
		return self.profile + ', ' + self.company_name


class Student(models.Model):
	user = models.OneToOneField(User)
	rollno = models.CharField("Roll No", max_length=10, primary_key=True)
	name = models.CharField("Full Name", max_length=100)
	batch = models.ForeignKey(Batch, related_name='studentsinbatch')
	dob = models.DateTimeField("Date of Birth")

	genderchoices = (
		('M', 'Male'),
		('F', 'Female'),
		)
	gender = models.CharField("Gender", max_length=1, choices=genderchoices, default='M')

	STARTYEARS = (
		(2003, '2003'),
		(2004, '2004'),
		(2005, '2005'),
		(2006, '2006'),
		(2007, '2007'),
		(2008, '2008'),
		(2009, '2009'),
		(2010, '2010'),
		(2011, '2011'),
		(2012, '2012'),
		(2013, '2013'),
		(2014, '2014'),
		)

	ENDYEARS = (
		(2007, '2007'),
		(2008, '2008'),
		(2009, '2009'),
		(2009, '2009'),
		(2010, '2010'),
		(2011, '2011'),
		(2011, '2011'),
		(2012, '2012'),
		(2013, '2013'),
		(2014, '2014'),
		(2015, '2015'),
		(2016, '2016'),
		(2017, '2017'),
		)
	startyear_ug = models.IntegerField("Undergraduate Starting Year", max_length=4, choices=STARTYEARS, default="2011",
		blank=True, null=True)
	passingyear_ug = models.IntegerField("Undergraduate Completion Year", max_length=4, choices=ENDYEARS,
		default="2015", blank=True, null=True)

	startyear_pg = models.IntegerField("Postgraduate Starting Year", max_length=4, choices=STARTYEARS, blank=True,
		null=True)
	passingyear_pg = models.IntegerField("Postgraduate Completion Year", max_length=4, choices=ENDYEARS, blank=True,
		null=True)

	phone = models.CharField("Phone Number", max_length=10)
	email = models.EmailField(max_length=70)
	email_personal = models.EmailField("Personal Email", max_length=70, blank=True, null=True)
	cgpa_ug = models.FloatField("Ug. CGPA", max_length=4, default=0)
	university_ug = models.CharField("Undergraduate University", default="IIIT Delhi", max_length=100)
	institution_ug = models.CharField("Undergraduate College", default="IIIT Delhi", max_length=100)

	passingyear_tenth = models.IntegerField("Class X Passing Year", max_length=4, default=2009)
	passingyear_twelfth = models.IntegerField("Class XII Passing Year", max_length=4, default=2011)
	percentage_tenth = models.FloatField("Class X Aggregate Percent", max_length=4)
	percentage_twelfth = models.FloatField("Class XII Aggregate Percent", max_length=4)

	cgpa_pg = models.FloatField("Pg. CGPA", max_length=4, default=0, blank=True, null=True)


	university_pg = models.CharField("Postgraduate University", max_length=100, blank=True, null=True)
	institution_pg = models.CharField("Postgraduate College", max_length=100, blank=True, null=True)

	backs = (
		(0, '0'),
		(1, '1'),
		(2, '2'),
		(3, '3'),
		(4, '4+'),
		)
	backlogs = models.IntegerField("Number of Backlogs", max_length=2, default=0, choices=backs)
	
	years = (
		(0, '0'),
		(1, '1'),
		(2, '2'),
		(3, '3'),
		(4, '4+'),
		)
	work_experience = models.IntegerField("Previous Work Experience (Years)", choices=years, max_length=2, default=0)
	
	home_city = models.CharField("Home City", max_length=20)
	home_state = models.CharField("Home State", max_length=20)

	credits_completed = models.CharField("Completed Credits", max_length=3, default=0, blank=True)

	resume = models.FileField("resume", upload_to='resume', default='', storage=OverwriteStorage())
	companyapplications = models.ManyToManyField(Job, related_name='applicants', null=True, blank=True)

	STATUS = (
		('P', 'Placed'),
		('N', 'Not Placed'),
		('D', 'Debarred'),       #Debarred from placement
		('NI', 'Not Interested') #for students who live a thuglife :P a+ ppl will also be categorised here
		)
	status = models.CharField(max_length=2, choices=STATUS, default='N')
	
	placedat = models.ManyToManyField(Job, related_name='selectedcandidates', null=True, blank=True)
	createdon = models.DateTimeField("Student Creation Date", default=datetime.now)

	def __str__(self):  # __unicode__ on Python 2
		return self.pk + ' ' + self.name


class Feedback(models.Model):
	TYPES = (
			('B', 'Bug Report'),
			('F', 'Feature Request'),
			('C', 'Comment'),
		)
	type = models.CharField("Feedback Type", max_length=1, choices=TYPES, default='C')
	title = models.CharField("Title", max_length=100)
	body = models.TextField("Feedback Details")
	createdon = models.DateTimeField(auto_now_add=True)
