from MakerWeek import app, realtimeServer

if __name__=="__main__":
    realtimeServer.run(app, host="0.0.0.0", debug=True)