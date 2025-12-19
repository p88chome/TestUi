import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'
import './style.css'
import App from './App.vue'
import router from './router'

import Tooltip from 'primevue/tooltip';

import { createPinia } from 'pinia'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: false || 'none', // Force Aura Light Mode by default, unless user wants dark
            cssLayer: {
                name: 'primevue',
                order: 'primevue, app-styles' // Establish layer order
            }
        }
    }
})
app.directive('tooltip', Tooltip);

app.mount('#app')
