$(document).ready(function() {
    popupName = "schedulePopupDiv"
    step = 1;
    setPrefPopup()
    smallCal = false;
    creatingSched = false;
    $("#id_department").change(function (e) {
        if ($(this).val()) {
            $.get('ajax/getcourses/'+$(this).val(),
                function (response) {
                    courses = $.parseJSON(response);
                    $("#id_course").html("");
                    for (i in courses) {
                        newinner = $("#id_course").html();
                        text = "<option value='"+courses[i].id+"'>"+courses[i].courseNumber+" - "+courses[i].name+"</option>";
                        newinner += text;
                        $("#id_course").html(newinner);
                    }
                });
        }
    });
    $("#step5ClassDropDown").change(function (e) {
        if ($(this).val()) {
            $.get('ajax/getcourses/'+$(this).val(),
                function (response) {
                    courses = $.parseJSON(response);
                    $("#classesList li").remove();
                    for (i in courses) {
                        text = '<li onClick="showClassInfo(\'' + courses[i].courseNumber + '\', \'' + courses[i].name + '\')">' + courses[i].courseNumber + " - " + courses[i].name + "</li>";
                        $("#classesList").append(text);
                    }
                });
        }
    });
    $("#blanket").click(function (e) {
        if (popupName == "popUpDiv")
            popup(popupName);
    });
    $("#addClass").click(function (e) {
        val = $("#id_course option:selected").text()
        if (jQuery.inArray(val,$.classList) == -1 && val != "") {
            $("#class_list").append("<li><span class=\"courseName\">" + val + "</span><span class='classRemove'><a onClick=\"removeClass('" + val + "')\">X</a></span></li>");
            $("#class_list_pref").append("<li><span class=\"courseName\"><a onClick=\"showPrefPopup()\">" + val + "</a></span>");
            $.classList.push(val)
            $.ajax({
                url: 'ajax/addclass',
                type: "POST",
                data: { 'class':val },
                success: function (response) {
                }
            });
        }
    });
    $("#class_list li .courseName").each( function () {
        $.classList.push($(this).text());
    });
    calendar = $('#calendar').fullCalendar({
        selectable: true,
        select: function(start, end, allDay) {
                    if (step == 1) {
                        var title = prompt('Event Title:');
                        if (title) {
                            calendar.fullCalendar('renderEvent',
                                {
                                    id: id,
                                    title: title,
                                    start: start,
                                    end: end,
                                    allDay: allDay,
                                    backgroundColor: "#1a9206",
                                    info: "PE"
                                },
                                true
                            );
                            $.ajax({
                                url: 'ajax/addpe',
                                type: "POST",
                                data: { 'id':id, 'title':title, 'start':start, 'end':end, 'info': 'PE' },
                                async: false
                            });
                            id = id + 1;
                        }
                        calendar.fullCalendar('unselect');
                    }
                    else {
                        calendar.fullCalendar('unselect');
                    }
                },
        eventRender: function(event, element) {
                        if (event.info == "PE") {
                            var remove = "<a class='removeLink' onclick=\"removePe('" + event.id + "');\">Remove</a>";
                            element.qtip({
                                content: event.info + ": " + event.title + "<br/>" + remove,
                                position: {
                                    corner: {
                                        target: 'bottomMiddle',
                                        tooltip: 'topMiddle'
                                    }
                                },
                                hide : {
                                    fixed:true
                                },
                                style: {
                                    tip:true,
                                    'text-align':'center',
                                    'font-size':'12px',
                                    color: 'white',
                                    border: {
                                     width: 2,
                                     radius: 3
                                    },
                                    padding: 3, 
                                    name:'dark'
                                }
                            });
                        }
                        else {
                            var remove = "<a class='removeLink' onclick=\"removeClassFromSched('" + event.id + "', '" + event.info + "');\">Remove</a>";
                            element.qtip({
                                content: event.info + ": " + event.title + "<br/>" + remove,
                                position: {
                                    corner: {
                                        target: 'bottomMiddle',
                                        tooltip: 'topMiddle'
                                    }
                                },
                                hide : {
                                    fixed:true
                                },
                                style: {
                                    tip:true,
                                    'text-align':'center',
                                    'font-size':'12px',
                                    color: 'white',
                                    border: {
                                     width: 2,
                                     radius: 3
                                    },
                                    padding: 3, 
                                    name:'dark'
                                }
                            });
                        }
                    }
    });
    $('.popbox').popbox();
})

