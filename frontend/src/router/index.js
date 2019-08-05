import Vue from 'vue'
import Router from 'vue-router'
const routerOptions = [
  { path: '/', component: 'buckets/List' },
  { path: '/buckets/new', component: 'buckets/Create' },
  { path: '/uploads', component: 'Upload' },
  { path: '/transfers', component: 'transfers/List' },
  { path: '/transfers/new', component: 'transfers/Create' },
  { path: '/about', component: 'About' },
  { path: '*', component: 'NotFound' }
]
const routes = routerOptions.map(route => {
  return {
    ...route,
    component: () => import(`@/components/${route.component}.vue`)
  }
})
Vue.use(Router)
export default new Router({
  routes,
  mode: 'history'
})
