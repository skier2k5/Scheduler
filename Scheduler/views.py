from django.forms.forms import Form
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.contrib import auth
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ObjectDoesNotExist
from django.utils import simplejson
from django.core.mail import send_mail
from Event.models import *
from django.core import serializers
from django.db.models import Q
import itertools

from django import forms
from django.forms import ModelForm

class DepartmentForm(forms.Form):
    department = forms.ModelChoiceField(queryset=Department.objects.exclude(classes=None))
    
def getDictArray(post, name):
    dic = {}
    for k in post.keys():
        if k.startswith(name):
            rest = k[len(name):]

            # split the string into different components
            parts = [p[:-1] for p in rest.split('[')][1:]
            print parts
            id = parts[0]

            # add a new dictionary if it doesn't exist yet
            if id not in dic:
                dic[id] = {}

            # add the information to the dictionary
            dic[id][parts[1]] = post.get(k)
    return dic

def convertNumToTime(num):
    if num < 48:
        time = str(int(((num / 12) + 8)))
        if num % 12 == 0:
            time = time + ":00"
        else:
            time = time + ":" + str((num % 12) * 5)
        return time + " a.m."
    else:
        if int(((num - 48) / 12)) == 0:
            time = "12"
        else:
            time = str(int(((num - 48) / 12)))
        if num % 12 == 0:
            time = time + ":00"
        else:
            time = time + ":" + str((num % 12) * 5)
        return time + " p.m."
    
def checkEmail(request, email):
    try:
        user = User.objects.get(email=email)
        check = True
    except ObjectDoesNotExist:
        check = False
    return HttpResponse(check)
    
def checkUser(request, username):
    try:
        user = User.objects.get(username=username)
        check = True
    except ObjectDoesNotExist:
        check = False
    return HttpResponse(check)
    
def regUser(request):
    if request.is_ajax():
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        regUser = True
        if username == "" or email == "" or pass1 == "":
            regUser = False
        if pass1 != pass2:
            regUser = False
        try:
            user = User.objects.get(username=username)
            user = User.objects.get(email=email)
            regUser = False
        except ObjectDoesNotExist:
            pass
        if regUser == True:
            #send_mail('Thank you for registering at TuftSched.com', 'Thank you for registering.', 
            #       'TuftSched@TuftSched.com', [email], fail_silently=False)
            #user = User.objects.create_user(username, email, pass1)
            #user.save()
            return HttpResponse("Success")
        else:
            return HttpResponse("Failed")
    else:
        return HttpResponse("Failed")
    
def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['pass']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponse("Success")
        else:
            return HttpResponse("Failed")
            
def clearSession(request):
    request.session.clear()
    return HttpResponse("Cleared")
    
def checkSession(request):
    return HttpResponse(request.session['classList'])
    
def addClass(request):
    if request.is_ajax():
        course = request.POST['class']
        if request.session.get('classList', False) == False:
            request.session['classList'] = list()
        if request.session['classList'].count(course) == 0:
            if len(request.session['classList']) < 10:
                request.session['classList'].append(course)
                if request.session.get('prefs', False) == False:
                    request.session['prefs'] = dict()
                    request.session['prefs']['monPref'] = "false"
                    request.session['prefs']['tuesPref'] = "false"
                    request.session['prefs']['wednPref'] = "false"
                    request.session['prefs']['thursPref'] = "false"
                    request.session['prefs']['friPref'] = "false"
                    request.session['prefs']['beforePref'] = "false"
                    request.session['prefs']['afterPref'] = "false"
                    request.session['prefs']['betweenPref'] = "false"
                    request.session['prefs']['beforeTime'] = "false"
                    request.session['prefs']['afterTime'] = "false"
                    request.session['prefs']['betweenStartTime'] = "false"
                    request.session['prefs']['betweenEndTime'] = "false"
                    request.session['prefs']['profPrefs'] = {}
                num, name = course.split(" - ")
                classes = ClassObject.objects.filter(courseNumber__startswith=num, name__startswith=name)
                profs = list()
                for c in classes:
                    if profs.count(c.professor) == 0:
                        profs.append(c.professor)
                request.session['prefs']['profPrefs'][num] = profs
                request.session.modified = True
                return HttpResponse("Success")
            else:
                return HttpResponse("Failed")
        else:
            return HttpResponse("Failed")
            
def removeClass(request):
    if request.is_ajax():
        course = request.POST['class']
        if request.session.get('classList', False) == False:
            return HttpResponse("Failed")
        if request.session['classList'].count(course) == 0:
            return HttpResponse("Failed")
        else:
            request.session['classList'].remove(course)
            request.session.modified = True
            return HttpResponse("Success")
            
def addPe(request):
    if request.is_ajax():
        id = request.POST['id']
        title = request.POST['title']
        start = request.POST['start']
        end = request.POST['end']
        info = request.POST['info']
        if request.user.is_authenticated():
            event = PersonalEvent(eventId = id, title = title, startTime = start, endTime = end, user = request.user)
            event.save()
            return HttpResponse("Success")
        else:
            event = { 'id':id, 'title':title, 'start':start, 'end':end, 'info':info }
            if request.session.get('persevents', False) == False:
                request.session['persevents'] = dict()
                request.session['persevents'][id] = event
            else:
                request.session['persevents'][id] = event
            request.session.modified = True
            return HttpResponse("Success")
            
def removePe(request):
    if request.is_ajax():
        id = request.POST['id']
        if request.user.is_authenticated():
            event = PersonalEvent.objects.filter(user = request.user.id, eventId = id)
            event.delete()
            return HttpResponse("Success")
        else:
            if request.session.get('persevents', False) == False:
                return HttpResponse("No Session")
            else:
                if request.session['persevents'].get(id, False) == False:
                    return HttpResponse("Invalid Key")
                else:
                    del request.session['persevents'][id]
                    request.session.modified = True
                    return HttpResponse("Success")

