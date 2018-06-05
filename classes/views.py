from django.shortcuts import render
from dataParser.models import (StudentInfo, Course, StudentGrade, Subject_desription,
                               Core_Competence, Learning_Objectives, Lecture_method,
                               Assignment, School_composition_ratio, Weekly_course_contents, Book)
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from datetime import datetime
from django.db.models import Q
from grades.views import getIntScore
import operator
from .models import *


def get_score_sum(hukbun):
    s = hukbun
    sum = 0
    scorelist = StudentGrade.objects.filter(hukbun=s).filter(valid='유효')
    scorelist = scorelist.exclude(grade__contains='P').values_list('score', flat=True)
    for i in scorelist:
        sum = sum + int(i)

    return sum

def get_avgGrade(hukbun):
    s = hukbun
    avg = 0.0
    sum = 0.0
    gradelist = StudentGrade.objects.filter(hukbun=s).filter(valid='유효').filter(
        Q(grade='A+') | Q(grade='A') | Q(grade='B+') | Q(grade='B') | Q(grade='C+') | Q(grade='C') | Q(grade='D+') | Q(
            grade='D'))
    for i in range(0, gradelist.count()):
        temp = getIntScore(gradelist[i].grade) * int(gradelist[i].score)
        sum = sum + temp
    score_sum = get_score_sum(hukbun)
    avg = sum / score_sum
    avg = round(avg, 3)
    return avg

