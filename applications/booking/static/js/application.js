//used to temporarily assign event id so that it can be used to keep the border 
//colored after the update button is clicked and page is loaded.
var current_type = 'all';
var current_event_id;
var current_cal_event;
var calender_div;
var AFFILIATE_BBN = 'obs-bris.appspot.com'
var AFFILIATE_MP = 'obs-mpfrankston.appspot.com'
//var AFFILIATE_MP = 'mopdevapp.appspot.com'
var AFFILIATE_MELB = 'dfsdevapp.appspot.com'
//var AFFILIATE_SYD = 'syddevapp1.appspot.com'
var AFFILIATE_SYD = 'dfs-syd.appspot.com'
var AFFILIATE_AUCK = 'auktestapp.appspot.com'

function deactivateConfirmation(event) {
    
    if (!confirm("Are you sure you want to deactivate this?")) {
        event.preventDefault();
    }
}
function activateConfirmation(event) {
    
    if (!confirm("Are you sure you want to activate this?")) {
        event.preventDefault();
    }
}
function addDeactivateLinkConfirmation(jqObj) {
    try {
        
        jqObj.find('a.deactivate').click(function(event) {
            deactivateConfirmation(event);
        });
    } catch (err) {}
}
function addDeactivateSubmitConfirmation(jqObj) {
    try {
        
        jqObj.find('input.deactivate').click(function(event) {
            deactivateConfirmation(event);
        });
    } catch (err) {}
}
function addDeactivateClassConfirmation(jqObj) {
    try {
        jqObj.find('.deactivate').click(function(event) {
            deactivateConfirmation(event);
        });
    } catch (err) {}
}
function addActivateClassConfirmation(jqObj) {
    try {
        jqObj.find('.activate').click(function(event) {
            activateConfirmation(event);
        });
    } catch (err) {}
}
function addFormConfirmation(parent) {
    var el = parent.find('tr.submitrow input[type="submit"]');
    addFormConfirmationToEl(el);
}
function addFormConfirmationToEl(el) {
    el.click(function(event) {
        if (!confirm("Please confirm you would like to submit the form.")) {
            event.preventDefault();
        }
    });
}
function addRegistrationConfirmation(parent,url) {  
    var submitb = parent.find('input[type="submit"]');
    submitb.click(function (event) {
        var value = $(this).attr('value');
        var message;
        var url_string = url;
        if (url_string == AFFILIATE_BBN )
            {
            if (value.toLowerCase().indexOf('unregister') != -1 ) {
                message = 'Please notify us immediately by phone on 07 3216 1969 regarding the unregistration of this client or volunteer.';
            } else {
                message = 'Please confirm you are aware of the 24 hour cancellation policy to proceed with the registration.';
            }
            }
        else if(url_string == AFFILIATE_MP)
            {
            if (value.toLowerCase().indexOf('unregister') != -1 ) {
                message = 'Please notify us immediately by phone regarding the unregistration of this client or volunteer.';
            } else {
                message = 'Please confirm you are aware of the 24 hour cancellation policy to proceed with the registration.';
            }
            }
        else if(url_string == AFFILIATE_SYD)
            {
            if (value.toLowerCase().indexOf('unregister') != -1 ) {
                message = 'Please notify us immediately by phone on 1800 773 456 regarding the unregistration of this client or volunteer.';
            } else {
                message = 'Please confirm you are aware of the 24 hour cancellation policy to proceed with the registration.';
            }
            }
        else if(url_string == AFFILIATE_MELB)
            {
            if (value.toLowerCase().indexOf('unregister') != -1 ) {
                message = 'Please notify us immediately by phone on 03 9078 1750 regarding the unregistration of this client or volunteer.';
            } else {
                message = 'Please confirm you are aware of the 24 hour cancellation policy to proceed with the registration.';
            }
            }
		else if(url_string == AFFILIATE_AUCK)
            {
            if (value.toLowerCase().indexOf('unregister') != -1 ) {
                message = 'Please confirm the unregistration of this client or volunteer from the event.';
            } else {
                message = 'Please confirm you are aware of the 24 hour cancellation policy to proceed with the registration.';
            }
            }
        else
            {
                if (value.toLowerCase().indexOf('unregister') != -1 ) {
                message = 'Please notify us immediately by phone regarding the unregistration of this client or volunteer.';
            } else {
                message = 'Please confirm you are aware of the 24 hour cancellation policy to proceed with the registration.';
            }
            }
        if (!confirm(message)) {
            event.preventDefault();
        }
    });
}
function addTableSorter() {
    $('.tablesorter').tablesorter();
}
function copyParamsToURL (url, params) {
    for(var i=params.length-1; i>=0; i--) {
        var name = params[i];
        var value = getParameterByName(name);
        if (value.length > 0) {
            addParamToURL(url, name, value);
        }
    }
    return url;
}

