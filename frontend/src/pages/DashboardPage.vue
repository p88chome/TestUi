<template>
  <div class="grid p-6">
    <!-- Page Header -->
    <div class="col-12 mb-4">
        <h1 class="text-heading-xl m-0 deloitte-green-dot">Dashboard</h1>
        <p class="text-body-lg mt-2 mb-0">Overview of your AI platform consumption and activities.</p>
    </div>

    <!-- Stats Cards - Deloitte Style -->
    <div class="col-12 md:col-6 lg:col-3">
        <div class="deloitte-card p-4">
            <div class="flex align-items-center gap-3 mb-3">
                <div class="deloitte-icon-circle">
                    <i class="pi pi-database text-xl"></i>
                </div>
                <div class="flex-1">
                    <span class="block text-body-md mb-1">Total Tokens</span>
                    <div class="text-heading-md">{{ totalTokens.toLocaleString() }}</div>
                </div>
            </div>
            <div class="flex align-items-center justify-content-between">
                <span class="text-body-sm">
                    <span class="status-success font-semibold">+24</span> since last visit
                </span>
            </div>
            <div class="deloitte-accent-bar mt-3"></div>
        </div>
    </div>
    <div class="col-12 md:col-6 lg:col-3">
        <div class="deloitte-card p-4">
            <div class="flex align-items-center gap-3 mb-3">
                <div class="deloitte-icon-circle deloitte-icon-circle--green">
                    <i class="pi pi-dollar text-xl"></i>
                </div>
                <div class="flex-1">
                    <span class="block text-body-md mb-1">Current Cost</span>
                    <div class="text-heading-md">${{ currentCost }}</div>
                </div>
            </div>
            <div class="flex align-items-center justify-content-between">
                <span class="text-body-sm">Billing cycle ends <span class="font-semibold">Dec 31</span></span>
            </div>
            <div class="deloitte-accent-bar mt-3"></div>
        </div>
    </div>
    <div class="col-12 md:col-6 lg:col-3">
        <div class="deloitte-card p-4">
            <div class="flex align-items-center gap-3 mb-3">
                <div class="deloitte-icon-circle">
                    <i class="pi pi-server text-xl"></i>
                </div>
                <div class="flex-1">
                    <span class="block text-body-md mb-1">Active Models</span>
                    <div class="text-heading-md">{{ activeModelName }}</div>
                </div>
            </div>
            <div class="flex align-items-center justify-content-between">
                <span class="text-body-sm">Status: <span class="status-success font-semibold">Operational</span></span>
            </div>
            <div class="deloitte-accent-bar mt-3"></div>
        </div>
    </div>
    <div class="col-12 md:col-6 lg:col-3">
        <div class="deloitte-card p-4">
            <div class="flex align-items-center gap-3 mb-3">
                <div class="deloitte-icon-circle">
                    <i class="pi pi-crown text-xl"></i>
                </div>
                <div class="flex-1">
                    <span class="block text-body-md mb-1">Plan</span>
                    <div class="text-heading-md">{{ userPlan }}</div>
                </div>
            </div>
            <div class="flex align-items-center justify-content-between">
                <span class="text-body-sm">Upgrade for <span class="status-info font-semibold">More Features</span></span>
            </div>
            <div class="deloitte-accent-bar mt-3"></div>
        </div>
    </div>

    <!-- Usage Chart -->
    <div class="col-12 lg:col-8">
        <div class="deloitte-card p-4 h-full">
            <div class="text-heading-lg mb-4 deloitte-green-dot">Azure Data Usage (Last 7 Days)</div>
            <Chart type="bar" :data="chartData" :options="chartOptions" class="h-30rem" />
        </div>
    </div>

    <!-- News & Updates -->
    <div class="col-12 lg:col-4">
        <div class="deloitte-card p-4 h-full">
            <div class="flex align-items-center justify-content-between mb-4">
                <span class="text-heading-lg deloitte-green-dot">Platform News</span>
                <Button v-if="isAdmin" icon="pi pi-plus" class="p-button-rounded p-button-text" @click="showPublishDialog = true" tooltip="Publish News" />
            </div>

             <div class="flex flex-column gap-3">
                 <div v-for="news in newsItems" :key="news.id" class="border-bottom-1 surface-border pb-3">
                    <div class="font-bold text-blue-900 mb-1">{{ news.title }}</div>
                    <div class="text-700 block mb-2" style="white-space: pre-wrap;">{{ news.content }}</div>
                    <small class="text-500">{{ formatDate(news.created_at) }}</small>
                 </div>
                 
                 <div v-if="newsItems.length === 0" class="text-center text-500">
                    No active announcements.
                 </div>
             </div>
        </div>
    </div>
    
    <!-- Admin Publish Dialog -->
    <Dialog v-model:visible="showPublishDialog" header="Publish News" :modal="true" class="p-fluid">
        <div class="field">
            <label for="title">Title</label>
            <InputText id="title" v-model="newsForm.title" />
        </div>
        <div class="field">
            <label for="content">Content</label>
            <Textarea id="content" v-model="newsForm.content" rows="5" />
        </div>
        <template #footer>
            <Button label="Cancel" icon="pi pi-times" class="p-button-text" @click="showPublishDialog = false" />
            <Button label="Publish" icon="pi pi-check" @click="publishNews" autofocus />
        </template>
    </Dialog>
    
     <!-- Recent Activity -->
    <div class="col-12">
        <div class="deloitte-card p-4">
            <div class="text-heading-lg mb-4 deloitte-green-dot">Recent Activity</div>
            <DataTable :value="recentActivity" responsiveLayout="scroll">
                <Column field="action" header="Action"></Column>
                <Column field="app" header="Application">
                    <template #body="slotProps">
                        <Tag :value="slotProps.data.app" :severity="getAppSeverity(slotProps.data.app)" />
                    </template>
                </Column>
                <Column field="details" header="Details"></Column>
                <Column field="time" header="Time"></Column>
                 <Column field="cost" header="Estimated Cost">
                     <template #body="slotProps">
                        {{ slotProps.data.cost }}
                     </template>
                 </Column>
            </DataTable>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import apiClient from '../api/client';
