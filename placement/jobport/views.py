# TODO
# Use decorators

import hashlib
import os
import zipfile
import StringIO
import csv

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import Group
from django.utils import timezone
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from multiprocessing import Process
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from placement import settings
from . import forms
from .models import Job, Student, Batch
from .helpers import is_admin, is_member, is_eligible, checkdeadline


def _send_mail(subject, text_content, host_user, recipient_list):
	msg = EmailMultiAlternatives(subject, text_content, host_user, recipient_list)
	a=msg.send()
	print "Mail sent"

def send_mail(subject, text_content, recipient_list):
	p = Process(target=_send_mail, args=(subject, text_content, settings.EMAIL_HOST_USER, recipient_list))
	p.start()

def server_error(request):
	response = render(request, "jobport/500.html")
	response.status_code = 500
	return response

def not_found(request):
	response = render(request, "jobport/404.html")
	response.status_code = 404
	return response



def test(request):
	return render(request, 'jobport/material.min.js.map')

def home(request):
	if request.user.is_authenticated():
		context = {'user': request.user, 'jobs': Job.objects.all().order_by('-deadline')}
		if is_member(request.user, 'admin'):
			return render(request, 'jobport/admin_home.html', context)
		else:
			studentgroup = Group.objects.get(name='student')
			if (not is_member(request.user, studentgroup)):
				return HttpResponseRedirect('/newuser')
			return render(request, 'jobport/home_student.html', context)
	return render(request, 'jobport/welcome.html')


@login_required()
def jobapply(request, jobid):
#	if request.user.is_authenticated():
	if (timezone.now() < Job.objects.get(pk=jobid).deadline):
		if (is_eligible(request.user.student, Job.objects.get(pk=jobid))['value']):
			request.user.student.companyapplications.add(Job.objects.get(pk=jobid))
			messages.success(request, 'Thanks for applying!')
			return HttpResponseRedirect('/')
		else:
			return render(request, 'jobport/badboy.html')

	else:
		return render(request, 'jobport/latedeadline.html')


@login_required()
def jobwithdraw(request, jobid):
#	if request.user.is_authenticated():
	if (timezone.now() < Job.objects.get(pk=jobid).deadline):
		request.user.student.companyapplications.remove(Job.objects.get(pk=jobid))
		messages.success(request, 'You have withdrawn!')
		return HttpResponseRedirect('/')
	else:
		return render(request, 'jobport/latedeadline.html')


@login_required()
def myapplications(request):
#	if request.user.is_authenticated():
	studentgroup = Group.objects.get(name='student')
	if (not is_member(request.user, studentgroup)):
		return HttpResponseRedirect('/newuser')
	context = {'user': request.user, 'jobs': request.user.student.companyapplications.all()}
	return render(request, 'jobport/applications_student.html', context)


@login_required()
def jobpage(request, jobid):
#	if request.user.is_authenticated():
	if is_admin(request.user):
		context = {'user': request.user, 'job': Job.objects.get(pk=jobid)}
		return render(request, 'jobport/admin_job.html', context)
	else:
		hasapplied = request.user.student.companyapplications.filter(pk__contains=jobid).count()
		iseligible = is_eligible(request.user.student, Job.objects.get(pk=jobid))
		deadlinepassed = checkdeadline(Job.objects.get(pk=jobid))
		context = {'user': request.user, 'job': Job.objects.get(pk=jobid), 'deadlinepassed': deadlinepassed,
				   'hasapplied': hasapplied, 'iseligible': iseligible['value'],
				   'iseligiblereasons': iseligible['reasons']}
		return render(request, 'jobport/job_student.html', context)