def getClassesInfo(request):
    if request.is_ajax():
        if request.session.get('classList', False) == False:
            return HttpResponse("Failed")
        else:
            classList = list()
            for course in request.session['classList']:
                num, name = course.split(" - ")
                classes = ClassObject.objects.filter(courseNumber__startswith=num, name__startswith=name)
                tempClass = dict()
                tempClass['name'] = course
                tempClass['num'] = num
                profs = list()
                for c in classes:
                    if profs.count(c.professor) == 0:
                        profs.append(c.professor)
                tempClass['profs'] = profs
                classList.append(tempClass)
            return HttpResponse(simplejson.dumps(classList))

def setPrefs(request):
    if request.is_ajax():
        if request.session.get('prefs', False) == False:
            request.session['prefs'] = dict()
        request.session['prefs']['monPref'] = request.POST['monPref']
        request.session['prefs']['tuesPref'] = request.POST['tuesPref']
        request.session['prefs']['wednPref'] = request.POST['wednPref']
        request.session['prefs']['thursPref'] = request.POST['thursPref']
        request.session['prefs']['friPref'] = request.POST['friPref']
        request.session['prefs']['beforePref'] = request.POST['beforePref']
        request.session['prefs']['afterPref'] = request.POST['afterPref']
        request.session['prefs']['betweenPref'] = request.POST['betweenPref']
        request.session['prefs']['beforeTime'] = request.POST['beforeTime']
        request.session['prefs']['afterTime'] = request.POST['afterTime']
        request.session['prefs']['betweenStartTime'] = request.POST['betweenStartTime']
        request.session['prefs']['betweenEndTime'] = request.POST['betweenEndTime']
        request.session['prefs']['profPrefs'] = getDictArray(request.POST, 'profPrefs')
        request.session.modified = True
        return HttpResponse(simplejson.dumps(request.session['prefs']))

def getPrefs(request):
    if request.is_ajax():
        if request.session.get('prefs', False) == False:
            return HttpResponse("None")
        return HttpResponse(simplejson.dumps(request.session['prefs']))

def logout(request):
    auth.logout(request)
    return redirect('/')
    
def getCourses(request,deptID):
    if deptID == "0":
        departments = Department.objects.exclude(classes=None)
        courses = list()
        for dep in departments:
            courses += list(dep.classes.all().values("courseNumber", "name").distinct())
        return HttpResponse(simplejson.dumps(courses))
    else:
        department = Department.objects.filter(id=deptID)[0]
        courses = list(department.classes.all().values("courseNumber","name").distinct())
        for course in courses:
            course['id'] = ClassObject.objects.filter(courseNumber=course['courseNumber'])[0].id
        print courses
        return HttpResponse(simplejson.dumps(courses))
        
def getSingleCourse(request, courseID, courseName):
    tempCourses = list(ClassObject.objects.all().filter(courseNumber=courseID, name=courseName))
    return HttpResponse(serializers.serialize("json", tempCourses))

def getSingleClass(request, callNum):
    classes = ClassObject.objects.filter(callNumber=callNum)
    return HttpResponse(serializers.serialize("json", classes))
    
