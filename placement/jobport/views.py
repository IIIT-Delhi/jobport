# //=======================================================================
# // Copyright JobPort, IIIT Delhi 2015.
# // Distributed under the MIT License.
# // (See accompanying file LICENSE or copy at
# //  http://opensource.org/licenses/MIT)
# //=======================================================================


# __author__ = 'naman'

import StringIO
import csv
import os
import zipfile
from multiprocessing import Process

from django.contrib import messages
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from jobport import forms
from jobport.helpers import is_admin, is_member, is_eligible, checkdeadline
from jobport.models import Job, Student, Batch
from placement import settings


def _send_mail(subject, text_content, host_user, recipient_list):
    """Sending mail to the recipient_list. Written by http://darkryder.me/."""
    msg = EmailMultiAlternatives(
        subject, text_content, host_user, recipient_list)
    a = msg.send()
    print "Mail sent"


def send_mail(subject, text_content, recipient_list):
    """Start the process for sending mails. Written by http://darkryder.me/."""
    p = Process(target=_send_mail, args=(subject, text_content,
                                         settings.EMAIL_HOST_USER, recipient_list))
    p.start()


def server_error(request):
    """Error page for 500."""
    response = render(request, "jobport/500.html")
    response.status_code = 500
    return response


def not_found(request):
    """Error page for 404."""
    response = render(request, "jobport/404.html")
    response.status_code = 404
    return response


# def test(request):
# 	return render(request, 'jobport/material.min.js.map')

def home(request):
    """Landing home page after login of student or admin."""
    if request.user.is_authenticated():
        context = {'user': request.user,
                   'jobs': Job.objects.all().order_by('-deadline')}
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
    """Apply for a job, if deadline permits."""
    if (timezone.now() < Job.objects.get(pk=jobid).deadline):
        if (is_eligible(request.user.student, Job.objects.get(pk=jobid))['value']):
            request.user.student.companyapplications.add(
                Job.objects.get(pk=jobid))
            messages.success(request, 'Thanks for applying!')
            return HttpResponseRedirect('/')
        else:
            return render(request, 'jobport/badboy.html')
    else:
        return render(request, 'jobport/latedeadline.html')


@login_required()
def jobwithdraw(request, jobid):
    """Withdraw from the job, if deadline permits."""
    if (timezone.now() < Job.objects.get(pk=jobid).deadline):
        request.user.student.companyapplications.remove(
            Job.objects.get(pk=jobid))
        messages.success(request, 'You have withdrawn!')
        return HttpResponseRedirect('/')
    else:
        return render(request, 'jobport/latedeadline.html')


@login_required()
def myapplications(request):
    """Enumerate student's applications for a job."""
    studentgroup = Group.objects.get(name='student')
    if (not is_member(request.user, studentgroup)):
        return HttpResponseRedirect('/newuser')
    context = {'user': request.user,
               'jobs': request.user.student.companyapplications.all()}
    return render(request, 'jobport/applications_student.html', context)


@login_required()
def jobpage(request, jobid):
    """Loads the page for a particular Job."""
    if is_admin(request.user):
        context = {'user': request.user, 'job': Job.objects.get(pk=jobid)}
        return render(request, 'jobport/admin_job.html', context)
    else:
        hasapplied = request.user.student.companyapplications.filter(
            pk__contains=jobid).count()
        iseligible = is_eligible(request.user.student,
                                 Job.objects.get(pk=jobid))
        deadlinepassed = checkdeadline(Job.objects.get(pk=jobid))
        context = {'user': request.user, 'job': Job.objects.get(pk=jobid), 'deadlinepassed': deadlinepassed,
                   'hasapplied': hasapplied, 'iseligible': iseligible['value'],
                   'iseligiblereasons': iseligible['reasons']}
        return render(request, 'jobport/job_student.html', context)


@login_required()
def admineditstudent(request, studentid):
    """Allows admin to change the student details."""
    if is_admin(request.user):
        if request.method == 'POST':
            form = forms.AdminStudentForm(
                request.POST, request.FILES, instance=Student.objects.get(pk=studentid))
            if form.is_valid():
                usr = form.save(commit=False)
                if (request.FILES.__len__() == 0):
                    usr.resume = Student.objects.get(pk=studentid).resume
                else:
                    my_student = Student.objects.get(pk=studentid)
                    usr.resume.name = my_student.batch.title + '_' + \
                        my_student.user.username.split('@')[0] + ".pdf"
                    if "@iiitd.ac.in" in request.user.username:
                        usr.email = Student.objects.get(
                            pk=studentid).user.username
                    else:
                        usr.email = Student.objects.get(
                            pk=studentid).user.username + "@iiitd.ac.in"
                usr.save()
                form.save_m2m()
                messages.success(request, 'Your form was saved')
                return HttpResponseRedirect('/batches')
            else:
                messages.error(request, 'Error in form!')
                context = {'form': form}
                return render(request, 'jobport/admin_editstudent.html', context)
        elif request.method == 'GET':
            studentform = forms.AdminStudentForm(
                instance=Student.objects.get(pk=studentid))
            context = {'user': request.user,
                       'form': studentform, 'layout': 'horizontal'}
            return render(request, 'jobport/admin_editstudent.html', context)
        return HttpResponseRedirect('/')
    else:
        return render(request, 'jobport/badboy.html')


