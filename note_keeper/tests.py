from django.test import TestCase
import datetime
from django.utils import timezone
from .models import Note
from django.urls import reverse
from http import HTTPStatus

# Create your tests here.
class NoteIndexViewTests(TestCase):
    def test_read_with_no_note(self):
        # If there is no note, an appropriate message is displayed
        response = self.client.get(reverse('note_keeper:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your notebook is empty right now!")
        self.assertQuerysetEqual(response.context['latest_note_list'], [])

class Notecreate_noteTests(TestCase):
    def test_create_note_with_no_title(self):
        # Testing Create a note without filling the title
        response = self.client.post(reverse('note_keeper:create_note'), {"title": "", "content": "asdfasdf"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
                response, "Title or Content is empty, please write the form again")
    
    def test_create_note_with_no_content(self):
        # Testing creating a note with title but without content
        response = self.client.post(reverse('note_keeper:create_note'), {"title": "Testing", "content": ""}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
                response, "Title or Content is empty, please write the form again")
    
    def test_create_note_with_no_title_content(self):
        # Testing creating a note without title / content
        response = self.client.post(reverse('note_keeper:create_note'), {"title": "", "content": ""}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
                response, "Title or Content is empty, please write the form again")
 
    def test_create_note_with_same_title(self):
        # Testing creating a note with the same title
        response = self.client.post(reverse('note_keeper:create_note'), {"title": "Testing", "content": "Content for Testing"}, follow=True)
        sec_response = self.client.post(reverse('note_keeper:create_note'), {"title": "Testing", "content": "Anything"}, follow=True)
        self.assertEqual(sec_response.status_code, 200)
        self.assertContains(
                sec_response, "Title is taken, remove the previous note first!")
    

class Note_Detail_View_test(TestCase):
    def test_read_an_existing_note(self):
        create_note = self.client.post(reverse('note_keeper:create_note'), {"title": "Testing at 1013", "content": "is there bug there?"}, follow=True)
        response = self.client.get(reverse('note_keeper:note', args=["Testing at 1013"]))

    def test_read_an_nonexisting_note(self):
        """
        This test is to see whether the user can open a note that is not exist or not. At first the issue presents itself of the response code of 404 in which is Page not found, Fixing it, require modifying the detailView on the 404 exception parts to give an appropriate message / and returning back to index page
        """
        response = self.client.get(reverse('note_keeper:note', args=["1013"]), follow=True)
        self.assertEqual(response.status_code, 200)

 
    def test_read_an_unprovided_title(self):
        """
        The same test like the previous one except this one is sending an extra space instead of other characters. This intended not to send any arg to request for the page, but then it gives out an error. This is more like the defined function that has problem than the view. To prevent this, can pass the spacing, and the solution of nonexisting note works the same for this.

        """
        response = self.client.get(reverse('note_keeper:note', args=[" "]), follow=True)
        self.assertEqual(response.status_code, 200)

    
class Note_update_note_test(TestCase):
    def test_update_with_provided_title_content(self):
        """
        This testing is to make sure the provided title / content works well.
        """
        create_note = self.client.post(reverse('note_keeper:create_note'), {"title": "test1", "content": "content1"}, follow=True)
        response = self.client.post(reverse('note_keeper:update_note'),{"title": "test2", "content": "content1 change to content2", "old_title": "test1"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Note.objects.filter(pk="test2").exists(), not Note.objects.filter(pk="test1").exists()) 


    def test_update_with_unprovided_new_title(self):
        """
        This test's purpose is to make sure the view function doesn't update the current title into whitespace title. Since the issue tells that the view is returning None, we just have to return something when the enter_title is not the same as curr_title, to make it safe, we added length checking as well.
        """
        create_note = self.client.post(reverse('note_keeper:create_note'), {"title": "test2", "content": "content is here"}, follow=True)
        response =self.client.post(reverse('note_keeper:update_note'), {"title": " ", "content": "content is here", "old_title": "test2"}, follow=True)
        self.assertEqual(response.status_code, 200)
 
    def test_update_without_curr_title(self):
        create_note = self.client.post(reverse('note_keeper:create_note'), {"title": "test2", "content": "content is here"}, follow=True)
        response = self.client.post(reverse('note_keeper:update_note'), {"title": "test2", "content": "Updating new contenT", "old_title": ""}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sorry, I cannot let you do this")

    def test_update_title_only(self):
        """
            The purpose of this test to test whether the modify date is update or not. First, a note is created and then another request sent to update the title. The issue is fixed by setting the modify_date a new value when updating the title.
        """
        create_note = self.client.post(reverse('note_keeper:create_note'), {"title": "test2", "content": "content is here"}, follow=True)
        curr_note = Note.objects.get(pk="test2")
        curr_note_modify_date = curr_note.modify_date
        curr_note_doc = curr_note.doc
        response = self.client.post(reverse('note_keeper:update_note'), {"title": "test3", "content": "Updating new contenT", "old_title": "test2"}, follow=True)
        new_note = Note.objects.get(pk="test3")
        change_modify_date = new_note.modify_date > curr_note_doc
        self.assertEqual(True, change_modify_date)
 

class Note_delete_note_test(TestCase):
    def test_delete_note(self):
        create_note = self.client.post(reverse('note_keeper:create_note'), {"title": "test1", "content": "content1"}, follow=True)
        response = self.client.post(reverse('note_keeper:delete_note', args=["test1"]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Note title #test1 has been deleted")
        
    def test_delete_empty_args(self):
        create_note = self.client.post(reverse('note_keeper:create_note'), {"title": "test1", "content": "content1"}, follow=True)
        response = self.client.post(reverse('note_keeper:delete_note', args=[" "]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_delete_non_existing_title(self):
        response = self.client.post(reverse('note_keeper:delete_note', args=["Non existing title"]), follow=True)
        self.assertEqual(response.status_code, 200)


    def test_delete_sent_double_delete_request(self):
        create_note = self.client.post(reverse('note_keeper:create_note'), {"title": "test1", "content": "content1"}, follow=True)
        response = self.client.post(reverse('note_keeper:delete_note', args=["test1"]), follow=True)
        response = self.client.post(reverse('note_keeper:delete_note', args=["test1"]), follow=True) 
        self.assertEqual(response.status_code, 200)


        


        