import Chart from 'primevue/chart';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';

// Register ChartJS components
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const auth = useAuthStore();
const userPlan = computed(() => auth.state.user?.plan_name || 'Starter');
const isAdmin = computed(() => auth.state.user?.is_superuser);

import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
// import { useToast } from 'primevue/usetoast';

// const toast = useToast(); // Removed unused toast to fix build error 
const showPublishDialog = ref(false);
const newsItems = ref<any[]>([]);
const newsForm = ref({ title: '', content: '' });

const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString() + ' ' + new Date(dateStr).toLocaleTimeString();
};

const loadNews = async () => {
    try {
        const res: any = await apiClient.get('/news');
        newsItems.value = res || [];
    } catch (e) {
        console.error("Failed to load news", e);
    }
};

const publishNews = async () => {
    try {
        await apiClient.post('/news', newsForm.value);
        showPublishDialog.value = false;
        newsForm.value = { title: '', content: '' };
        loadNews(); // Reload
    } catch (e) {
        console.error("Failed to publish news", e);
        alert("Failed to publish news");
    }
};

const totalTokens = ref(0);
const currentCost = ref('0.00');
const activeModelName = ref('Loading...');

// Chart Data (Initial Empty)
const chartData = ref({
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
        {
            label: 'Tokens',
            backgroundColor: '#86BC25',
            borderRadius: 2,
            data: [0, 0, 0, 0, 0, 0, 0]
        },
        {
            label: 'Cost ($)',
            backgroundColor: '#2C2C2C',
            borderRadius: 2,
            data: [0, 0, 0, 0, 0, 0, 0]
        }
    ]
});

const chartOptions = ref({
    plugins: {
        legend: {
            labels: {
                color: '#2C2C2C',
                font: { family: 'Inter, system-ui, sans-serif', size: 12, weight: '600' },
                usePointStyle: true,
                pointStyleWidth: 8
            }
        }
    },
    scales: {
        x: {
            ticks: { color: '#666666', font: { family: 'Inter, system-ui, sans-serif', size: 11 } },
            grid: { color: '#F0F0F0', drawBorder: false }
        },
        y: {
            ticks: { color: '#666666', font: { family: 'Inter, system-ui, sans-serif', size: 11 } },
            grid: { color: '#F0F0F0', drawBorder: false }
        }
    },
    borderRadius: 2
});

// Recent Activity Data
const recentActivity = ref([]);

const loadStats = async () => {
    try {
        // Fetch from new Stats API
        const res: any = await apiClient.get('/stats/dashboard');
        
        totalTokens.value = res.total_tokens || 0;
        currentCost.value = res.current_cost || '0.00';
        
        // Update Chart
        if (res.chart_data && res.chart_data.labels && res.chart_data.labels.length > 0) {
            chartData.value = res.chart_data;
        }
        
        // Update Activity
        recentActivity.value = res.recent_activity || [];
        
        // Update Active Model
        activeModelName.value = res.active_model || 'Unknown';
        
    } catch (e) {
        console.error("Failed to load dashboard stats", e);
    }
};

onMounted(() => {
    loadStats();
    loadNews();
});

const getAppSeverity = (app: string) => {
    if (app === 'Enterprise Chat') return 'success';
    if (app === 'Contract Helper') return 'info';
    if (app === 'Expense Helper') return 'warning';
    return 'info'; 
};
</script>