@login_required()
def getresumes(request, jobid):
    """Return resumes for students according to the incoming request."""
    if is_admin(request.user):
        filenames = []
        if (request.GET.get('req') == 'selected'):
            checklist = Job.objects.get(pk=jobid).selectedcandidates.all()
            zip_subdir = Job.objects.get(pk=jobid).company_name + "_" + Job.objects.get(
                pk=jobid).profile + "_Selected_Resumes"
        else:
            checklist = Job.objects.get(
                pk=jobid).applicants.all()  # AllApplicants
            zip_subdir = Job.objects.get(pk=jobid).company_name + "_" + Job.objects.get(
                pk=jobid).profile + "_Applicant_Resumes"
        for student in checklist:
            if (request.GET.get('qual') == 'G' and student.batch.pg_or_not == 'G'):
                continue
            if (request.GET.get('qual') == 'P' and student.batch.pg_or_not == 'P'):
                continue
            filenames.append(student.resume.path)
        zip_filename = "%s.zip" % zip_subdir
        s = StringIO.StringIO()
        zf = zipfile.ZipFile(s, "w")

        for fpath in filenames:
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)
            zf.write(fpath, zip_path)
        zf.close()
        resp = HttpResponse(
            s.getvalue(), mimetype="application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp
    else:
        return render(request, 'jobport/badboy.html')


@login_required()
def profile(request):
    """Allows editing student profile by themselves."""
    studentgroup = Group.objects.get(name='student')
    if (not is_member(request.user, studentgroup)):
        return HttpResponseRedirect('/newuser')
    if request.method == 'POST':
        form = forms.StudentForm(
            request.POST, request.FILES, instance=request.user.student)
        if form.is_valid():
            usr = form.save(commit=False)
            usr.user = request.user
            if "@iiitd.ac.in" in request.user.username:
                usr.email = request.user.username
            else:
                usr.email = usr.email = request.user.username + "@iiitd.ac.in"
            if (request.FILES.__len__() == 0):
                usr.resume = request.user.student.resume
            else:
                usr.resume.name = usr.batch.title + '_' + \
                    request.user.username.split('@')[0] + ".pdf"
            usr.save()
            messages.success(request, 'Your details were saved.')
            return HttpResponseRedirect('/')
        else:
            context = {'form': form, 'student': request.user.student}
            return render(request, 'jobport/student_profile.html', context)
    elif request.method == 'GET':
        studentform = forms.StudentForm(instance=request.user.student)
        context = {'user': request.user, 'form': studentform, 'layout': 'horizontal',
                   'student': request.user.student}
        return render(request, 'jobport/student_profile.html', context)


def newuser(request):
    """New User Sign Up form."""
    studentgroup, created = Group.objects.get_or_create(
        name='student')  # Creating user group
    if request.user.is_authenticated():
        if is_member(request.user, studentgroup):
            HttpResponseRedirect('/')
        if request.method == 'POST':
            form = forms.NewStudentForm(request.POST, request.FILES)
            # print form.cleaned_data
            if form.is_valid():
                usr = form.save(commit=False)
                usr.user = request.user
                usr.email = request.user.username + "@iiitd.ac.in"
                usr.name = request.user.first_name + " " + request.user.last_name
                usr.resume.name = request.user.username.split('@')[0] + ".pdf"
                usr.save()
                studentgroup.user_set.add(request.user)
                usr.batch = form.cleaned_data['batch']

                messages.success(
                    request, 'Your details were saved. Welcome to JobPort.')
                return HttpResponseRedirect('/')
            else:
                context = {'form': form, 'resumer_url': settings.RESUME_URL}
                return render(request, 'jobport/newstudent.html', context)
        elif request.method == 'GET':
            studentform = forms.NewStudentForm()
            context = {'user': request.user, 'form': studentform, 'layout': 'horizontal',
                       'resumer_url': settings.RESUME_URL}
            return render(request, 'jobport/newstudent.html', context)
    return HttpResponseRedirect('/')


def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect('/')


def needlogin(request):
    """need login"""
    return render(request, 'jobport/needlogin.html')


@login_required()
def openjob(request):
    """Open a new Job from admin side."""
    if is_admin(request.user):
        if request.method == 'POST':
            form = forms.JobForm(request.POST)
            if form.is_valid():
                tosavejob = form.save(commit=False)
                tosavejob.createdon = timezone.now()
                tosavejob.save()
                for x in form.cleaned_data['batch']:
                    tosavejob.batch.add(x)
                tosavejob.save()
                recipients = []
                for student in Student.objects.all():
                    if student.status == 'D' or student.status == 'NI':
                        continue
                recipients.append(student.email)

                settings.EMAIL_HOST_USER += 'jobportiiitd@gmail.com'
                send_mail(
                    'New Job in JobPort!',
                    'Hey!\n\nA new job for ' + tosavejob.profile + ', ' + tosavejob.company_name +
                    ' was added on JobPort. \n Please login at jobport.iiitd.edu.in:8081',
                    recipients
                )
                settings.EMAIL_HOST_USER += ''
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
    """Delete a Job from admin side."""
    if is_admin(request.user):
        Job.objects.get(pk=jobid).delete()
        return HttpResponseRedirect('/')


@login_required()
def jobedit(request, jobid):
    """Edit Job details from admin side."""
    if is_admin(request.user):
        if request.method == 'POST':
            form = forms.JobForm(request.POST, request.FILES,
                                 instance=Job.objects.get(pk=jobid))
            if form.is_valid():
                form.save()  # This does the trick!
                messages.success(request, 'Job was saved')
                return HttpResponseRedirect('/job/' + str(jobid) + '/')
            else:
                context = {'form': form}
                return render(request, 'jobport/admin_editjob.html', context)
        else:
            form = forms.JobForm(instance=Job.objects.get(pk=jobid))
            c = {'form': form}
            return render(request, 'jobport/admin_editjob.html', c)


@login_required()
def jobapplicants(request, jobid):
    """See the applicants for a particular Job."""
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
    """Send mail to selected students for a particular Job."""
    if is_admin(request.user):
        candemail = []
        thejob = Job.objects.get(pk=jobid)
        for candidate in thejob.selectedcandidates.all():
            candidate.status = 'P'
            candidate.save()
            candemail = candemail + [str(candidate.email)]
        settings.EMAIL_HOST_USER += 'jobportiiitd@gmail.com'
        send_mail(
            'Congratulations! You\'ve been placed! :D',
            "Hey!\n\nCongratulations! You have been placed as " +
            thejob.profile + ' at ' + thejob.company_name + "!!",
            candemail
        )
        settings.EMAIL_HOST_USER += ''
        messages.success(request, 'Mails Sent!')
    return HttpResponseRedirect('/')


@login_required()
def adminjobselected(request, jobid):
    """Select the final students fot the Job :D"""
    if is_admin(request.user):
        if request.method == 'POST':
            form = forms.AdminSelectedApplicantsForm(
                request.POST, instance=Job.objects.get(pk=jobid))
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
            form = forms.AdminSelectedApplicantsForm(
                instance=Job.objects.get(pk=jobid))
            context = {'selected': Job.objects.get(pk=jobid).selectedcandidates.all(), 'form': form,
                       'job': Job.objects.get(pk=jobid)}
            return render(request, 'jobport/admin_jobselections.html', context)


@login_required()
def uploadcgpa(request):
    """Upload the CGPA CSV for all the students, to update student CGPAs."""
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
                        stud.cgpa_pg = float(row[1])
                    else:
                        stud.cgpa_ug = float(row[1])
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
    """Calculating statistics for the statistics page."""
    if is_admin(request.user):
        numstudentsplaced = 0
        cgpahistdata = []
        uninterested_students = []
        Students = Student.objects.all()
        Jobs = Job.objects.all()
        for student in Students:
            if student.status == 'P':
                numstudentsplaced += 1
            if student.status == 'NI' or student.status == 'D':
                uninterested_students += 1
            # CGPA Hist
            if student.batch.pg_or_not == 'G':
                if student.cgpa_ug != None and student.cgpa_ug != 0:
                    cgpahistdata.append([student.rollno, student.cgpa_ug])
            else:
                if student.cgpa_pg != None and student.cgpa_pg != 0:
                    cgpahistdata.append([student.rollno, student.cgpa_pg])

        jobcgpahistdata = []
        for job in Jobs:
            if job.cgpa_min != None:
                jobcgpahistdata.append(
                    [(job.company_name + ", " + job.profile), job.cgpa_min])

        interested_students = len(Students) - len(uninterested_students)
        placedunplaceddata = [["Placed Students", numstudentsplaced],
                              ["Unplaced Students", interested_students - numstudentsplaced]]

        context = {'cgpahistdata': cgpahistdata, 'jobcgpahistdata': jobcgpahistdata,
                   'placedunplaceddata': placedunplaceddata, 'numstudents': interested_students,
                   'numstudentsplaced': numstudentsplaced, 'numjobs': len(Jobs)}
        return render(request, 'jobport/admin_stats.html', context)


@login_required()
def blockedUnplacedlist(request):
    """Retrieves the list for Unplaced or Blocked/Debarred students."""
    if is_admin(request.user):
        response = HttpResponse(content_type='text/csv')
        if (request.GET.get('req') == 'debarred'):
            students = Student.objects.filter(status='D')
            response[
                'Content-Disposition'] = str('attachment; filename="' + 'BlockedStudents_list.csv"')
        elif (request.GET.get('req') == 'unplaced'):
            students = Student.objects.filter(status='N')
            response[
                'Content-Disposition'] = str('attachment; filename="' + 'UnplacedStudents_list.csv"')
        elif (request.GET.get('req') == 'placed'):
            students = Student.objects.filter(status='P')
            response[
                'Content-Disposition'] = str('attachment; filename="' + 'PlacedStudents_list.csv"')
        elif (request.GET.get('req') == 'notInterested'):
            students = Student.objects.filter(status='NI')
            response[
                'Content-Disposition'] = str('attachment; filename="' + 'NotInterested_list.csv"')
        elif (request.GET.get('req') == 'all'):
            students = Student.objects.all()
            response[
                'Content-Disposition'] = str('attachment; filename="' + 'All_list.csv"')
        writer = csv.writer(response)
        writer.writerow(
            ["RollNo", "Name", "Email", "Gender", "Batch", "UnderGrad CGPA", "PostGrad CGPA{for PG}",
             "Graduating University",
             "PostGraduating University", "10th Marks", "12th Marks", "Backlogs", "Contact No."])
        for student in students:
            writer.writerow(
                [student.rollno, student.name, student.email, student.get_gender_display(), student.batch,
                 student.cgpa_ug,
                 student.cgpa_pg, student.university_ug, student.university_pg, student.percentage_tenth,
                 student.percentage_twelfth, student.get_backlogs_display(), student.phone])
        return response
    else:
        return render(request, 'jobport/badboy.html')


@login_required()
def getjobcsv(request, jobid):
    """Gets different (Eligible, Applied, Selected) CSVs for a particular Jobs."""
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

        response[
            'Content-Disposition'] = str('attachment; filename="' + name + '"')
        writer = csv.writer(response)
        writer.writerow([Job.objects.get(pk=jobid).company_name,
                         Job.objects.get(pk=jobid).profile])
        writer.writerow(
            ["RollNo", "Name", "Email", "Gender", "CGPA", "Batch", "Graduating University", "10th Marks",
             "12th Marks", "Backlogs", "Conact No.", "UnderGrad CGPA{PG}"]
        )
        for student in studlist:
            if (student.batch.pg_or_not == 'G' and request.GET.get('qualification') != 'pg'):
                writer.writerow(
                    [student.rollno, student.name, student.email, student.get_gender_display(), student.cgpa_ug,
                     student.batch,
                     student.university_ug, student.percentage_tenth, student.percentage_twelfth,
                     student.get_backlogs_display(), student.phone]
                )
            if (student.batch.pg_or_not == 'P' and request.GET.get('qualification') != 'ug'):
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
    """Retrieves the list for students in a Batch."""
    if is_admin(request.user):
        response = HttpResponse(content_type='text/csv')
        studlist = Batch.objects.get(pk=batchid).studentsinbatch.all()
        name = Batch.objects.get(pk=batchid).title
        response[
            'Content-Disposition'] = str('attachment; filename="' + name + '_list.csv"')
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
    """FeedbackForm"""
    if (request.method == 'POST'):
        form = forms.FeedbackForm(request.POST)
        # pdb.set_trace()
        if form.is_valid():
            form.save()
            type = form.cleaned_data['type']
            type = dict(form.fields['type'].choices)[type]
            settings.EMAIL_HOST_USER += 'Tester@jobport.iiitd.edu.in'
            send_mail(
                '[' + type + '] ' + form.cleaned_data['title'],
                'A new feedback was posted on JobPort' + '\n\n' +
                form.cleaned_data['body'], ['jobportiiitd@gmail.com']
            )
            settings.EMAIL_HOST_USER += ''
            messages.success(
                request, 'Thanks for filling your precious feedback! :) ')
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
    """Protect the resume location, by adding headers, using nginx."""
    response = HttpResponse()
    response['Content-Type'] = 'application/pdf'
    response['X-Accel-Redirect'] = "/protected/%s" % filename
    return response


@login_required()
def docfileview(request, filename):
    """Protect the job file location, by adding headers, using nginx."""
    response = HttpResponse()
    response['Content-Type'] = 'application/pdf'
    response['X-Accel-Redirect'] = "/jobfiles/%s" % filename
    return response


@login_required()
def batchcreate(request):
    """Create a Batch."""
    if is_admin(request.user):
        if request.method == 'POST':
            form = forms.BatchForm(request.POST)
            if form.is_valid():
                tosavebatch = form.save(commit=False)
                tosavebatch.createdon = timezone.now()
                tosavebatch.save()
            else:
                messages.error(
                    request, "There was error in the data, please try again!")
            return HttpResponseRedirect(reverse('viewbatches'))
        else:
            form = forms.BatchForm()
            c = {'form': form}
            return render(request, 'jobport/openbatch.html', c)
    else:
        return render(request, 'jobport/notallowed.html')


@login_required()
def batchdestroy(request, batchid):
    """Delete a Batch."""
    if is_admin(request.user):
        Batch.objects.get(pk=batchid).delete()
        return HttpResponseRedirect('/')


@login_required()
def batchedit(request, batchid):
    """Edit details of a Batch."""
    if is_admin(request.user):
        if request.method == 'POST':
            form = forms.BatchForm(
                request.POST, instance=Batch.objects.get(pk=batchid))
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
    """View the list of all Batches."""
    if is_admin(request.user):
        batches = Batch.objects.all()
        return render(request, 'jobport/batches.html', {'batch': batches})
    else:
        return render(request, 'jobport/badboy.html')


@login_required()
def batchpage(request, batchid):
    """Batch Page."""
    if is_admin(request.user):
        context = {'user': request.user, 'student': Batch.objects.get(pk=batchid).studentsinbatch.all(),
                   'batch': Batch.objects.get(pk=batchid)}

        return render(request, 'jobport/admin_batch.html', context)
    return render(request, 'jobport/welcome.html')


@login_required()
def getbatchresumes(request, batchid):
    """Get resumes for a Batch."""
    if is_admin(request.user):
        filenames = []
        checklist = Batch.objects.get(pk=batchid).studentsinbatch.all()
        zip_subdir = Batch.objects.get(pk=batchid).title + "_resumes"
        for student in checklist:
            filenames.append(student.resume.path)
        zip_filename = "%s.zip" % zip_subdir
        s = StringIO.StringIO()
        zf = zipfile.ZipFile(s, "w")
        for fpath in filenames:
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)
            zf.write(fpath, zip_path)
        zf.close()
        resp = HttpResponse(
            s.getvalue(), mimetype="application/x-zip-compressed")
        resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
        return resp
    else:
        return render(request, 'jobport/badboy.html')


