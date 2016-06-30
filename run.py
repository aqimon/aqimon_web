from MakerWeek.main import app, realtimeServer

if __name__=="__main__":
    # if len(sys.argv)==1:
    #     print("Starting server as production")
    #     app.config.from_object(config.ProductionConfig)
    # elif len(sys.argv)==2 and sys.argv[1]=="--dev":
    #     print("Starting server as development")
    #     app.config.from_object(config.DevelopmentConfig)
    # else:
    #     print("""
    #         Invalid arguments.
    #
    #         run.py - run MakerWeek server
    #         Argument:
    #             --dev: run the server as a development server (with debug features enabled)
    #     """)
    realtimeServer.run(app, host="0.0.0.0", debug=True)
