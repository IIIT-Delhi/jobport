import re

from django import forms
from bootstrap3_datetime.widgets import DateTimePicker
from django.template.defaultfilters import filesizeformat
from django.db.models.fields.files import FieldFile
from django.forms import RadioSelect
from django.utils import timezone
import haystack.forms

from .models import Job, Student, Feedback, Batch


EXTENSIONS = ['pdf']
MAX_UPLOAD_SIZE = "5242880"


class JobForm(forms.ModelForm):
	class Meta:
		model = Job
		exclude = ['createdon']
		widgets = {'deadline': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm", "pickTime": True}),
				   'dateofvisit': DateTimePicker(options={"format": "YYYY-MM-DD HH:mm", "pickTime": True}),
				   'batch': forms.CheckboxSelectMultiple}

	def clean_jobfile(self):
		jobfile = self.cleaned_data['jobfile']
		if type(jobfile) == FieldFile:
			return jobfile
		return jobfile

	def clean_percentage_tenth(self):
		percent10 = self.cleaned_data['percentage_tenth']
		if (percent10 > 100):
			raise forms.ValidationError("10th Percentage cannot be more than 100%!")
		if (percent10 < 0):
			raise forms.ValidationError("10th Percentage cannot be less than 0!")
		return percent10

	def clean_percentage_twelfth(self):
		percent12 = self.cleaned_data['percentage_twelfth']
		if (percent12 > 100):
			raise forms.ValidationError("12th Percentage cannot be more than 100%!")
		if (percent12 < 0):
			raise forms.ValidationError("12th Percentage cannot be less than 0!")
		return percent12

	def clean_dateofvisit(self):
		DateOfVisit = self.cleaned_data['dateofvisit']
		if (DateOfVisit < timezone.now()):
			raise forms.ValidationError("Date of Visit cannot be in the Past.")
		return DateOfVisit

	def clean_deadline(self):
		deadline = self.cleaned_data['deadline']
		if (deadline < timezone.now()):
			raise forms.ValidationError("Deadline cannot be in the Past.")
		return deadline


class AdminSelectedApplicantsForm(forms.ModelForm):
	class Meta:
		model = Job
		fields = ['selected']

	# widgets = {'CB':forms.CheckBoxSelectMultiple}

	# Representing the many to many related field in Job
	selected = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple, queryset=Student.objects.all(),
											  required=False)

	# Overriding __init__ here allows us to provide initial
	# data for 'selected' field
	def __init__(self, *args, **kwargs):
		# Only in case we build the form from an instance
		# (otherwise, 'selected' list should be empty)
		forms.ModelForm.__init__(self, *args, **kwargs)
		if 'instance' in kwargs:
			self.fields['selected'].queryset = kwargs['instance'].applicants.all()
			# We get the 'initial' keyword argument or initialize it
			# as a dict if it didn't exist.
			initial = kwargs.setdefault('initial', {})
			# The widget for a ModelMultipleChoiceField expects
			# a list of primary key for the selected data.
			# for t in kwargs['instance'].selectedcandidates.all():
			# print t
			initial['selected'] = [t.pk for t in kwargs['instance'].selectedcandidates.all()]  # applicants.all()]

	# Overriding save allows us to process the value of 'selected' field
	def save(self, commit=True):
		# Get the unsaved Job instance
		instance = forms.ModelForm.save(self, False)

		# Prepare a 'save_m2m' method for the form,
		old_save_m2m = self.save_m2m

		def save_m2m():
			old_save_m2m()
			# This is where we actually link the selected with job
			instance.selectedcandidates.clear()
			for student in self.cleaned_data['selected']:
				instance.selectedcandidates.add(student)

		self.save_m2m = save_m2m

		# Do we need to save all changes now?
		if commit:
			instance.save()
			self.save_m2m()

		return instance