def createSchedule(request):
    prefWeights = dict()
    prefWeights['base'] = 1
    prefWeights['baseConflict'] = 100
    prefWeights['persConflict'] = 50
    prefWeights['beforePref'] = 3
    prefWeights['afterPref'] = 3
    prefWeights['betweenPref'] = 7
    prefWeights['dayPref'] = 5
    prefWeights['profWantPref'] = 1
    prefWeights['profNonePref'] = 4
    prefWeights['profAvoidPref'] = 7
    courses = dict()
    if request.session.get('classList', False) == False:
        return HttpResponse("NoList")
    else:
        for c in request.session['classList']:
            num, name = c.split(" - ")
            courses[name] = list(ClassObject.objects.filter(courseNumber__startswith=num,name__startswith=name))
            clIndex = 0;
            cl2Index = 0;
            for cl in courses[name]:
                cl2Index = 0;
                for cl2 in courses[name]:
                    if cl != cl2:
                        if cl.professor == cl2.professor:
                            if cl.times == cl2.times:
                                if cl.days == cl2.days:
                                    if cl.locations == cl2.locations:
                                        if cl.closed == True and cl2.closed == True:
                                            courses[name].pop(cl2Index)
                                        elif cl.closed == True and cl2.closed == False:
                                            courses[name].pop(clIndex)
                                        elif cl.closed == False and cl2.closed == True:
                                            courses[name].pop(cl2Index)
                                        else:
                                            courses[name].pop(clIndex)
                    cl2Index += 1
                clIndex += 1
    def timeToSlot(timeString):
        if "NONE" in timeString or timeString == "":
            return 0
        try:
            am = "AM" in timeString
            hour = int(timeString[0:2])
            minutes = int(timeString[2:4])
            if am:
                return (hour-8)*12+(minutes/5)
            elif hour == 12:
                return minutes/5+48
            else:
                return hour*12+minutes/5+48
        except:
            return 0
            
    def persEventTimeToSlot(timeString):
        hour = int(timeString[:2])
        min = int(timeString[3:5])
        if hour < 12:
            return (hour-8)*12+(min/5)
        elif hour == 12:
            return min/5+48
        else:
            return (hour-12)*12+min/5+48
            
    needArrangements = list(itertools.product(*courses.values()))
    minConflict = 10000000
    minArrangement = None
    checkConflictArray = ['f'] * len(needArrangements)
    minConflictArray = [10000000] * len(needArrangements)
    arrangementNum = 0
    daysAndTimes = ""
    for arrangement in needArrangements:
        table = [[0 for col in range(0,5)] for row in range(0,169)]
        classObjNum = 0
        for classobj in arrangement:
            classObjNum+=1
            days = classobj.days
            times = classobj.times
            if "~" in days:
                days = days.split("~")
                times = times.split("~")
                for index in range(len(days)):
                    for char in days[index]:
                        startTime = timeToSlot(times[index][:6])
                        endTime = timeToSlot(times[index][7:])
                        dayOfWeek = 0
                        if "T" in char:
                            dayOfWeek = 1
                        elif "W" in char:
                            dayOfWeek = 2
                        elif "R" in char:
                            dayOfWeek = 3
                        elif "F" in char:
                            dayOfWeek = 4
                        conflictNum = prefWeights['base']
                        if request.session['prefs']['beforePref'] == "true":
                            if startTime < request.session['prefs']['beforeTime']:
                                conflictNum += prefWeights['beforePref']
                        if request.session['prefs']['afterPref'] == "true":
                            if endTime > request.session['prefs']['afterTime']:
                                conflictNum += prefWeights['afterPref']
                        if request.session['prefs']['betweenPref'] == "true":
                            if (endTime < request.session['prefs']['betweenEndTime'] and endTime > request.session['prefs']['betweenStartTime']) or (startTime < request.session['prefs']['betweenEndTime'] and startTime > request.session['prefs']['betweenStartTime']):
                                conflictNum += prefWeights['betweenPref']
                        if request.session['prefs']['monPref'] == "true":
                            if dayOfWeek == 0:
                                conflictNum += prefWeights['dayPref']
                        if request.session['prefs']['tuesPref'] == "true":
                            if dayOfWeek == 1:
                                conflictNum += prefWeights['dayPref']
                        if request.session['prefs']['wednPref'] == "true":
                            if dayOfWeek == 2:
                                conflictNum += prefWeights['dayPref']
                        if request.session['prefs']['thursPref'] == "true":
                            if dayOfWeek == 3:
                                conflictNum += prefWeights['dayPref']
                        if request.session['prefs']['friPref'] == "true":
                            if dayOfWeek == 4:
                                conflictNum += prefWeights['dayPref']
                        if request.session.get('persevents', False) != False:
                            for key in request.session['persevents'].keys():
                                persEventStartTime = persEventTimeToSlot(request.session['persevents'][key]['start'][16:21])
                                persEventEndTime = persEventTimeToSlot(request.session['persevents'][key]['end'][16:21])
                                if request.session['persevents'][key]['start'][:2] == "Mo" and dayOfWeek == 0:
                                    if (startTime > persEventStartTime and startTime < persEventEndTime) or (endTime > persEventStartTime and endTime < persEventEndTime):
                                        checkConflictArray[arrangementNum] = 'p'
                                        conflictNum += prefWeights['persConflict']
                                if request.session['persevents'][key]['start'][:2] == "Tu" and dayOfWeek == 1:
                                    if (startTime > persEventStartTime and startTime < persEventEndTime) or (endTime > persEventStartTime and endTime < persEventEndTime):
                                        checkConflictArray[arrangementNum] = 'p'
                                        conflictNum += prefWeights['persConflict']
                                if request.session['persevents'][key]['start'][:2] == "We" and dayOfWeek == 2:
                                    if (startTime > persEventStartTime and startTime < persEventEndTime) or (endTime > persEventStartTime and endTime < persEventEndTime):
                                        checkConflictArray[arrangementNum] = 'p'
                                        conflictNum += prefWeights['persConflict']
                                if request.session['persevents'][key]['start'][:2] == "Th" and dayOfWeek == 3:
                                    if (startTime > persEventStartTime and startTime < persEventEndTime) or (endTime > persEventStartTime and endTime < persEventEndTime):
                                        checkConflictArray[arrangementNum] = 'p'
                                        conflictNum += prefWeights['persConflict']
                                if request.session['persevents'][key]['start'][:2] == "Fr" and dayOfWeek == 4:
                                    if (startTime > persEventStartTime and startTime < persEventEndTime) or (endTime > persEventStartTime and endTime < persEventEndTime):
                                        checkConflictArray[arrangementNum] = 'p'
                                        conflictNum += prefWeights['persConflict']
                        for i in range(startTime,endTime):
                            if table[i][dayOfWeek] == 0:
                                table[i][dayOfWeek] = conflictNum
                            else:
                                checkConflictArray[arrangementNum] = 'c'
                                table[i][dayOfWeek] += conflictNum + prefWeights['baseConflict']
            elif "NONE" not in days:
                for char in days:
                    startTime = timeToSlot(times[:6])
                    endTime = timeToSlot(times[7:])
                    dayOfWeek = 0
                    if "T" in char:
                        dayOfWeek = 1
                    elif "W" in char:
                        dayOfWeek = 2
                    elif "R" in char:
                        dayOfWeek = 3
                    elif "F" in char:
                        dayOfWeek = 4
                    conflictNum = prefWeights['base']
                    if request.session['prefs']['beforePref'] == "true":
                        if startTime < request.session['prefs']['beforeTime']:
                            conflictNum += prefWeights['beforePref']
                    if request.session['prefs']['afterPref'] == "true":
                        if endTime > request.session['prefs']['afterTime']:
                            conflictNum += prefWeights['afterPref']
                    if request.session['prefs']['betweenPref'] == "true":
                        if (endTime < request.session['prefs']['betweenEndTime'] and endTime > request.session['prefs']['betweenStartTime']) or (startTime < request.session['prefs']['betweenEndTime'] and startTime > request.session['prefs']['betweenStartTime']):
                            conflictNum += prefWeights['betweenPref']
                    if request.session['prefs']['monPref'] == "true":
                        if dayOfWeek == 0:
                            conflictNum += prefWeights['dayPref']
                    if request.session['prefs']['tuesPref'] == "true":
                        if dayOfWeek == 1:
                            conflictNum += prefWeights['dayPref']
                    if request.session['prefs']['wednPref'] == "true":
                        if dayOfWeek == 2:
                            conflictNum += prefWeights['dayPref']
                    if request.session['prefs']['thursPref'] == "true":
                        if dayOfWeek == 3:
                            conflictNum += prefWeights['dayPref']
                    if request.session['prefs']['friPref'] == "true":
                        if dayOfWeek == 4:
                            conflictNum += prefWeights['dayPref']
                    if request.session.get('persevents', False) != False:
                        for key in request.session['persevents'].keys():
                            persEventStartTime = persEventTimeToSlot(request.session['persevents'][key]['start'][16:21])
                            persEventEndTime = persEventTimeToSlot(request.session['persevents'][key]['end'][16:21])
                            if request.session['persevents'][key]['start'][:2] == "Mo" and dayOfWeek == 0:
                                if (startTime > persEventStartTime and startTime < persEventEndTime) or (endTime > persEventStartTime and endTime < persEventEndTime):
                                    checkConflictArray[arrangementNum] = 'p'
                                    conflictNum += prefWeights['persConflict']
                            if request.session['persevents'][key]['start'][:2] == "Tu" and dayOfWeek == 1:
                                if (startTime > persEventStartTime and startTime < persEventEndTime) or (endTime > persEventStartTime and endTime < persEventEndTime):
                                    checkConflictArray[arrangementNum] = 'p'
                                    conflictNum += prefWeights['persConflict']
                            if request.session['persevents'][key]['start'][:2] == "We" and dayOfWeek == 2:
                                if (startTime > persEventStartTime and startTime < persEventEndTime) or (endTime > persEventStartTime and endTime < persEventEndTime):
                                    checkConflictArray[arrangementNum] = 'p'
                                    conflictNum += prefWeights['persConflict']
                            if request.session['persevents'][key]['start'][:2] == "Th" and dayOfWeek == 3:
                                if (startTime > persEventStartTime and startTime < persEventEndTime) or (endTime > persEventStartTime and endTime < persEventEndTime):
                                    checkConflictArray[arrangementNum] = 'p'
                                    conflictNum += prefWeights['persConflict']
                            if request.session['persevents'][key]['start'][:2] == "Fr" and dayOfWeek == 4:
                                if (startTime > persEventStartTime and startTime < persEventEndTime) or (endTime > persEventStartTime and endTime < persEventEndTime):
                                    checkConflictArray[arrangementNum] = 'p'
                                    conflictNum += prefWeights['persConflict']
                    for i in range(startTime,endTime):
                        if table[i][dayOfWeek] == 0:
                            table[i][dayOfWeek] = conflictNum
                        else:
                            checkConflictArray[arrangementNum] = 'c'
                            table[i][dayOfWeek] += conflictNum + prefWeights['baseConflict']
        tableSum = sum(sum(table[row][col] for row in range(0,169) ) for col in range(0,5))
        minConflictArray[arrangementNum] = tableSum
        arrangementNum += 1
    freeArrangements = list()
    persConflictArrangements = list()
    conflictArrangements = list()
    check = ""
    for x in range(0, len(checkConflictArray)):
        if checkConflictArray[x] == 'f':
            freeArrangements.append(x)
        elif checkConflictArray[x] == 'c':
            conflictArrangements.append(x)
        else:
            persConflictArrangements.append(x)
    minArrangements = [None] * 5
    minWeights = [9999996, 9999997, 9999998, 9999999, 10000000]
    calendarEvents = []
    if len(freeArrangements) > 0:
        calendarEvents.append({"conflict":"no"})
        for index in freeArrangements:
            if minConflictArray[index] < minWeights[0]:
                minWeights[0] = minConflictArray[index]
                minArrangements[0] = needArrangements[index]
            elif minConflictArray[index] < minWeights[1]:
                minWeights[1] = minConflictArray[index]
                minArrangements[1] = needArrangements[index]
            elif minConflictArray[index] < minWeights[2]:
                minWeights[2] = minConflictArray[index]
                minArrangements[2] = needArrangements[index]
            elif minConflictArray[index] < minWeights[3]:
                minWeights[3] = minConflictArray[index]
                minArrangements[3] = needArrangements[index]
            elif minConflictArray[index] < minWeights[4]:
                minWeights[4] = minConflictArray[index]
                minArrangements[4] = needArrangements[index]
    elif len(persConflictArrangements) > 0:
        calendarEvents.append({"conflict":"personal"})
        for index in persConflictArrangements:
            if minConflictArray[index] < minWeights[0]:
                minWeights[0] = minConflictArray[index]
                minArrangements[0] = needArrangements[index]
            elif minConflictArray[index] < minWeights[1]:
                minWeights[1] = minConflictArray[index]
                minArrangements[1] = needArrangements[index]
            elif minConflictArray[index] < minWeights[2]:
                minWeights[2] = minConflictArray[index]
                minArrangements[2] = needArrangements[index]
            elif minConflictArray[index] < minWeights[3]:
                minWeights[3] = minConflictArray[index]
                minArrangements[3] = needArrangements[index]
            elif minConflictArray[index] < minWeights[4]:
                minWeights[4] = minConflictArray[index]
                minArrangements[4] = needArrangements[index]
    elif len(conflictArrangements) > 0:
        calendarEvents.append({"conflict":"class"})
        for index in conflictArrangements:
            if minConflictArray[index] < minWeights[0]:
                minWeights[0] = minConflictArray[index]
                minArrangements[0] = needArrangements[index]
            elif minConflictArray[index] < minWeights[1]:
                minWeights[1] = minConflictArray[index]
                minArrangements[1] = needArrangements[index]
            elif minConflictArray[index] < minWeights[2]:
                minWeights[2] = minConflictArray[index]
                minArrangements[2] = needArrangements[index]
            elif minConflictArray[index] < minWeights[3]:
                minWeights[3] = minConflictArray[index]
                minArrangements[3] = needArrangements[index]
            elif minConflictArray[index] < minWeights[4]:
                minWeights[4] = minConflictArray[index]
                minArrangements[4] = needArrangements[index]
    numArrangements = 0
    for arrangement in minArrangements:
        if arrangement != None:
            clsEvent = []
            for cls in arrangement:
                day = cls.days
                times = cls.times.split("-")
                if not "NONE" in day:
                    for char in day:
                        date = 12
                        if "T" in char:
                            date = 13
                        if "W" in char:
                            date = 14
                        if "R" in char:
                            date = 15
                        if "F" in char:
                            date = 16
                        startTime = times[0]
                        endTime = times[1]
                        startHour = int(startTime[0:2])
                        if "P" in startTime and startHour != 12:
                            startHour += 12
                        startMinute = startTime[2:4]
                        endHour = int(endTime[0:2])
                        if "P" in endTime and endHour != 12:
                            endHour += 12
                        endMinute = endTime[2:4]
                        title = cls.name + " - " + cls.callNumber
                        clsEvent.append({"day":date,"id":cls.id,"startHour":startHour,"startMinute":startMinute,"endHour":endHour,"endMinute":endMinute,"title":title,"callNum":cls.callNumber})
            calendarEvents.append({"arrangement"+str(numArrangements):clsEvent})
            numArrangements += 1
    return HttpResponse(simplejson.dumps(calendarEvents))
    
