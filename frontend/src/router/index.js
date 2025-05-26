import { createRouter, createWebHistory } from 'vue-router'
import MainView from '@/views/MainView.vue'
import CommunityView from '@/views/CommunityView.vue'
import FinlifeView from '@/views/FinlifeView.vue'
import StockView from '@/views/StockView.vue'
import LoginView from '@/views/LoginView.vue'
import SignUpView from '@/views/SignUpView.vue'
import FindBankView from '@/views/FindBankView.vue'
import PostCreateView from '@/views/PostCreateView.vue'
import PostDetailView from '@/views/PostDetailView.vue'
import UserProfileCreateView from '@/views/UserProfileCreateView.vue'
import UserprofileUpdateview from '@/views/UserProfileUpdateView.vue'
import UserProfileUpdateInterestView from '@/views/UserProfileUpdateInterestView.vue'
import RankingView from '@/views/RankingView.vue'
import MyAssetsView from '@/views/MyAssetsView.vue'
import MyTradesView from '@/views/MyTradesView.vue'
import { useUserStore } from '@/stores/user'
import KakaoCallbackView from '@/views/KakaoCallbackView.vue'
import EmailVerifyView from '@/views/EmailVerifyView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
  {
      path: '/',
      name: 'main',
      component: MainView,
    },
    {
      path: '/community',
      name: 'community',
      component: CommunityView,
    },
    //게시글 상세조회
    {
      path: '/community/:id',
      name: 'post-detail',
      component: PostDetailView,
    },
    //게시글 생성
    {
    path: '/community/create',
    name: 'post-create',
    component: PostCreateView,
    },
    //게시글 수정
    {
      path: '/community/:id/edit',
      name: 'post-edit',
      component: () => import('@/views/PostEditView.vue')
    },
    {
      path: '/finlife',
      name: 'finlife',
      component: FinlifeView,
    },
    {
      path: '/stock',
      name: 'stock',
      component: StockView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('@/views/SignUpView.vue')
    },
      {
      path: '/findbank',
      name: 'find-bank',
      component: FindBankView,
    },
    // 프로필
      {
      path: '/profile-input',
      name: 'profile-input',
      component: UserProfileCreateView
    },
    {
      path: '/profile/:nickname',
      name: 'user-profile',
      component: () => import('@/views/UserProfileView.vue')
    },
    {
      path: '/profile/:nickname/interestedit',
      name: 'profile-interestedit',
      component: () => import('@/views/UserProfileUpdateInterestView.vue')
    },
    {
      path: '/profile/:nickname/edit',
      name: 'profile-edit',
      component: () => import('@/views/UserProfileUpdateView.vue')
    },
    {
      path: '/profile/create',
      name: 'profile-create',
      component: () => import('@/views/UserProfileCreateView.vue')
    },
    {
      path: '/stock/:code',
      name: 'stock-detail',
      component: () => import('@/views/StockDetailView.vue'),
      props: true
    },
    // 모의투자
    {
      path: '/my-assets',
      name: 'my-assets',
      component: MyAssetsView,
      meta: { requiresAuth: true }  // 라우터 가드용
    },
    {
    path: '/my-trades',
    name: 'my-trades',
    component: MyTradesView,
    meta: { requiresAuth: true }
    },
    {
    path: '/ranking',
    name: 'ranking',
    component: () => import('@/views/RankingView.vue')
    },
    {
    path: '/exchange',
    name: 'point-exchange',
    component: () => import('@/views/PointExchangeView.vue'),
    meta: { requiresAuth: true }
    },
    {
    path: '/accounts/kakao/callback/',
    name: 'kakao-callback',
    component: KakaoCallbackView,
    },
    {
    path: '/accounts/google/callback/',
    name: 'google-callback',
    component: () => import('@/views/GoogleCallbackView.vue'),
    },
    {
    path: '/accounts/naver/callback/',
    name: 'naver-callback',
    component: () => import('@/views/NaverCallbackView.vue'),
    },
    {
      path: '/verify-email/:code',
      name: 'verify-email',
      component: EmailVerifyView 
    },
  
  ],
})
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.token) {
    next({
      name: 'login',
      query: { next: to.fullPath } 
    })
  } else {
    next()
  }
})
export default router