function addParamToURL(url, name, value) {
    if (url.indexOf('?')<0) {
        url = url + '?' + name + '=' + value;
    }
    else {
        url = url + '&' + name + '=' + value;
    }
    return url
}

function disableFormFields(el) {
    el.find('input, textarea, button, select').attr('disabled', true);
}

function enableFormFields(div) {
    div.find('input, textarea, button, select').attr('disabled', false);
    showElement(div);
}

function showElement(el) {
    el.slideDown();
}

function hideElement(el) {
    el.slideUp();
}

function focusEl(el) {
    $('html, body').animate({ scrollTop: (el.offset().top - 350) }, 500);
}

function addDateTimePicker(jqObj) {
    jqObj.datetimepicker();
}


function getParameterByName(name)
{
    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regexS = "[\\?&]" + name + "=([^&#]*)";
    var regex = new RegExp(regexS);
    var results = regex.exec(window.location.href);
    if(results == null)
        return "";
    else
        return decodeURIComponent(results[1].replace(/\+/g, " "));
}

function ConvertRowsToLinks(xTableId)
{
    try {
        var rows = document.getElementById(xTableId).getElementsByTagName("tr");
       
        for(i=0;i<rows.length;i++){
            var link = rows[i].getElementsByTagName("a")
            if (link.length==1) {
                rows[i].onclick = new Function("document.location.href='" + link[0].href + "'");
            }
        }
    } catch(err) {}
}

function go_to(url) {
    document.location.href=url;
}




/*  Events  */

function fetchEvent(id) {
    var url = addParamToURL(update_url, 'event', id);
    var jqxhr = $.get(url, function(data) {
        addEventToDOM(data);
    });
    jqxhr.error(function() { 
        $('#current_event_content').html(jqxhr.responseText);
    });
}


function displayEvents(current, create) {
    currentdiv = $('#current_event_content');
    creatediv = $('#new_event_content');
    if (current) {
        showElement(currentdiv);
    } else {
        hideElement(currentdiv);
    }
    if (create) {
        showElement(creatediv);
    } else {
        hideElement(creatediv);
    }
}

function addEventToDOM(eventHtmlStr) {
    var jqObj = jQuery(eventHtmlStr);
    var event_div = $('#current_event_content');
    
    try {
        addDeactivateClassConfirmation(jqObj);
        attachEventSubmitHandler(jqObj.find('form').first());
    } catch(err) {}
    event_div.html(jqObj);
}

function submitUpdateFormAjax(form) {
    var url = form.attr('action');
    $.post( url, form.serialize(), function( data ) {
        if (data.indexOf('invalid') == -1) {
            refetchCalendar();
        }
        addEventToDOM(data);
    });
}

function attachEventSubmitHandler(xform) {
    xform.submit(function(event) {
        //stop form from submitting normally
        event.preventDefault();
        var form = $( this );
        submitUpdateFormAjax(form);
    });
}

function onEventCreated(id) {
    refetchCalendar();
    onEventClicked(id);
}
function onEventClicked(id) {
    displayEvents(true, false); //TODO only slide/show if not showing
    fetchEvent(id);
}

function refetchCalendar() {
    calender_div.fullCalendar('refetchEvents');
}
function rerenderCalendar() {
    calender_div.fullCalendar('rerenderEvents');
}