def saveClasses(request):
    if request.is_ajax():
        user = request.user
        courses = request.POST['courses'].split('/')
        if user.is_authenticated():
            classes = ClassEvent.objects.filter(user=user.id)
            for c in classes:
                c.delete()
            for course in courses:
                c = ClassObject.objects.filter(callNumber=course)[0]
                if c != None:
                    event = ClassEvent(user = request.user, classObject = c, priority = "1")
                    event.save()
            classes = ClassEvent.objects.filter(user=user.id)
            return HttpResponse(classes)
        else:
            request.session['schedule'] = list()
            for course in courses:
                c = ClassObject.objects.filter(callNumber=course)
                if c != None:
                    request.session['schedule'].append(course)
            request.session.modified = True
            return HttpResponse(request.session['schedule'])
    
def addClassesToSched(request):
    if request.is_ajax():
        user = request.user
        courseNum = request.POST['courseNum']
        if user.is_authenticated():
            c = ClassObject.objects.filter(callNumber=courseNum)[0]
            check = ClassEvent.objects.filter(user = request.user, classObject = c)
            if check != None:
                return HttpResponse("Failed")
            if c != None:
                event = ClassEvent(user = request.user, classObject = c, priority = "1")
                event.save()
            classes = ClassEvent.objects.filter(user=user.id)
            return HttpResponse("Success")
        else:
            c = ClassObject.objects.filter(callNumber=courseNum)
            if c != None:
                if request.session.get('schedule', False) == False:
                    request.session['schedule'] = list()
                if courseNum in request.session['schedule']:
                    return HttpResponse("Failed")
                request.session['schedule'].append(courseNum)
            request.session.modified = True
            return HttpResponse("Success")
        
