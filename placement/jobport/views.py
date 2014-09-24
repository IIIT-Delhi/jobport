from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import Group, User
from django.core.mail import send_mail
from django.utils import timezone
from jobport.forms import StudentForm, NewStudentForm, JobForm, AdminStudentForm, AdminSelectedApplicantsForm, FeedbackForm, BatchForm
from django.contrib import messages
from urlparse import urlparse
from .models import Job, Student, Batch
from post_office import mail
from django.conf import settings
from django.core.urlresolvers import reverse
import hashlib, os, zipfile, StringIO, csv, re, urllib2, simplejson

def server_error(request):
	response = render(request, "jobport/500.html")
	response.status_code = 500
	return response
def not_found(request):
	response = render(request, "jobport/404.html")
	response.status_code =404
	return response

def is_member(user,group):
	return user.groups.filter(name=group)

def is_eligible(candidate, job):
	eligibility={}
	eligibility['value']=True
	eligibility['reason']=""
	if (candidate.batch.pg_or_not == 'G'):
		if (candidate.cgpa_ug<job.cgpa_min):
				eligibility['value']=False
				eligibility['reason']="Your CGPA is below the requirement."
	else:
		if (candidate.cgpa_pg<job.cgpa_min):
			eligibility['value']=False
			eligibility['reason']="Your CGPA is below the requirement."
	if (candidate.percentage_tenth<job.min_tenthmarks):
		eligibility['value']=False
		eligibility['reason']="Your 10th Marks are below the requirement."
	if (candidate.percentage_twelfth<job.min_twelfthmarks):
		eligibility['value']=False
		eligibility['reason']="Your 12th Marks are below the requirement."
	if (candidate.backlogs>job.max_blacklogs):
		eligibility['value']=False
		eligibility['reason']="You have too many backlogs."
	if (candidate.status=='B'):
		eligibility['value']=False
		eligibility['reason']="You have been blocked by the placement cell."
	if (job.status=='C' or job.status=='A'):
		eligibility['value']=False
		eligibility['reason']="This Job cannot be applied to."
	Vals=[]
	for b in job.batch.all():
		if(b!= candidate.batch): Vals.append(False)
		else: Vals.append(True)
	if not any(Vals):
		temp = True
		eligibility['value'] = temp
		eligibility['value'] = "This job is not for you!"
	return eligibility


def checkdeadline(job):
	if (timezone.now()>job.deadline):
		return True
	else:
		return False

def is_admin(user):
	allowed_group = set(['admin'])
	usr = User.objects.get(username=user)
	groups = [ x.name for x in usr.groups.all()]
	if allowed_group.intersection(set(groups)):
	   return True
	return False

def home(request):
	if request.user.is_authenticated():
		context = {'user': request.user, 'jobs': Job.objects.all().order_by('-deadline')}
		if is_member(request.user, 'admin'):
			return render(request, 'jobport/admin_home.html', context)
		else:
			studentgroup=Group.objects.get(name='student')
			if (not is_member(request.user, studentgroup)):
				return HttpResponseRedirect('/newuser')
			return render(request, 'jobport/home_student.html', context)
	return render(request, 'jobport/welcome.html')

def jobapply(request, jobid):
	if request.user.is_authenticated():
		if (timezone.now()<Job.objects.get(pk=jobid).deadline):
			if(is_eligible(request.user.student,Job.objects.get(pk=jobid))['value']):
				request.user.student.companyapplications.add(Job.objects.get(pk=jobid))
				messages.success(request, 'Thanks for applying!')
				return HttpResponseRedirect('/')
			else:
				return render(request, 'jobport/badboy.html')

		else:
			return render(request, 'jobport/latedeadline.html')

def jobwithdraw(request, jobid):
	if request.user.is_authenticated():
		if (timezone.now()>Job.objects.get(pk=jobid).deadline):
			request.user.student.companyapplications.remove(Job.objects.get(pk=jobid))
			messages.success(request, 'You have withdrawn!')
			return HttpResponseRedirect('/')
		else:
			return render(request, 'jobport/latedeadline.html')