function customAfterRender(event, element, view) {
    //var titleHtml = element.find('.fc-event-title');
    var check = '<strong style="line-height:50%;height:5px;background-color:white;color:#008A00;">&#x2713;</strong>&nbsp;';
    
    
    if (event.is_full=='True') {
        color = 'grey';
        element.css('border-color', color);
        element.find('.fc-event-time').css('background-color', color);
        element.children().css('background-color', color);
        element.children().css('border-color', color);
    }
    
    if (event.id==current_event_id) {
        current_cal_event = event; //store again in case it was updated so that updateEventRegistration has the latest
        element.css('border', '3px solid green');
    }
    
    
    //remove the time and replace it with the title (in order for the title to have the darker background color)
    timeEl = element.find('.fc-event-time');
    
    var is_registered = event.is_registered;
    if (is_registered=='True') {
        if (event.remaining_slots == 'None'){
        timeEl.html(check + " " +event.slots + " " +event.title);
        }
        else {
        timeEl.html(check + " " +event.remaining_slots + " " +event.title);
        }
        //current_cal_event.val();
    } else {
        if (event.remaining_slots == 'None')
            {
            timeEl.html(" " +event.slots + " " +event.title);
            }
        else
            {
            timeEl.html(" " +event.remaining_slots + " " +event.title);
            }
        
        //timeEl.html(event.title);
    }   
    
    //replace the title with the description for agendaWeek or agendaDay. Just remove the old title for month 
    var contentEl = element.find('.fc-event-content');
    var view = calender_div.fullCalendar('getView');
    if (view.name!='month') {
        contentEl.html("<div class='fc-event-description'>" + htmlEscapeLocal(event.description) + "</div>");
    } else {
        element.find('.fc-event-title').remove();
    }
    
    //In case the event is very small, make it a bit taller and remove the description
    var height = parseInt(element.css('height').replace('px',''));
    if (height<16) {
        element.css('height','15px');
        contentEl.hide();
        element.find('.fc-event-bg').hide();
    }
}


function initCalendar(json_url) {
    
    try {
        calender_div = $('#calendar');
        calender_div.fullCalendar({
            editable: false,
            allDayDefault: false,
            allDaySlot: false,
            aspectRatio: 2,
            defaultView: 'agendaDay',
            minTime: 9,
            maxTime: 24,
            header: {
                left: 'prev,next today',
                center: 'title',
                right: 'month,agendaWeek,agendaDay'
            },
            eventClick: function(calEvent, jsEvent, view) {
                $('#reg_in_event').remove();
                
                if (current_cal_event) {
                    //rerender the border back to unselected
                    current_event_id = '';
                    calender_div.fullCalendar('updateEvent', current_cal_event);
                }
                
                current_cal_event = calEvent;
                current_event_id = calEvent.id;
                calender_div.fullCalendar('updateEvent', current_cal_event); //highlight as selected
                
                onEventClicked(calEvent.id); //Fetch
                                       
            },
            eventAfterRender: customAfterRender,
            eventRender: function(event, element) {
                if (current_type!='all' && event.type!=current_type) {
                    return false;
                }                   
        },
            events: json_url
        });
    } catch(err) {}
    //current_calendar_source = json_url; //save for removing later
}
function updateEventRegistration(is_registered, remaining_slots, is_full) {
    current_cal_event.is_full = is_full;
    current_cal_event.is_registered = is_registered;
    current_cal_event.remaining_slots = remaining_slots;
    calender_div.fullCalendar('updateEvent', current_cal_event);

}

function loadCreateForm(url) {
    web2py_component(url, 'new_event_content');
}

var hover_event_type_color = '';
var selected_event_type;
var selected_event_type_color;

function event_type_hover() {
    hover_event_type_color = $(this).css('background-color');
    $(this).css('background-color', darkerColor(hover_event_type_color, .2));
}
function event_type_hoverout() {
    if (hover_event_type_color) {
        $(this).css('background-color', hover_event_type_color);
    }
}
function select_create_event_type(type) {
    $('#new_event_content').find('select#events_type option:contains(' + type + ')').attr('selected', 'selected');
}
function event_type_click() {
    $(this).unbind('mouseenter mouseleave click');
    var prev_selected = $('#event_types_legend li.selected');
    prev_selected.removeClass('selected');
    prev_selected.addClass('clickable');
    prev_selected.hover(event_type_hover, event_type_hoverout);
    prev_selected.click(event_type_click);
    if (selected_event_type_color) {
        prev_selected.css('background-color', selected_event_type_color);
    }
    $(this).addClass('selected');
    $(this).removeClass('clickable');
    
    $('#current_event_content').html('Select an event');
    
    selected_event_type_color = hover_event_type_color;
    
    current_type = $(this).html();
    if (current_type!='all') {
        select_create_event_type(current_type);
        var full_list_url = addParamToURL(list_json_url, 'type', current_type);
    }
  
    
   rerenderCalendar();
    
}

function bind_event_type_events() {
  
    $('#event_types_legend li').not('.title').hover(event_type_hover, event_type_hoverout);
    $('#event_types_legend li').not('.title').click(event_type_click);
}



