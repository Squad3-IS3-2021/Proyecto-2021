from behave import *
from app.application import app

@fixture
def before_all(context):


@given(u'the mock url')
def step_impl(context):
    context.url = "http://localhost:5000"
