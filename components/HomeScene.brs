sub init()
    m.settings = readSettings()
    m.apps = m.settings.apps
    m.grid = m.top.FindNode("grid")
    m.status = m.top.FindNode("status")
    m.top.FindNode("title").text = m.settings.title
    m.top.FindNode("clock").visible = m.settings.show_clock
    m.top.FindNode("date").visible = m.settings.show_clock and m.settings.show_date
    content = CreateObject("roSGNode", "ContentNode")
    for each app in m.apps
        item = content.CreateChild("ContentNode")
        item.id = app.id
        item.title = app.name
        item.HDPosterUrl = localImage(app.icon)
        item.description = m.settings.accent_color
    end for
    columns = m.apps.Count()
    if columns > 4 then columns = 4
    rows = 1
    if m.apps.Count() > columns then rows = 2
    width = columns * 400 + (columns - 1) * 36
    m.grid.numColumns = columns
    m.grid.numRows = rows
    m.grid.translation = [(1920 - width) / 2, 350]
    if rows = 2 then m.grid.translation = [(1920 - width) / 2, 280]
    m.grid.content = content
    m.grid.ObserveField("itemSelected", "onAppSelected")
    m.grid.SetFocus(true)
    m.timer = m.top.FindNode("clockTimer")
    m.timer.ObserveField("fire", "updateClock")
    if m.settings.show_clock then m.timer.control = "start"
    updateClock()
end sub

function localImage(uri as string) as string
    if Left(uri, 12) <> "pkg:/images/" then return "pkg:/images/clean_placeholder.png"
    if Instr(1, uri, "..") > 0 then return "pkg:/images/clean_placeholder.png"
    return uri
end function

function readSettings() as object
    fallback = { title: "Your apps", show_clock: true, show_date: true, clock_format: "12h", accent_color: "0xA9C7FFFF", apps: [{name: "Netflix", id: "12", icon: "pkg:/images/clean_placeholder.png"}, {name: "Hulu", id: "2285", icon: "pkg:/images/clean_placeholder.png"}] }
    settings = ParseJson(ReadAsciiFile("pkg:/appsettings.json"))
    if type(settings) <> "roAssociativeArray" then return fallback
    if type(settings.apps) <> "roArray" then return fallback
    if settings.apps.Count() < 1 or settings.apps.Count() > 12 then return fallback
    return settings
end function

sub onAppSelected(event as object)
    index = event.GetData()
    if index < 0 or index >= m.apps.Count() then return
    if m.launcher <> invalid
        if m.launcher.state = "RUN" then return
    end if
    m.status.text = "Opening " + m.apps[index].name + "..."
    m.launcher = CreateObject("roSGNode", "Launcher")
    m.launcher.ObserveField("status", "onLaunchStatus")
    m.launcher.appId = m.apps[index].id
    m.launcher.control = "RUN"
end sub

sub onLaunchStatus(event as object)
    if event.GetData() = "failed"
        m.status.text = "This app could not open. Press Home and try it from Roku Home."
    else
        m.status.text = ""
    end if
end sub

sub updateClock()
    now = CreateObject("roDateTime")
    now.ToLocalTime()
    hour = now.GetHours()
    suffix = ""
    if m.settings.clock_format = "12h"
        suffix = " AM"
        if hour >= 12 then suffix = " PM"
        hour = hour mod 12
        if hour = 0 then hour = 12
    end if
    minute = now.GetMinutes().ToStr()
    if Len(minute) = 1 then minute = "0" + minute
    m.top.FindNode("clock").text = hour.ToStr() + ":" + minute + suffix
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    m.top.FindNode("date").text = now.GetWeekday() + ", " + months[now.GetMonth() - 1] + " " + now.GetDayOfMonth().ToStr()
end sub