def removeClassFromSched(request):
    if request.is_ajax():
        user = request.user
        callNum = request.POST['callNum']
        if user.is_authenticated():
            c = ClassObject.objects.filter(callNumber=callNum)[0]
            event = ClassEvent.objects.filter(classObject = c, user = user.id)[0]
            if event != None:
                event.delete()
            classes = ClassEvent.objects.filter(user=user.id)
            return HttpResponse(classes)
        else:
            if request.session.get('schedule', False) != False:
                if request.session['schedule'].count(callNum) > 0:
                    request.session['schedule'].remove(callNum)
            request.session.modified = True
            return HttpResponse(request.session['schedule'])

def searchClasses(request):
    if request.is_ajax():
        search = request.POST['search']
        classes = ClassObject.objects.filter(Q(courseNumber__icontains=search) | Q(name__icontains=search))
        return HttpResponse(serializers.serialize("json", classes))

def getPersEvents(request):
    user = request.user
    if request.user.is_authenticated():
        events = []
        eventModels = PersonalEvent.objects.filter(user=request.user.id)
        idStart = 0
        for event in eventModels:
            startday = event.startTime[8:10]
            starthour = event.startTime[16:18]
            startmin = event.startTime[19:21]
            endday = event.endTime[8:10]
            endhour = event.endTime[16:18]
            endmin = event.endTime[19:21]
            events.append({"id":event.eventId, "title":event.title, "day":startday, "startHour":starthour, "startMinute":startmin, "endHour":endhour, "endMinute":endmin})
            if int(event.eventId) > idStart:
                idStart = int(event.eventId)
        idStart += 1
    else:
        if request.session.get('persevents', False) == False:
            idStart = 1
            events = []
        else:
            keys = request.session['persevents'].keys()
            events = []
            maxKey = 0
            for key in keys:
                startday = request.session['persevents'][key]['start'][8:10]
                starthour = request.session['persevents'][key]['start'][16:18]
                startmin = request.session['persevents'][key]['start'][19:21]
                endday = request.session['persevents'][key]['end'][8:10]
                endhour = request.session['persevents'][key]['end'][16:18]
                endmin = request.session['persevents'][key]['end'][19:21]
                event = request.session['persevents'][key]
                events.append({"id":event['id'], "title":event['title'], "day":startday, "startHour":starthour, "startMinute":startmin, "endHour":endhour, "endMinute":endmin})
                if int(key) > maxKey:
                    maxKey = int(key)
            idStart = maxKey + 1
    return HttpResponse(simplejson.dumps(events))
    