@login_required()
def admineditstudent(request, studentid):
	if is_admin(request.user):
		if request.method == 'POST':
			form = forms.AdminStudentForm(request.POST, request.FILES, instance=Student.objects.get(pk=studentid))
			if form.is_valid():
				usr = form.save(commit=False)
				if (request.FILES.__len__() == 0):
					usr.resume = Student.objects.get(pk=studentid).resume;
				else:
					salt = "1eT4nfB5mR"
					usr.resume.name = Student.objects.get(pk=studentid).user.username.split('@')[
										  0] + '_resume_' + hashlib.sha1(
						request.user.username.split('@')[0] + salt).hexdigest() + "." + usr.resume.name.split('.')[
										  -1]
				usr.email = Student.objects.get(pk=studentid).user.username
				usr.save()
				form.save_m2m()
				messages.success(request, 'Your form was saved')
				return HttpResponseRedirect('/batches')
			else:
				messages.error(request, 'Error in form!')
				context = {'form': form}
				return render(request, 'jobport/admin_editstudent.html', context)
		elif request.method == 'GET':
			studentform = forms.AdminStudentForm(instance=Student.objects.get(pk=studentid))
			context = {'user': request.user, 'form': studentform, 'layout': 'horizontal'}
			return render(request, 'jobport/admin_editstudent.html', context)
		return HttpResponseRedirect('/')
	else:
		return render(request, 'jobport/badboy.html')


@login_required()
def getresumes(request, jobid):
	if is_admin(request.user):
		filenames = []
		if (request.GET.get('req') == 'selected'):
			checklist = Job.objects.get(pk=jobid).selectedcandidates.all()
			zip_subdir = Job.objects.get(pk=jobid).company_name + "_" + Job.objects.get(
				pk=jobid).profile + "_Selected_Resumes"
		else:
			checklist = Job.objects.get(pk=jobid).applicants.all()  # AllApplicants
			zip_subdir = Job.objects.get(pk=jobid).company_name + "_" + Job.objects.get(
				pk=jobid).profile + "_Applicant_Resumes"
		for student in checklist:
			if (request.GET.get('qual') == 'G' and student.batch.pg_or_not == 'G'):
				continue
			if (request.GET.get('qual') == 'P' and student.batch.pg_or_not == 'P'):
				continue
			filenames.append(student.resume.path)
		# Folder name in ZIP archive which contains the above files
		# E.g [thearchive.zip]/somefiles/file2.txt

		zip_filename = "%s.zip" % zip_subdir

		# Open StringIO to grab in-memory ZIP contents
		s = StringIO.StringIO()

		# The zip compressor
		zf = zipfile.ZipFile(s, "w")

		for fpath in filenames:
			# Calculate path for file in zip
			fdir, fname = os.path.split(fpath)
			zip_path = os.path.join(zip_subdir, fname)

			# Add file, at correct path
			zf.write(fpath, zip_path)

		# Must close zip for all contents to be written
		zf.close()

		# Grab ZIP file from in-memory, make response with correct MIME-type
		resp = HttpResponse(s.getvalue(), mimetype="application/x-zip-compressed")
		# ..and correct content-disposition
		resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

		return resp
	else:
		return render(request, 'jobport/badboy.html')


@login_required()
def profile(request):
	studentgroup = Group.objects.get(name='student')
	if (not is_member(request.user, studentgroup)):
		return HttpResponseRedirect('/newuser')
	if request.method == 'POST':
		form = forms.StudentForm(request.POST, request.FILES, instance=request.user.student)
		# print form.cleaned_data
		if form.is_valid():
			usr = form.save(commit=False)
			usr.user = request.user
			usr.email = request.user.username
			if (request.FILES.__len__() == 0):
				usr.resume = request.user.student.resume;
			else:
				salt = "1eT4nfB5mR"
				usr.resume.name = request.user.username.split('@')[0] + "_resume_" + hashlib.sha1(
					request.user.username.split('@')[0] + salt).hexdigest() + "." + usr.resume.name.split('.')[-1]
			# print str("Hello " + str(usr.resume))
			usr.save()
			messages.success(request, 'Your details were saved.')
			return HttpResponseRedirect('/')
		else:
			# Invalid form
			# messages.error(request, 'Error in form!')
			context = {'form': form, 'student': request.user.student}
			return render(request, 'jobport/student_profile.html', context)
	elif request.method == 'GET':
		studentform = forms.StudentForm(instance=request.user.student)
		context = {'user': request.user, 'form': studentform, 'layout': 'horizontal',
				   'student': request.user.student}
		return render(request, 'jobport/student_profile.html', context)