function showClassInfo(callNum, name) {
    $.get('ajax/getsinglecourse/'+callNum+'/'+name,
        function (response) {
            if (!smallCal) {
                height = parseInt($("#calendar").css("height"), 10);
                $("#calendar").css("height", height - 230 + "px");
                $("#calendar").css("overflow-y", "scroll");
                $("#calendar").css("overflow-x", "hidden");
                $("#rightHolder").append('<div id="courseInfoOutter"></div>');
                $("#courseInfoOutter").css("height", "200px");
                $("#courseInfoOutter").append('<div id="courseInfoContent"></div>');
                $("#courseInfoContent").css("height", "195px");
                $("#courseInfoContent").css("width", parseInt($("#courseInfoContent").css("width"), 10) - 5 + "px");
                $("#courseInfoContent").append("<button id='backButton' onClick='goBack()'>Back</button>");
                smallCal = true;
            }
            $("#courseInfoContent h3").remove();
            $("#courseInfoContent table").remove();
            courses = $.parseJSON(response);
            $("#courseInfoContent").append("<h3 id='classTitle'>" + courses[0].fields.courseNumber + " - " + courses[0].fields.name + "</h3>");
            tableText = "<table id='classTable'><tr><th>Teacher</th><th>Status</th><th>Location</th><th>Days</th><th>Times</th><th>Call Num</th></tr>";
            for (index in courses) {
                course = courses[index].fields;
                if (course.closed == "true") status = "Closed";
                else status = "Open";
                course.days = course.days.replace("~", "<br />");
                course.times = course.times.replace("~", "<br />");
                tableText += "<tr><td>" + course.professor + "</td><td>" + status + "</td><td>"
                                                + course.locations + "</td><td>" + course.days + "</td><td>" + course.times
                                                + "</td><td>" + course.callNumber + "</td><td><input type=\"button\" onClick='addClass(\"" + course.callNumber + "\")' value=\"Add Class\" class=\"classInfoButton\" /></td></tr>";
            }
            tableText += "</table>";
            $("#courseInfoContent").append(tableText);
        });
}

function searchClasses() {
    search = $("#classSearch").val();
    $.ajax({
        url: 'ajax/searchclasses/',
        data: { 'search':search },
        type: "POST",
        success: function (response) {
                    courses = $.parseJSON(response);
                    $("#classesList li").remove();
                    classes = new Array();
                    for (i in courses) {
                        tempName = courses[i].fields.courseNumber + " - " + courses[i].fields.name;
                        if (classes.indexOf(tempName) == -1) {
                            classes.push(tempName);
                            text = '<li onClick="showClassInfo(\'' + courses[i].fields.courseNumber + '\', \'' + courses[i].fields.name + '\')">' + courses[i].fields.courseNumber + " - " + courses[i].fields.name + "</li>";
                            $("#classesList").append(text);
                        }
                    }
                }
    });
}

function goBack() {
    height = parseInt($("#calendar").css("height"), 10);
    $("#calendar").css("height", (height + 230) + "px");
    $("#calendar").css("overflow-y", "none");
    $("#calendar").css("overflow-x", "none");
    $("#courseInfoOutter").remove();
    smallCal = false;
}