def printSched(request):
    user = request.user
    if request.user.is_authenticated():
        events = ""
        rows = ""
        eventModels = PersonalEvent.objects.filter(user=request.user.id)
        idStart = 0
        for event in eventModels:
            startday = event.startTime[8:10]
            starthour = event.startTime[16:18]
            startmin = event.startTime[19:21]
            endday = event.endTime[8:10]
            endhour = event.endTime[16:18]
            endmin = event.endTime[19:21]
            events += "$('#calendar').fullCalendar('renderEvent', {"
            events += "id: " + str(event.eventId) + ", "
            events += "title: '" + event.title + "', "
            events += "start: new Date(2011, 8, " + startday + ", " + starthour + ", " + startmin + "), "
            events += "end: new Date(2011, 8, " + endday + ", " + endhour + ", " + endmin + "), "
            events += "backgroundColor: \"#1a9206\","
            events += "info: 'PE'}, true);"
            if int(event.eventId) > idStart:
                idStart = int(event.eventId)
        idStart += 1
        classEvents = ClassEvent.objects.filter(user=user.id)
        for classEvent in classEvents:
            c = classEvent.classObject
            rows += "<tr><td>" + c.courseNumber + "</td><td>" + c.name + "</td><td>" + c.callNumber + "</td><td>" + c.professor + "</td><td>" + c.locations + "</td>"
            rows += "<td>" + c.days.replace("~", "<br />") + "</td><td>" + c.times.replace("~", "<br />") + "</td></tr>"
            tilde = False
            for day in c.days:
                if day == "~":
                    tilde = True
                    continue
                if day == "M":
                    day = 12
                if day == "T":
                    day = 13
                if day == "W":
                    day = 14
                if day == "R":
                    day = 15
                if day == "F":
                    day = 16
                if tilde:
                    startHour = c.times[14:16]
                    startMin = c.times[16:18]
                    ampm = c.times[18:20]
                    if ampm == "PM" and startHour != "12":
                        startHour = int(startHour) + 12
                    endHour = c.times[21:23]
                    endMin = c.times[23:25]
                    ampm = c.times[25:27]
                    if ampm == "PM" and endHour != "12":
                        endHour = int(endHour) + 12
                else:
                    startHour = c.times[0:2]
                    startMin = c.times[2:4]
                    ampm = c.times[4:6]
                    if ampm == "PM" and startHour != "12":
                        startHour = int(startHour) + 12
                    endHour = c.times[7:9]
                    endMin = c.times[9:11]
                    ampm = c.times[11:13]
                    if ampm == "PM" and endHour != "12":
                        endHour = int(endHour) + 12
                title = c.name + " - " + c.callNumber
                events += "$('#calendar').fullCalendar('renderEvent', {"
                events += "id: " + str(c.callNumber) + ", "
                events += "title: '" + title + "', "
                events += "start: new Date(2011, 8, " + str(day) + ", " + str(startHour) + ", " + str(startMin) + "), "
                events += "end: new Date(2011, 8, " + str(day) + ", " + str(endHour) + ", " + str(endMin) + "), "
                events += "info: '" + str(c.callNumber) + "'}, true);"
    else:
        if request.session.get('persevents', False) == False:
            idStart = 1
            events = ""
        else:
            keys = request.session['persevents'].keys()
            events = ""
            rows = ""
            maxKey = 0
            for key in keys:
                startday = request.session['persevents'][key]['start'][8:10]
                starthour = request.session['persevents'][key]['start'][16:18]
                startmin = request.session['persevents'][key]['start'][19:21]
                endday = request.session['persevents'][key]['end'][8:10]
                endhour = request.session['persevents'][key]['end'][16:18]
                endmin = request.session['persevents'][key]['end'][19:21]
                events += "$('#calendar').fullCalendar('renderEvent', {"
                events += "id: " + request.session['persevents'][key]['id'] + ", "
                events += "title: '" + request.session['persevents'][key]['title'] + "', "
                events += "start: new Date(2011, 8, " + startday + ", " + starthour + ", " + startmin + "), "
                events += "end: new Date(2011, 8, " + endday + ", " + endhour + ", " + endmin + "), "
                events += "backgroundColor: \"#1a9206\","
                events += "info: '" + request.session['persevents'][key]['info'] + "'}, true);"
                if int(key) > maxKey:
                    maxKey = int(key)
            idStart = maxKey + 1
        if request.session.get('schedule', False) != False:
            for callNumber in request.session['schedule']:
                c = ClassObject.objects.filter(callNumber=callNumber)[0]
                rows += "<tr><td>" + c.courseNumber + "</td><td>" + c.name + "</td><td>" + c.callNumber + "</td><td>" + c.professor + "</td><td>" + c.locations + "</td>"
                rows += "<td>" + c.days.replace("~", "<br />") + "</td><td>" + c.times.replace("~", "<br />") + "</td></tr>"
                tilde = False
                for day in c.days:
                    if day == "~":
                        tilde = True
                        continue
                    if day == "M":
                        day = 12
                    if day == "T":
                        day = 13
                    if day == "W":
                        day = 14
                    if day == "R":
                        day = 15
                    if day == "F":
                        day = 16
                    if tilde:
                        startHour = c.times[14:16]
                        startMin = c.times[16:18]
                        ampm = c.times[18:20]
                        if ampm == "PM" and startHour != "12":
                            startHour = int(startHour) + 12
                        endHour = c.times[21:23]
                        endMin = c.times[23:25]
                        ampm = c.times[25:27]
                        if ampm == "PM" and endHour != "12":
                            endHour = int(endHour) + 12
                    else:
                        startHour = c.times[0:2]
                        startMin = c.times[2:4]
                        ampm = c.times[4:6]
                        if ampm == "PM" and startHour != "12":
                            startHour = int(startHour) + 12
                        endHour = c.times[7:9]
                        endMin = c.times[9:11]
                        ampm = c.times[11:13]
                        if ampm == "PM" and endHour != "12":
                            endHour = int(endHour) + 12
                    title = c.name + " - " + c.callNumber
                    events += "$('#calendar').fullCalendar('renderEvent', {"
                    events += "id: " + str(c.callNumber) + ", "
                    events += "title: '" + title + "', "
                    events += "start: new Date(2011, 8, " + str(day) + ", " + str(startHour) + ", " + str(startMin) + "), "
                    events += "end: new Date(2011, 8, " + str(day) + ", " + str(endHour) + ", " + str(endMin) + "), "
                    events += "info: '" + str(c.callNumber) + "'}, true);"
    return render_to_response("printsched.html", RequestContext(request,{"events":events, "rows":rows}))
    