class StudentForm(forms.ModelForm):
	class Meta:
		model = Student
		fields = ['resume', 'phone', 'email_personal', 'percentage_tenth', 'percentage_twelfth', 'max_backlogs']
		widgets = {'dob': DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False})}

	def clean_resume(self):
		resume = self.cleaned_data['resume']
		resumeext = resume.name.split('.')[-1]
		if type(resume) == FieldFile:
			return resume
		if resumeext in EXTENSIONS:
			if resume._size > MAX_UPLOAD_SIZE:
				raise forms.ValidationError('Please keep filesize under %s. Current filesize %s') % (
					filesizeformat(MAX_UPLOAD_SIZE), filesizeformat(resume._size))
		else:
			raise forms.ValidationError('File type is not supported')
		return resume

	def clean_percentage_tenth(self):
		percent10 = self.cleaned_data['percentage_tenth']
		if (percent10 > 100):
			raise forms.ValidationError("10th Percentage cannot be more than 100%!")
		if (percent10 < 0):
			raise forms.ValidationError("10th Percentage cannot be less than 0!")
		return percent10

	def clean_percentage_twelfth(self):
		percent12 = self.cleaned_data['percentage_twelfth']
		if (percent12 > 100):
			raise forms.ValidationError("12th Percentage cannot be more than 100%!")
		if (percent12 < 0):
			raise forms.ValidationError("12th Percentage cannot be less than 0!")
		return percent12

	def clean_phone(self):
		phoneno = self.cleaned_data['phone']
		if (not phoneno.isdigit()):
			raise forms.ValidationError("Phone number must contain only numbers!")
		return phoneno

	def clean_dob(self):
		DateOB = self.cleaned_data['dob']
		if (DateOB > timezone.now()):
			raise forms.ValidationError("Are you from the Future?")
		return DateOB


class NewStudentForm(forms.ModelForm):
	class Meta:
		model = Student
		exclude = ['user', 'email', 'companyapplications', 'status', 'placedat', 'cgpa_ug', 'cgpa_pg', 'name',
				   'createdon']
		widgets = {'dob': DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False})}

	def clean_university_ug(self):
		cleaned_data = self.cleaned_data
		cleaned_data['university_ug'] = 'IIIT Delhi'
		return cleaned_data['university_ug']

	def clean_university_pg(self):
		cleaned_data = self.cleaned_data
		cleaned_data['university_pg'] = 'IIIT Delhi'
		return cleaned_data['university_pg']

	def clean_rollno(self):
		rollno = self.cleaned_data['rollno']
		rollno = rollno.upper()
		if (not rollno.isalnum()):
			raise forms.ValidationError("Roll number should not contain any special characters.")
		return rollno

	def clean_institution(self):
		cleaned_data = self.cleaned_data
		cleaned_data['institution'] = 'IIIT Delhi'
		return cleaned_data['institution']

	def clean_startyear(self):
		cleaned_data = self.cleaned_data
		return cleaned_data['startyear']

	def clean_passingyear(self):
		cleaned_data = self.cleaned_data
		return cleaned_data['passingyear']

	def clean_resume(self):
		resume = self.cleaned_data['resume']
		resumeext = resume.name.split('.')[-1]
		if type(resume) == FieldFile:
			return resume
		if resumeext in EXTENSIONS:
			if resume._size > MAX_UPLOAD_SIZE:
				raise forms.ValidationError('Please keep filesize under %s. Current filesize %s') % (
					filesizeformat(MAX_UPLOAD_SIZE), filesizeformat(resume._size))
		else:
			raise forms.ValidationError('File type is not supported')
		return resume

	def clean_percentage_tenth(self):
		percent10 = self.cleaned_data['percentage_tenth']
		if (percent10 > 100):
			raise forms.ValidationError("10th Percentage cannot be more than 100%!")
		if (percent10 < 0):
			raise forms.ValidationError("10th Percentage cannot be less than 0!")
		return percent10

	def clean_percentage_twelfth(self):
		percent12 = self.cleaned_data['percentage_twelfth']
		if (percent12 > 100):
			raise forms.ValidationError("12th Percentage cannot be more than 100%!")
		if (percent12 < 0):
			raise forms.ValidationError("12th Percentage cannot be less than 0!")
		return percent12

	def clean_passingyear_tenth(self):
		pass10 = self.cleaned_data['passingyear_tenth']
		if (pass10 > 2020 or pass10 < 2000):
			raise forms.ValidationError("Please enter a valid year")
		return pass10

	def clean_passingyear_twelfth(self):
		pass12 = self.cleaned_data['passingyear_twelfth']
		if (pass12 > 2020 or pass12 < 2000):
			raise forms.ValidationError("Please enter a valid year")
		return pass12

	def clean_phone(self):
		phoneno = self.cleaned_data['phone']
		if (not phoneno.isdigit()):
			raise forms.ValidationError("Phone number must contain only numbers!")
		return phoneno

	def clean_dob(self):
		DateOB = self.cleaned_data['dob']
		if (DateOB > timezone.now()):
			raise forms.ValidationError("Are you from the Future?")
		return DateOB


