import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../components/LoginPage.vue'
import DashboardComponent from '../components/DashboardComponent.vue'
import AdminDashboardComponent from '../components/AdminDashboardComponent.vue'
import LiveQuizComponent from '../components/LiveQuizComponent.vue'
import QuizInstructionsComponent from '../components/QuizInstructionsComponent.vue'
import StartQuizComponent from '../components/StartQuiz.vue'
import ScoresComponent from '../components/ScoresComponent.vue'
import ContactComponent from '../components/ContactComponent.vue'
import PersonalDetailsComponent from '../components/PersonalDetailsComponent.vue'
import AcademicDetailsComponent from '../components/AcademicDetailsComponent.vue'
import EditFieldComponent from '../components/EditFieldComponent.vue'
import QuizFormComponent from '../components/QuizFormComponent.vue'
import SubjectsPage from '../components/SubjectsPage.vue'
import SubjectFormComponent from '../components/SubjectFormComponent.vue'
import ChapterFormComponent from '../components/ChapterFormComponent.vue' // Import ChapterFormComponent
import ChaptersPage from '../components/ChaptersPage.vue' // Import ChaptersPage component (you'll need to create this)
import QuestionsPage from '../components/QuestionsPage.vue' // Import QuestionsPage component (you'll need to create this)
import QuestionFormComponent from '../components/QuestionFormComponent.vue' // Import QuestionsFormComponent
import AdminPersonalDetailsComponent from '../components/AdminPersonalDetailsComponent.vue' // Import AdminPersonalDetailsComponent
import AdminAcademicDetailsComponent from '../components/AdminAcademicDetailsComponent.vue' // Import AdminAcademicDetailsComponent
import TranscriptComponent from '../components/TranscriptComponent.vue' // Import TranscriptComponent

// Route Guard function to check if user is logged in
const requireAuth = (to, from, next) => {
  const token = localStorage.getItem('token')
  if (!token) {
    console.log('No token found, redirecting to login page.')
    next('/')
  } else {
    next()
  }
}
const requireadminAuth = (to, from, next) => {
  const admintoken = localStorage.getItem('adminToken') // Changed from 'token' to 'adminToken'
  if (!admintoken) {
    next('/')
  } else {
    next()
  }
}
const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginPage
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: DashboardComponent,
    beforeEnter: requireAuth
  },
  {
    path: '/admindashboard',
    name: 'AdminDashboard',
    component: AdminDashboardComponent,
    beforeEnter: requireadminAuth
  },
  {
    path: '/adminsubjects',
    name: 'AdminSubjects',
    component: SubjectsPage,
    beforeEnter: requireadminAuth
  },
  {
    path: '/adminchapters',
    name: 'AdminChapters',
    component: ChaptersPage,
    beforeEnter: requireadminAuth
  },
  {
    path: '/adminquestions',
    name: 'AdminQuestions',
    component: QuestionsPage,
    beforeEnter: requireadminAuth
  },
  {
    path: '/livequiz',
    name: 'LiveQuiz',
    component: LiveQuizComponent,
    beforeEnter: requireAuth
  },
  {
    path: '/quizinstructions/:quiz_id',
    name: 'QuizInstructions',
    component: QuizInstructionsComponent,
    props: true
  },
  {
    path: '/startquiz/:quiz_id',
    name: 'StartQuiz',
    component: StartQuizComponent,
    beforeEnter: requireAuth
  },
  {
    path: '/scores/:quiz_id/:uid/:time_taken',
    name: 'Scores',
    component: ScoresComponent,
    props: true,
    beforeEnter: requireAuth
  },
  {
    path: '/transcript/:quiz_id/:uid',
    name: 'Transcript',
    component: ScoresComponent,
    props: true,
    beforeEnter: requireAuth
  },
  {
    path: '/contact',
    name: 'Contact',
    component: ContactComponent,
    beforeEnter: requireAuth
  },
  {
    path: '/admin/quizzes/add',
    name: 'AddQuiz',
    component: QuizFormComponent,
    beforeEnter: requireadminAuth
  },
  {
    path: '/admin/quizzes/edit/:id',
    name: 'EditQuiz',
    component: QuizFormComponent,
    beforeEnter: requireadminAuth
  },
  // Routes for subjects
  {
    path: '/admin/subjects/add',
    name: 'AddSubject',
    component: SubjectFormComponent,
    beforeEnter: requireadminAuth
  },
  {
    path: '/admin/transcript/:quiz_id/:uid',
    name: 'Transcript',
    component: TranscriptComponent,
    props: true,
    beforeEnter: requireadminAuth
  },
  {
    path: '/admin/subjects/edit/:id',
    name: 'EditSubject',
    component: SubjectFormComponent,
    beforeEnter: requireadminAuth
  },
  // Routes for chapters
  {
    path: '/admin/chapters/add',
    name: 'AddChapter',
    component: ChapterFormComponent,
    beforeEnter: requireadminAuth
  },
  {
    path: '/admin/chapters/edit/:id',
    name: 'EditChapter',
    component: ChapterFormComponent,
    beforeEnter: requireadminAuth
  },
  {
    path: '/admin/questions/add',
    name: 'AddQuestion',
    component: QuestionFormComponent,
    beforeEnter: requireadminAuth
  },
  {
    path: '/admin/questions/edit/:id',
    name: 'EditQuestion',
    component: QuestionFormComponent,
    beforeEnter: requireadminAuth
  },
  {
    path: '/personal_details',
    name: 'PersonalDetails',
    component: PersonalDetailsComponent,
    beforeEnter: requireAuth
  },
  {
    path: '/admin/student/personal',
    name: 'AdminStudentPersonal',
    component: AdminPersonalDetailsComponent,
    beforeEnter: requireadminAuth
  },
  {
    path: '/academic_details',
    name: 'AcademicDetails',
    component: AcademicDetailsComponent,
    beforeEnter: requireAuth
  },
  {
    path: '/admin/student/academic',
    name: 'AdminStudentAcademic',
    component: AdminAcademicDetailsComponent,
    beforeEnter: requireadminAuth
  },
  // Add routes for editing personal details fields
  {
    path: '/edit/:field',
    name: 'EditField',
    component: EditFieldComponent,
    props: true,
    beforeEnter: requireAuth
  },
  // Redirect for editcomplete route - typically this would be an API endpoint, not a route
  {
    path: '/editcomplete',
    redirect: '/personal_details'
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router