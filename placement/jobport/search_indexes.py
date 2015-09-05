# //=======================================================================
# // Copyright JobPort, IIIT Delhi 2015.
# // Distributed under the MIT License.
# // (See accompanying file LICENSE or copy at
# //  http://opensource.org/licenses/MIT)
# //=======================================================================




# __author__ = 'naman'

from haystack import indexes
from django.utils import timezone
from .models import Batch, Job, Student


class BatchIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    pg_or_not = indexes.CharField(model_attr='pg_or_not')

    createdon = indexes.DateTimeField(model_attr='createdon')

    def get_model(self):
        return Batch

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(createdon__lte=timezone.now())


class JobIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    company_name = indexes.CharField(model_attr='company_name')
    profile = indexes.CharField(model_attr='profile')
    createdon = indexes.DateTimeField(model_attr='createdon')

    def get_model(self):
        return Job


def index_queryset(self, using=None):
    """Used when the entire index for model is updated."""
    return self.get_model().objects.filter(createdon__lte=timezone.now())


class StudentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.CharField(model_attr='name')
    rollno = indexes.CharField(model_attr='rollno')
    phone = indexes.CharField(model_attr='phone')
    # email = indexes.EmailField(model_attr='email')
    home_state = indexes.CharField(model_attr='home_state')
    home_city = indexes.CharField(model_attr='home_city')
    institution_ug = indexes.CharField(model_attr='institution_ug')
    institution_pg = indexes.CharField(model_attr='institution_pg')
    university_ug = indexes.CharField(model_attr='university_ug')
    university_pg = indexes.CharField(model_attr='university_pg')

    createdon = indexes.DateTimeField(model_attr='createdon')

    def get_model(self):
        return Student

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(createdon__lte=timezone.now())
