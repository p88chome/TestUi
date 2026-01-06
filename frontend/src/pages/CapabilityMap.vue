<template>
  <div class="capability-map-page">
    
    <!-- 1. Header Section -->
    <div class="header-section">
      <h1 class="page-title">核心能力地圖 (Capability Map)</h1>
      <p class="page-subtitle">
        選擇業務流程，檢視對應的 AI 核心元件
      </p>
    </div>

    <!-- 2. Business Flow Selector -->
    <div class="flow-selector-area">
      <div class="flow-left">
        <div class="section-label">業務流程</div>
        <div class="flow-buttons">
          <button
            v-for="flow in flows"
            :key="flow.id"
            @click="activateFlow(flow.id)"
            class="flow-btn"
            :class="{ 'active': activeFlow === flow.id }"
          >
            {{ flow.label }}
          </button>
        </div>
      </div>

      <!-- Navigation Button (Right aligned or next to flows) -->
      <button 
        v-if="currentFlow?.routeName"
        class="nav-action-btn"
        @click="navigateToApp(currentFlow.routeName)"
      >
        <i class="pi pi-external-link" style="margin-right: 0.5rem"></i>
        前往 {{ currentFlow.label }}
      </button>
    </div>

    <!-- 3. Component Library Section -->
    <div class="library-section">
      <h2 class="library-title">AI 標準元件庫</h2>
      
      <!-- Grid -->
      <div class="component-grid">
        <div
          v-for="comp in components"
          :key="comp.id"
          class="component-card"
          :class="{ 'active': isComponentActive(comp.id) }"
          @mouseenter="hoveredCompId = comp.id"
          @mouseleave="hoveredCompId = null"
        >
          <!-- Active Indicator Dot -->
          <div v-if="isComponentActive(comp.id)" class="active-indicator">
             <i class="pi pi-check-circle"></i>
          </div>

          <!-- Icon -->
          <div class="card-icon">
            <i :class="comp.icon"></i>
          </div>
          
          <!-- Text -->
          <div class="card-content">
             <span class="card-label">
               {{ comp.label }}
             </span>
             <!-- Description is now hidden by default or used for search, 
                  User wants popup on hover only. -->
             <!-- <span class="card-desc">{{ comp.description }}</span> -->
          </div>

          <!-- Hover Tooltip/Popup -->
          <div v-if="hoveredCompId === comp.id" class="hover-popup">
            <div class="popup-title">{{ comp.label }}</div>
            <div class="popup-desc">{{ comp.description }}</div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { components, flows } from '../data/capabilityMap';

const router = useRouter();
const activeFlow = ref<string | null>(flows[0]?.id || null);
const hoveredCompId = ref<string | null>(null);

const activateFlow = (flowId: string) => {
  activeFlow.value = flowId;
};

const currentFlow = computed(() => flows.find(f => f.id === activeFlow.value));

const isComponentActive = (compId: string) => {
  if (!activeFlow.value) return false;
  const flow = flows.find(f => f.id === activeFlow.value);
  return flow ? flow.activeComponents.includes(compId) : false;
};

const navigateToApp = (routeName: string) => {
  router.push({ name: routeName });
};
</script>

<style scoped>
/* Page Layout */
.capability-map-page {
  width: 100%;
  min-height: 100%;
  background-color: #f8fafc; /* Lighter, cleaner gray */
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
  padding: 3rem;
  box-sizing: border-box;
}

/* Header */
.header-section {
  margin-bottom: 3rem;
  padding-left: 0.5rem;
}

.page-title {
  font-size: 2rem;
  font-weight: 800;
  color: #1a1a1a;
  margin: 0 0 0.5rem 0;
  letter-spacing: -0.03em;
}

.page-subtitle {
  color: #64748b;
  font-size: 0.95rem;
  font-weight: 400;
  margin: 0;
}

/* Flow Selector */
.flow-selector-area {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 3.5rem;
  justify-content: space-between;
}

@media (min-width: 768px) {
  .flow-selector-area {
    flex-direction: row;
    align-items: center;
  }
}