def myapplications(request):
	if request.user.is_authenticated():
		studentgroup=Group.objects.get(name='student')
		if (not is_member(request.user, studentgroup)):
			return HttpResponseRedirect('/newuser')
		context = {'user': request.user, 'jobs': request.user.student.companyapplications.all()}
		return render(request, 'jobport/applications_student.html', context)
	return render(request, 'jobport/welcome.html')

def jobpage(request, jobid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			context = {'user': request.user, 'job': Job.objects.get(pk=jobid)}
			return render(request, 'jobport/admin_job.html', context)
		else:
			hasapplied=request.user.student.companyapplications.filter(pk__contains=jobid).count()
			iseligible = is_eligible(request.user.student,Job.objects.get(pk=jobid))
			deadlinepassed=checkdeadline(Job.objects.get(pk=jobid))
			context = {'user': request.user, 'job': Job.objects.get(pk=jobid), 'deadlinepassed': deadlinepassed, 'hasapplied': hasapplied, 'iseligible': iseligible['value'], 'iseligiblereason': iseligible['reason']}
			return render(request, 'jobport/job_student.html', context)
	return render(request, 'jobport/welcome.html')

def admineditstudent(request, studentid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			if request.method == 'POST':
				form = AdminStudentForm(request.POST, request.FILES, instance=Student.objects.get(pk=studentid))
				if form.is_valid():
					usr = form.save(commit=False)
					if(request.FILES.__len__()==0):
						usr.resume = Student.objects.get(pk=studentid).resume;
					else:
						usr.resume.name = Student.objects.get(pk=studentid).user.username.split('@')[0] +'_resume_' + hashlib.sha1(request.user.username.split('@')[0]).hexdigest() + "." + usr.resume.name.split('.')[-1]
					usr.email = Student.objects.get(pk=studentid).user.username
					usr.save()
					form.save_m2m()
					messages.success(request, 'Your form was saved')
					return HttpResponseRedirect('/batches')
				else:
					messages.error(request, 'Error in form!')
					context={'form': form}
					return render(request,'jobport/admin_editstudent.html', context)
			elif request.method == 'GET':
				studentform = AdminStudentForm(instance=Student.objects.get(pk=studentid))
				context = {'user': request.user, 'form': studentform, 'layout': 'horizontal'}
				return render(request, 'jobport/admin_editstudent.html', context)
			return HttpResponseRedirect('/')
		else:
			return render(request, 'jobport/badboy.html')
	else:
		return render(request, 'jobport/needlogin.html')

def getresumes(request,jobid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			filenames=[]
			if (request.GET.get('req')=='selected'):
				checklist=Job.objects.get(pk=jobid).selectedcandidates.all()
				zip_subdir = Job.objects.get(pk=jobid).company_name + "_" + Job.objects.get(pk=jobid).profile + "_Selected_Resumes"
			else:
				checklist=Job.objects.get(pk=jobid).applicants.all() #AllApplicants
				zip_subdir = Job.objects.get(pk=jobid).company_name + "_" + Job.objects.get(pk=jobid).profile + "_Applicant_Resumes"
			for student in checklist:
				if (request.GET.get('qual')=='G' and student.batch.pg_or_not=='G'):
					continue
				if (request.GET.get('qual')=='P' and student.batch.pg_or_not=='P'):
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
			resp = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
			# ..and correct content-disposition
			resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

			return resp
		else:
			return render(request, 'jobport/badboy.html')
	else:
		return render(request, 'jobport/needlogin.html')

def profile(request):
	if request.user.is_authenticated():
		studentgroup=Group.objects.get(name='student')
		if (not is_member(request.user, studentgroup)):
			return HttpResponseRedirect('/newuser')
		if request.method == 'POST':
			form = StudentForm(request.POST, request.FILES, instance=request.user.student)
			#print form.cleaned_data
			if form.is_valid():
				usr = form.save(commit=False)
				usr.user = request.user
				usr.email = request.user.username
				if(request.FILES.__len__()==0):
					usr.resume = request.user.student.resume;
				else:
					usr.resume.name = request.user.username.split('@')[0] + "_resume_" + hashlib.sha1(request.user.username.split('@')[0]).hexdigest() + "." + usr.resume.name.split('.')[-1]
				#print str("Hello " + str(usr.resume))
				usr.save()
				messages.success(request, 'Your details were saved.')
				return HttpResponseRedirect('/')
			else:
				#Invalid form
				#messages.error(request, 'Error in form!')
				context={'form': form, 'student': request.user.student}
				return render(request,'jobport/student_profile.html', context)
		elif request.method == 'GET':
			studentform = StudentForm(instance=request.user.student)
			context = {'user': request.user, 'form': studentform, 'layout': 'horizontal', 'student': request.user.student}
			return render(request, 'jobport/student_profile.html', context)
	return HttpResponseRedirect('/')

def newuser(request):
	studentgroup, created=Group.objects.get_or_create(name='student')    #Creating user group
	if request.user.is_authenticated():
		if is_member(request.user, studentgroup):
			HttpResponseRedirect('/')
		if request.method == 'POST':
			form = NewStudentForm(request.POST, request.FILES)
			#print form.cleaned_data
			if form.is_valid():
				# import pdb
				# pdb.set_trace()
				usr = form.save(commit=False)
				usr.user = request.user
				usr.email= request.user.username
				#usr.resume.name = request.user.username.split('@')[0]  + "_resume." + usr.resume.name.split('.')[-1]
			   # usr.resume.name = hashlib.sha256(request.user.username.split('@')[0] + "_resume." + usr.resume.name.split('.')[-1]).hexdigest() + '.pdf'
				usr.resume.name = request.user.username.split('@')[0] + "_resume_" + hashlib.sha1(request.user.username.split('@')[0]).hexdigest() +  "." + usr.resume.name.split('.')[-1]
				usr.save()
				#messages.success(request, 'Your form was saved')
				studentgroup.user_set.add(request.user)
				# batch.get.objects.get(pk=batchid).
				usr.batch = form.cleaned_data['batch']

				messages.success(request, 'Your details were saved. Welcome to JobPort.')
				return HttpResponseRedirect('/')
			else:
				#Invalid form
				#messages.error(request, 'Error in form!')
				context={'form': form}
				return render(request,'jobport/newstudent.html', context)
		elif request.method == 'GET':
			studentform = NewStudentForm()
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
#     uri = "https://api.datamarket.azure.com/Bing/Search/v1/Image?Query=%27"
#     appid =" hXUWxK4P+SdIi16Frvubczbv4jQVRnPMi4QOD+YpJo4"
#     return https://api.datamarket.azure.com/Bing/Search/v1/Image?Query=%27xbox%27

def openjob(request):
	if request.user.is_authenticated():
		if is_admin(request.user):
			if request.method == 'POST':
				form = JobForm(request.POST)
				if form.is_valid():
					tosavejob = form.save(commit=False)
					tosavejob.createdon=timezone.now()
					tosavejob.save()
					recipients=[]
					for student in Student.objects.all():
						recipients.append(student.email)
					mail.send(
						recipients,
						'jobportiiitd@gmail.com',
						subject='New Job in JobPort',
						message=('Hey!\n\nA new job for ' + tosavejob.profile + ', ' + tosavejob.company_name + ' was added on JobPort. \n login @ jobport.iiitd.edu.in:8081'),
						headers={'Reply-to': 'rashmil@iiitd.ac.in'},
						priority="high"
					)
					return HttpResponseRedirect('/')
				else:
					context={'form': form}
					return render(request,'jobport/openjob.html', context)
			else:
				form = JobForm()
				c = { 'form' : form }
				return render(request,'jobport/openjob.html', c)
		else:
			return render(request, 'jobport/notallowed.html')
	else:
		return render(request, 'jobport/needlogin.html')

def jobdelete(request,jobid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			Job.objects.get(pk=jobid).delete()
			return HttpResponseRedirect('/')
	else:
		return render(request, 'jobport/needlogin.html')
		#return render(request, 'home.html')

def jobedit(request,jobid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			if request.method == 'POST':
				form = JobForm(request.POST, request.FILES, instance=Job.objects.get(pk=jobid))
				if form.is_valid():
					#print "Valid form"
					form.save() #This does the trick!
					messages.success(request, 'Job was saved')
					return HttpResponseRedirect('/job/'+str(jobid)+'/')
				else:
					#Invalid form
					#messages.error(request, 'Error in form!')
					#print form
					context={'form': form}
					return render(request,'jobport/admin_editjob.html', context)
			else:
				form = JobForm(instance=Job.objects.get(pk=jobid))
				c = { 'form' : form }
				return render(request,'jobport/admin_editjob.html', c)
	else:
		return render(request, 'jobport/needlogin.html')
		#return render(request, 'home.html')

def jobapplicants(request, jobid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			count=0
			for student in Student.objects.all():
				if is_eligible(student, Job.objects.get(pk=jobid))['value']:
					count=count+1
			context={'eligiblestudentcount': count, 'applicants': Job.objects.get(pk=jobid).applicants.all(), 'job': Job.objects.get(pk=jobid)}
			return render(request,'jobport/admin_jobapplicants.html', context)
	return render(request, 'jobport/needlogin.html') #403 Error

def sendselectedemail(request, jobid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			candemail=[]
			thejob=Job.objects.get(pk=jobid)
			for candidate in thejob.selectedcandidates.all():
				candidate.status='P'
				candidate.save()
				candemail= candemail + [str(candidate.email)]
			mail.send(
				candemail,
				'jobportiiitd@gmail.com',
				subject='Congratulations! You\'ve been placed! :D',
				message=('Hey!\n\nCongratulations! You have been placed as ' + thejob.profile + ' at ' + thejob.company_name + '! Party Hard now!'),
				headers={'Reply-to': 'rashmil@iiitd.ac.in'},
				priority="high"
			)
			messages.success(request, 'Mails Sent!')
		return HttpResponseRedirect('/')
	return render(request, 'jobport/needlogin.html') #403 Error

def adminjobselected(request, jobid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			if request.method == 'POST':
				form = AdminSelectedApplicantsForm(request.POST, instance=Job.objects.get(pk=jobid))
				if form.is_valid():
					tosavejob = form.save(commit=False)
					tosavejob.save()
					form.save()
					form.save_m2m()
					for candidate in Job.objects.get(pk=jobid).selectedcandidates.all():
						candidate.status='P'
						candidate.save()
					return HttpResponseRedirect('/')
				else:
					context={'form': form}
					return render(request,'jobport/admin_jobselections.html', context)
			else:
				form = AdminSelectedApplicantsForm(instance=Job.objects.get(pk=jobid))
				context={'selected': Job.objects.get(pk=jobid).selectedcandidates.all(), 'form': form, 'job': Job.objects.get(pk=jobid)}
				return render(request,'jobport/admin_jobselections.html', context)
	return render(request, 'jobport/needlogin.html') #403 Error

def uploadcgpa(request):
	if request.user.is_authenticated():
		if is_admin(request.user):
			if request.method == 'POST':
				if (not request.FILES.get('cgpafile', None)) or not request.FILES['cgpafile'].size :
					messages.error(request,'File Not Found!')
					return render(request, 'jobport/admin_uploadcgpa.html')
				upload_file = request.FILES['cgpafile']
				notfound=[]
				for row in csv.reader(upload_file.read().splitlines()):
					try:
						stud = Student.objects.get(pk=row[0])
						if (row[0][:2].upper()=='MT'):
							stud.cgpa_mtech=float(row[1])
						else:
							stud.cgpa=float(row[1])
						stud.save()
					except ObjectDoesNotExist:
						notfound.append(row[0])
				context = {'notfound': notfound}
				messages.success(request, 'CGPA was succesfully uploaded')
				return render(request,'jobport/admin_uploadcgpa.html',context)
			else:
				return render(request,'jobport/admin_uploadcgpa.html')
		else:
			return render(request, 'jobport/notallowed.html') #403 Error
	return render(request, 'jobport/needlogin.html') #403 Error

def stats(request):
	if request.user.is_authenticated():
		if is_admin(request.user):
			numstudentsplaced=0
			cgpahistdata=[]
			Students=Student.objects.all()
			Jobs=Job.objects.all()
			for student in Students:
				if student.status=='P':
					numstudentsplaced=numstudentsplaced+1
				#CGPA Hist
				if student.batch.pg_or_not =='G':
					if student.cgpa_ug!=None and student.cgpa_ug!=0:
						cgpahistdata.append([student.rollno, student.cgpa_ug])
				else:
					if student.cgpa_pg!=None and student.cgpa_pg!=0:
						cgpahistdata.append([student.rollno, student.cgpa_pg])

			jobcgpahistdata=[]
			for job in Jobs:
				if job.cgpa_min!=None:
					jobcgpahistdata.append([(job.company_name + ", " + job.profile), job.cgpa_min])

			placedunplaceddata=[["Placed Students", numstudentsplaced],["Unplaced Students", len(Students)-numstudentsplaced]]


			context={'cgpahistdata': cgpahistdata, 'jobcgpahistdata': jobcgpahistdata, 'placedunplaceddata': placedunplaceddata, 'numstudents': len(Student.objects.all()),'numstudentsplaced': numstudentsplaced, 'numjobs': len(Job.objects.all())}
			return render(request,'jobport/admin_stats.html', context)
	return render(request, 'jobport/needlogin.html') #403 Error

def blockedUnplacedlist(request):
	if request.user.is_authenticated():
		if is_admin(request.user):
			response = HttpResponse(content_type='text/csv')

			if (request.GET.get('req')=='blocked'):
				students = Student.objects.filter(status='BL')
				response['Content-Disposition'] = str('attachment; filename="'+'BlockedStudents_list.csv"')
			elif(request.GET.get('req')=='unplaced'):
				students = Student.objects.filter(status='N')
				response['Content-Disposition'] = str('attachment; filename="'+'UnplacedStudents_list.csv"')
			elif(request.GET.get('req')=='placed'):
				students = Student.objects.filter(status='P')
				response['Content-Disposition'] = str('attachment; filename="'+'PlacedStudents_list.csv"')
			writer = csv.writer(response)
			writer.writerow(["RollNo", "Name", "Email", "Gender", "UnderGrad CGPA","PostGrad CGPA", "Graduating University","PostGraduating University", "10th Marks", "12th Marks", "Backlogs","Contact No."])
			for student in students:
					writer.writerow([student.rollno, student.name, student.email, student.get_gender_display(), student.cgpa_ug,student.cgpa_pg, student.university_ug,student.university_pg, student.percentage_tenth, student.percentage_twelfth, student.get_backlogs_display(),student.phone])
			return response
		else:
			return render(request, 'jobport/badboy.html')
	else:
		return render(request, 'jobport/needlogin.html')

def getjobcsv(request, jobid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			response = HttpResponse(content_type='text/csv')
			if (request.GET.get('req')=='selected'):
				studlist=Job.objects.get(pk=jobid).selectedcandidates.all()
				name=Job.objects.get(pk=jobid).company_name + "_" +Job.objects.get(pk=jobid).profile + "_Selected.csv"
			elif (request.GET.get('req')=='applied'):
				studlist=Job.objects.get(pk=jobid).applicants.all()
				name=Job.objects.get(pk=jobid).company_name + "_" +Job.objects.get(pk=jobid).profile + "_Applicants.csv"
			elif (request.GET.get('req')=='eligible'):
				studlist=[]
				for student in Student.objects.all():
					if is_eligible(student, Job.objects.get(pk=jobid))['value']:
						studlist.append(student)
				name=Job.objects.get(pk=jobid).company_name + "_" +Job.objects.get(pk=jobid).profile + "_Eligible.csv"
			#else:
			#    studlist=Student.objects.all()
			#    name="Students.csv"
			response['Content-Disposition'] = str('attachment; filename="'+name+'"')
			writer = csv.writer(response)
			writer.writerow([Job.objects.get(pk=jobid).company_name, Job.objects.get(pk=jobid).profile])
			for student in studlist:
				if (student.batch.pg_or_not=='G' and request.GET.get('qualification')!='pg'):
					writer.writerow(["RollNo", "Name", "Email", "Gender", "CGPA" ,"Batch", "Graduating University", "10th Marks", "12th Marks", "Backlogs", "Conact No."])
					writer.writerow([student.rollno, student.name, student.email, student.get_gender_display(), student.cgpa_ug, student.university_ug, student.percentage_tenth, student.percentage_twelfth, student.get_backlogs_display(),student.phone])
				if (student.batch.pg_or_not=='P' and request.GET.get('qualification')!='ug'):
					writer.writerow(["RollNo", "Name", "Email", "Gender", "CGPA" ,"Batch", "Graduating University", "10th Marks", "12th Marks", "Backlogs", "Conact No.","UnderGrad CGPA"])
					writer.writerow([student.rollno, student.name, student.email, student.get_gender_display(), student.cgpa_pg, student.batch, student.university_pg, student.percentage_tenth, student.percentage_twelfth, student.get_backlogs_display(),student.phone ,student.cgpa_ug])
			return response
		else:
			return render(request, 'jobport/badboy.html')
	else:
		return render(request, 'jobport/needlogin.html')

def getbatchlist(request,batchid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			response = HttpResponse(content_type='text/csv')
			studlist = Batch.objects.get(pk=batchid).studentsinbatch.all()
			name = Batch.objects.get(pk=batchid).text
			response['Content-Disposition'] = str('attachment; filename="'+name+'_list.csv"')
			writer = csv.writer(response)
			writer.writerow(["RollNo", "Name", "Email", "Gender", "UnderGrad CGPA","PostGrad CGPA", "Graduating University","PostGraduating University", "10th Marks", "12th Marks", "Backlogs","Contact No."])
			for student in studlist:
					writer.writerow([student.rollno, student.name, student.email, student.get_gender_display(), student.cgpa_ug,student.cgpa_pg, student.university_ug,student.university_pg, student.percentage_tenth, student.percentage_twelfth, student.get_backlogs_display(),student.phone])
			return response
		else:
			return render(request, 'jobport/badboy.html')
	else:
		return render(request, 'jobport/needlogin.html')

def feedback(request):
	if (request.method == 'POST'):
		form = FeedbackForm(request.POST)
		if form.is_valid():
			form.save()
			type = form.cleaned_data['type']
			type = dict(form.fields['type'].choices)[type]
			mail.send(
					['jobportiiitd@gmail.com'],
					'jobportiiitd@gmail.com',
					subject=('[' + type + '] '+ form.cleaned_data['title']),
					message=('A new feedback was posted on JobPort  -> ' + '\n\n' + form.cleaned_data['body']),
					# headers={'Reply-to': form.cleaned_data['email']},
					priority="high"
				)
			messages.success(request, 'Thanks for filling your precious feedback! :) ')
			return HttpResponseRedirect('/')
		else:
			context={'form': form}
			return render(request,'jobport/admin_jobselections.html', context)
	else:
		form = FeedbackForm()
		context = { 'form' : form }
		if request.user.is_authenticated():
			 if is_admin(request.user):
				 return render(request,'jobport/feedback_admin.html', context)
			 else:
				 return render(request,'jobport/feedback_student.html', context)
		else:
			return render(request,'jobport/feedback_loggedout.html', context)

# @@login_required
def fileview(request, filename):
	# current_url = request.get_full_path()
	# geturl = urlparse(current_url)
	# name = request.user.username.split('@')[0].lower()
	# if name != geturl.path.split('/')[-1].split('.')[0].split('_')[0].lower():
	   # return render(request, "jobport/notallowed.html")
	# else:
	# filename = name + "_resume." + 'pdf'
   # hash_object = hashlib.sha512(filename)
   # hex_digest = hash_object.hexdigsest()
	# print filename
	# response = HttpResponse(pdf.read(), mimetype='application/pdf')
	# if request.user.is_authenticated():
	response = HttpResponse()
	response['Content-Type'] = 'application/pdf'
	response['Content-Disposition'] = 'attachment; filename=%s'%os.path.join(settings.MEDIA_ROOT, "resume" + "filename")
		# response['X-Accel-Redirect'] = "/protected/%s"%request.user.resume

	return response

# def blank(request):
	# return render(request, 'jobport/badboy.html')

def batchcreate(request):
	if request.user.is_authenticated():
		if is_admin(request.user):
			if request.method == 'POST':
				form = BatchForm(request.POST)
				if form.is_valid():
					tosavebatch = form.save(commit=False)
					tosavebatch.createdon=timezone.now()
					tosavebatch.save()
				else:
					messages.error(request, "There was error in the data, please try again!")
				return HttpResponseRedirect(reverse('viewbatches'))
			else:
				form = BatchForm()
				c = { 'form' : form }
				return render(request,'jobport/openbatch.html', c)
		else:
			return render(request, 'jobport/notallowed.html')
	else:
		return render(request, 'jobport/needlogin.html')

def batchdestroy(request,batchid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			Batch.objects.get(pk=batchid).delete()
			return HttpResponseRedirect('/')
	else:
		return render(request, 'jobport/needlogin.html')

def batchedit(request,batchid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			if request.method == 'POST':
				form = BatchForm(request.POST, instance=Batch.objects.get(pk=batchid))
				if form.is_valid():
					form.save()
					messages.success(request, 'Batch was updated!')
					return HttpResponseRedirect('/batch/'+str(batchid)+'/')
				else:
					context={'form': form}
					return render(request,'jobport/admin_editbatch.html', context)
			else:
				form = BatchForm(instance=Batch.objects.get(pk=batchid))
				c = { 'form' : form }
				return render(request,'jobport/admin_editbatch.html', c)
	else:
		return render(request, 'jobport/needlogin.html')

def viewbatches(request):
  if request.user.is_authenticated():
	if is_admin(request.user):
		batches = Batch.objects.all()
		return render(request,'jobport/batches.html', {'batch':batches})
	else:
	  return render(request,'jobport/badboy.html')
  else:
	return render(request, 'jobport/needlogin.html')

def batchpage(request, batchid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			context = {'user': request.user, 'student': Batch.objects.get(pk=batchid).studentsinbatch.all(),
				'batch': Batch.objects.get(pk=batchid)}

			return render(request, 'jobport/admin_batch.html', context)
	return render(request, 'jobport/welcome.html')

def is_batch(candidate,batch):
  eligibility={}
  eligibility['value']=True
  if(batch!= candidate.batch):
	 eligibilty['value']=False
  return eligibility

def getbatchresumes(request,batchid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			# Files (local path) to put in the .zip
			filenames=[]
			checklist=Batch.objects.get(pk=batchid).studentsinbatch.all()
			zip_subdir = Batch.objects.get(pk=batchid).text + "_resumes"
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
			resp = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
			# ..and correct content-disposition
			resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename

			return resp
		else:
			return render(request, 'jobport/badboy.html')
	else:
		return render(request, 'jobport/needlogin.html')


def uploadstudentsinbatch(request,batchid):
	if request.user.is_authenticated():
		if is_admin(request.user):
			if request.method == 'POST':
				file = request.FILES['students']
				notfound=[]
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
				return render(request,'jobport/admin_addstudentstobatch.html',context)
			else:
				return render(request,'jobport/admin_addstudentstobatch.html')
		else:
			return render(request, 'jobport/needlogin.html') #403 Error
	return render(request, 'jobport/needlogin.html') #403 Error

def special_match(strg,search=re.compile(r'[^A-Za-z0-9., -]').search):
	return not bool(search(strg))

def contact_match(strg,search= re.compile(r'[0-9]\n').search):
	return not bool(search(strg))

def onlyspecchar_match(strg,search= re.compile(r'^[., -]').search):
	return not bool(search(strg))

def onlynumbers(strg,search= re.compile(r'^[0-9]').search):
	return bool(search(strg))
