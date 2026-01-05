<template>
  <div class="grid p-6">
    <!-- Stats Cards -->
    <div class="col-12 md:col-6 lg:col-3">
        <div class="surface-card shadow-2 p-3 border-round">
            <div class="flex justify-content-between mb-3">
                <div>
                    <span class="block text-500 font-medium mb-3">Total Tokens</span>
                    <div class="text-900 font-medium text-xl">{{ totalTokens.toLocaleString() }}</div>
                </div>
                <div class="flex align-items-center justify-content-center bg-blue-100 border-round" style="width:2.5rem;height:2.5rem">
                    <i class="pi pi-database text-blue-500 text-xl"></i>
                </div>
            </div>
            <span class="text-green-500 font-medium">24 new </span>
            <span class="text-500">since last visit</span>
        </div>
    </div>
    <div class="col-12 md:col-6 lg:col-3">
        <div class="surface-card shadow-2 p-3 border-round">
            <div class="flex justify-content-between mb-3">
                <div>
                    <span class="block text-500 font-medium mb-3">Current Cost</span>
                    <div class="text-900 font-medium text-xl">${{ currentCost }}</div>
                </div>
                <div class="flex align-items-center justify-content-center bg-orange-100 border-round" style="width:2.5rem;height:2.5rem">
                    <i class="pi pi-dollar text-orange-500 text-xl"></i>
                </div>
            </div>
             <span class="text-500">Billing cycle ends </span>
             <span class="text-green-500 font-medium">Dec 31</span>
        </div>
    </div>
    <div class="col-12 md:col-6 lg:col-3">
        <div class="surface-card shadow-2 p-3 border-round">
            <div class="flex justify-content-between mb-3">
                <div>
                    <span class="block text-500 font-medium mb-3">Active Models</span>
                    <div class="text-900 font-medium text-xl">{{ activeModelName }}</div>
                </div>
                <div class="flex align-items-center justify-content-center bg-cyan-100 border-round" style="width:2.5rem;height:2.5rem">
                    <i class="pi pi-server text-cyan-500 text-xl"></i>
                </div>
            </div>
            <span class="text-500">Status: </span>
            <span class="text-green-500 font-medium">Operational</span>
        </div>
    </div>
    <div class="col-12 md:col-6 lg:col-3">
        <div class="surface-card shadow-2 p-3 border-round">
            <div class="flex justify-content-between mb-3">
                <div>
                    <span class="block text-500 font-medium mb-3">Plan</span>
                    <div class="text-900 font-medium text-xl">{{ userPlan }}</div>
                </div>
                <div class="flex align-items-center justify-content-center bg-purple-100 border-round" style="width:2.5rem;height:2.5rem">
                    <i class="pi pi-crown text-purple-500 text-xl"></i>
                </div>
            </div>
             <span class="text-500">Upgrade for </span>
             <span class="text-blue-500 font-medium">More Features</span>
        </div>
    </div>

    <!-- Usage Chart -->
    <div class="col-12 lg:col-8">
        <div class="surface-card shadow-2 border-round p-4 h-full">
            <div class="text-xl font-bold text-900 mb-4">Azure Data Usage (Last 7 Days)</div>
            <Chart type="bar" :data="chartData" :options="chartOptions" class="h-30rem" />
        </div>
    </div>

    <!-- News & Updates -->
    <div class="col-12 lg:col-4">
        <div class="surface-card shadow-2 border-round p-4 h-full">
            <div class="flex align-items-center justify-content-between mb-4">
                <span class="text-xl font-bold text-900">Platform News</span>
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
        <div class="surface-card shadow-2 border-round p-4">
            <div class="text-xl font-bold text-900 mb-4">Recent Activity</div>
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
            backgroundColor: '#10b981', 
            data: [0, 0, 0, 0, 0, 0, 0]
        },
        {
            label: 'Cost ($)',
            backgroundColor: '#3b82f6',
            data: [0, 0, 0, 0, 0, 0, 0]
        }
    ]
});

const chartOptions = ref({
    plugins: {
        legend: {
            labels: {
                color: '#495057'
            }
        }
    },
    scales: {
        x: {
            ticks: {
                color: '#495057'
            },
            grid: {
                color: '#ebedef'
            }
        },
        y: {
            ticks: {
                color: '#495057'
            },
            grid: {
                color: '#ebedef'
            }
        }
    }
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
