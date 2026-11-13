sub Main()
    screen = CreateObject("roSGScreen")
    port = CreateObject("roMessagePort")
    screen.SetMessagePort(port)
    scene = screen.CreateScene("HomeScene")
    if scene = invalid then return
    screen.Show()
    while true
        message = wait(0, port)
        if type(message) = "roSGScreenEvent"
            if message.IsScreenClosed() then return
        end if
    end while
end sub