function onActivitiesTypeChange(select_val, no_show) {
    var checked = no_show.is(':checked');
    
    var items_div = $('#items_provided');
    var service_div = $('#services_provided');
    
    //var a_type_val = select.val();
    
    if (checked) {
        items_div.slideUp();
        service_div.slideUp();
    } else if (select_val=='Dressings') {
        items_div.slideDown();
        service_div.slideUp();
    } else if (select_val=='Resource Centre') {
        items_div.slideUp();
        service_div.slideDown();
    } else {
        items_div.slideUp();
        service_div.slideUp();
    }
    
}

function onActivitiesFormPageReady() {
    var a_type = $(document).find('select#activities_type');
    var no_show = $(document).find('#activities_is_no_show');
    var a_type_val;
    
    
    //See if the type is a dropdown (create/update form) or div (readonly view)
    if (a_type.length) {
        a_type_val = a_type.val(); 
        
        a_type.change(function() {
            var no_show = $(document).find('#activities_is_no_show');
            onActivitiesTypeChange($(this).val(), no_show);
        });
        
        no_show.change(function() {
            var a_type = $(document).find('#activities_type');
            onActivitiesTypeChange(a_type.val(), $(this));
        });
    }
    else {
        a_type = $(document).find('div#activities_type');
        a_type_val = a_type.html();
    }
    
    onActivitiesTypeChange(a_type_val, no_show); //initialize it when the page is loaded in case of existing activity update
}

function onActivitiesShowChecked()
{
    var no_show = $(document).find('#activities_is_no_show');
    var gender_div = $('#gender_time');
    var checked = no_show.is(':checked');
    if(checked)
        {
            gender_div.slideUp();
        }
    no_show.change(function() {
        
        var checked = no_show.is(':checked');
        var gender_div = $('#gender_time');
        if(checked)
            {
            gender_div.slideUp();
            }
        else
            {
            gender_div.slideDown();
            }
    });
}

function onOrganisationFormPageReady() {

    var a_type = $(document).find('select#organisations_organisations_types');

    var items_div = $('#referral_organisation');

    var service_div = $('#sponsor');



    a_type.change(function() {

            if ($(this).val()=='Referral Organisation') {

            items_div.slideDown();

            service_div.slideUp();

        }else if(a_type.val()=='Sponsor'){

            items_div.slideUp();

            service_div.slideDown();

        }else {

            items_div.slideUp();

            service_div.slideUp();

        } 

   });
}

function efDateCompareHandler(form)
{
    form.submit(function(event) {
        try{
            var ef_date = form.find("#effective_date").val();
            if (ef_date==null || ef_date=='')
            {
                return true;
            }
            var effect_date = isDate(ef_date);
            if ( effect_date==false)
            {
                form.find('#date_effect_error').show();
                event.preventDefault();
            }
        else
            {
                form.find('#date_effect_error').hide();
            }
        }
        catch (err) {}
    });
}


function addDateCompareHandler(form) {
    form.submit(function(event) {
        try {
            form = $(this);
            var start_date = form.find("#start_date").val();
            var end_date = form.find("#end_date").val();
            if ((start_date ==null ||start_date=='') &&(end_date ==null ||end_date==''))
                {
                    return true;
                }
            if (((start_date ==null ||start_date=='') &&(end_date !=null ||end_date!=''))||((start_date !=null ||start_date!='')&&(end_date ==null ||end_date=='')))
                {
                    if (isDate(start_date)==true || isDate(end_date)==true)
                    {
                        return true;
                    }
                    else
                    {
                        form.find('#date_effect_error').show();
                        event.preventDefault();
                    }
                }
            var sday = start_date.split('-');
            var eday = end_date.split('-');   
            var st_date = isDate(start_date);
            var en_date = isDate(end_date);
            if(navigator.appName=='Netscape')
            {
                var new_st = sday[2]+"/"+sday[1]+"/"+sday[0];
                var new_en = eday[2]+"/"+eday[1]+"/"+eday[0];
            }
            else
            {
                var new_st = sday[1]+"-"+sday[0]+"-"+sday[2];
                var new_en = eday[1]+"-"+eday[0]+"-"+eday[2];
            }
            var new_st_date = new Date(new_st);
            var new_en_date = new Date(new_en);
            if (st_date==true && en_date==true)
                {
                        var date_gl = new_st_date < new_en_date;
                        if (date_gl == false) {
                            form.find('#error').show();
                            event.preventDefault();                     
                        } else {
                            form.find('#error').hide();
                        }
                }
            else
                {
                    form.find('#date_effect_error').show();
                    event.preventDefault();
                
                }
        }
        catch (err) {}
    });
}

