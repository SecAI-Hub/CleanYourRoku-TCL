sub init()
    m.top.functionName = "launchSelectedApp"
end sub

function configuredApp(id as string) as boolean
    if Len(id) < 1 or Len(id) > 12 then return false
    for index = 1 to Len(id)
        digit = Mid(id, index, 1)
        if digit < "0" or digit > "9" then return false
    end for
    settings = ParseJson(ReadAsciiFile("pkg:/appsettings.json"))
    if type(settings) <> "roAssociativeArray" then return false
    if type(settings.apps) <> "roArray" then return false
    for each app in settings.apps
        if app.id = id then return true
    end for
    return false
end function

sub launchSelectedApp()
    if not configuredApp(m.top.appId)
        m.top.status = "failed"
        return
    end if
    try
        manager = CreateObject("roAppManager")
        result = manager.LaunchApp(m.top.appId, "", {})
        m.top.status = "returned"
        if type(result) = "Boolean"
            if not result then m.top.status = "failed"
        end if
    catch error
        ' Display a local recovery message; do not log app use or exception data.
        m.top.status = "failed"
    end try
end sub