def newuser(request):
	studentgroup, created = Group.objects.get_or_create(name='student')  # Creating user group
	if request.user.is_authenticated():
		if is_member(request.user, studentgroup):
			HttpResponseRedirect('/')
		if request.method == 'POST':
			form = forms.NewStudentForm(request.POST, request.FILES)
			# print form.cleaned_data
			if form.is_valid():
				# import pdb
				# pdb.set_trace()
				usr = form.save(commit=False)
				usr.user = request.user
				usr.email = request.user.username
				# usr.resume.name = request.user.username.split('@')[0]  + "_resume." + usr.resume.name.split('.')[-1]
				# usr.resume.name = hashlib.sha256(request.user.username.split('@')[0] + "_resume." + usr.resume.name.split('.')[-1]).hexdigest() + '.pdf'
				salt = "1eT4nfB5mR"
				usr.resume.name = request.user.username.split('@')[0] + "_resume_" + hashlib.sha1(
					request.user.username.split('@')[0] + salt).hexdigest() + "." + usr.resume.name.split('.')[-1]
				usr.save()
				# messages.success(request, 'Your form was saved')
				studentgroup.user_set.add(request.user)
				# batch.get.objects.get(pk=batchid).
				usr.batch = form.cleaned_data['batch']

				messages.success(request, 'Your details were saved. Welcome to JobPort.')
				return HttpResponseRedirect('/')
			else:
				# Invalid form
				# messages.error(request, 'Error in form!')
				context = {'form': form}
				return render(request, 'jobport/newstudent.html', context)
		elif request.method == 'GET':
			studentform = forms.NewStudentForm()
			context = {'user': request.user, 'form': studentform, 'layout': 'horizontal'}
			return render(request, 'jobport/newstudent.html', context)
	return HttpResponseRedirect('/')


def logout(request):
	"""Logs out user"""
	auth_logout(request)
	return HttpResponseRedirect('/')


def needlogin(request):
	return render(request, 'jobport/needlogin.html')


# def BingSearchAPI(request):
# uri = "https://api.datamarket.azure.com/Bing/Search/v1/Image?Query=%27"
# appid =" hXUWxK4P+SdIi16Frvubczbv4jQVRnPMi4QOD+YpJo4"
# return https://api.datamarket.azure.com/Bing/Search/v1/Image?Query=%27xbox%27


@login_required()
def openjob(request):
	if is_admin(request.user):
		if request.method == 'POST':
			form = forms.JobForm(request.POST)
			if form.is_valid():
				tosavejob = form.save(commit=False	)
				tosavejob.createdon = timezone.now()
				allowed_batches  = tosavejob.batch
				tosavejob.save()
				recipients = []
				for student in Student.objects.all():
					recipients.append(student.email)
				settings.EMAIL_HOST_USER+='JobPort'
				send_mail(
				'New Job in JobPort!',
				'Hey!\n\nA new job for ' + tosavejob.profile + ', ' + tosavejob.company_name + ' was added on JobPort. \n Please login at jobport.iiitd.edu.in:8081', recipients
				)
				settings.EMAIL_HOST_USER+=''
				return HttpResponseRedirect('/')
			else:
				context = {'form': form}
				return render(request, 'jobport/openjob.html', context)
		else:
			form = forms.JobForm()
			c = {'form': form}
			return render(request, 'jobport/openjob.html', c)
	else:
		return render(request, 'jobport/notallowed.html')


@login_required()
def jobdelete(request, jobid):
	if is_admin(request.user):
		Job.objects.get(pk=jobid).delete()
		return HttpResponseRedirect('/')