def index(request):
    c = RequestContext(request)
    user = request.user
    if request.user.is_authenticated():
        events = ""
        eventModels = PersonalEvent.objects.filter(user=request.user.id)
        idStart = 0
        for event in eventModels:
            startday = event.startTime[8:10]
            starthour = event.startTime[16:18]
            startmin = event.startTime[19:21]
            endday = event.endTime[8:10]
            endhour = event.endTime[16:18]
            endmin = event.endTime[19:21]
            events += "$('#calendar').fullCalendar('renderEvent', {"
            events += "id: " + str(event.eventId) + ", "
            events += "title: '" + event.title + "', "
            events += "start: new Date(2011, 8, " + startday + ", " + starthour + ", " + startmin + "), "
            events += "end: new Date(2011, 8, " + endday + ", " + endhour + ", " + endmin + "), "
            events += "backgroundColor: \"#1a9206\","
            events += "info: 'PE'}, true);"
            if int(event.eventId) > idStart:
                idStart = int(event.eventId)
        idStart += 1
        classEvents = ClassEvent.objects.filter(user=user.id)
        for classEvent in classEvents:
            c = classEvent.classObject
            tilde = False
            for day in c.days:
                if day == "~":
                    tilde = True
                    continue
                if day == "M":
                    day = 12
                if day == "T":
                    day = 13
                if day == "W":
                    day = 14
                if day == "R":
                    day = 15
                if day == "F":
                    day = 16
                if tilde:
                    startHour = c.times[14:16]
                    startMin = c.times[16:18]
                    ampm = c.times[18:20]
                    if ampm == "PM" and startHour != "12":
                        startHour = int(startHour) + 12
                    endHour = c.times[21:23]
                    endMin = c.times[23:25]
                    ampm = c.times[25:27]
                    if ampm == "PM" and endHour != "12":
                        endHour = int(endHour) + 12
                else:
                    startHour = c.times[0:2]
                    startMin = c.times[2:4]
                    ampm = c.times[4:6]
                    if ampm == "PM" and startHour != "12":
                        startHour = int(startHour) + 12
                    endHour = c.times[7:9]
                    endMin = c.times[9:11]
                    ampm = c.times[11:13]
                    if ampm == "PM" and endHour != "12":
                        endHour = int(endHour) + 12
                title = c.name + " - " + c.callNumber
                events += "$('#calendar').fullCalendar('renderEvent', {"
                events += "id: " + str(c.callNumber) + ", "
                events += "title: '" + title + "', "
                events += "start: new Date(2011, 8, " + str(day) + ", " + str(startHour) + ", " + str(startMin) + "), "
                events += "end: new Date(2011, 8, " + str(day) + ", " + str(endHour) + ", " + str(endMin) + "), "
                events += "info: '" + str(c.callNumber) + "'}, true);"
    else:
        if request.session.get('persevents', False) == False:
            idStart = 1
            events = ""
        else:
            keys = request.session['persevents'].keys()
            events = ""
            maxKey = 0
            for key in keys:
                startday = request.session['persevents'][key]['start'][8:10]
                starthour = request.session['persevents'][key]['start'][16:18]
                startmin = request.session['persevents'][key]['start'][19:21]
                endday = request.session['persevents'][key]['end'][8:10]
                endhour = request.session['persevents'][key]['end'][16:18]
                endmin = request.session['persevents'][key]['end'][19:21]
                events += "$('#calendar').fullCalendar('renderEvent', {"
                events += "id: " + request.session['persevents'][key]['id'] + ", "
                events += "title: '" + request.session['persevents'][key]['title'] + "', "
                events += "start: new Date(2011, 8, " + startday + ", " + starthour + ", " + startmin + "), "
                events += "end: new Date(2011, 8, " + endday + ", " + endhour + ", " + endmin + "), "
                events += "backgroundColor: \"#1a9206\","
                events += "info: '" + request.session['persevents'][key]['info'] + "'}, true);"
                if int(key) > maxKey:
                    maxKey = int(key)
            idStart = maxKey + 1
        if request.session.get('schedule', False) != False:
            for callNumber in request.session['schedule']:
                c = ClassObject.objects.filter(callNumber=callNumber)[0]
                tilde = False
                for day in c.days:
                    if day == "~":
                        tilde = True
                        continue
                    if day == "M":
                        day = 12
                    if day == "T":
                        day = 13
                    if day == "W":
                        day = 14
                    if day == "R":
                        day = 15
                    if day == "F":
                        day = 16
                    if tilde:
                        startHour = c.times[14:16]
                        startMin = c.times[16:18]
                        ampm = c.times[18:20]
                        if ampm == "PM" and startHour != "12":
                            startHour = int(startHour) + 12
                        endHour = c.times[21:23]
                        endMin = c.times[23:25]
                        ampm = c.times[25:27]
                        if ampm == "PM" and endHour != "12":
                            endHour = int(endHour) + 12
                    else:
                        startHour = c.times[0:2]
                        startMin = c.times[2:4]
                        ampm = c.times[4:6]
                        if ampm == "PM" and startHour != "12":
                            startHour = int(startHour) + 12
                        endHour = c.times[7:9]
                        endMin = c.times[9:11]
                        ampm = c.times[11:13]
                        if ampm == "PM" and endHour != "12":
                            endHour = int(endHour) + 12
                    title = c.name + " - " + c.callNumber
                    events += "$('#calendar').fullCalendar('renderEvent', {"
                    events += "id: " + str(c.callNumber) + ", "
                    events += "title: '" + title + "', "
                    events += "start: new Date(2011, 8, " + str(day) + ", " + str(startHour) + ", " + str(startMin) + "), "
                    events += "end: new Date(2011, 8, " + str(day) + ", " + str(endHour) + ", " + str(endMin) + "), "
                    events += "info: '" + str(c.callNumber) + "'}, true);"
    if request.session.get('classList', False) == False:
        classes = ""
        classPrefs = ""
    else:
        classes = ""
        classPrefs = ""
        for c in request.session['classList']:
            classes += "<li><span class=\"courseName\">" + c + "</span><span class='classRemove'><a onClick=\"removeClass('" + c + "')\">X</a></span></li>"
            classPrefs += "<li><span class=\"courseName\"><a onClick=\"showPrefPopup()\">" + c + "</a></span></li>"
    if request.session.get('prefs', False) == False:
        prefs = dict()
        beforeOptions = ""
        for i in range(0, 49, 3):
            beforeOptions += '<option value="' + str(48 - i) + '">' + convertNumToTime(48 - i) + '</option>'
        afterOptions = ""
        for i in range(48, 157, 6):
            afterOptions += '<option value="' + str(i) + '">' + convertNumToTime(i) + '</option>'
        betweenStartOptions = ""
        for i in range(0, 163, 3):
            betweenStartOptions += '<option value="' + str(i) + '">' + convertNumToTime(i) + '</option>'
        betweenEndOptions = ""
        for i in range(0, 163, 3):
            betweenEndOptions += '<option value="' + str(162 - i) + '">' + convertNumToTime(162 - i) + '</option>'
    else:
        prefs = request.session['prefs']
        beforeOptions = ""
        for i in range(0, 49, 3):
            beforeOptions += '<option value="' + str(48 - i) + '"'
            if request.session['prefs']['beforeTime'] == str(48 - i):
                beforeOptions += " selected"
            beforeOptions += '>' + convertNumToTime(48 - i) + '</option>'
        afterOptions = ""
        for i in range(48, 157, 6):
            afterOptions += '<option value="' + str(i) + '"'
            if request.session['prefs']['afterTime'] == str(i):
                afterOptions += " selected"
            afterOptions += '>' + convertNumToTime(i) + '</option>'
        betweenStartOptions = ""
        for i in range(0, 163, 3):
            betweenStartOptions += '<option value="' + str(i) + '"'
            if request.session['prefs']['betweenStartTime'] == str(i):
                betweenStartOptions += " selected"
            betweenStartOptions += '>' + convertNumToTime(i) + '</option>'
        betweenEndOptions = ""
        for i in range(0, 163, 3):
            betweenEndOptions += '<option value="' + str(162 - i) + '"'
            if request.session['prefs']['betweenEndTime'] == str(162 - i):
                betweenEndOptions += " selected"
            betweenEndOptions += '>' + convertNumToTime(162 - i) + '</option>'
    depObjects = Department.objects.exclude(classes=None)
    departmentdropdown = '<option value="0">All</option>'
    classdropdown = ''
    for tempDep in depObjects:
        departmentdropdown += '<option value="' + str(tempDep.id) + '">' + tempDep.title + '</option>'
        classObjects = list(tempDep.classes.all().values("courseNumber", "name").distinct())
        for tempClass in classObjects:
            classdropdown += '<li onClick="showClassInfo(\'' + tempClass['courseNumber'] + '\', \'' + tempClass['name'] + '\')">' + tempClass['courseNumber'] + ' - ' + tempClass['name'] + '</li>'
    userform = UserCreationForm()
    departments = DepartmentForm()
    return render_to_response("index.html",RequestContext(request,{"classes":classes,
                                                                   "classPrefs":classPrefs,
                                                                   "prefs":prefs,
                                                                   "events":events,
                                                                   "departments":departments,
                                                                   "depdropdown":departmentdropdown,
                                                                   "classdropdown":classdropdown,
                                                                   "idStart":idStart,
                                                                   "beforeOptions":beforeOptions,
                                                                   "afterOptions":afterOptions,
                                                                   "betweenStartOptions":betweenStartOptions,
                                                                   "betweenEndOptions":betweenEndOptions}))