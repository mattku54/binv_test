# BINVENTORY
#### Video Demo:  <URL [https://youtu.be/baHyRb0dPkY]>
#### Description:

# Summary
Binventory is a web application that tracks the status (CLEAN, PARTIAL, DIRTY, MISSING) of laboratory items that are in a bin in a chemistry teaching lab. The bins are used across many different classes that meet in the laboratory classroom at different times. This app is designed to keep track of the status of items in a bin and flag which users and bins are not practicing proper hygiene in regards to cleaning and maintaining their bin.

# Users
There will be two different types of users using Binventory: students and admin. Upon registering with their email and id, users will be assigned a different role that will have different functionalities.

## Logging In and Logging Out
All users will need the e-mail they registered with as well as their registered password to log in. The Binventory homepage by default will go to the student log in page. Those who wish to log in as an admin should click on the Admin Login page.

Note: Eventually there will be a way to recover a password but that is not currently a function. Also, this will require the use of an email server.

## Registration
By default, the user will register as a student. The user will need their school id and e-mail to register. They will also be required to register a password. Admin registration will be handled in a separate site that can be accessed from the default registration page. Admins will need the same information as those registering as a student but also need the Admin Key to register.

## Students
Students will be able to register for a class, be assigned a bin, and update the status of items in their bin during every laboratory session. After logging in, students will first register for a class and a bin ('Bin Assignment'). Every time the student comes in to the lab classroom they will be required to Check In ('Check In') the status of items in their bin. At the end of the class, they will also Check Out ('Check Out') by updating the status of items in their bin.

### Future notes
In the future, students will also be able to send a message to the last student who used the bin. These messages will inform the previous user of items that were left dirty, misplaced, etc. Upon logging in, the student that was flagged will see the flagged message and should mark it as resolved before continuing.

## Admins
Admins should register and login in the separate registration and login sites. Admin will have the ability to check the status of all of the bins for a class at once and see the status for each item in every bin. Admin should be able to also observe students checking in and checking out to make sure that students are indeed checking in and out.

### Class Bin Status
This page will allow the admin to view the status of all of the bins for their class. Admin can select the class with the semester and crn to view a table that will show every assigned bin for that class as well as the current status of every item in the bin. Table will also show the last time the student checked in and out.

Note: Right now the titles of each item are all nicknames.

### Register Class
This page will be used for a teacher/admin to register a class. This must be done before any students can be registered into the class. Admins will have to put in the semester (FA, WI, SP, SUM) along with the year (i.e. - FA22). In addition, the class must also have a course registration number (CRN).

### Register Bins
This will mostly be done by an admin managing the stockroom or who is in charge of putting together the individual bins for a classroom. Admin will put in the room number as well as the number of bins to register. By default, bins will be assigned a numberical bin number.

Note: Eventually there will be functionality to just add bins. Duplicate bin numbers should not be allowed to register.

### Edit Class Bin Assignments
If necessary, admin may also change the bin assignment of students that are registered in a class. Classes will be identified by the semester and the CRN of the class. There is currently no option to delete a student from a class roster but only to change which bin that that student is assigned.

### Edit Bin Content Status
Admin also have the ability to manually change the status of items in a bin. The bin will be identified by the semester and the CRN of the class as well as the bin number. Once that is identified, admin can change the status of each item in the bin.

### Future Notes
Once the flagged messages functionality is open, admin will also be able to see which students have been flagged.
