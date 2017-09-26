$( "#missionName" ).autocomplete({
  source: getMissionNames,
  select: function( event, ui ) { addMission(ui.item.value);}
});

function loadSession() {
    //load mission if exists
    var queryDict = getQueryDict();

    if(queryDict['sessionId'] != null) {
        jQuery.get("sessions", queryDict, function (data, status, jqXHR) {
            var sessions = eval(data);
            if(sessions.length > 0) {
                var session = sessions[0]
                $('.editMissionsTitle').append(' Edit Session');
                $('#editMissionsHeader').children().append('Edit Session');
                $("#sessionHost").val(session.host);
                $("#sessionName").val(session.name);
                $("#sessionPlayers").val(session.players);
                $("#sessionDate").val(session.date);
                var contents = $.render.sessionMissionTmpl(session.missionNamesList.map(function(item){return {missionName:item};}));
                $("#missionList").html(contents);
            }
        });
    }else {

                $('.editMissionsTitle').append(' Add Session');
                $('#editMissionsHeader').children().append('Add Session');
    }
}
function getMissionNames(request, response) {
    var params = {};
    params['name'] = request.term;
    jQuery.get("missions", params, function(data, status, jqXHR) {
        json = eval(data);
        values = []
        json.forEach(function(item) {values.push(item.missionName)});
        response(values);
    });
}

function addMission(name) {
    $("#missionList").loadTemplate("sessionMissionTemplate.html",
    {
        missionName:name
    }, { append: true});
}

function removeMission(button) {
    $(button).parent().remove()
}

function saveSession() {

    if ($("#sessionHost").val() == null || $("#sessionHost").val() == "") {
        MissionSaveError("Session Host is required");
        return false;
    }
    if ($("#sessionDate").val() == null || $("#sessionDate").val() == "") {
        MissionSaveError("Session Date is required");
        return false;
    }
    if ($("#sessionName").val() == null || $("#sessionName").val() == "") {
        MissionSaveError("Session Name is required");
        return false;
    }
    if ($("#sessionPlayers").val() == null || $("#sessionPlayers").val() == "") {
        MissionSaveError("Session Players is required");
        return false;
    }

    var params = {};
    if(getQueryDict()['sessionId'] != null) {

        params.id = getQueryDict()['sessionId'];
    }
    params['host'] = $("#sessionHost").val();
    params['name'] = $("#sessionName").val();
    params['players'] = $("#sessionPlayers").val();
    params['missionNames'] = [];
    params['date'] = $("#sessionDate").val();
    $("#missionList").find(".missionNameDiv").toArray().forEach(function(item){
        params['missionNames'].push(item.textContent)
    });

    if (params['missionNames'].length == 0) {
        MissionSaveError("Session requires at least one mission");
        return false;
    }

    jQuery.post("editSession", JSON.stringify(params), function(data, status, jqXHR) {

        data = data.replace("location: ", "");
        data = data.replace(/(?:\r\n|\r|\n).*/g, "");
        if(status == "success") {
            window.location.href = "sessions.html?sessionId="+data;
        }else {
            MissionSaveError(data.responseText);
        }
    });
}
function MissionSaveError(string) {
    $("#errorEdit").text(string);
}

loadSession();
