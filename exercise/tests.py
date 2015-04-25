# Django
from django.test import TestCase
from django.utils.datastructures import MultiValueDict

# Aalto+
from exercise.exercise_models import *
from exercise.submission_models import *
from userprofile.models import *

# Python
from datetime import datetime, timedelta

class ExerciseTest(TestCase):
    def setUp(self):
        self.user = User(username="testUser", first_name="First", last_name="Last")
        self.user.set_password("testPassword")
        self.user.save()

        self.grader = User(username="grader")
        self.grader.set_password("graderPassword")
        self.grader.save()

        self.teacher = User(username="staff", is_staff=True)
        self.teacher.set_password("staffPassword")
        self.teacher.save()

        self.user2 = User(username="testUser2", first_name="Strange", last_name="Fellow")
        self.user2.set_password("testPassword2")
        self.user2.save()

        self.course = Course.objects.create(
            name="test course",
            code="123456",
            url="Course-Url"
        )
        self.course.teachers.add(self.teacher.get_profile())

        self.today = datetime.now()
        self.yesterday = self.today - timedelta(days=1)
        self.tomorrow = self.today + timedelta(days=1)
        self.two_days_from_now = self.tomorrow + timedelta(days=1)
        self.three_days_from_now = self.two_days_from_now + timedelta(days=1)

        self.course_instance = CourseInstance.objects.create(
            instance_name="Fall 2011 day 1",
            website="http://www.example.com",
            starting_time=self.today,
            ending_time=self.tomorrow,
            course=self.course,
            url="T-00.1000_d1"
        )
        self.course_instance.assistants.add(self.grader.get_profile())

        self.course_module = CourseModule.objects.create(
            name="test module",
            points_to_pass=15,
            course_instance=self.course_instance,
            opening_time=self.today,
            closing_time=self.tomorrow
        )

        self.course_module_with_late_submissions_allowed = CourseModule.objects.create(
            name="test module",
            points_to_pass=50,
            course_instance=self.course_instance,
            opening_time=self.today,
            closing_time=self.tomorrow,
            late_submissions_allowed=True,
            late_submission_deadline=self.two_days_from_now,
            late_submission_penalty=0.2
        )

        self.old_course_module = CourseModule.objects.create(
            name="test module",
            points_to_pass=15,
            course_instance=self.course_instance,
            opening_time=self.yesterday,
            closing_time=self.today
        )

        self.learning_object_category = LearningObjectCategory.objects.create(
            name="test category",
            course_instance=self.course_instance,
            points_to_pass=5
        )

        self.hidden_learning_object_category = LearningObjectCategory.objects.create(
            name="hidden category",
            course_instance=self.course_instance
        )
        self.hidden_learning_object_category.hidden_to.add(self.user.get_profile())

        self.learning_object = LearningObject.objects.create(
            name="test learning object",
            course_module=self.course_module,
            category=self.learning_object_category
        )

        self.broken_learning_object = LearningObject.objects.create(
            name="test learning object",
            course_module=self.course_module_with_late_submissions_allowed,
            category=self.learning_object_category
        )

        self.base_exercise = BaseExercise.objects.create(
            name="test exercise",
            course_module=self.course_module,
            category=self.learning_object_category,
            max_submissions=1
        )

        self.static_exercise = StaticExercise.objects.create(
            name="test exercise 2",
            course_module=self.course_module,
            category=self.learning_object_category,
            max_points=50,
            points_to_pass=50,
            service_url="/testServiceURL",
            exercise_page_content="test_page_content",
            submission_page_content="test_submission_content"
        )

        self.exercise_with_attachment = ExerciseWithAttachment.objects.create(
            name="test exercise 3",
            course_module=self.course_module,
            category=self.learning_object_category,
            max_points=50,
            points_to_pass=50,
            max_submissions=0,
            files_to_submit="test1.txt|test2.txt|img.png",
            instructions="test_instructions"
        )

        self.old_base_exercise = BaseExercise.objects.create(
            name="test exercise",
            course_module=self.old_course_module,
            category=self.learning_object_category,
            max_submissions=1
        )

        self.base_exercise_with_late_submission_allowed = BaseExercise.objects.create(
            name="test exercise with late submissions allowed",
            course_module=self.course_module_with_late_submissions_allowed,
            category=self.learning_object_category
        )

        self.submission = Submission.objects.create(
            exercise=self.base_exercise,
            grader=self.grader.get_profile()
        )
        self.submission.submitters.add(self.user.get_profile())

        self.submission_with_two_submitters = Submission.objects.create(
            exercise=self.base_exercise,
            grader=self.grader.get_profile()
        )
        self.submission_with_two_submitters.submitters.add(self.user.get_profile())
        self.submission_with_two_submitters.submitters.add(self.user2.get_profile())

        self.late_submission = Submission.objects.create(
            exercise=self.base_exercise,
            grader=self.grader.get_profile()
        )
        self.late_submission.submission_time=self.two_days_from_now
        self.late_submission.submitters.add(self.user.get_profile())

        self.submission_when_late_allowed = Submission.objects.create(
            exercise=self.base_exercise_with_late_submission_allowed,
            grader=self.grader.get_profile()
        )
        self.submission_when_late_allowed.submitters.add(self.user.get_profile())

        self.late_submission_when_late_allowed = Submission.objects.create(
            exercise=self.base_exercise_with_late_submission_allowed,
            grader=self.grader.get_profile()
        )
        self.late_submission_when_late_allowed.submission_time=self.two_days_from_now
        self.late_submission_when_late_allowed.submitters.add(self.user.get_profile())

        self.late_late_submission_when_late_allowed = Submission.objects.create(
            exercise=self.base_exercise_with_late_submission_allowed,
            grader=self.grader.get_profile()
        )
        self.late_late_submission_when_late_allowed.submission_time=self.three_days_from_now
        self.late_late_submission_when_late_allowed.submitters.add(self.user.get_profile())

        self.course_hook = CourseHook.objects.create(
            hook_url="test_hook_url",
            course_instance=self.course_instance
        )

        self.deadline_rule_deviation = DeadlineRuleDeviation.objects.create(
            exercise=self.exercise_with_attachment,
            submitter=self.user.get_profile(),
            extra_minutes=1440  # One day
        )

        self.submitted_file1 = SubmittedFile.objects.create(
            submission=self.submission,
            param_name="testParam"
        )

        self.submitted_file2 = SubmittedFile.objects.create(
            submission=self.submission_with_two_submitters,
            param_name="testParam2"
        )

    def test_course_module_exercises_list(self):
        exercises = self.course_module.get_exercises()
        exercises_with_late_submission_allowed = self.course_module_with_late_submissions_allowed.get_exercises()
        self.assertEquals(3, len(exercises))
        self.assertEquals("test exercise", exercises[0].name)
        self.assertEquals("test exercise 2", exercises[1].name)
        self.assertEquals("test exercise 3", exercises[2].name)
        self.assertEquals(1, len(exercises_with_late_submission_allowed))
        self.assertEquals("test exercise with late submissions allowed", exercises_with_late_submission_allowed[0].name)

    def test_course_module_maximum_points(self):
        self.assertEquals(200, self.course_module.get_maximum_points())
        self.assertEquals(100, self.course_module_with_late_submissions_allowed.get_maximum_points())

    def test_course_module_required_percentage(self):
        self.assertEquals(8, self.course_module.get_required_percentage())
        self.assertEquals(50, self.course_module_with_late_submissions_allowed.get_required_percentage())

    def test_course_module_late_submission_point_worth(self):
        self.assertEquals(100, self.course_module.get_late_submission_point_worth())
        self.assertEquals(80, self.course_module_with_late_submissions_allowed.get_late_submission_point_worth())

    def test_course_module_open(self):
        self.assertFalse(self.course_module.is_open(self.yesterday))
        self.assertTrue(self.course_module.is_open(self.today))
        self.assertTrue(self.course_module.is_open())
        self.assertTrue(self.course_module.is_open(self.tomorrow))
        self.assertFalse(self.course_module.is_open(self.two_days_from_now))

    def test_course_module_expired(self):
        self.assertFalse(self.course_module.is_expired(self.yesterday))
        self.assertFalse(self.course_module.is_expired(self.today))
        self.assertFalse(self.course_module.is_expired())
        self.assertFalse(self.course_module.is_expired(self.tomorrow))
        self.assertTrue(self.course_module.is_expired(self.two_days_from_now))

    def test_course_module_after_open(self):
        self.assertFalse(self.course_module.is_expired(self.yesterday))
        self.assertFalse(self.course_module.is_expired(self.today))
        self.assertFalse(self.course_module.is_expired())
        self.assertFalse(self.course_module.is_expired(self.tomorrow))
        self.assertTrue(self.course_module.is_expired(self.two_days_from_now))

    def test_course_module_breadcrumb(self):
        breadcrumb = self.course_module.get_breadcrumb()
        self.assertEqual(2, len(breadcrumb))
        self.assertEqual(2, len(breadcrumb[0]))
        self.assertEqual(2, len(breadcrumb[1]))
        self.assertEqual("123456 test course", breadcrumb[0][0])
        self.assertEqual("/course/Course-Url/", breadcrumb[0][1])
        self.assertEqual("Fall 2011 day 1", breadcrumb[1][0])
        self.assertEqual("/course/Course-Url/T-00.1000_d1/", breadcrumb[1][1])

    def test_learning_object_category_unicode_string(self):
        self.assertEqual("test category -- 123456: Fall 2011 day 1", str(self.learning_object_category))
        self.assertEqual("hidden category -- 123456: Fall 2011 day 1", str(self.hidden_learning_object_category))

    def test_learning_object_category_exercises(self):
        self.assertEquals(5, len(self.learning_object_category.get_exercises()))
        self.assertEquals(0, len(self.hidden_learning_object_category.get_exercises()))

    def test_learning_object_category_max_points(self):
        self.assertEquals(400, self.learning_object_category.get_maximum_points())
        self.assertEquals(0, self.hidden_learning_object_category.get_maximum_points())

    def test_learning_object_category_required_percentage(self):
        self.assertEquals(1, self.learning_object_category.get_required_percentage())
        self.assertEquals(0, self.hidden_learning_object_category.get_required_percentage())

    def test_learning_object_category_hiding(self):
        self.assertFalse(self.learning_object_category.is_hidden_to(self.user.get_profile()))
        self.assertFalse(self.learning_object_category.is_hidden_to(self.grader.get_profile()))
        self.assertTrue(self.hidden_learning_object_category.is_hidden_to(self.user.get_profile()))
        self.assertFalse(self.hidden_learning_object_category.is_hidden_to(self.grader.get_profile()))

        self.hidden_learning_object_category.set_hidden_to(self.user.get_profile(), False)
        self.hidden_learning_object_category.set_hidden_to(self.grader.get_profile())

        self.assertFalse(self.hidden_learning_object_category.is_hidden_to(self.user.get_profile()))
        self.assertTrue(self.hidden_learning_object_category.is_hidden_to(self.grader.get_profile()))

        self.hidden_learning_object_category.set_hidden_to(self.user.get_profile(), True)
        self.hidden_learning_object_category.set_hidden_to(self.grader.get_profile(), False)

        self.assertTrue(self.hidden_learning_object_category.is_hidden_to(self.user.get_profile()))
        self.assertFalse(self.hidden_learning_object_category.is_hidden_to(self.grader.get_profile()))

    def test_learning_object_clean(self):
        try:
            self.learning_object.clean()
        except ValidationError:
            self.fail()
        self.assertRaises(ValidationError, self.broken_learning_object.clean())

    def test_learning_object_absolute_url(self):
        self.assertEqual("", self.learning_object.get_absolute_url())
        self.assertEqual("", self.broken_learning_object.get_absolute_url())

    def test_learning_object_course_instance(self):
        self.assertEqual(self.course_instance, self.learning_object.get_course_instance())
        self.assertEqual(self.course_instance, self.broken_learning_object.get_course_instance())

    def test_base_exercise_course_instance_max_points(self):
        self.assertEqual(400, self.base_exercise.get_course_instance_max_points(self.base_exercise.course_module.course_instance))

    def test_base_exercise_average_percentage(self):
        self.assertEqual(0, self.base_exercise.get_average_percentage())
        self.base_exercise.summary["average_grade"] = 50
        self.assertEqual(50, self.base_exercise.get_average_percentage())
        self.base_exercise.summary["average_grade"] = 0
        self.assertEqual(0, self.base_exercise.get_average_percentage())

    def test_base_exercise_deadline(self):
        self.assertEqual(self.tomorrow, self.base_exercise.get_deadline())
        self.assertEqual(self.tomorrow, self.base_exercise_with_late_submission_allowed.get_deadline())

    def test_base_exercise_percentage_to_pass(self):
        self.assertEqual(40, self.base_exercise.get_percentage_to_pass())
        self.assertEqual(100, self.static_exercise.get_percentage_to_pass())
        self.assertEqual(100, self.exercise_with_attachment.get_percentage_to_pass())

    def test_base_exercise_have_submissions_left(self):
        self.assertFalse(self.base_exercise.have_submissions_left([self.user]))
        self.assertTrue(self.static_exercise.have_submissions_left([self.user]))
        self.assertTrue(self.exercise_with_attachment.have_submissions_left([self.user]))

    def test_base_exercise_max_submissions(self):
        self.assertEqual(1, self.base_exercise.max_submissions_for(self.user))
        self.assertEqual(10, self.static_exercise.max_submissions_for(self.user))
        self.assertEqual(0, self.exercise_with_attachment.max_submissions_for(self.user))

    def test_base_exercise_submissions_left(self):
        self.assertEqual(-2, self.base_exercise.submissions_left(self.user))
        self.assertEqual(10, self.static_exercise.submissions_left(self.user))
        self.assertEqual(None, self.exercise_with_attachment.submissions_left(self.user))

    def test_base_exercise_is_open(self):
        self.assertTrue(self.base_exercise.is_open())
        self.assertTrue(self.static_exercise.is_open())
        self.assertTrue(self.exercise_with_attachment.is_open())
        self.assertFalse(self.old_base_exercise.is_open())
        self.assertFalse(self.base_exercise.is_open(self.yesterday))
        self.assertFalse(self.static_exercise.is_open(self.yesterday))
        self.assertFalse(self.exercise_with_attachment.is_open(self.yesterday))
        self.assertTrue(self.old_base_exercise.is_open(self.yesterday))
        self.assertTrue(self.base_exercise.is_open(self.tomorrow))
        self.assertTrue(self.static_exercise.is_open(self.tomorrow))
        self.assertTrue(self.exercise_with_attachment.is_open(self.tomorrow))
        self.assertFalse(self.old_base_exercise.is_open(self.tomorrow))

    def test_base_exercise_is_open_for(self):
        self.assertTrue(self.base_exercise.is_open_for([self.user.get_profile()]))
        self.assertTrue(self.static_exercise.is_open_for([self.user.get_profile()]))
        self.assertTrue(self.exercise_with_attachment.is_open_for([self.user.get_profile()]))
        self.assertFalse(self.old_base_exercise.is_open_for([self.user.get_profile()]))
        self.assertFalse(self.base_exercise.is_open_for([self.user.get_profile()], self.yesterday))
        self.assertFalse(self.static_exercise.is_open_for([self.user.get_profile()], self.yesterday))
        self.assertTrue(self.exercise_with_attachment.is_open_for([self.user.get_profile()], self.yesterday))
        self.assertTrue(self.old_base_exercise.is_open_for([self.user.get_profile()], self.yesterday))
        self.assertTrue(self.base_exercise.is_open_for([self.user.get_profile()], self.tomorrow))
        self.assertTrue(self.static_exercise.is_open_for([self.user.get_profile()], self.tomorrow))
        self.assertTrue(self.exercise_with_attachment.is_open_for([self.user.get_profile()], self.tomorrow))
        self.assertFalse(self.old_base_exercise.is_open_for([self.user.get_profile()], self.tomorrow))

    def test_base_exercise_submission_allowed(self):
        self.assertFalse(self.base_exercise.is_submission_allowed([self.user.get_profile()])[0])
        self.assertTrue(self.static_exercise.is_submission_allowed([self.user.get_profile()])[0])
        self.assertTrue(self.exercise_with_attachment.is_submission_allowed([self.user.get_profile()])[0])
        self.assertTrue(self.old_base_exercise.is_submission_allowed([self.user.get_profile()])[0])
        self.assertFalse(self.base_exercise.is_submission_allowed([self.user.get_profile(), self.grader.get_profile()])[0])
        self.assertFalse(self.static_exercise.is_submission_allowed([self.user.get_profile(), self.grader.get_profile()])[0])
        self.assertFalse(self.exercise_with_attachment.is_submission_allowed([self.user.get_profile(), self.grader.get_profile()])[0])
        self.assertFalse(self.old_base_exercise.is_submission_allowed([self.user.get_profile(), self.grader.get_profile()])[0])
        self.assertTrue(self.base_exercise.is_submission_allowed([self.grader.get_profile()])[0])
        self.assertTrue(self.static_exercise.is_submission_allowed([self.grader.get_profile()])[0])
        self.assertTrue(self.exercise_with_attachment.is_submission_allowed([self.grader.get_profile()])[0])
        self.assertTrue(self.old_base_exercise.is_submission_allowed([self.grader.get_profile()])[0])

    def test_base_exercise_late_submission_allowed(self):
        self.assertFalse(self.base_exercise.is_late_submission_allowed())
        self.assertTrue(self.base_exercise_with_late_submission_allowed.is_late_submission_allowed())

    def test_base_exercise_late_submission_penalty(self):
        self.assertEqual(0.5, self.base_exercise.get_late_submission_penalty())
        self.assertEqual(0.2, self.base_exercise_with_late_submission_allowed.get_late_submission_penalty())

    def test_base_exercise_service_url(self):
        self.assertEqual("?submission_url=http%3A%2F%2Flocalhost%3A8000%2FtestSubmissionURL&max_points=100", self.base_exercise.build_service_url("/testSubmissionURL"))
        self.assertEqual("/testServiceURL?submission_url=http%3A%2F%2Flocalhost%3A8000%2FtestSubmissionURL&max_points=50", self.static_exercise.build_service_url("/testSubmissionURL"))

    def test_base_exercise_submissions_for_student(self):
        submissions = self.base_exercise.get_submissions_for_student(self.user.get_profile())
        self.assertEqual(3, len(submissions))
        submissions = self.static_exercise.get_submissions_for_student(self.user.get_profile())
        self.assertEqual(0, len(submissions))

    def test_base_exercise_unicode_string(self):
        self.assertEqual("test exercise", str(self.base_exercise))
        self.assertEqual("test exercise 2", str(self.static_exercise))
        self.assertEqual("test exercise 3", str(self.exercise_with_attachment))

    def test_base_exercise_absolute_url(self):
        self.assertEqual("/exercise/3/", self.base_exercise.get_absolute_url())
        self.assertEqual("/exercise/4/", self.static_exercise.get_absolute_url())
        self.assertEqual("/exercise/5/", self.exercise_with_attachment.get_absolute_url())

    def test_base_exercise_submission_parameters_for_students(self):
        parameters = self.base_exercise.get_submission_parameters_for_students([self.user.get_profile()])
        self.assertEqual("1", parameters[0])
        self.assertEqual("4bdcd7674311971e4886a8cb90a0d9d399a0b4f8c0ed32335fb520ed23945cfb", parameters[1])
        parameters = self.base_exercise.get_submission_parameters_for_students([self.user.get_profile(), self.grader.get_profile()])
        self.assertEqual("1-2", parameters[0])
        self.assertEqual("feea43b6ce4c5bd53d4b063637144c449a0d9bd0bf773b901719390d68712304", parameters[1])

    def test_base_exercise_submission_url_for_students(self):
        self.assertEqual(('1', '4bdcd7674311971e4886a8cb90a0d9d399a0b4f8c0ed32335fb520ed23945cfb'), self.base_exercise.get_submission_parameters_for_students([self.user.get_profile()]))
        self.assertEqual(('1-2', 'feea43b6ce4c5bd53d4b063637144c449a0d9bd0bf773b901719390d68712304'),
                         self.base_exercise.get_submission_parameters_for_students([self.user.get_profile(), self.grader.get_profile()]))

    def test_base_exercise_summary(self):
        summary = self.base_exercise.summary
        self.assertEqual(3, summary["submission_count"])
        self.assertEqual(2, summary["submitter_count"])
        self.assertEqual(0, summary["average_grade"])
        self.assertEqual(2, summary["average_submissions"])

    def test_base_exercise_get_exercise(self):
        self.assertIsInstance(self.base_exercise.get_exercise(name='test exercise 2'), BaseExercise)
        self.assertIsInstance(self.base_exercise.get_exercise(name='test exercise 3'), ExerciseWithAttachment)

    def test_base_exercise_breadcrumb(self):
        self.assertEqual([('123456 test course', '/course/Course-Url/'), ('Fall 2011 day 1', '/course/Course-Url/T-00.1000_d1/'), ('test exercise', '/exercise/3/')],
                         self.base_exercise.get_breadcrumb())
        self.assertEqual([('123456 test course', '/course/Course-Url/'), ('Fall 2011 day 1', '/course/Course-Url/T-00.1000_d1/'), ('test exercise 2', '/exercise/4/')],
                         self.static_exercise.get_breadcrumb())
        self.assertEqual([('123456 test course', '/course/Course-Url/'), ('Fall 2011 day 1', '/course/Course-Url/T-00.1000_d1/'), ('test exercise 3', '/exercise/5/')],
                         self.exercise_with_attachment.get_breadcrumb())

    def test_base_exercise_can_edit(self):
        self.assertFalse(self.base_exercise.can_edit(self.user.get_profile()))
        self.assertFalse(self.base_exercise.can_edit(self.grader.get_profile()))
        self.assertTrue(self.base_exercise.can_edit(self.teacher.get_profile()))

    def test_static_exercise_page(self):
        static_exercise_page = self.static_exercise.get_page()
        self.assertIsInstance(static_exercise_page, ExercisePage)
        self.assertEqual("test_page_content", static_exercise_page.content)

    def test_static_exercise_submit(self):
        static_exercise_page = self.static_exercise.submit("Fake submission")
        self.assertIsInstance(static_exercise_page, ExercisePage)
        self.assertTrue(static_exercise_page.is_accepted)
        self.assertEqual("test_submission_content", static_exercise_page.content)

    def test_exercise_upload_dir(self):
        self.assertEqual("exercise_attachments/exercise_5/test_file_name", exercise_models.build_upload_dir(self.exercise_with_attachment, "test_file_name"))

    def test_exercise_with_attachment_files_to_submit(self):
        files = self.exercise_with_attachment.get_files_to_submit()
        self.assertEqual(3, len(files))
        self.assertEqual("test1.txt", files[0])
        self.assertEqual("test2.txt", files[1])
        self.assertEqual("img.png", files[2])

    def test_exercise_with_attachment_page(self):
        exercise_with_attachment_page = self.exercise_with_attachment.get_page()
        self.assertIsInstance(exercise_with_attachment_page, ExercisePage)
        self.assertEqual('test_instructions\n<form enctype="multipart/form-data" method="post" class="form-stacked">\n  <fieldset>\n    <legend>Submit</legend>\n    \n    <div class=\'clearfix\'>\n  '
                         + '    <label>test1.txt</label>\n      <input type="hidden" name="file_1" value="test1.txt" />\n      <div class=\'input\'><input name=\'file[]\' type=\'file\' /></div>\n    '
                         + '</div>\n    \n    <div class=\'clearfix\'>\n      <label>test2.txt</label>\n      <input type="hidden" name="file_2" value="test2.txt" />\n      <div class=\'input\'><inpu'
                         + 't name=\'file[]\' type=\'file\' /></div>\n    </div>\n    \n    <div class=\'clearfix\'>\n      <label>img.png</label>\n      <input type="hidden" name="file_3" value="img'
                         + '.png" />\n      <div class=\'input\'><input name=\'file[]\' type=\'file\' /></div>\n    </div>\n    \n  </fieldset>\n  <div class="actions">\n    <input type="submit" valu'
                         + 'e="Submit" class="btn primary" />\n  </div>\n</form>\n', exercise_with_attachment_page.content)

    def test_deadline_rule_deviation_extra_time(self):
        self.assertEqual(timedelta(days=1), self.deadline_rule_deviation.get_extra_time())

    def test_deadline_rule_deviation_new_deadline(self):
        self.assertEqual(self.two_days_from_now, self.deadline_rule_deviation.get_new_deadline())

    def test_deadline_rule_deviation_normal_deadline(self):
        self.assertEqual(self.tomorrow, self.deadline_rule_deviation.get_normal_deadline())

    def test_submission_submitters(self):
        submitters = self.submission.submitters.all()
        self.assertEqual(1, len(submitters))
        self.assertEqual(self.user.get_profile(), submitters[0])

        self.submission.add_submitter(self.grader.get_profile())
        submitters = self.submission.submitters.all()
        self.assertEqual(2, len(submitters))
        self.assertEqual(self.user.get_profile(), submitters[0])
        self.assertEqual(self.grader.get_profile(), submitters[1])

        self.submission.submitters.clear()
        submitters = self.submission.submitters.all()
        self.assertEqual(0, len(submitters))
        self.submission.add_submitters([self.user.get_profile(), self.grader.get_profile()])
        submitters = self.submission.submitters.all()
        self.assertEqual(self.user.get_profile(), submitters[0])
        self.assertEqual(self.grader.get_profile(), submitters[1])

        self.submission.submitters.clear()
        self.submission.add_submitter(self.user.get_profile())
        submitters = self.submission.submitters.all()
        self.assertEqual(1, len(submitters))
        self.assertEqual(self.user.get_profile(), submitters[0])

    def test_submission_files(self):
        self.assertEqual(1, len(self.submission.files.all()))
        self.submission.add_files(MultiValueDict({
            "key1": ["test_file1.txt", "test_file2.txt"],
            "key2": ["test_image.png", "test_audio.wav", "test_pdf.pdf"]
        }))
        self.assertEqual(6, len(self.submission.files.all()))

    def test_submission_user_permission(self):
        self.assertTrue(self.submission.check_user_permission(self.user.get_profile()))
        self.assertFalse(self.submission.check_user_permission(self.user2.get_profile()))
        self.assertTrue(self.submission.check_user_permission(self.grader.get_profile()))
        self.assertTrue(self.submission.check_user_permission(self.teacher.get_profile()))

    def test_submission_course(self):
        self.assertEqual(self.course, self.submission.get_course())

    def test_submission_course_instance(self):
        self.assertEqual(self.course_instance, self.submission.get_course_instance())

    def test_submission_points(self):
        try:
            self.submission.set_points(10, 5)
            self.fail("Should not be able to set points higher than max points!")
        except AssertionError:
            self.submission.set_points(5, 10)
            self.assertEqual(50, self.submission.grade)
            self.late_submission_when_late_allowed.set_points(10, 10)
            self.assertEqual(80, self.late_submission_when_late_allowed.grade)

    def test_submission_submitted_late(self):
        self.assertFalse(self.submission.is_submitted_late())
        self.assertTrue(self.late_submission.is_submitted_late())
        self.assertFalse(self.submission_when_late_allowed.is_submitted_late())
        self.assertTrue(self.late_submission_when_late_allowed.is_submitted_late())
        self.assertTrue(self.late_late_submission_when_late_allowed.is_submitted_late())

    def test_submission_grading_data(self):
        self.assertEqual('', self.submission.grading_data)
        self.submission.set_grading_data({"a": "test", "b": "test2"})
        self.assertEqual({"a": "test", "b": "test2"}, self.submission.grading_data)

    def test_submission_submitter_string(self):
        self.assertEqual("First Last", self.submission.submitter_string())
        self.assertEqual("First Last, Strange Fellow", self.submission_with_two_submitters.submitter_string())

    def test_submission_unicode_string(self):
        self.assertEqual("1", str(self.submission))
        self.assertEqual("2", str(self.submission_with_two_submitters))
        self.assertEqual("3", str(self.late_submission))
        self.assertEqual("4", str(self.submission_when_late_allowed))
        self.assertEqual("5", str(self.late_submission_when_late_allowed))
        self.assertEqual("6", str(self.late_late_submission_when_late_allowed))

    def test_submission_status(self):
        self.assertEqual("initialized", self.submission.status)
        self.assertFalse(self.submission.is_graded())
        self.submission._set_status("error")
        self.assertEqual("error", self.submission.status)
        self.assertFalse(self.submission.is_graded())
        self.submission.set_waiting()
        self.assertEqual("waiting", self.submission.status)
        self.assertFalse(self.submission.is_graded())
        self.submission.set_error()
        self.assertEqual("error", self.submission.status)
        self.assertFalse(self.submission.is_graded())
        self.assertEqual(None, self.submission.grading_time)
        self.submission.set_ready()
        self.assertIsInstance(self.submission.grading_time, datetime)
        self.assertEqual("ready", self.submission.status)
        self.assertTrue(self.submission.is_graded())

    def test_submission_absolute_url(self):
        self.assertEqual("/exercise/submission/1/", self.submission.get_absolute_url())
        self.assertEqual("/exercise/submission/3/", self.late_submission.get_absolute_url())

    def test_submission_callback_url(self):
        self.assertEqual("/exercise/rest/submission/1/" + self.submission.hash + "/", self.submission.get_callback_url())
        self.assertEqual("/exercise/rest/submission/3/" + self.late_submission.hash + "/", self.late_submission.get_callback_url())

    def test_submission_staff_url(self):
        self.assertEqual("/exercise/submissions/inspect/1/", self.submission.get_staff_url())
        self.assertEqual("/exercise/submissions/inspect/3/", self.late_submission.get_staff_url())

    def test_submission_breadcrumb(self):
        breadcrumb = self.submission.get_breadcrumb()
        self.assertEqual(4, len(breadcrumb))
        self.assertEqual(('123456 test course', '/course/Course-Url/'), breadcrumb[0])
        self.assertEqual(('Fall 2011 day 1', '/course/Course-Url/T-00.1000_d1/'), breadcrumb[1])
        self.assertEqual(('test exercise', '/exercise/3/'), breadcrumb[2])
        self.assertEqual(2, len(breadcrumb[3]))
        self.assertEqual('/exercise/submission/1/', breadcrumb[3][1])
        breadcrumb = self.late_submission.get_breadcrumb()
        self.assertEqual(4, len(breadcrumb))
        self.assertEqual(('123456 test course', '/course/Course-Url/'), breadcrumb[0])
        self.assertEqual(('Fall 2011 day 1', '/course/Course-Url/T-00.1000_d1/'), breadcrumb[1])
        self.assertEqual(('test exercise', '/exercise/3/'), breadcrumb[2])
        self.assertEqual(2, len(breadcrumb[3]))
        self.assertEqual('/exercise/submission/3/', breadcrumb[3][1])

    def test_submission_upload_dir(self):
        self.assertEqual("submissions/course_instance_1/exercise_3/users_1/submission_1/test_file_name", build_upload_dir(self.submitted_file1, "test_file_name"))
        self.assertEqual("submissions/course_instance_1/exercise_3/users_1-4/submission_2/test_file_name", build_upload_dir(self.submitted_file2, "test_file_name"))