sub init()
    m.top.scaleRotateCenter = [200, 150]
    m.logo = m.top.FindNode("logo")
    m.name = m.top.FindNode("name")
    m.focus = m.top.FindNode("focus")
    showFocus()
end sub

sub showContent()
    item = m.top.itemContent
    if item = invalid then return
    uri = item.HDPosterUrl
    if Left(uri, 12) <> "pkg:/images/" or Instr(1, uri, "..") > 0
        uri = "pkg:/images/clean_placeholder.png"
    end if
    m.logo.uri = uri
    m.name.text = item.title
    m.focus.blendColor = item.description
end sub

sub showFocus()
    amount = m.top.focusPercent
    if not m.top.gridHasFocus then amount = 0
    m.focus.opacity = amount
    ' Keep the focus border inside the grid cell so outer corners are not clipped.
    m.top.scale = [1.0, 1.0]
    m.top.opacity = 0.78 + 0.22 * amount
end sub
