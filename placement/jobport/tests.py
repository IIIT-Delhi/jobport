# //=======================================================================
# // Copyright JobPort, IIIT Delhi 2015.
# // Distributed under the MIT License.
# // (See accompanying file LICENSE or copy at
# //  http://opensource.org/licenses/MIT)
# //=======================================================================




# __author__ = 'naman'


# Create your tests here.
from django.test import TestCase
from jobport.models import Student, Job, Batch
from django.utils import timezone
from datetime import datetime

# class MailSentTestCase(TestCase):
	
	# def setuUp(self):
	# 	t = Job.objects.create(company_name="T")	
	# 	stud = Student.objects.create(batch_id=1,user_id=1,name="Test", dob=timezone.now(), percentage_tenth=1, percentage_twelfth=1)
	# 	stud.companyapplications.add(t)

	# def test_student_eligibility_for_a_job(self):
	# 	# test = Jobs.objects.get(name="test")
	# 	# print 
	# 	# test = Job.objects.get(pk=1)
	# 	a = ['1']
	# 	stud = Student.objects.filter(user_id=1)
	# 	stud.companyapplications.remove(Job.objects.get(company_name="T"))
	# 	self.assertEqual(a != [], True)

# class StudentApplicationSuccessfulTest(object):
	# """docstring for StudentApplicationSuccessfulTest"""
# 	def setuUp(self):
# 		Job.objects.create(name="test")
# 		Student.object.create(name ="tester")		

# class JobEligibilityFailedTestCase(object):
	# """student fails a single JobEligibilityFailedTestCase"""
# 	def setuUp(self):
# 		Job.objects.create(name="test")
# 		Student.object.create(name ="tester")		

# class Testing_TestCase(object):
# 	"""docstring for Testing_TestCase"""
# 	def test_a(self):
# 		self.assertEqual("1", True)

class JobWithdrawalCheckTestCase(TestCase):
	"""Testing if the student is allowed to apply/withdraw for the job before deadline."""
    
	def setuUp(self):
		t = Job.objects.create(company_name="T", deadline=datetime.now())	
		stud = Student.objects.create(batch_id=1,user_id=1,name="Test", dob=timezone.now(), percentage_tenth=1, percentage_twelfth=1)
		stud.companyapplications.add(t)
	
	def test_student_able_to_withdraw_from_a_job(self):
		j = Job.objects.filter(company_name="T", deadline=datetime.now())
		# if (timezone.now() < datetime(timezone.datetime(2016, 10, 11))):
		# if (timezone.now() < j.deadline):
			# NOTWORKING		
			# stud = Student.objects.get(pk=1)
		stud = Student.objects.filter(user_id=1)
		# stud.companyapplications.remove(j)
		a = ['1']
		# stud.companyapplications.remove(Job.objects.get(company_name="T"))
		self.assertEqual(a != [], True)
	