function addVolunteerDateCompareHandler(form) {
    form.submit(function(event) {
        try {
            form = $(this);
            var start_date = form.find("#start_date").val();
            var end_date = form.find("#end_date").val();
            if (((start_date == null||start_date =="") && end_date!="")||((end_date==null ||end_date=="")&& start_date !="" ))
            {
                form.find('#volunteer_act_error').show();
                event.preventDefault();
            }
            else {
                form.find('#volunteer_act_error').hide();

            }
        } 
        catch (err) {}
    });
}

function onClientsFormPageReady() {
    var gender = $(document).find("#auth_user_gender");
    gender.change(function () {
        onClientsGenderChange($(this));
    });
    onClientsGenderChange(gender); //initialize it when the page is loaded in case of existing client update
}
function onClientsGenderChange(gender_sel) {
    //var shoe_size.val='';
    shoe_size = $("#auth_user_shoe_size");
    clothing_size = $("#auth_user_clothing_size");
    
    if (!window.shoe_size_val) shoe_size_val = {log: function() {}};//added to eliminate undefined varibale error at the bottom of the page in IE
    if (!window.clothing_size_val) clothing_size_val = {log: function() {}};//added to eliminate undefined varibale error at the bottom of the page in IE
    //save the values only if they are set (may get unset when changing between Male and Female)
    if (shoe_size.val().length>0) {
        shoe_size_val = shoe_size.val();
    }
    if (clothing_size.val().length>0) {
        clothing_size_val = clothing_size.val();
    }
    if (shoe_size.val().length==0) {
        shoe_size_val = shoe_size.val();
    }
    switch(gender_sel.val())
    {
        case 'Male':
            shoe_size.html("<option value=''></option><option value='7.0'>7.0</option><option value='7.5'>7.5</option><option value='8.0'>8.0</option><option value='8.5'>8.5</option><option value='9.0'>9.0</option><option value='9.5'>9.5</option><option value='10.0'>10.0</option><option value='10.5'>10.5</option><option value='11.0'>11.0</option><option value='11.5'>11.5</option><option value='12.0'>12.0</option><option value='12.5'>12.5</option><option value='13.0'>13</option><option value='13+'>13+</option>");
            clothing_size.html("<option value=''></option><option value='XS'>XS</option><option value='S'>S</option><option value='M'>M</option><option value='L'>L</option><option value='XL'>XL</option><option value='2XL'>2XL</option><option value='3XL'>3XL</option><option value='4XL'>4XL</option><option value='4XL+'>4XL+</option>");
            break;
        case 'Female':
            shoe_size.html("<option value=''></option><option value='5.0'>5.0</option><option value='6.0'>6.0</option><option value='6.5'>6.5</option><option value='7.0'>7.0</option><option value='7.5'>7.5</option><option value='8.0'>8.0</option><option value='8.5'>8.5</option><option value='9.0'>9.0</option><option value='9.5'>9.5</option><option value='10.0'>10.0</option><option value='10.5'>10.5</option><option value='11.0'>11.0</option><option value='11.5'>11.5</option>");
            clothing_size.html("<option value=''></option><option value='6'>6</option><option value='8'>8</option><option value='10'>10</option><option value='12'>12</option><option value='14'>14</option><option value='16'>16</option><option value='18'>18</option><option value='20'>20</option><option value='22'>22</option><option value='24'>24</option><option value='26'>26</option><option value='28'>28</option>");
            break;
        default:
            shoe_size.html(full_shoe_size_options);
            clothing_size.html(full_clothing_size_options);
    }
    shoe_size.val(shoe_size_val);
    clothing_size.val(clothing_size_val);
}



/* The following code is for shading the event types in the legend darker and ligher */

var app_pad = function(num, totalChars) {
var xpad = '0';
num = num + '';
while (num.length < totalChars) {
    num = xpad + num;
}
return num;
};