function isValidEmailAddress(emailAddress) {
    var pattern = new RegExp(/^((([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+(\.([a-z]|\d|[!#\$%&'\*\+\-\/=\?\^_`{\|}~]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])+)*)|((\x22)((((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(([\x01-\x08\x0b\x0c\x0e-\x1f\x7f]|\x21|[\x23-\x5b]|[\x5d-\x7e]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(\\([\x01-\x09\x0b\x0c\x0d-\x7f]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF]))))*(((\x20|\x09)*(\x0d\x0a))?(\x20|\x09)+)?(\x22)))@((([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|\d|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.)+(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])|(([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])([a-z]|\d|-|\.|_|~|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])*([a-z]|[\u00A0-\uD7FF\uF900-\uFDCF\uFDF0-\uFFEF])))\.?$/i);
    return pattern.test(emailAddress);
};

function register() {
    $(".regError").css("display", "none");
    username = $("#username").val();
    email = $("#email").val();
    pass1 = $("#pass1").val();
    pass2 = $("#pass2").val();
    regUser = true;
    if (username == "") {
        $("#blankUserError").css("display", "inline");
        regUser = false;
    }
    if (email == "") {
        $("#blankEmailError").css("display", "inline");
        regUser = false;
    }
    if (email != "" && !isValidEmailAddress(email)) {
        $("#validEmailError").css("display", "inline");
        regUser = false;
    }
    if (pass1 == "") {
        $("#blankPassError").css("display", "inline");
        regUser = false;
    }
    if (pass1 != "" && pass1 != pass2) {
        $("#passError").css("display", "inline");
        regUser = false;
    }
    $.ajax({
        url: 'ajax/checkuser/'+username,
        async: false,
        success: function (response) {
                    if (response == "True") {
                        $("#userError").css("display", "inline");
                        regUser = false;
                    }
                    else {
                        regUser = true && regUser;
                    }
                }
    });
    if (regUser) {
        $.ajax({
            url: 'ajax/checkemail/'+email,
            async: false,
            success: function (response) {
                        if (response == "True") {
                            $("#emailError").css("display", "inline");
                            regUser = false;
                        }
                        else {
                            regUser = true && regUser;
                        }
                    }
        });
    }
    if (regUser) {
        $.ajax({
            url: 'ajax/reguser',
            data: { 'email':email, 'username':username, 'pass1': pass1, 'pass2':pass2 },
            type: "POST",
            async: false,
            success: function (response) {
                        if (response == "Success") {
                            $("#regForm").css("display", "none");
                            $("#regSuccess").css("display", "inline");
                        }
                        else {
                            alert("We are sorry there was an error registering your account. Please refresh and try again");
                        }
                    }
        });
    }
}

function login() {
    $(".regError").css("display", "none");
    username = $("#loginUser").val();
    pass = $("#loginPass").val();
    $.ajax({
        url: 'ajax/login',
        data: { 'username':username, 'pass':pass },
        type: "POST",
        success: function (response) {
                    if (response == "Success") {
                        location.reload()
                    }
                    else {
                        $("#loginError").css("display", "inline");
                    }
                }
    });
}

function addClass(callNum) {
    $.ajax({
            url: 'ajax/addclassestosched/',
            data: {'courseNum':callNum},
            type: "POST",
            success: function (r) {
                if (r == "Success") {
                    $.get('ajax/getsingleclass/'+callNum,
                        function (response) {
                            classes = $.parseJSON(response);
                            console.log(classes);
                            days = classes[0].fields.days;
                            fields = classes[0].fields;
                            tilde = false;
                            for (i = 0; i < days.length; i++) {
                                day = days.substring(i, i + 1);
                                if (day == "~") {
                                    tilde = true;
                                    continue;
                                }
                                if (day == "M") day = 12;
                                if (day == "T") day = 13;
                                if (day == "W") day = 14;
                                if (day == "R") day = 15;
                                if (day == "F") day = 16;
                                if (!tilde) {
                                    startHour = fields.times.substring(0, 2);
                                    startMinute = fields.times.substring(2, 4);
                                    ampm = fields.times.substring(4, 6);
                                    if (ampm == "PM" && startHour != "12")
                                        startHour = parseInt(startHour) + 12;
                                    endHour = fields.times.substring(7, 9);
                                    endMinute = fields.times.substring(9, 11);
                                    ampm = fields.times.substring(11, 13);
                                    if (ampm == "PM" && endHour != "12")
                                        endHour = parseInt(endHour) + 12;
                                }
                                else {
                                    startHour = fields.times.substring(14, 16);
                                    startMinute = fields.times.substring(16, 18);
                                    ampm = fields.times.substring(18, 20);
                                    if (ampm == "PM" && startHour != "12")
                                        startHour = parseInt(startHour) + 12;
                                    endHour = fields.times.substring(21, 23);
                                    endMinute = fields.times.substring(23, 25);
                                    ampm = fields.times.substring(25, 27);
                                    if (ampm == "PM" && endHour != "12")
                                        endHour = parseInt(endHour) + 12;
                                }
                                $("#calendar").fullCalendar('renderEvent', {
                                    id: fields.courseNumber,
                                    info: fields.callNumber,
                                    title: fields.name + " - " + fields.callNumber,
                                    start: new Date(2011, 8, day, startHour, startMinute),
                                    end: new Date(2011, 8, day, endHour, endMinute)}, true);
                            }
                        });
                }
            }
        });
}

function removePe(id) {
    $('#calendar').fullCalendar('removeEvents', id);
    console.log(id);
    $.ajax({
        url: 'ajax/removepe',
        data: { 'id':id },
        type: "POST"
    });
}

function removeClassFromSched(id, callNum) {
    $('#calendar').fullCalendar('removeEvents', id);
    $.ajax({
        url: 'ajax/removeclassfromsched/',
        data: { 'callNum':callNum },
        type: "POST",
        success: function (r) {
            console.log(r);
        }
    });
}

function removeClass(course) {
    $.ajax({
        url: 'ajax/removeclass',
        data: { 'class':course },
        type: "POST",
        success: function (response) {
            if (response == "Success") {
                index = $.classList.indexOf(course);
                $.classList.splice(index, 1);
                $("#class_list").text("");
                $.classList.forEach(function (value) {
                    $("#class_list").append("<li><span class=\"courseName\">" + value + "</span><span class='classRemove'><a onClick=\"removeClass('" + value + "')\">X</a></span></li>")
                });
                $("#class_list_pref").text("");
                $.classList.forEach(function (value) {
                    $("#class_list_pref").append("<li><span class=\"courseName\"><a onClick=\"showPrefPopup()\">" + value + "</a></span></li>")
                });
            }
        }
    })
}

function setPrefPopup() {
    $.ajax({
        url: 'ajax/getclassinfo',
        type: "GET",
        success: function (response) {
            if (response == "Failed") {
               //alert("Something went wrong. Please reload the page and try again");
            }
            else {
                classList = $.parseJSON(response);
                $('#popUpContent').text("")
                table = "<table id='popUpTable'>";
                $.each(classList, function (index, elem) {
                    row = "<tr><td class='classNamePopUp' rowspan='" + elem.profs.length + "'>" + elem.name + "</td>"
                    row += "<td id='classProfPopUp'>" + elem.profs[0];
                    row += "<select id='" + elem.num + "' class='profPrefSelect' info='" + elem.profs[0] + "'>";
                    row += "<option value='want'>Want</option>";
                    row += "<option value='none' selected>Don't Care</option>";
                    row += "<option value='avoid'>Avoid</option>";
                    row += "</select></td></tr>"
                    $.each(elem.profs, function (i, e) {
                        if (i != 0) {
                            row += "<tr><td>" + e;
                            row += "<select id='" + elem.num + "' class='profPrefSelect' info='" + e + "'>";
                            row += "<option value='want'>Want</option>";
                            row += "<option value='none' selected>Don't Care</option>";
                            row += "<option value='avoid'>Avoid</option>";
                            row += "</select></td></tr>"
                        }
                    });
                    row += "</td></tr>";
                    table += row
                });
                table += "</table>";
                $('#popUpContent').append(table);
            }
        }
    });
}

function showPrefPopup() {
    prefs = "none"
    $.ajax({
        url: 'ajax/getprefs',
        type: "GET",
        async: false,
        success: function (response) {
            if (response != "None") {
                prefs = $.parseJSON(response)
            }
        }
    });
    $.ajax({
        url: 'ajax/getclassinfo',
        type: "GET",
        success: function (response) {
            if (response == "Failed") {
                alert("Something went wrong. Please reload the page and try again");
            }
            else {
                classList = $.parseJSON(response);
                $('#popUpContent').text("")
                table = "<table id='popUpTable'>";
                $.each(classList, function (index, elem) {
                    row = "<tr><td class='classNamePopUp' rowspan='" + elem.profs.length + "'>" + elem.name + "</td>"
                    row += "<td id='classProfPopUp'>" + elem.profs[0];
                    row += "<select id='" + elem.num + "' class='profPrefSelect' info='" + elem.profs[0] + "' onChange='savePref()'>";
                    if (prefs == "none" || prefs["profPrefs"][elem.num] == undefined) {
                        row += "<option value='want'>Want</option>";
                        row += "<option value='none' selected>Don't Care</option>";
                        row += "<option value='avoid'>Avoid</option>";
                    }
                    else {
                        console.log(elem.num)
                        console.log(prefs["profPrefs"])
                        if (prefs["profPrefs"][elem.num][elem.profs[0]] == "want")
                            row += "<option value='want' selected>Want</option>";
                        else
                            row += "<option value='want'>Want</option>";
                        if (prefs["profPrefs"][elem.num][elem.profs[0]] == "none")
                            row += "<option value='none' selected>Don't Care</option>";
                        else
                            row += "<option value='none'>Don't Care</option>";
                        if (prefs["profPrefs"][elem.num][elem.profs[0]] == "avoid")
                            row += "<option value='avoid' selected>Avoid</option>";
                        else
                            row += "<option value='avoid'>Avoid</option>";
                    }
                    row += "</select></td></tr>"
                    $.each(elem.profs, function (i, e) {
                        if (i != 0) {
                            row += "<tr><td>" + e;
                            row += "<select id='" + elem.num + "' class='profPrefSelect' info='" + e + "' onChange='savePref()'>";
                            if (prefs == "none") {
                                console.log("no")
                                row += "<option value='want'>Want</option>";
                                row += "<option value='none' selected>Don't Care</option>";
                                row += "<option value='avoid'>Avoid</option>";
                            }
                            else {
                                if (prefs["profPrefs"][elem.num][e] == "want")
                                    row += "<option value='want' selected>Want</option>";
                                else
                                    row += "<option value='want'>Want</option>";
                                if (prefs["profPrefs"][elem.num][e] == "none")
                                    row += "<option value='none' selected>Don't Care</option>";
                                else
                                    row += "<option value='none'>Don't Care</option>";
                                if (prefs["profPrefs"][elem.num][e] == "avoid")
                                    row += "<option value='avoid' selected>Avoid</option>";
                                else
                                    row += "<option value='avoid'>Avoid</option>";
                            }
                            row += "</select></td></tr>"
                        }
                    });
                    row += "</td></tr>";
                    table += row
                });
                table += "</table>";
                $('#popUpContent').append(table);
                popup('popUpDiv');
            }
        }
    });
}

function savePref() {
    monPref = $('#monPref').is(':checked')
    tuesPref = $('#tuesPref').is(':checked')
    wednPref = $('#wednPref').is(':checked')
    thursPref = $('#thursPref').is(':checked')
    friPref = $('#friPref').is(':checked')
    beforePref = $('#beforePref').is(':checked')
    afterPref = $('#afterPref').is(':checked')
    betweenPref = $('#betweenPref').is(':checked')
    beforeTime = $('#beforeSelect').val()
    afterTime = $('#afterSelect').val()
    betweenStartTime = $('#betweenStartSelect').val()
    betweenEndTime = $('#betweenEndSelect').val()
    profPrefs = {}
    $('.profPrefSelect').each(function () {
        id = $(this).attr("id");
        info = $(this).attr("info");
        if (!(id in profPrefs))
            profPrefs[id] = {}
        profPrefs[id][info] = $(this).val()
    });
    data = { 'monPref':monPref, 'tuesPref':tuesPref, 'wednPref':wednPref, 'thursPref':thursPref, 'friPref':friPref, 'beforePref':beforePref, 'afterPref':afterPref, 'betweenPref':betweenPref, 'beforeTime':beforeTime, 'afterTime':afterTime, 'betweenStartTime':betweenStartTime, 'betweenEndTime':betweenEndTime, 'profPrefs':profPrefs };
    console.log(data);
    $.ajax({
        url: 'ajax/setprefs',
        data: data,
        type: "POST"
    });
}

function tabChange(id) {
    num = id.substring(4);
    $("#selectSchedButton").attr("onClick","selectSchedule(" + num + ")");
    $(".active").removeClass("active");
    $("#" + id).addClass("active");
    $(".content").slideUp();
    var content_show = $("#" + id).attr("title");
    $("#"+content_show).slideDown();
}

function selectSchedule (scheduleNum) {
    sched = schedulesArray[scheduleNum - 1];
    popup('schedulePopupDiv');
    $.ajax({
        url: 'ajax/getpersevents',
        type: "GET",
        success: function (r) {
            events = $.parseJSON(r);
            savedCourses = "";
            savedCoursesArray = new Array();
            for (eventId in sched) {
                if (savedCourses == "") {
                    savedCourses += sched[eventId]['callNum'];
                    savedCoursesArray.push(sched[eventId]['callNum']);
                }
                else {
                    if (savedCoursesArray.indexOf(sched[eventId]['callNum']) == -1) {
                        savedCoursesArray.push(sched[eventId]['callNum']);
                        savedCourses += "/" + sched[eventId]['callNum'];
                    }
                }
                $("#calendar").fullCalendar('renderEvent', {
                    id: sched[eventId]['id'],
                    info: sched[eventId]['callNum'],
                    title: sched[eventId]['title'],
                    start: new Date(2011, 8, sched[eventId]['day'], sched[eventId]['startHour'], sched[eventId]['startMinute']),
                    end: new Date(2011, 8, sched[eventId]['day'], sched[eventId]['endHour'], sched[eventId]['endMinute'])}, true);
            }
            $.ajax({
                url: 'ajax/saveclasses/',
                type: "POST",
                data: {'courses':savedCourses},
                success: function (r) {
                    console.log(r);
                }
            });
            for (event in events) {
                $("#calendar").fullCalendar('renderEvent', {
                    id: events[event]['id'], 
                    title: events[event]['title'], 
                    start: new Date(2011, 8, events[event]['day'], events[event]['startHour'], events[event]['startMinute']), 
                    end: new Date(2011, 8, events[event]['day'], events[event]['endHour'], events[event]['endMinute']),
                    backgroundColor: "#1a9206",
                    info: "PE"}, true);
            }
        }
    });
}

schedulesArray = new Array();

function create() {
    if (!creatingSched) {
        creatingSched = true;
        $.ajax({
            url: 'ajax/courses',
            type: "GET",
            async: false,
            success: function (response) {
                schedules = $.parseJSON(response);
                $("#calendar").fullCalendar('removeEvents');
                $.ajax({
                    url: 'ajax/getpersevents',
                    type: "GET",
                    async: false,
                    success: function (r) {
                        $("#tabList li").remove();
                        $("#contentList div").remove();
                        events = $.parseJSON(r);
                        $("#selectSchedButton").remove();
                        button = '<input type="button" id="selectSchedButton" onClick="selectSchedule(1)" value="Select Schedule" />';
                        $("#schedulePopupContent").prepend(button);
                        if (schedules.length == 2) {
                            alert("We only found 1 schedule and there are " + schedules[0]["conflict"] + " conflicts")
                            for (event in events) {
                                $("#calendar").fullCalendar('renderEvent', {
                                    id: events[event]['id'], 
                                    title: events[event]['title'], 
                                    start: new Date(2011, 8, events[event]['day'], events[event]['startHour'], events[event]['startMinute']), 
                                    end: new Date(2011, 8, events[event]['day'], events[event]['endHour'], events[event]['endMinute']),
                                    backgroundColor: "#1a9206",
                                    info: "PE"}, true);
                            }
                            savedCourses = "";
                            savedCoursesArray = new Array();
                            for (arrangement in schedules[1]) {
                                for (cls in schedules[1][arrangement]) {
                                    event = schedules[1][arrangement][cls]
                                    if (savedCourses == "") {
                                        savedCourses += event.callNum;
                                        savedCoursesArray.push(event.callNum);
                                    }
                                    else {
                                        if (savedCoursesArray.indexOf(event.callNum) == -1) {
                                            savedCoursesArray.push(event.callNum);
                                            savedCourses += "/" + event.callNum;
                                        }
                                    }
                                    $("#calendar").fullCalendar('renderEvent', {
                                        id:event.id, 
                                        info: event.callNum,
                                        title:event.title, 
                                        start:new Date(2011,8,event.day,event.startHour,event.startMinute), 
                                        end:new Date(2011,8,event.day,event.endHour,event.endMinute)},true)
                                }
                            }
                            $.ajax({
                                url: 'ajax/saveclasses/',
                                type: "POST",
                                data: {'courses':savedCourses},
                                success: function (r) {
                                    console.log(r);
                                }
                            });
                        }
                        else if (schedules.length > 2) {
                            alert("We found " + (schedules.length - 1) + " schedules and there are " + schedules[0]["conflict"] + " conflicts")
                            for (i = 1; i < schedules.length; i++) {
                                if (i == 1) {
                                    tab = '<li><a href="#" onClick="tabChange(\'tab_1\')" id="tab_1" title="content_1" class="tab active">Schedule 1</a></li>'
                                    content = '<div id="content_1" class="content"><div id="schedCalendar1"></div></div>'
                                }
                                else {
                                    tab = '<li><a href="#" onClick="tabChange(\'tab_' + i + '\')" id="tab_' + i + '" title="content_' + i + '" class="tab">Schedule ' + i + '</a></li>'
                                    content = '<div id="content_' + i + '" class="content"><div id="schedCalendar' + i +'"></div></div>'
                                }
                                $("#tabList").append(tab)
                                $("#contentList").append(content)
                            }
                            popup('schedulePopupDiv');
                            showCalendars(schedules.length);
                            schedulesArray = new Array();
                            for (i = 1; i < schedules.length; i++) {
                                for (arrangement in schedules[i]) {
                                    tempSched = new Array();
                                    for (cls in schedules[i][arrangement]) {
                                        tempSched.push(schedules[i][arrangement][cls]);
                                        event = schedules[i][arrangement][cls];
                                        $("#schedCalendar" + i).fullCalendar('renderEvent', {id:event.id, title:event.title, start:new Date(2011,8,event.day,event.startHour,event.startMinute), end:new Date(2011,8,event.day,event.endHour,event.endMinute)},true)
                                    }
                                    schedulesArray.push(tempSched);
                                }
                                for (event in events) {
                                    $("#schedCalendar" + i).fullCalendar('renderEvent', {
                                        id: events[event]['id'], 
                                        title: events[event]['title'], 
                                        start: new Date(2011, 8, events[event]['day'], events[event]['startHour'], events[event]['startMinute']), 
                                        end: new Date(2011, 8, events[event]['day'], events[event]['endHour'], events[event]['endMinute']),
                                        backgroundColor: "#1a9206",
                                        info: "PE"}, true);
                                }
                            }
                        }
                    }
                });
                creatingSched = false;
            }
        });
    }
}

function showCalendars(num) {
    for (i = 1; i < num; i++) {
        tabChange('tab_' + i)
        $('#schedCalendar' + i).fullCalendar({})
    }
    tabChange('tab_1')
}

function slideTabs(stepNum) {
    $('#addClasses').slideUp();
    $('#persEvent').slideUp();
    $('#prefs').slideUp();
    $('#addClassesToSched').slideUp();
    if (stepNum != step) {
        if (stepNum == 1)
            $('#persEvent').slideDown();
        if (stepNum == 2)
            $('#addClasses').slideDown();
        if (stepNum == 3)
            $('#prefs').slideDown();
        if (stepNum == 5)
            $('#addClassesToSched').slideDown();
        step = stepNum;
    }
    else {
        step = 0;
    }
}

function printSched() {
    window.open("/printsched", "_blank");
}