@login_required()
def jobedit(request, jobid):
	if is_admin(request.user):
		if request.method == 'POST':
			form = forms.JobForm(request.POST, request.FILES, instance=Job.objects.get(pk=jobid))
			if form.is_valid():
				#print "Valid form"
				form.save()  # This does the trick!
				messages.success(request, 'Job was saved')
				return HttpResponseRedirect('/job/' + str(jobid) + '/')
			else:
				#Invalid form
				#messages.error(request, 'Error in form!')
				#print form
				context = {'form': form}
				return render(request, 'jobport/admin_editjob.html', context)
		else:
			form = forms.JobForm(instance=Job.objects.get(pk=jobid))
			c = {'form': form}
			return render(request, 'jobport/admin_editjob.html', c)


@login_required()
def jobapplicants(request, jobid):
	if is_admin(request.user):
		count = 0
		for student in Student.objects.all():
			if is_eligible(student, Job.objects.get(pk=jobid))['value']:
				count = count + 1
		context = {'eligiblestudentcount': count, 'applicants': Job.objects.get(pk=jobid).applicants.all(),
				   'job': Job.objects.get(pk=jobid)}
		return render(request, 'jobport/admin_jobapplicants.html', context)


@login_required()
def sendselectedemail(request, jobid):
	if is_admin(request.user):
		candemail = []
		thejob = Job.objects.get(pk=jobid)
		for candidate in thejob.selectedcandidates.all():
			candidate.status = 'P'
			candidate.save()
			candemail = candemail + [str(candidate.email)]
		send_mail(
				'Congratulations! You\'ve been placed! :D',
				"Hey!\n\nCongratulations! You have been placed as ' + thejob.profile + ' at ' + thejob.company_name!!", candemail
				)
		messages.success(request, 'Mails Sent!')
	return HttpResponseRedirect('/')


@login_required()
def adminjobselected(request, jobid):
	if is_admin(request.user):
		if request.method == 'POST':
			form = forms.AdminSelectedApplicantsForm(request.POST, instance=Job.objects.get(pk=jobid))
			if form.is_valid():
				tosavejob = form.save(commit=False)
				tosavejob.save()
				form.save()
				form.save_m2m()
				for candidate in Job.objects.get(pk=jobid).selectedcandidates.all():
					candidate.status = 'P'
					candidate.save()
				return HttpResponseRedirect('/')
			else:
				context = {'form': form}
				return render(request, 'jobport/admin_jobselections.html', context)
		else:
			form = forms.AdminSelectedApplicantsForm(instance=Job.objects.get(pk=jobid))
			context = {'selected': Job.objects.get(pk=jobid).selectedcandidates.all(), 'form': form,
					   'job': Job.objects.get(pk=jobid)}
			return render(request, 'jobport/admin_jobselections.html', context)


@login_required()
def uploadcgpa(request):
	if is_admin(request.user):
		if request.method == 'POST':
			if (not request.FILES.get('cgpafile', None)) or not request.FILES['cgpafile'].size:
				messages.error(request, 'File Not Found!')
				return render(request, 'jobport/admin_uploadcgpa.html')
			upload_file = request.FILES['cgpafile']
			notfound = []
			for row in csv.reader(upload_file.read().splitlines()):
				try:
					stud = Student.objects.get(pk=row[0])
					if (row[0][:2].upper() == 'MT'):
						stud.cgpa_mtech = float(row[1])
					else:
						stud.cgpa = float(row[1])
					stud.save()
				except ObjectDoesNotExist:
					notfound.append(row[0])
			context = {'notfound': notfound}
			messages.success(request, 'CGPA was succesfully uploaded')
			return render(request, 'jobport/admin_uploadcgpa.html', context)
		else:
			return render(request, 'jobport/admin_uploadcgpa.html')
	else:
		return render(request, 'jobport/notallowed.html')  # 403 Error


