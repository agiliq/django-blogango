#### Added pagination

* Pagination for blog entries by a specific author.
* Pagination for blog entries tagged with a specific tag.

#### Changes on **Write new blog entry** page

We are talking about **/blog/admin/entry/new**.

* Make tag field autocomplete. We send all the tags in the system in template
context and tag suggestions are provided while user is typing in tag field. We use jquery autocomplete for it.
* Populate date and time fields with current date and time.

#### Changes on **Manage comments** page

We are talking about **blog/admin/comments/manage/**.

* Show `Approved` and `Blocked` comments in separate subnavs.
* Ajaxify `Approve` and `Block` comment process.

#### Fixes

* Change save() of Comment. Make sure a comment is never marked as both spam
and public.
* After editing tags of BlogEntry, the entry was still remaining tagged with
older tags. It is fixed.
* Fix issue with BlogEntry duplicate slugs. Now if you try three entries with
slugs *abc* they will have slugs set as *abc*, *abc-2* and *abc-3*
respectively.
* Since request.path is used in many templates, request context processor must
be available. Add request context processor to TEMPLATE_CONTEXT_PROCESSORS of example
project. 
* Fix path of static files.
* **/blog/install/** was raising an error when no Blog was added. Fixed.
* Removed permalink decorator form various places as it's no longer
recommended.
* Add markup types to requirements.

#### Changes for Django 1.5

* We have a view to show month archive which was earlier using a generic view
from module `date_based`. This module has been removed in Django 1.5 and a class
based view `MonthArchiveView` needs to be used for the same purpose. Made a
change for the same.
* Latest version of blogango which is 0.6 needs to be used with Django 1.5.