def onlynumbers(strg, search=re.compile(r'^[0-9]').search):
	return bool(search(strg))


class AdminStudentForm(forms.ModelForm):
	class Meta:
		model = Student
		exclude = ['user']
		widgets = {'dob': DateTimePicker(options={"format": "YYYY-MM-DD", "pickTime": False}), 'gender': RadioSelect(),
				   'companyapplications': forms.CheckboxSelectMultiple, 'placedat': forms.CheckboxSelectMultiple}

	"""def clean(self):
		cleaned_data = super(AdminStudentForm, self).clean()
		#raise forms.ValidationError("This error was added to show the non field errors styling.")
		return cleaned_data"""

	def clean_resume(self):
		resume = self.cleaned_data['resume']
		resumeext = resume.name.split('.')[-1]
		if type(resume) == FieldFile:
			return resume
		if resumeext in EXTENSIONS:
			if resume._size > MAX_UPLOAD_SIZE:
				raise forms.ValidationError('Please keep filesize under %s. Current filesize %s') % (
					filesizeformat(MAX_UPLOAD_SIZE), filesizeformat(resume._size))
		else:
			raise forms.ValidationError('File type is not supported')
		return resume

	def clean_cgpa_ug(self):
		cgpa = self.cleaned_data['cgpa_ug']
		if (cgpa > 10):
			raise forms.ValidationError("CGPA cannot be more than 10!")
		return cgpa

	def clean_cgpa_pg(self):
		cgpa = self.cleaned_data['cgpa_pg']
		if (cgpa > 10):
			raise forms.ValidationError("CGPA cannot be more than 10!")
		return cgpa

	def clean_percentage_tenth(self):
		percent10 = self.cleaned_data['percentage_tenth']
		if (percent10 > 100):
			raise forms.ValidationError("10th Percentage cannot be more than 100%!")
		if (percent10 < 0):
			raise forms.ValidationError("10th Percentage cannot be less than 0!")
		return percent10

	def clean_percentage_twelfth(self):
		percent12 = self.cleaned_data['percentage_twelfth']
		if (percent12 > 100):
			raise forms.ValidationError("12th Percentage cannot be more than 100%!")
		if (percent12 < 0):
			raise forms.ValidationError("12th Percentage cannot be less than 0!")
		return percent12

	def clean_passingyear_tenth(self):
		pass10 = self.cleaned_data['passingyear_tenth']
		if (pass10 > 2020 or pass10 < 2000):
			raise forms.ValidationError("Please enter a valid year")
		return pass10

	def clean_passingyear_twelfth(self):
		pass12 = self.cleaned_data['passingyear_twelfth']
		if (pass12 > 2020 or pass12 < 2000):
			raise forms.ValidationError("Please enter a valid year")
		return pass12

	def clean_phone(self):
		phoneno = self.cleaned_data['phone']
		if (not phoneno.isdigit()):
			raise forms.ValidationError("Phone number must contain only numbers!")
		return phoneno


class FeedbackForm(forms.ModelForm):
	class Meta:
		model = Feedback
		widgets = {'type': RadioSelect()}


class BatchForm(forms.ModelForm):
	class Meta:
		model = Batch
		exclude = ['createdon']


class RootSearchForm(haystack.forms.SearchForm):
	def no_query_found(self):
		return self.searchqueryset.all()

	def search(self):
		# First, store the SearchQuerySet received from other processing. (the main work is run internally by Haystack here).
		sqs = super(RootSearchForm, self).search()
		# if something goes wrong
		if not self.is_valid():
			return self.no_query_found()
		# you can then adjust the search results and ask for instance to order the results by title
		# sqs = sqs.order_by(title)
		return sqs