@login_required()
def stats(request):
	if is_admin(request.user):
		numstudentsplaced = 0
		cgpahistdata = []
		Students = Student.objects.all()
		Jobs = Job.objects.all()
		for student in Students:
			if student.status == 'P':
				numstudentsplaced = numstudentsplaced + 1
			#CGPA Hist
			if student.batch.pg_or_not == 'G':
				if student.cgpa_ug != None and student.cgpa_ug != 0:
					cgpahistdata.append([student.rollno, student.cgpa_ug])
			else:
				if student.cgpa_pg != None and student.cgpa_pg != 0:
					cgpahistdata.append([student.rollno, student.cgpa_pg])

		jobcgpahistdata = []
		for job in Jobs:
			if job.cgpa_min != None:
				jobcgpahistdata.append([(job.company_name + ", " + job.profile), job.cgpa_min])

		placedunplaceddata = [["Placed Students", numstudentsplaced],
							  ["Unplaced Students", len(Students) - numstudentsplaced]]

		context = {'cgpahistdata': cgpahistdata, 'jobcgpahistdata': jobcgpahistdata,
				   'placedunplaceddata': placedunplaceddata, 'numstudents': len(Student.objects.all()),
				   'numstudentsplaced': numstudentsplaced, 'numjobs': len(Job.objects.all())}
		return render(request, 'jobport/admin_stats.html', context)


@login_required()
def blockedUnplacedlist(request):
	if is_admin(request.user):
		response = HttpResponse(content_type='text/csv')

		if (request.GET.get('req') == 'blocked'):
			students = Student.objects.filter(status='BL')
			response['Content-Disposition'] = str('attachment; filename="' + 'BlockedStudents_list.csv"')
		elif (request.GET.get('req') == 'unplaced'):
			students = Student.objects.filter(status='N')
			response['Content-Disposition'] = str('attachment; filename="' + 'UnplacedStudents_list.csv"')
		elif (request.GET.get('req') == 'placed'):
			students = Student.objects.filter(status='P')
			response['Content-Disposition'] = str('attachment; filename="' + 'PlacedStudents_list.csv"')
		writer = csv.writer(response)
		writer.writerow(
			["RollNo", "Name", "Email", "Gender", "UnderGrad CGPA", "PostGrad CGPA", "Graduating University",
			 "PostGraduating University", "10th Marks", "12th Marks", "Backlogs", "Contact No."])
		for student in students:
			writer.writerow(
				[student.rollno, student.name, student.email, student.get_gender_display(), student.cgpa_ug,
				 student.cgpa_pg, student.university_ug, student.university_pg, student.percentage_tenth,
				 student.percentage_twelfth, student.get_backlogs_display(), student.phone])
		return response
	else:
		return render(request, 'jobport/badboy.html')


@login_required()
def getjobcsv(request, jobid):
	if is_admin(request.user):
		response = HttpResponse(content_type='text/csv')
		if (request.GET.get('req') == 'selected'):
			studlist = Job.objects.get(pk=jobid).selectedcandidates.all()
			name = Job.objects.get(pk=jobid).company_name + "_" + Job.objects.get(
				pk=jobid).profile + "_Selected.csv"
		elif (request.GET.get('req') == 'applied'):
			studlist = Job.objects.get(pk=jobid).applicants.all()
			name = Job.objects.get(pk=jobid).company_name + "_" + Job.objects.get(
				pk=jobid).profile + "_Applicants.csv"
		elif (request.GET.get('req') == 'eligible'):
			studlist = []
			for student in Student.objects.all():
				if is_eligible(student, Job.objects.get(pk=jobid))['value']:
					studlist.append(student)
			name = Job.objects.get(pk=jobid).company_name + "_" + Job.objects.get(
				pk=jobid).profile + "_Eligible.csv"

		response['Content-Disposition'] = str('attachment; filename="' + name + '"')
		writer = csv.writer(response)
		writer.writerow([Job.objects.get(pk=jobid).company_name, Job.objects.get(pk=jobid).profile])
		for student in studlist:
			if (student.batch.pg_or_not == 'G' and request.GET.get('qualification') != 'pg'):
				writer.writerow(
					["RollNo", "Name", "Email", "Gender", "CGPA", "Batch", "Graduating University", "10th Marks",
					 "12th Marks", "Backlogs", "Conact No."]
				)
				writer.writerow(
					[student.rollno, student.name, student.email, student.get_gender_display(), student.cgpa_ug,
					 student.university_ug, student.percentage_tenth, student.percentage_twelfth,
					 student.get_backlogs_display(), student.phone]
				)
			if (student.batch.pg_or_not == 'P' and request.GET.get('qualification') != 'ug'):
				writer.writerow(
					["RollNo", "Name", "Email", "Gender", "CGPA", "Batch", "Graduating University", "10th Marks",
					 "12th Marks", "Backlogs", "Conact No.", "UnderGrad CGPA"]
				)
				writer.writerow(
					[student.rollno, student.name, student.email, student.get_gender_display(), student.cgpa_pg,
					 student.batch, student.university_pg, student.percentage_tenth, student.percentage_twelfth,
					 student.get_backlogs_display(), student.phone, student.cgpa_ug]
				)
		return response
	else:
		return render(request, 'jobport/badboy.html')