.flow-left {
  display: flex;
  gap: 1.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.section-label {
  font-weight: 700;
  font-size: 1.125rem;
  color: #1e293b;
  white-space: nowrap;
}

.flow-buttons {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
}

/* Flow Buttons */
.flow-btn {
  padding: 0.6rem 1.25rem;
  border-radius: 12px;
  font-size: 0.9rem;
  font-weight: 600;
  border: 1px solid transparent; /* Clean look */
  background-color: white;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 2px rgba(0,0,0,0.05); /* Subtle shadow */
}

.flow-btn:hover {
  background-color: #f1f5f9;
  color: #334155;
  transform: translateY(-1px);
}

.flow-btn.active {
  background-color: #86BC25;
  color: white;
  box-shadow: 0 4px 12px rgba(134, 188, 37, 0.3); /* Green glow */
  transform: translateY(-1px);
}

/* Navigation Action Button */
.nav-action-btn {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  background-color: #1e293b;
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}

.nav-action-btn:hover {
  background-color: #86BC25;
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(134, 188, 37, 0.25);
}

/* Library Section */
.library-section {
  width: 100%;
}

.library-title {
  text-align: left;
  color: #1e293b;
  font-weight: 700;
  font-size: 1.25rem;
  margin-bottom: 2rem;
  padding-left: 1rem;
  border-left: 4px solid #86BC25;
}

/* Grid */
.component-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  width: 100%;
}

@media (min-width: 768px) {
  .component-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .component-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* Component Cards - Dribbble Style */
.component-card {
  position: relative;
  display: flex;
  align-items: center;
  padding: 1.5rem;
  background-color: white;
  border-radius: 16px; /* Larger radius */
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 120px;
  cursor: default;
  
  /* Inactive: Clean shadow, no border */
  border: 1px solid rgba(226, 232, 240, 0.6);
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
  
  /* Less opacity for inactive to indicate state, but keeping it clean */
  opacity: 0.5;
  filter: grayscale(1);
}

.component-card:hover {
  opacity: 1;
  filter: grayscale(0);
  transform: translateY(-4px); /* Lift */
  box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.1);
  z-index: 20;
}

/* Active Card State */
.component-card.active {
  border: 1px solid #86BC25; /* Subtle green border */
  opacity: 1;
  filter: grayscale(0);
  box-shadow: 0 8px 16px -4px rgba(134, 188, 37, 0.15); /* Green tinted shadow */
  transform: translateY(0); /* Active creates base state */
  z-index: 10;
}

.component-card.active:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -6px rgba(134, 188, 37, 0.25);
}

/* Icon Container */
.card-icon {
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1.25rem;
  font-size: 1.5rem;
  transition: all 0.3s;
  
  /* Inactive Icon Background */
  background-color: #f1f5f9;
  color: #94a3b8; 
}

.component-card:hover .card-icon {
  background-color: #e2e8f0;
  color: #64748b;
}

.component-card.active .card-icon {
  /* Active Icon Background: Brand Tint */
  background-color: rgba(134, 188, 37, 0.1); 
  color: #86BC25;
}

/* Content */
.card-content {
  display: flex;
  flex-direction: column;
}

.card-label {
  font-size: 1.125rem;
  font-weight: 700;
  line-height: 1.2;
  transition: color 0.3s;
  color: #94a3b8; /* Inactive text */
}

.component-card.active .card-label {
  color: #1e293b; /* Active text */
}

/* Hover Popup */
.hover-popup {
  position: absolute;
  bottom: calc(100% + 10px);
  left: 50%;
  transform: translateX(-50%);
  width: 220px;
  background-color: #0f172a;
  color: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  text-align: left;
  animation: popIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.hover-popup::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -6px;
  border-width: 6px;
  border-style: solid;
  border-color: #0f172a transparent transparent transparent;
}

.popup-title {
  font-weight: 700;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
  color: #86BC25;
}

.popup-desc {
  font-size: 0.8rem;
  line-height: 1.5;
  color: #cbd5e1;
}

@keyframes popIn {
  from { opacity: 0; transform: translate(-50%, 8px) scale(0.95); }
  to { opacity: 1; transform: translate(-50%, 0) scale(1); }
}

/* Indicator */
.active-indicator {
  position: absolute;
  top: -6px;
  right: -6px;
  background: white;
  border-radius: 50%;
  padding: 2px;
  color: #86BC25;
  font-size: 1.1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 5;
}
</style>