@login_required()
def uploadstudentsinbatch(request, batchid):
    """Add students in a batch, by uploading a CSV. Will not be required IMHO."""
    if is_admin(request.user):
        if request.method == 'POST':
            file = request.FILES['students']
            notfound = []
            for row in csv.reader(file.read().splitlines()):
                try:
                    stud = Student.objects.get(pk=row[0])
                    batch = Batch.get.objects(pk=batchid)
                    stud.batch = batch
                    stud.save()
                except ObjectDoesNotExist:
                    notfound.append(row[0])
            context = {'notfound': notfound}
            messages.success(
                request, 'Students succesfully added to the Batch!')
            return render(request, 'jobport/admin_addstudentstobatch.html', context)
        else:
            return render(request, 'jobport/admin_addstudentstobatch.html')
    else:
        return render(request, 'jobport/notallowed.html')  # 403 Error


@login_required()
def search(request):
    """Search, something. anything."""
    if is_admin(request.user):
        form = forms.RootSearchForm(request.GET)
        query = request.GET.get('q')
        if query == '':
            messages.error(request, 'Please enter a Query!')
            return render(request, 'jobport/notallowed.html')
        else:
            return render(request, 'jobport/result.html',
                          {'search_query': query, 'results': form.search()})
    else:
        return render(request, 'jobport/notallowed.html')  # 403 Error
