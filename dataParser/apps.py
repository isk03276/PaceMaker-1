from django.apps import AppConfig




class DataparserConfig(AppConfig):
    name = 'dataParser'
    def ready(self):
        from dataParser.parser import ServerParser
        admin_id = "201511868"
        admin_pw = "1019711"
        print("init")
        parser = ServerParser(admin_id, admin_pw)
        for year in range(2009, 2018):
            for semester in range(10, 20):
                parser.save_course_major(year, semester, parser.parse_course_major(year, semester))