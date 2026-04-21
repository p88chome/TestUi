import { createApp } from 'vue'
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import 'primeicons/primeicons.css'
import 'primeflex/primeflex.css'
import './style.css'
import './deloitte-theme.css'
import App from './App.vue'
import router from './router'

import Tooltip from 'primevue/tooltip';
import ToastService from 'primevue/toastservice';

import { createPinia } from 'pinia'

import {
    Chart as ChartJS,
    Title,
    Tooltip as ChartTooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale,
    LineElement,
    PointElement,
    ArcElement,
} from 'chart.js';

ChartJS.register(
    Title,
    ChartTooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale,
    LineElement,
    PointElement,
    ArcElement,
);

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ToastService);
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