@login_required()
def getbatchlist(request, batchid):
	if is_admin(request.user):
		response = HttpResponse(content_type='text/csv')
		studlist = Batch.objects.get(pk=batchid).studentsinbatch.all()
		name = Batch.objects.get(pk=batchid).title
		response['Content-Disposition'] = str('attachment; filename="' + name + '_list.csv"')
		writer = csv.writer(response)
		writer.writerow(
			["RollNo", "Name", "Email", "Gender", "UnderGrad CGPA", "PostGrad CGPA", "Graduating University",
			 "PostGraduating University", "10th Marks", "12th Marks", "Backlogs", "Contact No."])
		for student in studlist:
			writer.writerow(
				[student.rollno, student.name, student.email, student.get_gender_display(), student.cgpa_ug,
				 student.cgpa_pg, student.university_ug, student.university_pg, student.percentage_tenth,
				 student.percentage_twelfth, student.get_backlogs_display(), student.phone])
		return response
	else:
		return render(request, 'jobport/badboy.html')


def feedback(request):
	if (request.method == 'POST'):
		form = forms.FeedbackForm(request.POST)
		# pdb.set_trace()
		if form.is_valid():
			form.save()
			type = form.cleaned_data['type']
			type = dict(form.fields['type'].choices)[type]
			settings.EMAIL_HOST_USER+='Tester'
			send_mail(
				'[' + type + '] ' + form.cleaned_data['title'],
				'A new feedback was posted on JobPort' + '\n\n' + form.cleaned_data['body'], ['jobportiiitd@gmail.com']
				)
			settings.EMAIL_HOST_USER+=''
			messages.success(request, 'Thanks for filling your precious feedback! :) ')
			return HttpResponseRedirect('/')
		else:
			context = {'form': form}
			return render(request, 'jobport/feedback.html', context)
	else:
		form = forms.FeedbackForm()
		context = {'form': form}
		return render(request, 'jobport/feedback.html', context)


@login_required()
def fileview(request, filename):
		response = HttpResponse()
		response['Content-Type'] = 'application/pdf'
		# response['X-Accel-Redirect'] = "/protected/%s"%filename
		# response['Content-Disposition'] = 'filename="somefilename.pdf"'
		return response


@login_required()
def batchcreate(request):
	if is_admin(request.user):
		if request.method == 'POST':
			form = forms.BatchForm(request.POST)
			if form.is_valid():
				tosavebatch = form.save(commit=False)
				tosavebatch.createdon = timezone.now()
				tosavebatch.save()
			else:
				messages.error(request, "There was error in the data, please try again!")
			return HttpResponseRedirect(reverse('viewbatches'))
		else:
			form = forms.BatchForm()
			c = {'form': form}
			return render(request, 'jobport/openbatch.html', c)
	else:
		return render(request, 'jobport/notallowed.html')


@login_required()
def batchdestroy(request, batchid):
	if is_admin(request.user):
		Batch.objects.get(pk=batchid).delete()
		return HttpResponseRedirect('/')