# Create your views here.
class majorLV(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'classes/majorAll.html'
    context_object_name = 'subjects'
    paginate_by = 20

    def get_queryset(self):
        return Course.objects.filter(year=datetime.today().year).order_by('grade', 'subjectName')


class majorDV(LoginRequiredMixin, TemplateView):
    template_name = 'classes/majorDetail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(majorDV, self).get_context_data(**kwargs)
        # Add in a QuerySet of all the books

        # Subject_desription, Core_Competence, Learning_Objectives,
        # Lecture_method, Assignment, School_composition_ratio, Weekly_course_contents, Book
        try:
            context['subjectName'] = Course.objects.get(id=context['pk'])
        except:
            context['subjectName'] = None
        try:
            context['subjectDescriptions'] = Subject_desription.objects.filter(course=context['pk'])
        except:
            context['subjectDescriptions'] = None
        try:
            context['coreCompetences'] = Core_Competence.objects.filter(id=context['pk'])
        except:
            context['coreCompetences'] = None
        try:
            context['learningObjectives'] = Learning_Objectives.objects.filter(id=context['pk'])
        except:
            context['learningObjectives'] = None
        try:
            context['lectureMethods'] = Lecture_method.objects.filter(id=context['pk'])
        except:
            context['lectureMethods'] = None
        try:
            context['assignments'] = Assignment.objects.filter(id=context['pk'])
        except:
            context['assignments'] = None
        try:
            context['schoolCompositionRatios'] = School_composition_ratio.objects.filter(id=context['pk'])
        except:
            context['schoolCompositionRatios'] = None
        try:
            context['weeklyCourseContents'] = Weekly_course_contents.objects.filter(id=context['pk'])
        except:
            context['weeklyCourseContents'] = None
        try:
            context['books'] = Book.objects.filter(id=context['pk'])
        except:
            context['books'] = None
        return context


class SpecialCourseRecommandView(LoginRequiredMixin, TemplateView):
    template_name = "classes/special_recommand.html"

    def get_context_data(self, **kwargs):
        context = super(SpecialCourseRecommandView, self).get_context_data(**kwargs)
        student = StudentInfo.objects.get(hukbun=self.request.user.hukbun)

        context['specialCoursesDic'] = self.getSpecialCase()
        return context

    def getSpecialCase(self):  # 자신의 학년과 맞지 않게 다른 학년의 수업을 들은 경우를 보여줌
        """
        grade에 yearNsemester에서 yyyy년도s학기 정보가 나옴.
        filter로 학생의 모든 grade정보를 가져와서 yearNsemester를 중복제거한 리스트로 보자. 이의 개수 하나당 학기 하나 -> 들었을 때 학년을 알 수 있다.
        얻어진 학년과 studentGrade에서 year,semester,subject_code를 이용해서 얻어진 course의 학년과 비교해서 다를 경우
            과목, 들었을 때의 학년 정보를 딕셔너리화해서 저장하자
        """
        specialCoursesDic = dict()
        for student in StudentInfo.objects.all():  # 모든 학생
            studentGrades = StudentGrade.objects.filter(hukbun=student.hukbun)  # 학생의 grade 쿼리셋
            semesterList = studentGrades.values_list('yearNsemester', flat=True)  # 학생의 학기 list
            semesterList = sorted(list(set(semesterList)))  # 중복제거하여 정렬
            for grade in studentGrades:  # 학생이 과목을 들었을 때 학년이 일치하는 지 확인한다.
                semester = semesterList.index(  # semester = 학생이 들었던 해당 수업을 들었을 때의 학기
                    grade.yearNsemester)  # 해당 과목의 학기가 semesterList에서 검색해 index를 반환한다 => 해당 과목이 몇학기에 들은 과목인가 검사
                courses = Course.objects.filter(subjectName=grade.subject)  # 해당 수업의 이름과 동일한 course 쿼리셋 가져오기
                if courses.count() == 0:  # 만약 해당하는 수업이 없다면 걍 무시
                    continue
                courseInfoes = []
                course = courses.first()
                courseGrade = courses.first().grade  # 수업을 대충 하나 가져와서 추천 학년을 저장
                if int(semester / 2) + 1 != int(courseGrade):  # 추천 학년대로 과목을 안 들었을 경우
                    courseInfoes.append(course.grade)  # 추천 학년
                    courseInfoes.append(int(semester / 2) + 1)  # 들었던 학년
                    courseInfoes.append(course.eisu)  # 이수
                    courseInfoes.append(course.score)  # 학점
                    specialCoursesDic[grade] = courseInfoes

        # 이제 중복된 전공을 없애고 카운트하는게 필요
        grades = list(specialCoursesDic.keys())  # grade 객체 리스트
        gradesSubjectName = []
        resultDic = specialCoursesDic.copy()
        for grade in grades:  # grades := grades의 과목 이름 리스트
            gradesSubjectName.append(grade.subject)
        notDuplicatedGrades = list(set(gradesSubjectName))
        for notDuplicatedGrade in notDuplicatedGrades:
            count = 0
            for grade in specialCoursesDic.keys():
                if notDuplicatedGrade == grade.subject:
                    if count > 0:
                        del resultDic[grade]
                    count += 1
            grades = list(resultDic.keys())  # grade 객체 리스트
            for grade in grades:
                if grade.subject == notDuplicatedGrade:
                    resultDic[grade].append(count)

        return resultDic

class TopStudentRecommandView(LoginRequiredMixin, TemplateView):
    template_name = "classes/topStudent_recommand.html"

    def get_context_data(self, **kwargs):
        context = super(TopStudentRecommandView, self).get_context_data(**kwargs)
        context['Top5Grades'] = self.getTop5Grades()

        return context

    def getTop5Grades(self):
        allStudentHukbun = StudentGrade.objects.all().values_list('hukbun', flat=True) #모든 학생의 학번을 가져옴
        allStudentScoreDic = dict() #모든 학생의 총점을 저장할 dic
        for hukbun in allStudentHukbun: #각 학생의 총점 저장
            allStudentScoreDic[hukbun] = 3#get_avgGrade(hukbun) 너무 느려ㅠ
        sortedAllStudentScoreList = sorted(allStudentScoreDic.items(), key = operator.itemgetter(1), reverse=True) #value를 기준으로 내림차순 정렬
        topStudentGradesScoreDic = dict()
        valueDict = dict()
        for topStudent in sortedAllStudentScoreList[:5]: #top 5학생의 [학번,총점]을 가져옴
            valueDict[StudentGrade.objects.filter(hukbun=topStudent[0]).order_by('yearNsemester', 'subject')] = topStudent[1]
            topStudentGradesScoreDic[topStudent[0]] = valueDict

        return topStudentGradesScoreDic
class RetakeRecommandView(LoginRequiredMixin, TemplateView):
    template_name = "classes/retaking_recommand.html"
    """
    1. 내가 들을 수 있는 아직 듣지 않은 전공 수업들 보여줌
    2. 제일 잘 나가는 타 학생의 전공 수업들을 보여줌
    3. 재수강 추천 과목을 보여줌 (낮은 성적부터)
    """
    topStudentCourses = []

    def get_context_data(self, **kwargs):
        context = super(RetakeRecommandView, self).get_context_data(**kwargs)
        student = StudentInfo.objects.get(hukbun=self.request.user.hukbun)
        takenCoursesGrades = StudentGrade.objects.filter(hukbun=student.hukbun)
        # self.getRetakeCourses(student, takenCoursesGrades)
        context['retakeGrades'] = self.getRetakeCourses(student, takenCoursesGrades).order_by('yearNsemester',
                                                                                              'subject')

        return context

    def getRetakeCourses(self, student, takenCoursesGrades):
        takenCoursesScoresDic = dict()
        retakeCoursesName = []
        canceledList = []
        for takenCourseGrade in takenCoursesGrades:  # 딕셔너리에 과목코드:(int)점수 저장
            try:
                if getIntScore(takenCourseGrade.grade) <= 2.5:  # 2.5
                    takenCoursesScoresDic[takenCourseGrade.subject] = getIntScore(takenCourseGrade.grade)
            except:
                continue

        sortedTakenCoursesScoresList = sorted(takenCoursesScoresDic.items(), key=lambda x: x[1]) #정렬
        for sortedTakenCoursesScores in sortedTakenCoursesScoresList:
            retakeCoursesName.append(sortedTakenCoursesScores[0])

        resultGrades = StudentGrade.objects.filter(subject__in=retakeCoursesName,
                                                   hukbun=student.hukbun)  # 재수강 추천 과목 쿼리셋을 리턴
        for resultGrade in resultGrades:
            try:
                if getIntScore(resultGrade.grade) >= 2.5:
                    resultGrades.difference(resultGrades.filter(subject=resultGrade.subject))
            except:
                continue
        canceledList = resultGrades.filter(valid='재수강무효').values_list('subject')
        return resultGrades.difference(resultGrades.filter(valid='재수강무효')).difference(
            resultGrades.filter(subject__in=canceledList))

    def getTopStudentCourses(self):
        # 지훈이가 하길 기다리자
        pass

class preCourseRecommandView(LoginRequiredMixin, TemplateView):
    template_name = "classes/pre_recommand.html"

    def get_context_data(self, **kwargs):
        context = super(preCourseRecommandView, self).get_context_data(**kwargs)
        context['necessaryGrades'] = self.getNecessrayGrades()
        context['promotedGrades'] = self.getPromotedGrades()
        return context

    def getNecessrayGrades(self): #선수 과목
        student = self.request.user #현재 로그인된 학생
        currentSemester = len((list(set(StudentGrade.objects.all().values_list('yearNsemester'))))) #학생이 현재까지 들은 학기
        if(currentSemester%2 == 1): #홀수라면
            nextGrade = (currentSemester+1)/2
        else: #짝수일 경우
            nextGrade = currentSemester/2 + 1
        recommendedCoursesNameList = Course.objects.filter(grade=nextGrade).values_list('subjectName') #해당 학년에 해당하는 추천 course 이름 리스트를 가져옴
        recommendedCoursesNameList = list(set(recommendedCoursesNameList)) #중복제거
        necessrayCourses = necessaryCourse.objects.filter(childCourse__in=recommendedCoursesNameList)
        necessaryCourseNameList = []
        for necessaryCourse1 in necessrayCourses:
            if necessaryCourse1.childCourse.subjectName in recommendedCoursesNameList:
                necessaryCourseNameList.append(necessaryCourse1.childCourse.subjectName)

        return StudentGrade.objects.filter(subject__in=necessaryCourseNameList).order_by('yearNsemester', 'subject')

    def getPromotedGrades(self): #권장 과목
        student = self.request.user  # 현재 로그인된 학생
        currentSemester = len((list(set(StudentGrade.objects.all().values_list('yearNsemester')))))  # 학생이 현재까지 들은 학기
        if (currentSemester % 2 == 1):  # 홀수라면
            nextGrade = (currentSemester + 1) / 2
        else:  # 짝수일 경우
            nextGrade = currentSemester / 2 + 1
        recommendedCoursesNameList = Course.objects.filter(grade=nextGrade).values_list(
            'subjectName')  # 해당 학년에 해당하는 추천 course 이름 리스트를 가져옴
        recommendedCoursesNameList = list(set(recommendedCoursesNameList))  # 중복제거
        promotedCourses = promotedCourse.objects.filter(childCourse__in=recommendedCoursesNameList)
        promotedCourseNameList = []
        for promotedCourse1 in promotedCourses:
            if promotedCourse1.childCourse.subjectName in recommendedCoursesNameList:
                promotedCourseNameList.append(promotedCourse1.childCourse.subjectName)

        return StudentGrade.objects.filter(subject__in=promotedCourseNameList).order_by('yearNsemester', 'subject')