//Ratio is between 0 and 1
var colorRatio = function(color, ratio, darker) {
// Trim trailing/leading whitespace
color = color.replace(/^\s*|\s*$/, '');

// Expand three-digit hex
color = color.replace(
    /^#?([a-f0-9])([a-f0-9])([a-f0-9])$/i,
    '#$1$1$2$2$3$3'
);

// Calculate ratio
var difference = Math.round(ratio * 256) * (darker ? -1 : 1),
    // Determine if input is RGB(A)
    rgb = color.match(new RegExp('^rgba?\\(\\s*' +
        '(\\d|[1-9]\\d|1\\d{2}|2[0-4][0-9]|25[0-5])' +
        '\\s*,\\s*' +
        '(\\d|[1-9]\\d|1\\d{2}|2[0-4][0-9]|25[0-5])' +
        '\\s*,\\s*' +
        '(\\d|[1-9]\\d|1\\d{2}|2[0-4][0-9]|25[0-5])' +
        '(?:\\s*,\\s*' +
        '(0|1|0?\\.\\d+))?' +
        '\\s*\\)$'
    , 'i')),
    alpha = !!rgb && rgb[4] != null ? rgb[4] : null,

    // Convert hex to decimal
    decimal = !!rgb? [rgb[1], rgb[2], rgb[3]] : color.replace(
        /^#?([a-f0-9][a-f0-9])([a-f0-9][a-f0-9])([a-f0-9][a-f0-9])/i,
        function() {
            return parseInt(arguments[1], 16) + ',' +
                parseInt(arguments[2], 16) + ',' +
                parseInt(arguments[3], 16);
        }
    ).split(/,/),
    returnValue;

// Return RGB(A)
return !!rgb ?
    'rgb' + (alpha !== null ? 'a' : '') + '(' +
        Math[darker ? 'max' : 'min'](
            parseInt(decimal[0], 10) + difference, darker ? 0 : 255
        ) + ', ' +
        Math[darker ? 'max' : 'min'](
            parseInt(decimal[1], 10) + difference, darker ? 0 : 255
        ) + ', ' +
        Math[darker ? 'max' : 'min'](
            parseInt(decimal[2], 10) + difference, darker ? 0 : 255
        ) +
        (alpha !== null ? ', ' + alpha : '') +
        ')' :
    // Return hex
    [
        '#',
        app_pad(Math[darker ? 'max' : 'min'](
            parseInt(decimal[0], 10) + difference, darker ? 0 : 255
        ).toString(16), 2),
        app_pad(Math[darker ? 'max' : 'min'](
            parseInt(decimal[1], 10) + difference, darker ? 0 : 255
        ).toString(16), 2),
        app_pad(Math[darker ? 'max' : 'min'](
            parseInt(decimal[2], 10) + difference, darker ? 0 : 255
        ).toString(16), 2)
    ].join('');
};
var lighterColor = function(color, ratio) {
return colorRatio(color, ratio, false);
};
var darkerColor = function(color, ratio) {
return colorRatio(color, ratio, true);
};

function htmlEscapeLocal(s) {
    return s.replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/'/g, '&#039;')
        .replace(/"/g, '&quot;')
        .replace(/\n/g, '<br />');
}

/* added for update popup for volunteer*/
function updateEventConfirmationToEl(el) {
    el.click(function(event) {
        var value = $(this).attr('value');
        if (value=='Submit')
        {
            if (!confirm("Please confirm you would like to submit the form.")) {
            event.preventDefault();}
        }
        if (value=='Update Event')
        {
            if (!confirm("Are you sure you want to update this event? If there is change in date and time, please notify all participants immediately.")) {
            event.preventDefault();
        }
        }
    });
}


/* added for deactivate popup for volunteer*/
function deactivateEventConfirmationToEl(el) {
    el.click(function(event) {
        if (!confirm("Are you sure you want to deactivate this event? If yes, please notify all participants immediately.")) {
            event.preventDefault();
        }
    });
}
function client_activities_report(){
	data = {
		gender : $("#gender option:selected").val(),
		start_date : $("#start_date").val(),
		end_date : $("#end_date").val(),
		
	}
    $.ajax({
		url: "/reports/client_activities", 
		type: 'POST',
		data : data,
		success: function(result){
			$("#task_response").html('The All Client Activities report mailed to the admin');
			$("#search").css("display","none");
		}
	});
}

/* Date validation 
*/
function isDate(sDate) {
       var re = /^\d{1,2}\-\d{1,2}\-\d{4}$/
       if (re.test(sDate)) {
          var dArr = sDate.split("-");
          if(navigator.appName=='Netscape')
           {
            var sd = dArr[2] + "/" + dArr[1] + "/" + dArr[0];       
           }
           else
           {
            var sd = dArr[1] + "-" + dArr[0] + "-" + dArr[2];
           }
          
          var d = new Date(sd);
          return ((d.getDate() == dArr[0]) && (d.getMonth() + 1 == dArr[1]) && (d.getFullYear() == dArr[2]));
       }
       else {
          return false;
       }
    }
jQuery('#exitPage').live('pagebeforecreate', function(){
    jQuery(document).empty();
    window.location.replace('/');
});