@login_required()
def batchedit(request, batchid):
	if is_admin(request.user):
		if request.method == 'POST':
			form = forms.BatchForm(request.POST, instance=Batch.objects.get(pk=batchid))
			if form.is_valid():
				form.save()
				messages.success(request, 'Batch was updated!')
				return HttpResponseRedirect('/batch/' + str(batchid) + '/')
			else:
				context = {'form': form}
				return render(request, 'jobport/admin_editbatch.html', context)
		else:
			form = forms.BatchForm(instance=Batch.objects.get(pk=batchid))
			c = {'form': form}
			return render(request, 'jobport/admin_editbatch.html', c)


@login_required()
def viewbatches(request):
	if is_admin(request.user):
		batches = Batch.objects.all()
		return render(request, 'jobport/batches.html', {'batch': batches})
	else:
		return render(request, 'jobport/badboy.html')


@login_required()
def batchpage(request, batchid):
	if is_admin(request.user):
		context = {'user': request.user, 'student': Batch.objects.get(pk=batchid).studentsinbatch.all(),
				   'batch': Batch.objects.get(pk=batchid)}

		return render(request, 'jobport/admin_batch.html', context)
	return render(request, 'jobport/welcome.html')


@login_required()
def getbatchresumes(request, batchid):
	if is_admin(request.user):
		# Files (local path) to put in the .zip
		filenames = []
		checklist = Batch.objects.get(pk=batchid).studentsinbatch.all()
		zip_subdir = Batch.objects.get(pk=batchid).title + "_resumes"
		for student in checklist:
			# if (request.GET.get('qualification')=='btech' and student.qualification!='B'):
			# continue
			# if (request.GET.get('qualification')=='mtech' and student.qualification!='M'):
			filenames.append(student.resume.path)
		# continue
		# Folder name in ZIP archive which contains the above files
		# E.g [thearchive.zip]/somefiles/file2.txt

		zip_filename = "%s.zip" % zip_subdir

		# Open StringIO to grab in-memory ZIP contents
		s = StringIO.StringIO()

		# The zip compressor
		zf = zipfile.ZipFile(s, "w")

		for fpath in filenames:
			# Calculate path for file in zip
			fdir, fname = os.path.split(fpath)
			zip_path = os.path.join(zip_subdir, fname)

			# Add file, at correct path
			zf.write(fpath, zip_path)

		# Must close zip for all contents to be written
		zf.close()

		# Grab ZIP file from in-memory, make response with correct MIME-type
		resp = HttpResponse(s.getvalue(), mimetype="application/x-zip-compressed")
		# ..and correct content-disposition
		resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

		return resp
	else:
		return render(request, 'jobport/badboy.html')


@login_required()
def uploadstudentsinbatch(request, batchid):
	if is_admin(request.user):
		if request.method == 'POST':
			file = request.FILES['students']
			notfound = []
			for row in csv.reader(file.read().splitlines()):
				try:
					stud = Student.objects.get(pk=row[0])
					batch = Batch.get.objects(pk=batchid)
					stud.batch = batch
					# stud.cgpa=float(row[1])
					stud.save()
				except ObjectDoesNotExist:
					notfound.append(row[0])
			context = {'notfound': notfound}
			messages.success(request, 'Students succesfully added to the Batch!')
			return render(request, 'jobport/admin_addstudentstobatch.html', context)
		else:
			return render(request, 'jobport/admin_addstudentstobatch.html')
	else:
		return render(request, 'jobport/notallowed.html')  # 403 Error


@login_required()
def search(request):
	if is_admin(request.user):
		form = forms.RootSearchForm(request.GET)
		query = request.GET.get('q')
		if query=='':
			messages.error(request, 'Please enter a Query!')
			return render(request, 'jobport/notallowed.html')
		else:
			return render(request, 'jobport/result.html',
					  {'search_query': query, 'results': form.search()})
	else:
		return render(request, 'jobport/notallowed.html')  # 403 Error
